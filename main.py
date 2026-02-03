"""
一人一策记录本 - 主程序入口
"""
import sys
from PyQt5.QtWidgets import QApplication
from database.db_manager import DatabaseManager
from services.auth_service import AuthService
from services.import_service import ImportService
from services.export_service import ExportService
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        
        # 初始化服务
        self.db_manager = DatabaseManager()
        self.auth_service = AuthService(self.db_manager)
        self.import_service = ImportService(self.db_manager)
        self.export_service = ExportService(self.db_manager)
        
        self.login_window = None
        self.main_window = None
    
    def run(self):
        """运行应用"""
        self.show_login()
        sys.exit(self.app.exec_())
    
    def show_login(self):
        """显示登录窗口"""
        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, user):
        """登录成功回调"""
        self.main_window = MainWindow(
            self.db_manager,
            self.import_service,
            self.export_service,
            user
        )
        self.main_window.show()


if __name__ == '__main__':
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
