# 认证管理类
# 负责用户注册、登录、登出等认证操作

import hashlib
from sqlalchemy.orm import Session
from models import User
from logger_config import logger

class AuthManager:
    
    # 初始对象实例
    def __init__(self, db: Session):
        self.db = db    # 将数据库会话存放在自己的属性里
        self.current_user = None  # 当前登录用户

    def hash_password(self, password):
        # 密码哈希加密
        return hashlib.sha256(password.encode()).hexdigest()

    # 用户注册
    def register(self, username, password, is_admin=False):
        if self.db.query(User).filter(User.username == username).first():
            logger.warning(f"Registration failed: Username '{username}' already exists")
            return False, "用户名已存在"
        
        try:
            role = 'admin' if is_admin else 'user'

            new_user = User(
                username=username,
                password_hash=self.hash_password(password),
                role=role
            )
            # 将新用户添加到数据库会话
            self.db.add(new_user)
            self.db.commit()
            logger.info(f"User registered: {username} (Role: {role})")
            return True, "注册成功"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Registration error for {username}: {e}")
            return False, f"注册失败: {e}"

    # 用户登录
    def login(self, username, password):
        user = self.db.query(User).filter(User.username == username).first()
        
        if user and user.password_hash == self.hash_password(password):
            self.current_user = user
            logger.info(f"User logged in: {username}")
            return True, "登录成功"
        
        logger.warning(f"Login failed for user: {username}")
        return False, "用户名或密码错误"

    # 用户登出
    def logout(self):
        if self.current_user:
            logger.info(f"User logged out: {self.current_user.username}")
            self.current_user = None
