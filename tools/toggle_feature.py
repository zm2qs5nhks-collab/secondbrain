"""
一键开关功能模块 —— 改 .env 并（可选）重启服务。

用途：知识问答 / 设置页暂时下线，以后要恢复时不用手改配置文件。

用法（在项目根目录）：
    venv/bin/python tools/toggle_feature.py status
    venv/bin/python tools/toggle_feature.py chat on
    venv/bin/python tools/toggle_feature.py chat off
    venv/bin/python tools/toggle_feature.py settings on
    venv/bin/python tools/toggle_feature.py all off
    venv/bin/python tools/toggle_feature.py chat on --no-restart

说明：
- 只改 .env 里对应的键，其它配置原样保留；
- 默认会在检测到 systemd 服务时自动 restart，否则打印手动重启命令；
- 不会动数据库、不会删代码，关掉只是"导航里不显示 + 分支不可达"。
"""

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_ENV = ROOT / ".env"

FEATURES = {
    "chat": ("ENABLE_CHAT", "智能问答"),
    "settings": ("ENABLE_SETTINGS", "设置页"),
}

SERVICE = "secondbrain"


def read_env(path: pathlib.Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def write_env(path: pathlib.Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def get_value(lines: list[str], key: str) -> str | None:
    prefix = f"{key}="
    for line in reversed(lines):
        if line.strip().startswith(prefix):
            return line.strip()[len(prefix):].strip().strip('"').strip("'")
    return None


def set_value(lines: list[str], key: str, value: str) -> list[str]:
    """替换已有的键（去掉重复），没有就追加到末尾。"""
    kept = [ln for ln in lines if not ln.strip().startswith(f"{key}=")]
    kept.append(f"{key}={value}")
    return kept


def restart() -> bool:
    try:
        active = subprocess.run(
            ["systemctl", "is-active", SERVICE],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except Exception:  # noqa: BLE001
        active = ""

    if active != "active":
        print(f"[!] 没检测到 systemd 服务 {SERVICE} 在运行，不自动重启。")
        print("    手动重启：")
        print(f"      pkill -f 'streamlit run app.py' || true")
        print(f"      cd {ROOT} && setsid nohup venv/bin/streamlit run app.py "
              f"> /tmp/streamlit.log 2>&1 < /dev/null &")
        return False

    print(f"[..] systemctl restart {SERVICE}")
    r = subprocess.run(["systemctl", "restart", SERVICE], capture_output=True, text=True)
    if r.returncode == 0:
        print("[ok] 服务已重启")
        return True
    print(f"[x] 重启失败：{r.stderr.strip()}")
    return False


def cmd_status(env_path: pathlib.Path) -> int:
    lines = read_env(env_path)
    print(f"配置文件：{env_path}")
    print()
    for alias, (key, label) in FEATURES.items():
        raw = get_value(lines, key)
        state = "开启" if (raw or "").lower() in ("1", "true", "yes", "on") else "关闭"
        print(f"  {label:<8} {key:<18} = {state}    (当前值：{raw or '未设置→默认关闭'})")
    print()
    print("开启：venv/bin/python tools/toggle_feature.py all on")
    return 0


def cmd_toggle(env_path: pathlib.Path, target: str, enable: bool, do_restart: bool) -> int:
    lines = read_env(env_path)
    value = "true" if enable else "false"

    targets = list(FEATURES) if target == "all" else [target]
    for name in targets:
        key, label = FEATURES[name]
        lines = set_value(lines, key, value)
        print(f"[ok] {label} ({key}) = {value}")

    write_env(env_path, lines)

    if do_restart:
        restart()
    else:
        print("[i] 未重启，改动要重启后才生效：systemctl restart secondbrain")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="开关知识问答 / 设置页")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV), help="默认项目根目录下的 .env")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="查看当前开关状态").set_defaults(
        func=lambda a: cmd_status(pathlib.Path(a.env_file))
    )

    p_on = sub.add_parser("on", help="开启（chat / settings / all）")
    p_on.add_argument("target", choices=[*FEATURES, "all"])
    p_on.add_argument("--no-restart", action="store_true")
    p_on.set_defaults(func=lambda a: cmd_toggle(pathlib.Path(a.env_file), a.target, True, not a.no_restart))

    p_off = sub.add_parser("off", help="关闭（chat / settings / all）")
    p_off.add_argument("target", choices=[*FEATURES, "all"])
    p_off.add_argument("--no-restart", action="store_true")
    p_off.set_defaults(func=lambda a: cmd_toggle(pathlib.Path(a.env_file), a.target, False, not a.no_restart))

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
