#!/bin/bash
# AFlow 测试入口脚本
# 自动调用 tests 目录中的测试

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 显示帮助
show_help() {
    echo "AFlow 测试工具"
    echo ""
    echo "用法: ./test.sh [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  quick         快速验证测试"
    echo "  demo          MCTS 工作流演示"
    echo "  gpu           GPU 本地模型测试"
    echo "  full          完整工作流测试 (需要 GPU)"
    echo "  run [args]    运行 AFlow 优化 (默认命令)"
    echo ""
    echo "选项 (用于 run 命令):"
    echo "  --dataset     数据集 (GSM8K/MATH/HumanEval/MBPP/HotpotQA/DROP)"
    echo "  --sample      样本数 (默认: 2)"
    echo "  --max_rounds  最大轮数 (默认: 3)"
    echo ""
    echo "示例:"
    echo "  ./test.sh quick"
    echo "  ./test.sh gpu"
    echo "  ./test.sh run --dataset GSM8K --sample 4 --max_rounds 10"
    echo "  ./test.sh tests/test_aflow.sh GSM8K 2 3"
}

# 检查参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

COMMAND=$1
shift

case $COMMAND in
    quick)
        echo "运行快速验证测试..."
        python "$SCRIPT_DIR/tests/test_aflow_quick.py"
        ;;
    demo)
        echo "运行 MCTS 工作流演示..."
        python "$SCRIPT_DIR/tests/demo_aflow.py"
        ;;
    gpu)
        echo "运行 GPU 本地模型测试..."
        python "$SCRIPT_DIR/tests/test_gpu_auto.py"
        ;;
    full)
        echo "运行完整工作流测试..."
        python "$SCRIPT_DIR/tests/test_aflow_full_gpu.py"
        ;;
    run)
        echo "运行 AFlow 优化..."
        cd "$SCRIPT_DIR"
        python run.py "$@"
        ;;
    tests/test_aflow.sh|./tests/test_aflow.sh|test_aflow.sh)
        # 调用完整测试脚本
        cd "$SCRIPT_DIR"
        bash "$SCRIPT_DIR/tests/test_aflow.sh" "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        # 默认调用 run.py
        echo "运行 AFlow: python run.py $COMMAND $@"
        cd "$SCRIPT_DIR"
        python run.py "$COMMAND" "$@"
        ;;
esac
