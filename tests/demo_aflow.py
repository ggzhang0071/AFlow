#!/usr/bin/env python3
"""
AFlow 演示脚本 - 展示工作流优化过程
"""

import os
import sys
import json
import random
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*70)
print("🚀 AFlow 工作流优化演示")
print("="*70)
print()
print("AFlow 使用蒙特卡洛树搜索(MCTS)来自动优化 Agentic 工作流")
print()

# ==================== 模拟组件 ====================

class MockNode:
    """模拟 Node 组件"""
    def __init__(self, name: str, action: str):
        self.name = name
        self.action = action
    
    def __repr__(self):
        return f"Node({self.name})"

class MockOperator:
    """模拟 Operator 组件"""
    def __init__(self, name: str, nodes: List[MockNode]):
        self.name = name
        self.nodes = nodes
    
    def __repr__(self):
        return f"Operator({self.name}, nodes={len(self.nodes)})"

class MockWorkflow:
    """模拟 Workflow 组件"""
    def __init__(self, operators: List[MockOperator], name: str = "Workflow"):
        self.name = name
        self.operators = operators
        self.score = 0.0
        self.visits = 0
    
    def execute(self, problem: str) -> str:
        """模拟执行工作流"""
        # 这里模拟不同操作符组合的效果
        base_score = 0.5
        
        # Custom 操作符加分
        if any(op.name == "Custom" for op in self.operators):
            base_score += 0.1
        
        # Programmer 操作符对数学问题加分
        if any(op.name == "Programmer" for op in self.operators):
            base_score += 0.15
        
        # ScEnsemble 操作符加分
        if any(op.name == "ScEnsemble" for op in self.operators):
            base_score += 0.1
        
        # 添加随机性
        result_score = base_score + random.uniform(-0.1, 0.1)
        return min(max(result_score, 0.0), 1.0)
    
    def __repr__(self):
        ops = " -> ".join([op.name for op in self.operators])
        return f"Workflow([{ops}], score={self.score:.3f})"

class MockMCNode:
    """模拟蒙特卡洛树节点"""
    def __init__(self, workflow: MockWorkflow, parent=None):
        self.workflow = workflow
        self.parent = parent
        self.children: List[MockMCNode] = []
        self.visits = 0
        self.value = 0.0
    
    def uct_score(self, exploration_weight=1.414) -> float:
        """UCB1 公式计算分数"""
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.value / self.visits
        exploration = exploration_weight * (2 * (self.parent.visits ** 0.5) / self.visits if self.parent else 0)
        return exploitation + exploration
    
    def __repr__(self):
        return f"MCNode({self.workflow.name}, visits={self.visits}, value={self.value:.3f})"

# ==================== 模拟数据集 ====================

class MockDataset:
    """模拟数据集"""
    def __init__(self, name: str, problems: List[Dict]):
        self.name = name
        self.problems = problems
    
    def sample(self, n: int = 1) -> List[Dict]:
        return random.sample(self.problems, min(n, len(self.problems)))

# 示例数学问题 (GSM8K 风格)
GSM8K_PROBLEMS = [
    {
        "question": "小明有 5 个苹果，他给了小红 2 个，然后又买了 3 个。现在小明有多少个苹果？",
        "answer": "6"
    },
    {
        "question": "一个长方形的长是 8 厘米，宽是 5 厘米，它的面积是多少？",
        "answer": "40"
    },
    {
        "question": "一辆汽车每小时行驶 60 公里，3 小时能行驶多远？",
        "answer": "180"
    },
    {
        "question": "一个班级有 30 个学生，其中 40% 是女生，有多少个女生？",
        "answer": "12"
    },
    {
        "question": "一本书 240 页，小明每天看 20 页，需要多少天看完？",
        "answer": "12"
    }
]

# ==================== 模拟优化器 ====================

class MockOptimizer:
    """模拟 AFlow 优化器"""
    
    AVAILABLE_OPERATORS = [
        MockOperator("Custom", [MockNode("Generate", "generate")]),
        MockOperator("ScEnsemble", [MockNode("Ensemble", "ensemble")]),
        MockOperator("Programmer", [MockNode("Code", "code")]),
    ]
    
    def __init__(self, dataset: MockDataset, max_rounds: int = 5, sample: int = 3):
        self.dataset = dataset
        self.max_rounds = max_rounds
        self.sample = sample
        self.root = MockMCNode(MockWorkflow([], "Root"))
        self.best_workflow = None
        self.best_score = 0.0
        self.history = []
    
    def generate_workflow(self) -> MockWorkflow:
        """生成随机工作流"""
        num_ops = random.randint(1, 3)
        ops = random.sample(self.AVAILABLE_OPERATORS, num_ops)
        return MockWorkflow(ops, name=f"Workflow_{random.randint(1000, 9999)}")
    
    def evaluate(self, workflow: MockWorkflow) -> float:
        """评估工作流性能"""
        test_problems = self.dataset.sample(2)
        scores = []
        
        for problem in test_problems:
            score = workflow.execute(problem["question"])
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    def select(self, node: MockMCNode) -> MockMCNode:
        """选择阶段: UCT 选择"""
        if not node.children:
            return node
        
        # 选择 UCT 分数最高的子节点
        best_child = max(node.children, key=lambda c: c.uct_score())
        return self.select(best_child)
    
    def expand(self, node: MockMCNode) -> MockMCNode:
        """扩展阶段: 生成新工作流"""
        new_workflow = self.generate_workflow()
        child = MockMCNode(new_workflow, parent=node)
        node.children.append(child)
        return child
    
    def simulate(self, node: MockMCNode) -> float:
        """模拟阶段: 评估工作流"""
        score = self.evaluate(node.workflow)
        node.workflow.score = score
        return score
    
    def backpropagate(self, node: MockMCNode, score: float):
        """反向传播: 更新节点统计"""
        current = node
        while current:
            current.visits += 1
            current.value += score
            current = current.parent
    
    def optimize(self):
        """执行 MCTS 优化"""
        print(f"开始优化: 数据集={self.dataset.name}, 轮数={self.max_rounds}, 采样={self.sample}")
        print()
        
        for round_num in range(1, self.max_rounds + 1):
            print(f"Round {round_num}/{self.max_rounds}")
            print("-" * 50)
            
            round_best_score = 0.0
            round_best_workflow = None
            
            for sample_idx in range(self.sample):
                # MCTS 四步骤
                # 1. 选择
                selected = self.select(self.root)
                print(f"  Sample {sample_idx + 1}: 选择节点 (深度={self.get_depth(selected)})")
                
                # 2. 扩展
                if selected.visits > 0 or selected == self.root:
                    selected = self.expand(selected)
                    ops = " -> ".join([op.name for op in selected.workflow.operators])
                    print(f"    扩展新工作流: [{ops}]")
                
                # 3. 模拟 (评估)
                score = self.simulate(selected)
                print(f"    评估得分: {score:.3f}")
                
                # 更新最佳
                if score > round_best_score:
                    round_best_score = score
                    round_best_workflow = selected.workflow
                
                # 4. 反向传播
                self.backpropagate(selected, score)
            
            # 更新全局最佳
            if round_best_score > self.best_score:
                self.best_score = round_best_score
                self.best_workflow = round_best_workflow
            
            self.history.append({
                "round": round_num,
                "best_score": round_best_score,
                "global_best": self.best_score
            })
            
            print(f"  本轮最佳: {round_best_score:.3f} | 全局最佳: {self.best_score:.3f}")
            print()
        
        return self.best_workflow
    
    def get_depth(self, node: MockMCNode) -> int:
        """获取节点深度"""
        depth = 0
        current = node
        while current.parent:
            depth += 1
            current = current.parent
        return depth
    
    def report(self):
        """生成优化报告"""
        print("=" * 70)
        print("📊 优化报告")
        print("=" * 70)
        print()
        print(f"数据集: {self.dataset.name}")
        print(f"总轮数: {self.max_rounds}")
        print(f"每轮采样: {self.sample}")
        print()
        print("🎯 最佳工作流:")
        if self.best_workflow:
            ops = " -> ".join([op.name for op in self.best_workflow.operators])
            print(f"   结构: [{ops}]")
            print(f"   得分: {self.best_score:.3f}")
        print()
        print("📈 优化历史:")
        for h in self.history:
            print(f"   Round {h['round']}: {h['global_best']:.3f}")
        print()

# ==================== 运行演示 ====================

def main():
    print("初始化组件...")
    print()
    
    # 创建数据集
    dataset = MockDataset("GSM8K-Mock", GSM8K_PROBLEMS)
    print(f"✓ 加载数据集: {dataset.name} ({len(dataset.problems)} 个问题)")
    
    # 显示示例问题
    print("\n示例问题:")
    for i, prob in enumerate(dataset.sample(2), 1):
        print(f"  {i}. {prob['question'][:50]}...")
    print()
    
    # 创建优化器
    optimizer = MockOptimizer(
        dataset=dataset,
        max_rounds=3,
        sample=2
    )
    print(f"✓ 初始化优化器")
    print(f"  - 可用操作符: {[op.name for op in optimizer.AVAILABLE_OPERATORS]}")
    print(f"  - 最大轮数: {optimizer.max_rounds}")
    print(f"  - 每轮采样: {optimizer.sample}")
    print()
    
    # 执行优化
    print("开始执行 MCTS 优化...")
    print()
    best_workflow = optimizer.optimize()
    
    # 生成报告
    optimizer.report()
    
    # 演示最佳工作流
    print("=" * 70)
    print("🔍 最佳工作流详细分析")
    print("=" * 70)
    print()
    
    if best_workflow:
        print(f"工作流名称: {best_workflow.name}")
        print(f"最终得分: {best_workflow.score:.3f}")
        print()
        print("操作符链:")
        for i, op in enumerate(best_workflow.operators, 1):
            print(f"  {i}. {op.name}")
            print(f"     功能: {get_operator_desc(op.name)}")
            print(f"     节点: {[n.name for n in op.nodes]}")
        print()
        
        # 模拟执行
        print("测试执行:")
        test_problem = dataset.sample(1)[0]
        print(f"  问题: {test_problem['question']}")
        print(f"  答案: {test_problem['answer']}")
        result = best_workflow.execute(test_problem['question'])
        print(f"  工作流置信度: {result:.3f}")
    
    print()
    print("=" * 70)
    print("✅ AFlow 演示完成!")
    print("=" * 70)
    print()
    print("💡 总结:")
    print("  • AFlow 使用 MCTS 自动搜索最优工作流结构")
    print("  • 通过 Selection -> Expansion -> Simulation -> Backpropagation 循环优化")
    print("  • 支持多种操作符组合，适应不同任务类型")
    print("  • 实际使用时需要配置 LLM API 或本地模型")
    print()
    print("🚀 实际运行命令:")
    print("  cd /mnt/newdisk/agent/AFlow")
    print("  python run.py --dataset GSM8K --sample 4 --max_rounds 20")

def get_operator_desc(name: str) -> str:
    """获取操作符描述"""
    descriptions = {
        "Custom": "自定义生成操作符，用于基础内容生成",
        "ScEnsemble": "自一致性集成，通过多轮采样投票提高准确性",
        "Programmer": "编程助手，生成和执行代码解决问题"
    }
    return descriptions.get(name, "未知操作符")

if __name__ == "__main__":
    main()
