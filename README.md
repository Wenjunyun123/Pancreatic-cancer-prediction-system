# 乳腺癌预测系统UI包

这个包含了乳腺癌预测系统的UI界面和预测模型，允许用户通过Web界面对乳腺癌进行良恶性预测。

## 包内容

- `app_new.py`: Web应用主程序
- `implementation.py`: 模型实现代码
- `config.py`: 配置文件
- `utils.py`: 工具函数
- `requirements.txt`: 依赖库列表
- `templates/`: HTML模板目录
- `static/`: 静态资源目录(CSS、JS、图片)
- `models/`: 预训练模型文件
- `乳腺癌预测器UI项目报告.md`: 项目详细报告
- `todo.md`: 待办事项列表

## 安装步骤

1. 确保已安装Python 3.7+
2. 解压此压缩包：
   ```
   tar -xzvf breast_cancer_predictor_ui.tar.gz
   cd breast_cancer_predictor_ui
   ```
3. 安装依赖库：
   ```
   pip install -r requirements.txt
   ```

## 启动应用

```bash
python app_new.py
```

启动后，在浏览器中访问 http://localhost:5000 即可使用系统。

## 使用方法

1. 在首页点击"开始预测"
2. 按照表单提示填写30个细胞核特征参数
3. 提交表单后，系统将显示预测结果及置信度

## 项目说明

本系统使用随机森林算法，基于威斯康星乳腺癌数据集训练，预测准确率达到96%以上。详细内容请参见`乳腺癌预测器UI项目报告.md`文件。