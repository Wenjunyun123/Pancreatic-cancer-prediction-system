"""
用户管理模块
提供用户注册、登录、验证等功能
"""

import json
import os
import hashlib
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.users = self._load_users()
        
    def _load_users(self):
        """加载用户数据"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
                logger.info(f"加载了 {len(users)} 个用户")
                return users
            else:
                # 创建默认演示用户
                default_users = {
                    "demo": {
                        "user_id": str(uuid.uuid4()),
                        "username": "demo",
                        "email": "demo@example.com",
                        "full_name": "演示用户",
                        "password_hash": self._hash_password("demo123"),
                        "role": "patient",
                        "created_at": datetime.now().isoformat(),
                        "last_login": None,
                        "is_active": True,
                        "prediction_count": 0
                    }
                }
                self._save_users(default_users)
                logger.info("创建了默认演示用户")
                return default_users
        except Exception as e:
            logger.error(f"加载用户数据失败: {e}")
            return {}
    
    def _save_users(self, users=None):
        """保存用户数据"""
        try:
            if users is None:
                users = self.users
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            logger.info("用户数据已保存")
        except Exception as e:
            logger.error(f"保存用户数据失败: {e}")
    
    def _hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password, password_hash):
        """验证密码"""
        return self._hash_password(password) == password_hash
    
    def register_user(self, username, email, password, full_name="", role="patient"):
        """注册新用户"""
        try:
            # 检查用户名是否已存在
            if username in self.users:
                return False, "用户名已存在"
            
            # 检查邮箱是否已存在
            for user_data in self.users.values():
                if user_data.get('email') == email:
                    return False, "邮箱已被注册"
            
            # 验证用户名格式
            if not username or len(username) < 3 or len(username) > 20:
                return False, "用户名长度必须在3-20个字符之间"
            
            # 验证密码长度
            if not password or len(password) < 6:
                return False, "密码长度至少6位"
            
            # 创建新用户
            user_data = {
                "user_id": str(uuid.uuid4()),
                "username": username,
                "email": email,
                "full_name": full_name,
                "password_hash": self._hash_password(password),
                "role": role,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "is_active": True,
                "prediction_count": 0
            }
            
            self.users[username] = user_data
            self._save_users()
            
            logger.info(f"新用户注册成功: {username}")
            return True, "注册成功"
            
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return False, "注册失败，请重试"
    
    def authenticate_user(self, username, password):
        """用户登录验证"""
        try:
            if username not in self.users:
                return False, "用户名不存在"
            
            user_data = self.users[username]
            
            if not user_data.get('is_active', True):
                return False, "账户已被禁用"
            
            if not self._verify_password(password, user_data['password_hash']):
                return False, "密码错误"
            
            # 更新最后登录时间
            user_data['last_login'] = datetime.now().isoformat()
            self._save_users()
            
            logger.info(f"用户登录成功: {username}")
            return True, user_data
            
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return False, "登录失败，请重试"
    
    def get_user(self, username):
        """获取用户信息"""
        return self.users.get(username)
    
    def update_user(self, username, **kwargs):
        """更新用户信息"""
        try:
            if username not in self.users:
                return False, "用户不存在"
            
            user_data = self.users[username]
            
            # 更新允许的字段
            allowed_fields = ['email', 'full_name', 'role']
            for field, value in kwargs.items():
                if field in allowed_fields:
                    user_data[field] = value
            
            user_data['updated_at'] = datetime.now().isoformat()
            self._save_users()
            
            logger.info(f"用户信息更新成功: {username}")
            return True, "更新成功"
            
        except Exception as e:
            logger.error(f"用户信息更新失败: {e}")
            return False, "更新失败，请重试"
    
    def change_password(self, username, old_password, new_password):
        """修改密码"""
        try:
            if username not in self.users:
                return False, "用户不存在"
            
            user_data = self.users[username]
            
            # 验证旧密码
            if not self._verify_password(old_password, user_data['password_hash']):
                return False, "原密码错误"
            
            # 验证新密码长度
            if len(new_password) < 6:
                return False, "新密码长度至少6位"
            
            # 更新密码
            user_data['password_hash'] = self._hash_password(new_password)
            user_data['password_updated_at'] = datetime.now().isoformat()
            self._save_users()
            
            logger.info(f"用户密码修改成功: {username}")
            return True, "密码修改成功"
            
        except Exception as e:
            logger.error(f"密码修改失败: {e}")
            return False, "密码修改失败，请重试"
    
    def increment_prediction_count(self, username):
        """增加预测次数"""
        try:
            if username in self.users:
                self.users[username]['prediction_count'] = self.users[username].get('prediction_count', 0) + 1
                self._save_users()
                logger.info(f"用户 {username} 预测次数已更新")
        except Exception as e:
            logger.error(f"更新预测次数失败: {e}")
    
    def get_user_stats(self):
        """获取用户统计信息"""
        try:
            total_users = len(self.users)
            active_users = sum(1 for user in self.users.values() if user.get('is_active', True))
            total_predictions = sum(user.get('prediction_count', 0) for user in self.users.values())
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_predictions': total_predictions
            }
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {'total_users': 0, 'active_users': 0, 'total_predictions': 0}

# 全局用户管理器实例
user_manager = UserManager()
