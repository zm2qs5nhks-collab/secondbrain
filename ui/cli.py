"""
命令行界面
"""

from agent.core import SecondBrainAgent


def print_banner():
    print("=" * 55)
    print("  🧠 第二大脑 —— 个人知识管理 Agent")
    print("=" * 55)
    print("  命令: quit/exit=退出  clear=清空对话  help=帮助")
    print("=" * 55)
    print()


def print_help():
    print("""
可用命令：
  quit / exit    退出程序
  clear          清空对话历史
  help           显示此帮助
  demo           运行演示流程

直接输入文字即可与 Agent 对话，例如：
  "帮我记一下 Python GIL 是全局解释器锁"
  "我之前学过什么关于 Redis 的内容？"
  "列出我的所有笔记"
  "有什么需要复习的吗？"
""")


def run_demo(agent: SecondBrainAgent):
    print("\n" + "=" * 55)
    print("  🎬 演示流程开始")
    print("=" * 55)

    demos = [
        ("添加笔记", "帮我记下来：Python 的 GIL 全局解释器锁会导致多线程在CPU密集型任务中无法真正并行，只有IO密集型任务才能从多线程中受益"),
        ("添加笔记", "保存这条：Redis 使用 LRU（最近最少使用）算法来淘汰缓存数据，可以通过 maxmemory-policy 配置"),
        ("搜索知识", "我之前学过什么关于 Redis 的内容？"),
        ("知识管理", "帮我看看知识库一共有多少条笔记"),
        ("复习提醒", "有什么需要复习的内容吗？"),
    ]

    for step, (label, query) in enumerate(demos, 1):
        print(f"\n--- 第{step}步: {label} ---")
        print(f"用户: {query}")
        try:
            response = agent.chat(query)
            print(f"Agent: {response}")
        except Exception as e:
            print(f"[错误] {e}")

    print("\n" + "=" * 55)
    print("  🎬 演示流程结束")
    print("=" * 55)


def start_cli():
    print_banner()
    agent = SecondBrainAgent()

    while True:
        try:
            user_input = input("你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("quit", "exit", "q"):
            print("再见！保持学习，保持思考。")
            break
        elif cmd == "clear":
            agent.memory.clear()
            print("✅ 对话历史已清空")
            continue
        elif cmd == "help":
            print_help()
            continue
        elif cmd == "demo":
            run_demo(agent)
            continue

        try:
            response = agent.chat(user_input)
            print(f"\n🧠 > {response}\n")
        except Exception as e:
            print(f"\n[错误] {e}\n")
