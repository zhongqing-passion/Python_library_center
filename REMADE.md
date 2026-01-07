<!--
 * @Author: 
 * @Date: 2026-01-07 23:37:18
 * @Last Modified by: 
 * @Last Modified time: 
-->
# 简易图书管理系统  (GUI & 扫码版)

这是一个基于 Python 开发的现代化图书管理系统。项目从 v1.0 的命令行界面（CLI）全面升级到了 v2.0 的图形用户界面（GUI），并集成了摄像头扫码功能，旨在为学校或小型图书馆提供一个轻量级、易于使用的管理方案。



## 🌟 核心特性

- **现代 GUI 交互**：采用 Tkinter (ttk) 构建，具备美观的卡片式登录界面和响应式操作面板。
- **双角色管理体系**：
  - **管理员**：拥有最高权限，可进行图书入库（支持扫码）、查看系统统计数据、监控逾期情况。
  - **普通用户**：可进行图书查询、借阅和归还操作。
- **智能扫码识别**：集成 OpenCV 技术，支持通过电脑摄像头直接扫描书籍背面的 ISBN 条形码，实现快速入库和借还。
- **数据持久化**：使用 SQLAlchemy ORM 框架配合 SQLite 数据库，确保书籍、用户及借阅记录的安全存储。
- **实时统计**：自动计算热门图书 TOP 5 及系统逾期记录。



## 🛠️ 技术栈

- **语言**：Python 3.x
- **前端界面**：Tkinter (Customized ttk styles)
- **数据库**：SQLite + SQLAlchemy (ORM)
- **扫码技术**：OpenCV + PyZbar
- **日志系统**：Python logging



## 📂 项目结构

```text
c:/project/library_python/
├── gui_main.py      # 程序主入口，负责 GUI 渲染与页面跳转
├── auth.py          # 用户认证模块（登录、注册、权限校验）
├── manager.py       # 业务逻辑层（借还逻辑、库存管理、统计分析）
├── models.py        # 数据库模型定义（User, Book, BorrowRecord）
├── db.py            # 数据库连接与初始化配置
├── scanner.py       # 摄像头条形码扫描核心模块
├── logger_config.py # 系统运行日志配置
└── library.db       # SQLite 数据库文件（存储实际数据）
```



## 🚀 快速启动

1. **环境准备**：
   确保已安装 Python 3.7+，并安装必要的第三方库：

   ```bash
   pip install sqlalchemy opencv-python pyzbar
   ```

2. **运行程序**：
   在项目根目录下执行：

   ```bash
   python main.py
   ```

3. **使用提示**：

   - 首次启动可先点击“注册”创建一个管理员账号。
   - 在“借阅/归还”或“添加图书”界面，点击“扫码”按钮即可调用摄像头识别。



## 📅 版本历史

- **v1.0 (CLI)**：基础增删改查功能，通过控制台交互。
- **v2.0 (GUI)**：
  - 引入 Tkinter 界面。
  - 增加摄像头扫码识别。
  - 重新设计数据库架构，支持更复杂的关联查询。
  - 优化 UI 配色与用户体验。

