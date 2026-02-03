"""
登录界面
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QKeyEvent


class LoginWindow(QWidget):
    login_success = pyqtSignal(object)
    
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('一人一策记录本 - 登录')
        self.setFixedSize(480, 340)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # 标题
        title = QLabel('一人一策记录本')
        title.setFont(QFont('Microsoft YaHei', 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(False)  # 禁止自动换行
        title.setMinimumWidth(400)  # 设置最小宽度
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
        # 用户名
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入账号')
        self.username_input.setFont(QFont('Microsoft YaHei', 11))
        self.username_input.setFixedHeight(35)
        # 安装事件过滤器以处理键盘事件
        self.username_input.installEventFilter(self)
        layout.addWidget(self.username_input)
        
        # 密码
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setFont(QFont('Microsoft YaHei', 11))
        self.password_input.setFixedHeight(35)
        # 安装事件过滤器以处理键盘事件
        self.password_input.installEventFilter(self)
        layout.addWidget(self.password_input)
        
        # 登录按钮
        self.login_btn = QPushButton('登录')
        self.login_btn.setFont(QFont('Microsoft YaHei', 12))
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        # 提示信息
        hint = QLabel('默认账户: admin / admin123\n提示: 按Enter键切换输入框，在密码框按Enter登录')
        hint.setStyleSheet('color: gray; font-size: 10px;')
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        
        self.setLayout(layout)
        
        # 设置Tab顺序
        self.setTabOrder(self.username_input, self.password_input)
        self.setTabOrder(self.password_input, self.login_btn)
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理键盘事件"""
        if event.type() == QKeyEvent.Type.KeyPress:
            key = event.key()
            
            # 在用户名输入框
            if obj == self.username_input:
                if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                    # Enter键：跳转到密码框
                    self.password_input.setFocus()
                    return True
                elif key == Qt.Key.Key_Down:
                    # 下方向键：跳转到密码框
                    self.password_input.setFocus()
                    return True
            
            # 在密码输入框
            elif obj == self.password_input:
                if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                    # Enter键：执行登录
                    self.handle_login()
                    return True
                elif key == Qt.Key.Key_Up:
                    # 上方向键：跳转到用户名框
                    self.username_input.setFocus()
                    return True
                elif key == Qt.Key.Key_Down:
                    # 下方向键：跳转到登录按钮
                    self.login_btn.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, '提示', '请输入账户和密码')
            return
        
        if self.auth_service.login(username, password):
            user = self.auth_service.get_current_user()
            self.login_success.emit(user)
            self.close()
        else:
            QMessageBox.warning(self, '登录失败', '账户或密码错误')
            self.password_input.clear()
