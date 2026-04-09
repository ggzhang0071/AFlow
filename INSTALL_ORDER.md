# AFlow 依赖安装顺序

## 📋 推荐安装顺序

在 Conda 环境中，按以下顺序安装依赖：

### 1. 创建并激活 Conda 环境

```bash
# 创建环境
conda create -n aflow python=3.9 -y

# 激活环境
conda activate aflow

# 升级 pip
pip install --upgrade pip
```

### 2. 安装 Conda 专属包（可选但推荐）

```bash
# 如果使用 GPU，先用 conda 安装 PyTorch（更快更稳定）
conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia -y

# 安装其他 conda 可用的包
conda install -c conda-forge pandas numpy pyyaml -y
```

### 3. 安装 requirements.txt

```bash
# 进入 AFlow 目录
cd /mnt/newdisk/agent/AFlow

# 安装 requirements.txt
pip install -r requirements.txt
```

### 4. 安装 GPU 相关包（可选）

```bash
# 如果在第2步没安装 PyTorch，这里用 pip 安装
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装 transformers
pip install transformers accelerate sentencepiece protobuf
```

---

## ❓ 常见问题

### Q1: 为什么要在 Conda 环境中用 pip？

```
Conda 和 Pip 的关系：
- Conda: 管理环境、Python 版本、系统级依赖
- Pip: 安装 Python 包

它们可以共存，推荐：
1. 用 Conda 创建环境和管理 Python 版本
2. 用 Pip 安装 requirements.txt 中的包
```

### Q2: requirements.txt 中的包会和 Conda 冲突吗？

```bash
# 一般不会冲突，因为 Conda 环境的 pip 是独立的
which pip
# 输出: /home/.../miniconda3/envs/aflow/bin/pip

# 这个 pip 只安装到 aflow 环境，不影响其他环境
```

### Q3: 可以全部用 Conda 安装吗？

```bash
# 可以，但需要转换 requirements.txt
conda install --file requirements.txt  # 可能失败，因为不是所有包都有 conda 版本

# 推荐的做法：
# 1. 先用 conda 安装能安装的
conda install pandas numpy pyyaml

# 2. 再用 pip 安装剩下的
pip install openai tenacity tqdm
```

---

## ✅ 完整安装命令（复制即用）

### 方式 1：全部用 pip（最简单）

```bash
# 创建环境
conda create -n aflow python=3.9 -y
conda activate aflow

# 进入目录
cd /mnt/newdisk/agent/AFlow

# 安装所有依赖（用 pip）
pip install -r requirements.txt

# 如果使用 GPU，再安装 torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 方式 2：Conda + Pip 混合（推荐）

```bash
# 1. 创建环境
conda create -n aflow python=3.9 -y
conda activate aflow

# 2. 用 conda 安装基础包
conda install -c conda-forge pandas numpy pyyaml -y

# 3. 如果用 GPU，安装 PyTorch
conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia -y

# 4. 进入目录
cd /mnt/newdisk/agent/AFlow

# 5. 用 pip 安装剩余依赖
pip install -r requirements.txt

# 此时 requirements.txt 中与 conda 重复的安装会跳过
# 只安装 conda 没有的包（如 openai, tenacity 等）
```

---

## 🔍 验证安装

```bash
# 确认在 conda 环境中
conda activate aflow
which python
# 输出应包含: .../envs/aflow/bin/python

# 检查 requirements.txt 中的包
pip list | grep -E "openai|pandas|pyyaml|tenacity"

# 测试导入
python -c "import openai, pandas, yaml; print('✓ 所有包安装成功')"
```

---

## 📝 总结

| 问题 | 答案 |
|------|------|
| Conda 环境要装 requirements.txt 吗？ | **要**，用 `pip install -r requirements.txt` |
| 用 conda 还是 pip 安装？ | 都可以，pip 更简单，conda+pip 更稳定 |
| 会和其他环境冲突吗？ | **不会**，每个 conda 环境是独立的 |
| PyTorch 用什么装？ | 推荐 conda，更快且自动处理 CUDA |

---

**一句话总结**: 在 Conda 环境中，使用 `pip install -r requirements.txt` 安装依赖是完全正确且推荐的做法！
