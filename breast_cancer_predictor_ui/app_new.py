from flask import Flask, render_template, request, redirect, url_for, flash, session
from implementation import randorm_forest_test, random_forest_train, random_forest_predict, load_model
from user_manager import user_manager
import numpy as np
import os
import sys
import logging
from time import time
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = 'breast-cancer-predictor-secret-key-2025'  # 用于session和flash消息

# 全局模型变量
clf = None
model_accuracy = None

# 登录装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录后再使用预测功能', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """首页路由"""
    return render_template('home_new.html')

@app.route('/predict-form')
def predict_form():
    """参数输入表单页面"""
    return render_template('predict_form.html')

@app.route('/params-info')
def params_info():
    """参数解释页面"""
    return render_template('params_info.html')

@app.route('/about')
def about():
    """关于项目页面"""
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not username or not password:
            return render_template('login.html', error='请输入用户名和密码')

        success, result = user_manager.authenticate_user(username, password)

        if success:
            # 登录成功，设置session
            session['user_id'] = result['user_id']
            session['username'] = result['username']
            session['role'] = result['role']
            session['full_name'] = result.get('full_name', '')

            # 如果选择记住我，设置session为永久
            if remember:
                session.permanent = True

            logger.info(f"用户登录成功: {username}")
            flash(f'欢迎回来，{result.get("full_name") or username}！', 'success')

            # 重定向到原来要访问的页面或首页
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            return render_template('login.html', error=result)

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'patient')
        agree_terms = request.form.get('agree_terms') == 'on'

        # 验证必填字段
        if not all([username, email, password, confirm_password]):
            return render_template('register.html', error='请填写所有必填字段')

        # 验证密码确认
        if password != confirm_password:
            return render_template('register.html', error='两次输入的密码不一致')

        # 验证服务条款
        if not agree_terms:
            return render_template('register.html', error='请同意服务条款和隐私政策')

        # 注册用户
        success, message = user_manager.register_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role
        )

        if success:
            logger.info(f"新用户注册成功: {username}")
            flash('注册成功！请登录您的账户。', 'success')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error=message)

    return render_template('register.html')

@app.route('/logout')
def logout():
    """用户登出"""
    username = session.get('username', '未知用户')
    session.clear()
    logger.info(f"用户登出: {username}")
    flash('您已成功登出', 'info')
    return redirect(url_for('index'))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """处理预测请求"""
    try:
        # 获取表单数据
        data_points = []
        data = []

        # 从表单中提取30个特征值
        for i in range(1, 31):
            try:
                value = float(request.form[f'value{i}'])
                data.append(value)
            except (ValueError, KeyError) as e:
                logger.error(f"参数 value{i} 格式错误: {e}")
                return render_template('predict_form.html', error=f"参数 {i} 格式错误，请输入有效数字")

        for i in range(30):
            data_points.append(data[i])

        # 使用日志记录而不是print，避免管道错误
        logger.info(f"输入特征数量: {len(data_points)}")
        logger.debug(f"输入特征: {data_points}")

        # 检查模型是否已加载
        if clf is None:
            logger.error("模型未加载")
            return render_template('predict_form.html', error="模型未加载，请重启应用")

        # 转换为NumPy数组
        data_np = np.asarray(data, dtype=float)
        data_np = data_np.reshape(1, -1)

        # 进行预测
        result = random_forest_predict(clf, data_np)
        if result is None or result[0] is None:
            logger.error("预测失败")
            return render_template('predict_form.html', error="预测失败，请检查输入数据")

        out, prob, t = result

        # 解释预测结果
        if out[0] == 1:
            output = 'Malignant'
        else:
            output = 'Benign'

        # 获取预测概率
        prob_benign = prob[0][0]
        prob_malignant = prob[0][1]

        # 获取最终概率值
        final_prob = max(prob_benign, prob_malignant)

        logger.info(f"预测完成: {output}, 置信度: {final_prob:.4f}, 用时: {t:.4f}s")

        # 记录用户预测次数
        if 'username' in session:
            user_manager.increment_prediction_count(session['username'])

        return render_template('result_new.html', output=output, accuracy=final_prob, time=t)

    except Exception as e:
        logger.error(f"预测过程中发生错误: {str(e)}", exc_info=True)
        return render_template('predict_form.html', error="预测过程中发生错误，请重试")

@app.route('/profile')
@login_required
def profile():
    """用户个人资料页面"""
    username = session.get('username')
    user_data = user_manager.get_user(username)
    if user_data:
        return render_template('profile.html', user=user_data)
    else:
        flash('用户信息不存在', 'error')
        return redirect(url_for('logout'))

@app.route('/history')
@login_required
def history():
    """用户预测历史页面"""
    username = session.get('username')
    user_data = user_manager.get_user(username)
    return render_template('history.html', user=user_data)

@app.route('/test-login')
def test_login():
    """测试登录功能页面"""
    return render_template('test_login.html')

# 添加flash消息显示的上下文处理器
@app.context_processor
def inject_flash_messages():
    from flask import get_flashed_messages
    return dict(get_flashed_messages=get_flashed_messages)

def init_model():
    """初始化模型 - 如果已保存则加载，否则训练新模型"""
    global clf, model_accuracy

    try:
        model_file = 'models/random_forest_model.joblib'

        # 检查模型文件是否存在
        if os.path.exists(model_file):
            logger.info("加载现有模型...")
            clf = load_model()
            if clf is None:
                logger.warning("模型加载失败，尝试重新训练...")
                clf = random_forest_train()
        else:
            logger.info("训练新模型...")
            clf = random_forest_train()

        if clf is None:
            logger.error("模型初始化失败")
            return False

        # 测试模型性能
        try:
            model_accuracy = randorm_forest_test(clf)
            logger.info(f"模型准确率: {model_accuracy}")
        except Exception as e:
            logger.warning(f"模型测试失败: {e}")
            model_accuracy = None

        return True

    except Exception as e:
        logger.error(f"模型初始化过程中发生错误: {str(e)}", exc_info=True)
        return False

if __name__ == '__main__':
    # 初始化模型
    if init_model():
        logger.info("模型初始化成功，启动Flask应用...")
        # 启动Flask应用，关闭调试模式以避免管道错误
        app.run(debug=False, host='0.0.0.0', port=5000)
    else:
        logger.error("模型初始化失败，无法启动应用")
        sys.exit(1)