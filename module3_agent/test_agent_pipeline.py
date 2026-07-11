"""测试 Agent 管道（纯文本，不生成图）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from module3_agent.agent_pipeline import run_agent

# 测试用例
test_cases = [
    "20平米的侘寂风客厅，带落地窗，空间要有呼吸感，实木家具",
    "法式奶油风卧室，15平米，需要石膏线和雕花，温柔浪漫",
]

for user_input in test_cases:
    result = run_agent(user_input, generate=False)

    if result.get("error"):
        print(f"\n❌ 失败: {result['error']}")
        continue

    print(f"\n{'─' * 60}")
    print("📋 最终结果汇总")
    print(f"{'─' * 60}")
    print(f"  风格: {result['detected_style']}")
    print(f"  房间: {result['detected_room']}")
    print(f"  正向 Prompt ({len(result['positive_prompt'])} chars):")
    print(f"    {result['positive_prompt'][:300]}...")
    print(f"  负向 Prompt:")
    print(f"    {result['negative_prompt'][:200]}...")
    print(f"  参数: CFG={result['params']['cfg_scale']}, "
          f"Steps={result['params']['steps']}, "
          f"Sampler={result['params']['sampler']}")

    # RAG 检索内容
    rag = result.get("rag_context", "")
    if rag:
        print(f"\n  RAG 上下文 ({len(rag)} chars) 预览:")
        print(f"    {rag[:400]}...")
