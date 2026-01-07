# 数据库模型定义
# 定义数据库模型（表结构）
# 每个 Python 类都对应数据库中的一个表，类的属性对应表的列。
# SQLAlchemy 会自动将这个 Python 类转换成 SQLite 的建表语句。

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import datetime

# 创建对象的基类
Base = declarative_base()

# 定义映射对象

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), default='user') # 'admin' or 'user'
    
    # 关联模型(关联表)
    borrow_records = relationship("BorrowRecord", back_populates="user")

    # 便于打印
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    isbn = Column(String(20), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    category = Column(String(50))
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    
    borrow_records = relationship("BorrowRecord", back_populates="book")

    def __repr__(self):
        return f"<Book(title='{self.title}', available={self.available_copies}/{self.total_copies})>"

class BorrowRecord(Base):
    __tablename__ = 'borrow_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    borrow_date = Column(DateTime, default=datetime.datetime.now)
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")

    def __repr__(self):
        return f"<BorrowRecord(user='{self.user.username}', book='{self.book.title}', due='{self.due_date}')>"
