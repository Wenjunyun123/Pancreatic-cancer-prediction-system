#!/usr/bin/env python3
"""
测试修复后的应用
"""

import sys
import os
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_loading():
    """测试模型加载功能"""
    try:
        from implementation import load_model, random_forest_train
        
        print("测试模型加载...")
        
        # 尝试加载现有模型
        clf = load_model()
        
        if clf is None:
            print("模型不存在，尝试训练新模型...")
            clf = random_forest_train()
            
        if clf is not None:
            print("✓ 模型加载/训练成功")
            return True
        else:
            print("✗ 模型加载/训练失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        return False

def test_prediction():
    """测试预测功能"""
    try:
        from implementation import load_model, random_forest_predict
        import numpy as np
        
        print("测试预测功能...")
        
        # 加载模型
        clf = load_model()
        if clf is None:
            print("✗ 无法加载模型进行预测测试")
            return False
            
        # 创建测试数据（良性样本）
        test_data = np.array([[
            13.54, 14.36, 87.46, 566.3, 0.09779, 0.08129, 0.06664, 0.04781, 0.1885, 0.05766,
            0.2031, 0.9861, 1.809, 33.5, 0.00126, 0.01291, 0.01881, 0.01252, 0.01619, 0.003142,
            15.11, 19.26, 99.7, 711.2, 0.144, 0.1773, 0.239, 0.1288, 0.2977, 0.07259
        ]])
        
        # 进行预测
        result = random_forest_predict(clf, test_data)
        
        if result is not None and result[0] is not None:
            output, prob, time_taken = result
            print(f"✓ 预测成功: {output[0]}, 概率: {prob[0]}, 用时: {time_taken:.4f}s")
            return True
        else:
            print("✗ 预测失败")
            return False
            
    except Exception as e:
        print(f"✗ 预测测试过程中发生错误: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试修复后的应用...")
    print("=" * 50)
    
    # 测试模型加载
    model_test = test_model_loading()
    print()
    
    # 测试预测功能
    prediction_test = test_prediction()
    print()
    
    # 总结
    print("=" * 50)
    if model_test and prediction_test:
        print("✓ 所有测试通过！应用修复成功。")
        print("现在可以启动Flask应用：python app_new.py")
        return True
    else:
        print("✗ 部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
