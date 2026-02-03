"""
系统配置文件
"""

# 数据库配置
DATABASE_PATH = 'youth_records.db'

# 默认管理员账户
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin123'

# 文件上传配置
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}

# 导出配置
EXPORT_FOLDER = 'exports'

# 每日统计配置
DAILY_CHART_DAYS = 30  # 显示最近30天的数据

# 评分映射
MOOD_SCORES = {
    '良好': 4,
    '一般': 3,
    '较差': 2,
    '异常': 1
}

PHYSICAL_SCORES = {
    '健康': 4,
    '轻微不适': 3,
    '不适': 2,
    '需关注': 1
}

TRAINING_SCORES = {
    '优秀': 4,
    '良好': 3,
    '正常': 2,
    '需改进': 1
}

# 界面配置
WINDOW_TITLE = '一人一策记录本'
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'system.log'
