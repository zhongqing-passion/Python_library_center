# 图书管理类
# 负责图书的添加、删除、查询等操作

import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Book, BorrowRecord, User
from logger_config import logger

class LibraryManager:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user = current_user

    # --- Book Management (Admin) ---
    # 管理员添加图书
    def add_book(self, isbn, title, author, category, total_copies):
        if self.user.role != 'admin':
            return False, "权限不足"
        
        try:
            book = self.db.query(Book).filter(Book.isbn == isbn).first()
            if book:
                # Update existing book copies
                book.total_copies += int(total_copies)
                book.available_copies += int(total_copies)
                msg = f"图书已存在，库存增加。当前库存: {book.available_copies}/{book.total_copies}"
            else:
                new_book = Book(
                    isbn=isbn,
                    title=title,
                    author=author,
                    category=category,
                    total_copies=int(total_copies),
                    available_copies=int(total_copies)
                )
                self.db.add(new_book)   # 标记为待添加
                msg = "新书添加成功"
            
            self.db.commit()    # 提交事务，此时数据库中才会有新的图书记录
            logger.info(f"Admin {self.user.username} added book: {title} (ISBN: {isbn})")
            return True, msg
        except Exception as e:
            self.db.rollback()
            logger.error(f"Add book failed: {e}")
            return False, f"操作失败: {e}"


    # 管理员删除图书
    # def remove_book(self, isbn):
    #     if self.user.role != 'admin':
    #         return False, "权限不足"
            
    #     book = self.db.query(Book).filter(Book.isbn == isbn).first()
    #     if not book:
    #         return False, "未找到该图书"
            
    #     try:
    #         self.db.delete(book)
    #         self.db.commit()
    #         logger.info(f"Admin {self.user.username} removed book: {book.title} (ISBN: {isbn})")
    #         return True, "图书删除成功"
    #     except Exception as e:
    #         self.db.rollback()
    #         logger.error(f"Remove book failed: {e}")
    #         return False, f"删除失败(可能存在关联借阅记录): {e}"
    def remove_book(self, title):
        if self.user.role != 'admin':
            return False, "权限不足"
            
        book = self.db.query(Book).filter(Book.title == title).first()
        if not book:
            return False, "未找到该图书"
            
        try:
            self.db.delete(book)
            self.db.commit()
            logger.info(f"Admin {self.user.username} removed book: {book.title} (ISBN: {book.isbn})")
            return True, "图书删除成功"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Remove book failed: {e}")
            return False, f"删除失败(可能存在关联借阅记录): {e}"

    # --- Borrowing Logic ---
    # 用户借阅图书
    def borrow_book(self, isbn):
        book = self.db.query(Book).filter(Book.isbn == isbn).first()
        if not book:
            return False, "未找到该图书"
        
        if book.available_copies <= 0:
            return False, "暂无库存"
            
        try:
            book.available_copies -= 1
            due_date = datetime.datetime.now() + datetime.timedelta(days=3)
            
            record = BorrowRecord(
                user_id=self.user.id,
                book_id=book.id,
                due_date=due_date
            )
            self.db.add(record)
            self.db.commit()
            logger.info(f"User {self.user.username} borrowed '{book.title}'")
            return True, f"借阅成功，请于 {due_date.strftime('%Y-%m-%d')} 前归还"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Borrow failed: {e}")
            return False, f"借阅失败: {e}"

    # 用户归还图书
    def return_book(self, isbn):
        # 查找该图书的借阅记录book_id
        # 借阅表只存储了book_id，所以要通过isbn关联查询book_id
        record = self.db.query(BorrowRecord).join(Book).filter(
            BorrowRecord.user_id == self.user.id,       # 归还的用户是当前登录用户
            Book.isbn == isbn,      # 借阅书的ISBN必须与归还的ISBN一致
            BorrowRecord.return_date == None    # 归还日期必须为空，表示未还
        ).first()
        
        if not record:
            return False, "未找到该书的借阅记录"
            
        try:
            record.return_date = datetime.datetime.now()
            record.book.available_copies += 1
            self.db.commit()
            logger.info(f"User {self.user.username} returned '{record.book.title}' (ISBN: {record.book.isbn})")
            return True, "归还成功"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Return failed: {e}")
            return False, f"归还失败: {e}"

    # 用户查询图书(根据书名或作者作为关键词查询)
    def list_books(self, keyword=None):
        query = self.db.query(Book)
        if keyword:
            query = query.filter(
                (Book.title.contains(keyword)) | 
                (Book.author.contains(keyword))
            )
        return query.all()

    # 管理员查询统计信息(热门图书、逾期图书)
    def get_stats(self):
        if self.user.role != 'admin':
            return None
            
        # 1. 最受欢迎的图书(借阅次数最多的前5本)
        hot_books = self.db.query(
            Book.title, func.count(BorrowRecord.id).label('count')
        ).join(BorrowRecord).group_by(Book.id).order_by(func.count(BorrowRecord.id).desc()).limit(5).all()
        
        # 2. 逾期图书列表(未归还且超期的图书)
        overdue = self.db.query(BorrowRecord).filter(
            BorrowRecord.return_date == None,
            BorrowRecord.due_date < datetime.datetime.now()
        ).all()
        
        # 3. 逾期图书详情(包括用户、图书、超期时间)
        # 使用 select_from 明确查询主体，解决多表 Join 时的路径歧义问题
        overdue_details = self.db.query(
            User.username, Book.title, BorrowRecord.due_date
        ).select_from(BorrowRecord).join(User).join(Book).filter(
            BorrowRecord.return_date == None,
            BorrowRecord.due_date < datetime.datetime.now()
        ).all()
        
        return {
            "hot_books": hot_books,
            "overdue_count": len(overdue),
            "overdue_list": overdue_details
        }
