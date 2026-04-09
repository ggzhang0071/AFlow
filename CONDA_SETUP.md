# AFlow Conda 环境配置指南

本指南详细介绍如何使用 Conda 配置 AFlow 项目的运行环境。

## 🎯 推荐配置

AFlow 项目**推荐在 Conda 虚拟环境中执行**，这样可以：
- 隔离项目依赖，避免冲突
- 方便管理 Python 版本
- 支持 GPU 环境配置

---

## 📋 前提条件

### 1. 安装 Miniconda/Anaconda

如果未安装 Conda：

```bash
# 下载 Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 安装
bash Miniconda3-latest-Linux-x86_64.sh

# 重新加载配置
source ~/.bashrc
```

### 2. 验证安装

```bash
conda --version
# 输出: conda 23.x.x 或更高版本
```

---

## 🚀 快速配置（推荐）

### 方式 1：使用一键脚本

```bash
cd /mnt/newdisk/agent/AFlow

# 创建并配置conda环境
./setup_conda.sh
```

### 方式 2：手动配置

```bash
# 步骤 1: 创建conda环境
cd /mnt/newdisk/agent/AFlow
conda create -n aflow python=3.9 -y

# 步骤 2: 激活环境
conda activate aflow

# 步骤 3: 安装依赖
pip install -r requirements.txt

# 步骤 4: 验证
python tests/test_aflow_quick.py
```

---

## 🔧 详细配置步骤

### 1. 创建 Conda 环境

```bash
# 创建Python 3.9环境
conda create -n aflow python=3.9 -y

# 查看创建的环境
conda env list
```

输出示例：
```
# conda environments:
#
base                  *  /home/ubt/miniconda3
aflow                    /home/ubt/miniconda3/envs/aflow
```

### 2. 激活环境

```bash
# 激活aflow环境
conda activate aflow

# 验证激活成功
which python
# 输出: /home/ubt/miniconda3/envs/aflow/bin/python

python --version
# 输出: Python 3.9.x
```

### 3. 安装依赖

```bash
# 确保在aflow环境中
conda activate aflow

# 进入AFlow目录
cd /mnt/newdisk/agent/AFlow

# 升级pip
pip install --upgrade pip

# 安装基础依赖
pip install -r requirements.txt

# 如果使用GPU，安装PyTorch
conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia -y
# 或使用pip
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装transformers
pip install transformers accelerate sentencepiece protobuf
```

### 4. 验证安装

```bash
# 检查Python
python --version

# 检查关键包
python -c "import openai, pandas, torch; print('✓ 所有包安装成功')"

# 检查GPU
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
```

### 5. 配置API密钥

```bash
# 方式1: 环境变量
export OPENAI_API_KEY="sk-your-api-key"

# 添加到~/.bashrc使其永久生效
echo 'export OPENAI_API_KEY="sk-your-api-key"' >> ~/.bashrc

# 方式2: 编辑配置文件
nano config/config2.yaml
```

---

## 📊 Conda环境管理

### 常用命令

```bash
# 查看所有环境
conda env list

# 激活环境
conda activate aflow

# 退出环境
conda deactivate

# 删除环境（如果需要重新创建）
conda remove -n aflow --all

# 导出环境配置
conda env export > environment.yml

# 从文件创建环境
conda env create -f environment.yml
```

### 环境导出/导入

```bash
# 导出当前环境
conda activate aflow
conda env export > aflow_environment.yml

# 在其他机器上创建相同环境
conda env create -f aflow_environment.yml
```

---

## 🎮 运行AFlow

### 在Conda环境中运行

```bash
# 每次使用前激活环境
conda activate aflow

# 进入AFlow目录
cd /mnt/newdisk/agent/AFlow

# 运行测试
./test.sh quick

# 或运行完整优化
./test.sh run --dataset GSM8K --sample 2 --max_rounds 3
```

### 一键运行脚本

创建 `run_in_conda.sh`：

```bash
#!/bin/bash
# 在conda环境中运行AFlow

# 激活环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate aflow

# 进入目录
cd /mnt/newdisk/agent/AFlow

# 运行命令
$@
```

使用方法：
```bash
chmod +x run_in_conda.sh
./run_in_conda.sh ./test.sh quick
./run_in_conda.sh ./test.sh run --dataset GSM8K
```

---

## 🔍 故障排除

### Q1: 激活环境后显示(base)

```bash
# 问题: conda activate aflow后提示符仍显示(base)

# 解决方案1: 重新初始化conda
conda init bash
source ~/.bashrc

# 解决方案2: 手动激活
source $(conda info --base)/etc/profile.d/conda.sh
conda activate aflow
```

### Q2: 包安装冲突

```bash
# 问题: pip安装时出现依赖冲突

# 解决方案: 使用conda安装冲突的包
conda activate aflow
conda install -c conda-forge pandas numpy pyyaml
pip install openai tenacity tqdm
```

### Q3: CUDA版本不匹配

```bash
# 查看当前CUDA版本
conda activate aflow
python -c "import torch; print(torch.version.cuda)"

# 安装匹配的PyTorch版本
# CUDA 12.1
conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia

# CUDA 11.8
conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia
```

### Q4: 找不到conda命令

```bash
# 添加conda到PATH
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## 📁 环境文件

### aflow_environment.yml

```yaml
name: aflow
dependencies:
  - python=3.9
  - pip
  - pip:
    - openai==1.82.0
    - pandas==2.2.3
    - pyaml==25.1.0
    - pydantic==2.11.5
    - PyYAML==6.0.2
    - tenacity==9.1.2
    - tqdm==4.67.1
    - numpy==2.0.2
    - transformers
    - accelerate
    - sentencepiece
    - protobuf
    - torch
    - torchvision
    - torchaudio
```

创建环境：
```bash
conda env create -f aflow_environment.yml
```

---

## ✅ 验证清单

| 检查项 | 命令 | 预期结果 |
|--------|------|----------|
| Conda安装 | `conda --version` | conda 23.x.x |
| 环境创建 | `conda env list` | 显示aflow环境 |
| 环境激活 | `echo $CONDA_DEFAULT_ENV` | aflow |
| Python版本 | `python --version` | Python 3.9.x |
| 依赖安装 | `pip list \| grep openai` | 显示版本号 |
| GPU可用 | `python -c "import torch; print(torch.cuda.is_available())"` | True/False |

---

## 🔄 切换环境

```bash
# 从其他环境切换到aflow
conda deactivate  # 先退出当前环境
conda activate aflow

# 或者直接从base激活
conda activate aflow
```

---

## 💡 最佳实践

1. **始终激活环境**：运行AFlow前确保已激活`aflow`环境
2. **不要混用环境**：base环境和其他项目环境不要混用
3. **定期更新**：`conda update -n aflow --all`
4. **导出备份**：定期导出环境配置备份

---

## 📚 相关文档

- `ENVIRONMENT_SETUP.md` - 通用环境配置
- `CONDA_SETUP.md` - 本文件
- `README.md` - 项目主文档

---

**总结**: AFlow推荐在Conda虚拟环境中执行，使用 `conda activate aflow` 激活后运行所有命令。
