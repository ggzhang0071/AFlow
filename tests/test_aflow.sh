#!/bin/bash
# AFlow 一键测试脚本
# 使用方法: ./test_aflow.sh [dataset] [sample] [rounds]
# 示例: ./test_aflow.sh GSM8K 2 3

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 参数设置
DATASET=${1:-GSM8K}
SAMPLE=${2:-2}
ROUNDS=${3:-3}

# 显示 banner
echo -e "${BLUE}"
echo "============================================================"
echo "  AFlow 自动化工作流生成框架 - 测试脚本"
echo "============================================================"
echo -e "${NC}"

# 检查虚拟环境
echo -e "${YELLOW}[1/6] 检查虚拟环境...${NC}"
if [ -z "$CONDA_DEFAULT_ENV" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}警告: 未检测到虚拟环境${NC}"
    echo "建议使用虚拟环境:"
    echo "  conda create -n agent python=3.9"
    echo "  conda activate agent"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
fi

# 检查目录
echo -e "${YELLOW}[2/6] 检查项目目录...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
echo -e "${GREEN}✓ 进入 AFlow 目录: $(pwd)${NC}"

# 检查 Python
echo -e "${YELLOW}[3/6] 检查 Python 环境...${NC}"
python --version
echo -e "${GREEN}✓ Python 版本检查完成${NC}"

# 检查配置
echo -e "${YELLOW}[4/6] 检查配置文件...${NC}"
if [ ! -f "config/config2.yaml" ]; then
    echo -e "${YELLOW}创建配置文件...${NC}"
    cat > config/config2.yaml << 'EOF'
models:
  gpt-4o:
    api_type: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "YOUR_API_KEY_HERE"
    model: "gpt-4o"
    temperature: 0
  
  gpt-4o-mini:
    api_type: "openai"
    base_url: "https://api.openai.com/v1"
    api_key: "YOUR_API_KEY_HERE"
    model: "gpt-4o-mini"
    temperature: 0
EOF
    echo -e "${RED}请编辑 config/config2.yaml 添加你的 OpenAI API 密钥${NC}"
    echo "或者设置环境变量: export OPENAI_API_KEY=your-key"
    exit 1
fi
echo -e "${GREEN}✓ 配置文件存在${NC}"

# 检查依赖
echo -e "${YELLOW}[5/6] 检查依赖...${NC}"
python -c "import openai, pandas, yaml" 2>/dev/null || {
    echo -e "${YELLOW}安装依赖...${NC}"
    pip install -q openai pandas pyyaml tenacity tqdm numpy
}
echo -e "${GREEN}✓ 依赖检查完成${NC}"

# 运行测试
echo -e "${YELLOW}[6/6] 运行 AFlow 测试...${NC}"
echo ""
echo "============================================================"
echo "  测试配置:"
echo "    数据集: $DATASET"
echo "    样本数: $SAMPLE"
echo "    轮数: $ROUNDS"
echo "============================================================"
echo ""

# 检查 API 密钥
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}警告: 未设置 OPENAI_API_KEY 环境变量${NC}"
    echo "尝试从配置文件读取..."
fi

# 执行测试
echo -e "${BLUE}开始执行...${NC}"
echo ""

python run.py \
    --dataset "$DATASET" \
    --sample "$SAMPLE" \
    --max_rounds "$ROUNDS" \
    --validation_rounds 1 \
    --check_convergence True \
    --optimized_path "workspace_${DATASET}_test"

# 检查结果
echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  ✅ 测试完成!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "结果位置:"
echo "  workspace_${DATASET}_test/"
echo ""
echo "查看结果:"
echo "  ls -la workspace_${DATASET}_test/"
echo "  cat workspace_${DATASET}_test/*/scores.json 2>/dev/null || echo '结果文件可能在子目录中'"
echo ""
echo "其他可用数据集:"
echo "  - GSM8K (小学数学)"
echo "  - MATH (高中数学竞赛)"
echo "  - HumanEval (代码生成)"
echo "  - MBPP (Python编程)"
echo "  - HotpotQA (多跳问答)"
echo "  - DROP (离散推理)"
echo ""
echo "使用示例:"
echo "  ./test_aflow.sh GSM8K 4 10    # GSM8K, 4样本, 10轮"
echo "  ./test_aflow.sh MATH 2 5      # MATH, 2样本, 5轮"
