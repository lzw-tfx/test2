"""
认证服务
"""

class AuthService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_user = None
    
    def login(self, username, password):
        """登录"""
        user = self.db_manager.authenticate_user(username, password)
        if user:
            self.current_user = user
            return True
        return False
    
    def logout(self):
        """登出"""
        self.current_user = None
    
    def is_authenticated(self):
        """检查是否已认证"""
        return self.current_user is not None
    
    def get_current_user(self):
        """获取当前用户"""
        return self.current_user
