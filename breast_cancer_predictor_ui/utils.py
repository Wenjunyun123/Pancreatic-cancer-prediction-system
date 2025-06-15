"""
工具函数模块，包含各种辅助功能。
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
from config import MODEL_CONFIG, DATASET_CONFIG, FEATURE_NAMES

def load_model_components():
    """加载模型及相关组件
    
    Returns:
        tuple: (model, scaler, encoder) 或在失败时返回 (None, None, None)
    """
    model_dir = MODEL_CONFIG['model_dir']
    model_file = os.path.join(model_dir, MODEL_CONFIG['model_file'])
    scaler_file = os.path.join(model_dir, MODEL_CONFIG['scaler_file'])
    encoder_file = os.path.join(model_dir, MODEL_CONFIG['encoder_file'])
    
    # 检查文件是否存在
    if not all(os.path.exists(f) for f in [model_file, scaler_file, encoder_file]):
        print("警告：一个或多个模型文件不存在。请先训练模型。")
        return None, None, None
    
    try:
        model = joblib.load(model_file)
        scaler = joblib.load(scaler_file)
        encoder = joblib.load(encoder_file)
        return model, scaler, encoder
    except Exception as e:
        print(f"加载模型组件时出错: {str(e)}")
        return None, None, None

def preprocess_input(input_data, scaler):
    """预处理输入数据
    
    Args:
        input_data: 输入特征，可以是列表、NumPy数组或Pandas DataFrame
        scaler: 标准化器对象
        
    Returns:
        numpy.ndarray: 预处理后的特征数组
    """
    # 转换为NumPy数组
    if isinstance(input_data, list):
        input_array = np.array(input_data).reshape(1, -1)
    elif isinstance(input_data, pd.DataFrame):
        input_array = input_data.values
    else:
        input_array = input_data
        
    # 确保是二维数组
    if input_array.ndim == 1:
        input_array = input_array.reshape(1, -1)
        
    # 应用标准化
    return scaler.transform(input_array)

def get_feature_importance(model, feature_names=FEATURE_NAMES):
    """获取特征重要性
    
    Args:
        model: 训练好的模型对象
        feature_names: 特征名称列表
        
    Returns:
        pandas.DataFrame: 包含特征名称和重要性得分的DataFrame，按重要性降序排列
    """
    # 获取特征重要性
    importances = model.feature_importances_
    
    # 创建DataFrame
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    })
    
    # 按重要性降序排序
    importance_df = importance_df.sort_values('Importance', ascending=False)
    
    return importance_df

def evaluate_model(model, X_test, y_test, feature_names=FEATURE_NAMES):
    """评估模型性能并生成报告
    
    Args:
        model: 训练好的模型对象
        X_test: 测试特征
        y_test: 实际标签
        feature_names: 特征名称列表
        
    Returns:
        dict: 包含各种评估指标的字典
    """
    # 预测
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]  # 获取正类的概率
    
    # 计算基本指标
    accuracy = accuracy_score(y_test, y_pred)
    class_report = classification_report(y_test, y_pred, target_names=['Benign', 'Malignant'])
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    # 计算ROC曲线数据
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    # 特征重要性
    importance_df = get_feature_importance(model, feature_names)
    
    # 返回评估结果
    return {
        'accuracy': accuracy,
        'classification_report': class_report,
        'confusion_matrix': conf_matrix,
        'feature_importance': importance_df,
        'roc_curve': {
            'fpr': fpr,
            'tpr': tpr,
            'auc': roc_auc
        }
    }

def plot_roc_curve(fpr, tpr, roc_auc, save_path=None):
    """绘制ROC曲线
    
    Args:
        fpr: 假正例率
        tpr: 真正例率
        roc_auc: AUC值
        save_path: 保存图像的路径，如果为None则显示图像
    """
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_feature_importance(importance_df, top_n=10, save_path=None):
    """绘制特征重要性图
    
    Args:
        importance_df: 包含特征和重要性的DataFrame
        top_n: 显示前N个重要特征
        save_path: 保存图像的路径，如果为None则显示图像
    """
    # 获取前N个特征
    top_features = importance_df.head(top_n)
    
    plt.figure(figsize=(12, 8))
    bars = plt.barh(top_features['Feature'], top_features['Importance'], color='skyblue')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.title(f'Top {top_n} Important Features')
    plt.gca().invert_yaxis()  # 按重要性降序显示
    
    # 添加数据标签
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.005, bar.get_y() + bar.get_height()/2, f'{width:.4f}', 
                 ha='left', va='center')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def save_evaluation_results(results, output_dir='evaluation_results'):
    """保存评估结果到文件
    
    Args:
        results: 评估结果字典
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存文本结果
    with open(os.path.join(output_dir, 'evaluation_metrics.txt'), 'w') as f:
        f.write(f"模型准确率: {results['accuracy']:.4f}\n\n")
        f.write("分类报告:\n")
        f.write(results['classification_report'])
        f.write("\n混淆矩阵:\n")
        f.write(str(results['confusion_matrix']))
    
    # 保存特征重要性
    results['feature_importance'].to_csv(os.path.join(output_dir, 'feature_importance.csv'), index=False)
    
    # 保存图表
    plot_roc_curve(results['roc_curve']['fpr'], results['roc_curve']['tpr'], 
                  results['roc_curve']['auc'], save_path=os.path.join(output_dir, 'roc_curve.png'))
    
    plot_feature_importance(results['feature_importance'], save_path=os.path.join(output_dir, 'feature_importance.png'))
    
    print(f"评估结果已保存到 {output_dir} 目录")