from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from logger_config import logger

# Configuration
# For production PostgreSQL:
# DB_URL = "postgresql://user:password@localhost/library_db"

# For local testing (SQLite):
# 当前所在目录下的library.db文件即为数据库
DB_URL = "sqlite:///library.db"

engine = None
SessionLocal = None

# 初始化数据库
def init_db():
    global engine, SessionLocal
    try:
        # 创建数据库引擎
        engine = create_engine(DB_URL, echo=False)
        # 创建数据库会话工厂
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        # 通过之前定义的 Base 基类，自动创建所有继承 Base 的模型对应的数据库表
        Base.metadata.create_all(bind=engine)
        logger.info(f"数据库初始化成功: {DB_URL}")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

# 获取数据库会话
# 每次请求结束后，会自动关闭会话，释放资源
def get_db():
    if SessionLocal is None:
        init_db()
    # 通过会话工厂创建一个具体的会话实例
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
