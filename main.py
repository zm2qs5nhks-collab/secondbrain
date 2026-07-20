"""
第二大脑 —— 个人知识管理 Agent
主入口
"""

import sys
import os

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))


def main():
    import config
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your-api-key-here":
        print("⚠️  请先配置 OpenAI API Key")
        print("   1. 复制 .env.example 为 .env")
        print("   2. 在 .env 中填入你的 API Key")
        print("   或者设置环境变量: set OPENAI_API_KEY=sk-xxx")
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        from ui.cli import start_cli, run_demo, print_banner
        from agent.core import SecondBrainAgent
        print_banner()
        agent = SecondBrainAgent()
        run_demo(agent)
    else:
        from ui.cli import start_cli
        start_cli()


if __name__ == "__main__":
    main()
