"""
乳腺癌预测系统配置文件
"""

import os

# 项目路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 模型配置
MODEL_CONFIG = {
    'model_dir': os.path.join(PROJECT_ROOT, 'models'),
    'model_file': 'random_forest_model.joblib',
    'scaler_file': 'scaler.joblib',
    'encoder_file': 'label_encoder.joblib',
}

# 数据集配置
DATASET_CONFIG = {
    'dataset_file': os.path.join(PROJECT_ROOT, 'Breast Cancer Data.csv'),
    'train_test_split': 0.2,
    'random_state': 42,
}

# Web应用配置
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'static_dir': os.path.join(PROJECT_ROOT, 'static'),
    'templates_dir': os.path.join(PROJECT_ROOT, 'templates'),
}

# 系统特征列表
FEATURE_NAMES = [
    "radius_mean", "texture_mean", "perimeter_mean", "area_mean", "smoothness_mean",
    "compactness_mean", "concavity_mean", "concave points_mean", "symmetry_mean", "fractal_dimension_mean",
    "radius_se", "texture_se", "perimeter_se", "area_se", "smoothness_se",
    "compactness_se", "concavity_se", "concave points_se", "symmetry_se", "fractal_dimension_se",
    "radius_worst", "texture_worst", "perimeter_worst", "area_worst", "smoothness_worst",
    "compactness_worst", "concavity_worst", "concave points_worst", "symmetry_worst", "fractal_dimension_worst"
]

# 模型超参数
MODEL_PARAMS = {
    'n_estimators': 100,
    'criterion': 'gini',
    'max_depth': None,
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'random_state': 42,
}