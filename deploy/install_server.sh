#!/usr/bin/env bash
# ============================================================
#  第二大脑 —— 服务器初始化（Nginx + systemd + 依赖）
#
#  在服务器上以 root 执行，可重复运行：
#      cd /root/secondbrain
#      bash deploy/install_server.sh
#
#  备案还没下来、想继续用 http://<IP>:8501 访问：
#      SB_BIND=0.0.0.0 bash deploy/install_server.sh
#
#  可覆盖的环境变量：
#      APP_DIR        项目目录           默认 /root/secondbrain
#      DOMAIN         域名               默认 caojinwen.cn
#      SB_BIND        Streamlit 绑定地址 默认 127.0.0.1
#      SB_API_BIND    API 绑定地址       默认 127.0.0.1
#
#  注意：证书签好后（certbot 改写过 conf），再跑本脚本不会覆盖
#        带 ssl_certificate 的配置文件。
# ============================================================
set -euo pipefail

APP_DIR="${APP_DIR:-/root/secondbrain}"
DOMAIN="${DOMAIN:-caojinwen.cn}"
SB_BIND="${SB_BIND:-127.0.0.1}"
SB_API_BIND="${SB_API_BIND:-127.0.0.1}"

log()  { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m[!] %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m[x] %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "请用 root 运行"
[ -f "$APP_DIR/app.py" ] || die "找不到 $APP_DIR/app.py，可用 APP_DIR=/your/path 指定"
[ -x "$APP_DIR/venv/bin/python" ] || die "找不到 $APP_DIR/venv/bin/python，虚拟环境不存在"

log "1/7 安装 Nginx"
if command -v apt-get >/dev/null 2>&1; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nginx
elif command -v dnf >/dev/null 2>&1; then
    dnf install -y -q nginx
elif command -v yum >/dev/null 2>&1; then
    yum install -y -q nginx
else
    die "没识别到包管理器，请手动安装 nginx 后重跑"
fi
systemctl enable nginx >/dev/null 2>&1 || true

log "2/7 安装 Python 依赖（本次新增 bcrypt）"
"$APP_DIR/venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"
"$APP_DIR/venv/bin/python" -c "import bcrypt, streamlit, psycopg2; print('依赖 OK: bcrypt', bcrypt.__version__)"

log "3/7 写入 Nginx 站点配置"
install -d /var/www/certbot /etc/nginx/conf.d
for f in "$APP_DIR"/deploy/nginx/*.conf; do
    [ -e "$f" ] || continue
    target="/etc/nginx/conf.d/$(basename "$f")"
    if [ -f "$target" ] && grep -q "ssl_certificate" "$target"; then
        warn "跳过 $target（已含证书配置，避免覆盖 certbot 的改动）"
        continue
    fi
    sed "s/caojinwen\.cn/${DOMAIN}/g" "$f" > "$target"
    echo "    -> $target"
done
nginx -t
systemctl reload nginx 2>/dev/null || systemctl restart nginx

log "4/7 写入运行参数 /etc/default/secondbrain"
cat > /etc/default/secondbrain <<EOF
# 由 deploy/install_server.sh 生成；改完 systemctl restart secondbrain 生效
SB_BIND=${SB_BIND}
SB_PORT=8501
SB_API_BIND=${SB_API_BIND}
SB_API_PORT=8000
EOF
cat /etc/default/secondbrain

log "5/7 安装 systemd 服务"
install -m 0644 "$APP_DIR/deploy/secondbrain.service"     /etc/systemd/system/secondbrain.service
install -m 0644 "$APP_DIR/deploy/secondbrain-api.service" /etc/systemd/system/secondbrain-api.service
systemctl daemon-reload

log "6/7 停掉旧的 nohup 进程"
pkill -f "streamlit run app.py" 2>/dev/null || true
pkill -f "uvicorn api:app"      2>/dev/null || true
sleep 2

log "7/7 启动并检查"
systemctl enable secondbrain >/dev/null 2>&1 || true
systemctl restart secondbrain || warn "secondbrain 启动失败，看 journalctl -u secondbrain -n 50"
systemctl enable secondbrain-api >/dev/null 2>&1 || true
systemctl restart secondbrain-api || warn "secondbrain-api 启动失败，看 journalctl -u secondbrain-api -n 50"
sleep 3

systemctl --no-pager --lines=0 status secondbrain     || true
systemctl --no-pager --lines=0 status secondbrain-api || true

echo
curl -s -o /dev/null -w "本地 8501  -> HTTP %{http_code}\n" http://127.0.0.1:8501/ || true
curl -s -o /dev/null -w "本地 8000  -> HTTP %{http_code}\n" http://127.0.0.1:8000/api/health || true

cat <<EOF

$(printf '\033[1;32m==> 完成\033[0m')

当前绑定：
  Streamlit : ${SB_BIND}:8501
  API       : ${SB_API_BIND}:8000

接下来（按顺序）：
  1. 备案下来前，若想继续用 IP:8501 访问：
       sed -i 's/^SB_BIND=.*/SB_BIND=0.0.0.0/' /etc/default/secondbrain
       systemctl restart secondbrain
  2. 备案下来后：
       a) 安全组放行 80/443，关闭 8000/8501
       b) DNS 加 A 记录：@ 和 www 指向本机公网 IP
       c) 签证书：
            apt install -y certbot python3-certbot-nginx
            certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} -d api.${DOMAIN}
       d) 把 /etc/default/secondbrain 里的 SB_BIND / SB_API_BIND 改成 127.0.0.1
          （如果本来就是 127.0.0.1 则跳过），然后 systemctl restart secondbrain secondbrain-api
  3. 排查命令：
       journalctl -u secondbrain -n 80 --no-pager
       tail -n 50 /var/log/nginx/error.log

EOF
