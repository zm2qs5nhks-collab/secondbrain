# 以后想重新挂域名：恢复步骤

> 当前状态：**只用 `http://39.96.27.17:8501` 访问，不挂域名、不做备案运营**。
> 这份文档是"哪天又想挂域名了"时的操作清单，照做即可，不需要重新摸索。

## 前提

| 项 | 说明 |
|---|---|
| 域名 | `caojinwen.cn`（阿里云，需在有效期内，约 ¥42/年） |
| ICP 备案 | 目前**未注销**，仍然有效。如果已被注销，需重新备案 1~3 周 |
| 公安备案 | 2026-11-05 已被属地注销；重新挂站后需在**实际所在地**（学校所在地）重新办理 |
| 服务器 | 阿里云 ECS `39.96.27.17`，安全组能开 80/443 |

## 步骤

### 1. 恢复 nginx 站点配置

仓库里 `deploy/nginx/` 下有现成配置（`caojinwen.cn.conf` 含 www 301 跳转，`api.caojinwen.cn.conf` 给 REST/MCP）：

```bash
cd /root/secondbrain
cp deploy/nginx/caojinwen.cn.conf      /etc/nginx/conf.d/
cp deploy/nginx/api.caojinwen.cn.conf  /etc/nginx/conf.d/
nginx -t && systemctl enable --now nginx && systemctl reload nginx
```

### 2. 加回 DNS 解析

阿里云 → 域名控制台 → 解析设置 → 添加：

| 主机记录 | 类型 | 值 |
|---|---|---|
| `@` | A | `39.96.27.17` |
| `www` | A | `39.96.27.17` |
| `api` | A | `39.96.27.17` |

等 10 分钟（TTL 600s），验证：

```bash
nslookup caojinwen.cn 223.5.5.5
```

### 3. 安全组放行 80 / 443

阿里云 → ECS → 安全组 → 入方向：添加 80、443（来源 `0.0.0.0/0`）。
**8501 建议同时删掉**，让流量只走 nginx（否则别人可以绕过）。

### 4. 签 HTTPS 证书

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d caojinwen.cn -d www.caojinwen.cn -d api.caojinwen.cn
systemctl status certbot.timer          # 确认自动续期已启用
```

> 注意：证书续期依赖 DNS 指向本机（HTTP-01 验证）。如果长期不解析，续期会失败，
> 到时候重新挂站要重新签一次。

### 5. 让后端只听 127.0.0.1

```bash
cat > /etc/default/secondbrain <<'EOF'
SB_BIND=127.0.0.1
SB_PORT=8501
SB_API_BIND=127.0.0.1
SB_API_PORT=8000
EOF
systemctl restart secondbrain
```

### 6. 恢复备案号展示

在 `/root/secondbrain/.env` 里加：

```bash
SITE_ICP=鲁ICP备2026066331号
SITE_POLICE=鲁公网安备xxxxxxxxxxxxxx号    # 公安备案重新办下来后填
```

然后 `systemctl restart secondbrain`，页脚与侧边栏会重新显示。

### 7. 验证

```bash
curl -sI https://caojinwen.cn | head -2          # 200 + nginx
curl -s https://caojinwen.cn/api/health 2>/dev/null || true
curl -m 5 http://39.96.27.17:8501/ || echo "8501 已关闭（符合预期）"
```

浏览器打开 `https://caojinwen.cn`，确认：
- 地址栏有锁
- 页脚显示 ICP 号
- 左侧导航 6 项（智能问答/设置仍下线）

## 回退（万一又不想挂了）

```bash
rm -f /etc/nginx/conf.d/caojinwen.cn.conf /etc/nginx/conf.d/api.caojinwen.cn.conf
systemctl disable --now nginx
sed -i 's/^SB_BIND=.*/SB_BIND=0.0.0.0/' /etc/default/secondbrain
systemctl restart secondbrain
```

再删掉 DNS 解析即可。
