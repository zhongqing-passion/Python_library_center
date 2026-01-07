import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from db import get_db, init_db
from auth import AuthManager
from manager import LibraryManager
from scanner import BarcodeScanner
from models import Book

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("简易图书管理系统")
        self.root.geometry("900x600")
        
        # 初始化数据库连接
        init_db()
        self.db = next(get_db())
        self.auth = AuthManager(self.db)
        self.scanner = BarcodeScanner()
        
        self.current_user = None
        self.manager = None

        # 设置样式
        self.setup_styles()
        
        # 显示登录界面
        self.show_login_screen()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # 定义现代配色方案
        self.colors = {
            "bg": "#f0f2f5",         # 浅灰背景
            "card": "#ffffff",       # 卡片白色背景
            "primary": "#1890ff",    # 主色调（蓝）
            "primary_hover": "#40a9ff",
            "text": "#333333",       # 主要文字
            "text_light": "#666666", # 次要文字
            "success": "#52c41a",
            "warning": "#faad14"
        }

        # 设置根窗口背景色
        self.root.configure(bg=self.colors["bg"])

        # 配置通用字体
        base_font = ("Microsoft YaHei UI", 10)
        
        # --- Frame 样式 ---
        # 默认 Frame 跟随窗口背景
        style.configure("TFrame", background=self.colors["bg"])
        # 卡片 Frame (用于登录框、内容区)
        style.configure("Card.TFrame", background=self.colors["card"], relief="flat")
        # LabelFrame 样式
        style.configure("TLabelframe", background=self.colors["bg"], relief="groove")
        style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["text"], font=("Microsoft YaHei UI", 10, "bold"))
        
        # --- Label 样式 ---
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=base_font)
        style.configure("Card.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=base_font)
        
        # 标题
        style.configure("Header.TLabel", background=self.colors["card"], foreground=self.colors["text"], font=("Microsoft YaHei UI", 24, "bold"))
        # 顶部栏信息
        style.configure("Info.TLabel", background=self.colors["bg"], foreground=self.colors["text_light"], font=("Microsoft YaHei UI", 10))

        # --- Button 样式 ---
        style.configure("TButton", font=base_font, padding=5)
        
        # 大按钮 (用于登录、借还书等主要操作)
        style.configure("Big.TButton", font=("Microsoft YaHei UI", 12, "bold"), padding=10, background=self.colors["primary"], foreground="white", borderwidth=0)
        style.map("Big.TButton", 
                  background=[("active", self.colors["primary_hover"])],
                  foreground=[("active", "white")])
        
        # 次要按钮 (注册等)
        style.configure("Secondary.TButton", font=("Microsoft YaHei UI", 11), padding=8)

        # --- Checkbutton ---
        style.configure("Card.TCheckbutton", background=self.colors["card"], font=base_font)
        
        # --- Treeview ---
        style.configure("Treeview", font=("Microsoft YaHei UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"))

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==========================================
    # 登录/注册 模块
    # ==========================================
    def show_login_screen(self):
        self.clear_window()
        
        # 居中容器
        container = ttk.Frame(self.root)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 登录卡片
        card = ttk.Frame(container, style="Card.TFrame", padding="40")
        card.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(card, text="图书管理系统", style="Header.TLabel").pack(pady=(0, 30))
        
        # 输入区
        input_frame = ttk.Frame(card, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=10)
        
        # 用户名
        ttk.Label(input_frame, text="账号", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 5))
        self.entry_user = ttk.Entry(input_frame, width=32, font=("Microsoft YaHei UI", 11))
        self.entry_user.pack(fill=tk.X, pady=(0, 15))
        
        # 密码
        ttk.Label(input_frame, text="密码", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 5))
        self.entry_pass = ttk.Entry(input_frame, show="●", width=32, font=("Microsoft YaHei UI", 11))
        self.entry_pass.pack(fill=tk.X, pady=(0, 15))
        
        # 选项
        self.var_is_admin = tk.BooleanVar()
        self.chk_admin = ttk.Checkbutton(input_frame, text="注册为管理员", variable=self.var_is_admin, style="Card.TCheckbutton", cursor="hand2")
        self.chk_admin.pack(anchor=tk.W, pady=(0, 20))
        
        # 按钮区
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="立即登录", command=self.perform_login, style="Big.TButton", cursor="hand2").pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="注册账号", command=self.perform_register, style="Secondary.TButton", cursor="hand2").pack(fill=tk.X, pady=5)

    def perform_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        success, msg = self.auth.login(username, password)
        if success:
            self.current_user = self.auth.current_user
            self.manager = LibraryManager(self.db, self.current_user)
            self.show_main_screen()
        else:
            messagebox.showerror("登录失败", msg)

    def perform_register(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        is_admin = self.var_is_admin.get()

        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        success, msg = self.auth.register(username, password, is_admin)
        if success:
            messagebox.showinfo("注册成功", msg)
        else:
            messagebox.showerror("注册失败", msg)

    def logout(self):
        if self.auth:
            self.auth.logout()
        self.current_user = None
        self.manager = None
        self.show_login_screen()

    # ==========================================
    # 主界面 模块
    # ==========================================
    def show_main_screen(self):
        self.clear_window()
        
        # 顶部栏
        top_bar = ttk.Frame(self.root, padding="10")
        top_bar.pack(fill=tk.X)
        
        user_role = "管理员" if self.current_user.role == 'admin' else "普通用户"
        ttk.Label(top_bar, text=f"当前用户: {self.current_user.username} ({user_role})", style="Info.TLabel").pack(side=tk.LEFT)
        ttk.Button(top_bar, text="退出登录", command=self.logout).pack(side=tk.RIGHT)

        # 选项卡控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Tab 1: 图书列表 (所有人都可见)
        self.tab_books = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_books, text='图书查询')
        self.build_book_list_tab(self.tab_books)

        # Tab 2: 借阅/归还 (所有人都可见)
        self.tab_borrow = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_borrow, text='借阅/归还')
        self.build_borrow_return_tab(self.tab_borrow)

        # Tab 3: 管理员面板 (仅管理员可见)
        if self.current_user.role == 'admin':
            self.tab_admin = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_admin, text='管理员面板')
            self.build_admin_tab(self.tab_admin)

    # ------------------------------------------
    # Tab 1: 图书查询
    # ------------------------------------------
    def build_book_list_tab(self, parent):
        # 搜索栏
        search_frame = ttk.Frame(parent, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="关键词:").pack(side=tk.LEFT)
        self.entry_search = ttk.Entry(search_frame, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        # 绑定回车键搜索
        self.entry_search.bind('<Return>', lambda event: self.refresh_book_list())
        
        ttk.Button(search_frame, text="搜索", command=self.refresh_book_list).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="显示全部", command=lambda: [self.entry_search.delete(0, tk.END), self.refresh_book_list()]).pack(side=tk.LEFT, padx=5)

        # 列表 (Treeview)
        columns = ("isbn", "title", "author", "category", "available")
        self.tree_books = ttk.Treeview(parent, columns=columns, show="headings")
        
        self.tree_books.heading("isbn", text="ISBN")
        self.tree_books.heading("title", text="书名")
        self.tree_books.heading("author", text="作者")
        self.tree_books.heading("category", text="分类")
        self.tree_books.heading("available", text="库存")
        
        self.tree_books.column("isbn", width=120)
        self.tree_books.column("title", width=200)
        self.tree_books.column("author", width=100)
        self.tree_books.column("category", width=80)
        self.tree_books.column("available", width=80)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree_books.yview)
        self.tree_books.configure(yscroll=scrollbar.set)
        
        self.tree_books.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # 初始加载
        self.refresh_book_list()

    def refresh_book_list(self):
        # 清空现有
        for i in self.tree_books.get_children():
            self.tree_books.delete(i)
            
        keyword = self.entry_search.get()
        books = self.manager.list_books(keyword)
        
        if books:
            for b in books:
                self.tree_books.insert("", tk.END, values=(b.isbn, b.title, b.author, b.category, f"{b.available_copies}/{b.total_copies}"))

    # ------------------------------------------
    # Tab 2: 借阅/归还 (带扫码)
    # ------------------------------------------
    def build_borrow_return_tab(self, parent):
        frame = ttk.Frame(parent, padding="40")
        frame.pack(fill=tk.BOTH, expand=True)

        # 操作区域
        op_frame = ttk.LabelFrame(frame, text="操作区域", padding="20")
        op_frame.pack(fill=tk.X, pady=20)

        ttk.Label(op_frame, text="图书 ISBN:").grid(row=0, column=0, sticky=tk.W, pady=10)
        
        self.entry_isbn_op = ttk.Entry(op_frame, width=30, font=("Arial", 14))
        self.entry_isbn_op.grid(row=0, column=1, padx=10, pady=10)

        # 扫码按钮 (移除Emoji，防止Windows显示问题)
        btn_scan = ttk.Button(op_frame, text="扫码输入", command=self.scan_isbn_for_op)
        btn_scan.grid(row=0, column=2, padx=10)

        # 借还按钮
        btn_borrow = ttk.Button(op_frame, text="借阅图书", command=self.action_borrow, style="Big.TButton")
        btn_borrow.grid(row=1, column=1, pady=20, sticky=tk.W)
        
        btn_return = ttk.Button(op_frame, text="归还图书", command=self.action_return, style="Big.TButton")
        btn_return.grid(row=1, column=2, pady=20, sticky=tk.W)

        # 说明
        ttk.Label(frame, text="提示: 您可以手动输入ISBN，或点击'扫码输入'使用摄像头识别书籍背面的条形码。", foreground="gray").pack(pady=10)

    def scan_isbn_for_op(self):
        isbn = self.scanner.scan_isbn()
        if isbn:
            self.entry_isbn_op.delete(0, tk.END)
            self.entry_isbn_op.insert(0, isbn)
            messagebox.showinfo("扫码成功", f"已识别 ISBN: {isbn}")
        else:
            # 如果是取消，通常不需要弹窗，或者在scanner里打印了
            pass

    def action_borrow(self):
        isbn = self.entry_isbn_op.get().strip()
        if not isbn:
            messagebox.showwarning("提示", "请输入或扫描 ISBN")
            return
        
        success, msg = self.manager.borrow_book(isbn)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_book_list() # 刷新库存显示
        else:
            messagebox.showerror("失败", msg)

    def action_return(self):
        isbn = self.entry_isbn_op.get().strip()
        if not isbn:
            messagebox.showwarning("提示", "请输入或扫描 ISBN")
            return
        
        success, msg = self.manager.return_book(isbn)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_book_list()
        else:
            messagebox.showerror("失败", msg)

    # ------------------------------------------
    # Tab 3: 管理员面板
    # ------------------------------------------
    def build_admin_tab(self, parent):
        # 左右分栏
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧：添加图书
        frame_add = ttk.LabelFrame(paned, text="添加图书", padding="10", width=300)
        paned.add(frame_add, weight=1)

        ttk.Label(frame_add, text="ISBN:").pack(anchor=tk.W)
        self.entry_add_isbn = ttk.Entry(frame_add)
        self.entry_add_isbn.pack(fill=tk.X, pady=2)
        
        # 扫码填入 ISBN (移除Emoji)
        ttk.Button(frame_add, text="扫码填入", command=self.scan_isbn_for_add).pack(anchor=tk.W, pady=2)

        ttk.Label(frame_add, text="书名:").pack(anchor=tk.W, pady=(10,0))
        self.entry_add_title = ttk.Entry(frame_add)
        self.entry_add_title.pack(fill=tk.X, pady=2)

        ttk.Label(frame_add, text="作者:").pack(anchor=tk.W, pady=(10,0))
        self.entry_add_author = ttk.Entry(frame_add)
        self.entry_add_author.pack(fill=tk.X, pady=2)

        ttk.Label(frame_add, text="分类:").pack(anchor=tk.W, pady=(10,0))
        self.entry_add_category = ttk.Entry(frame_add)
        self.entry_add_category.pack(fill=tk.X, pady=2)

        ttk.Label(frame_add, text="数量:").pack(anchor=tk.W, pady=(10,0))
        self.entry_add_copies = ttk.Entry(frame_add)
        self.entry_add_copies.pack(fill=tk.X, pady=2)

        ttk.Button(frame_add, text="确认添加", command=self.action_add_book, style="Big.TButton").pack(pady=20, fill=tk.X)

        # 右侧：统计数据
        frame_stats = ttk.LabelFrame(paned, text="统计概览", padding="10")
        paned.add(frame_stats, weight=2)

        self.lbl_stats_overdue = ttk.Label(frame_stats, text="当前逾期记录: 0")
        self.lbl_stats_overdue.pack(anchor=tk.W)

        ttk.Label(frame_stats, text="热门图书 TOP 5:").pack(anchor=tk.W, pady=(10, 5))
        
        self.tree_hot = ttk.Treeview(frame_stats, columns=("title", "count"), show="headings", height=5)
        self.tree_hot.heading("title", text="书名")
        self.tree_hot.heading("count", text="借阅次数")
        self.tree_hot.column("title", width=200)
        self.tree_hot.column("count", width=80)
        self.tree_hot.pack(fill=tk.X)

        ttk.Button(frame_stats, text="刷新统计", command=self.refresh_stats).pack(pady=10)
        
        # 初始加载统计
        self.refresh_stats()

    def scan_isbn_for_add(self):
        isbn = self.scanner.scan_isbn()
        if isbn:
            self.entry_add_isbn.delete(0, tk.END)
            self.entry_add_isbn.insert(0, isbn)

    def action_add_book(self):
        isbn = self.entry_add_isbn.get()
        title = self.entry_add_title.get()
        author = self.entry_add_author.get()
        category = self.entry_add_category.get()
        copies = self.entry_add_copies.get()

        if not all([isbn, title, author, category, copies]):
            messagebox.showwarning("提示", "请填写所有字段")
            return
        
        try:
            copies = int(copies)
        except ValueError:
            messagebox.showerror("错误", "数量必须是数字")
            return

        success, msg = self.manager.add_book(isbn, title, author, category, copies)
        if success:
            messagebox.showinfo("成功", msg)
            self.refresh_book_list()
            # 清空输入
            self.entry_add_isbn.delete(0, tk.END)
            self.entry_add_title.delete(0, tk.END)
            self.entry_add_author.delete(0, tk.END)
            self.entry_add_category.delete(0, tk.END)
            self.entry_add_copies.delete(0, tk.END)
        else:
            messagebox.showerror("失败", msg)

    def refresh_stats(self):
        if not self.manager:
            return
        stats = self.manager.get_stats()
        
        # 更新逾期数
        self.lbl_stats_overdue.config(text=f"当前逾期记录: {stats['overdue_count']}")
        
        # 更新热门图书
        for i in self.tree_hot.get_children():
            self.tree_hot.delete(i)
        
        for title, count in stats['hot_books']:
            self.tree_hot.insert("", tk.END, values=(title, count))


if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
