import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import joblib
import logging
import sys

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from time import time
from sklearn.preprocessing import StandardScaler, LabelEncoder

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('model.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 全局变量
X_test = None
y_test = None
sc = None
model_path = 'models'

def random_forest_train():
    global X_test, y_test, sc

    try:
        # 创建模型目录（如果不存在）
        if not os.path.exists(model_path):
            os.makedirs(model_path)

        # 导入数据集
        csv_file_path = 'Breast Cancer Data.csv'
        if not os.path.exists(csv_file_path):
            error_msg = f'未找到 CSV 文件，请将 `Breast Cancer Data.csv` 文件放置到 {os.path.abspath(".")} 目录下。'
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info("开始加载数据集...")
        dataset = pd.read_csv(csv_file_path)
        X = dataset.iloc[:, 2:32].values
        y = dataset.iloc[:, 1].values
        logger.info(f"数据集加载完成，样本数: {len(X)}, 特征数: {X.shape[1]}")

        # 对目标进行编码
        labelencoder = LabelEncoder()
        y = labelencoder.fit_transform(y)

        # 保存编码器
        joblib.dump(labelencoder, os.path.join(model_path, 'label_encoder.joblib'))

        # 分割数据集为训练集和测试集
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
        logger.info(f"数据集分割完成，训练集: {len(X_train)}, 测试集: {len(X_test)}")

        # 特征缩放
        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test)

        # 保存缩放器
        joblib.dump(sc, os.path.join(model_path, 'scaler.joblib'))

        # 训练随机森林模型
        logger.info("开始训练随机森林模型...")
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        # 保存模型
        model_file = os.path.join(model_path, 'random_forest_model.joblib')
        joblib.dump(clf, model_file)

        logger.info(f"模型已保存到 {model_file}")
        return clf

    except Exception as e:
        logger.error(f"模型训练过程中发生错误: {str(e)}", exc_info=True)
        return None

def load_model():
    """加载已保存的模型和相关预处理工具"""
    global sc

    try:
        model_file = os.path.join(model_path, 'random_forest_model.joblib')
        scaler_file = os.path.join(model_path, 'scaler.joblib')

        if not os.path.exists(model_file):
            logger.warning("模型文件不存在，需要先训练模型")
            return None

        if not os.path.exists(scaler_file):
            logger.warning("缩放器文件不存在，需要先训练模型")
            return None

        # 加载模型
        logger.info("加载模型文件...")
        clf = joblib.load(model_file)

        # 加载缩放器
        logger.info("加载缩放器文件...")
        sc = joblib.load(scaler_file)

        logger.info("模型和缩放器加载成功")
        return clf

    except Exception as e:
        logger.error(f"加载模型时发生错误: {str(e)}", exc_info=True)
        return None

def randorm_forest_test(clf):
    """测试模型准确性"""
    try:
        if X_test is None or y_test is None:
            logger.warning("没有测试数据，需要先运行训练函数")
            return None

        t = time()
        output = clf.predict(X_test)
        acc = accuracy_score(y_test, output)
        elapsed_time = time()-t

        logger.info(f"测试数据的准确率: {acc:.4f}")
        logger.info(f"测试运行时间: {elapsed_time:.4f}s")
        return acc

    except Exception as e:
        logger.error(f"模型测试时发生错误: {str(e)}", exc_info=True)
        return None

def random_forest_predict(clf, inp):
    """对新数据进行预测"""
    global sc

    try:
        if sc is None:
            # 如果scaler没有被初始化，尝试加载
            try:
                sc = joblib.load(os.path.join(model_path, 'scaler.joblib'))
                logger.info("成功加载缩放器")
            except Exception as e:
                logger.error(f"未找到scaler模型，请确保已正确训练模型: {e}")
                return None, None, 0

        t = time()
        inp_scaled = sc.transform(inp)
        output = clf.predict(inp_scaled)
        proba = clf.predict_proba(inp_scaled)
        elapsed_time = time()-t

        logger.info(f"预测运行时间: {elapsed_time:.4f}s")
        logger.debug(f"预测结果: {output}, 概率: {proba}")

        return output, proba, elapsed_time

    except Exception as e:
        logger.error(f"预测过程中发生错误: {str(e)}", exc_info=True)
        return None, None, 0