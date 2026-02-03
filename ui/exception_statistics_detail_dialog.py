"""
异常情况统计详情对话框 - 四个独立坐标系折线图显示
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QMessageBox, QScrollArea, QWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis, QCategoryAxis, QScatterSeries
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QDateTime
from datetime import datetime, timedelta


class ExceptionDetailDialog(QDialog):
    """异常详情弹窗"""
    
    def __init__(self, parent=None, date_str=None, source_key=None, user_name=None, db_manager=None, user_id=None):
        super().__init__(parent)
        self.date_str = date_str
        self.source_key = source_key
        self.user_name = user_name
        self.user_id = user_id
        self.db_manager = db_manager
        self.init_ui()
        self.load_exception_details()
    
    def init_ui(self):
        self.setWindowTitle(f'异常详情 - {self.date_str}')
        self.setMinimumSize(1000, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(f'{self.user_name} - {self.date_str} 异常详情')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #2c3e50; margin: 10px 0;')
        layout.addWidget(title_label)
        
        # 详情内容区域
        self.content_area = QScrollArea()
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_area.setWidget(self.content_widget)
        self.content_area.setWidgetResizable(True)
        layout.addWidget(self.content_area)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_exception_details(self):
        """加载异常详情 - 只显示真正异常的数据源的详细信息"""
        try:
            if not self.db_manager or not self.user_id:
                self.add_section_title("错误")
                self.add_no_data_label("无法获取数据库连接或用户信息")
                return
            
            # 从异常统计视图获取该用户该日期的数据，确认是否有异常
            view_records = self.db_manager.get_exception_statistics_view_data(
                start_date=self.date_str,
                end_date=self.date_str,
                id_card=self.user_id
            )
            
            # 找到匹配的记录
            target_record = None
            for record in view_records:
                if record[0] == self.user_id and record[14] == self.date_str:
                    target_record = record
                    break
            
            if target_record:
                # 视图字段索引：8=思想是否异常, 9=身体是否异常, 10=精神是否异常, 11=训练是否异常, 12=管理是否异常, 13=其他(异常来源)
                exception_sources = target_record[13] or ''
                
                # 显示所有6个数据源，但只有异常的数据源显示具体数据，正常的显示"无"
                self.load_medical_screening_details('病史筛查' in exception_sources)
                self.load_political_assessment_details('政治考核' in exception_sources)
                self.load_physical_examination_details('体检' in exception_sources)
                self.load_daily_stat_details('每日统计' in exception_sources)
                self.load_town_interview_details('镇街谈话' in exception_sources)
                self.load_leader_interview_details('领导谈话' in exception_sources)
                
                # 如果没有任何异常来源，显示提示信息
                if not exception_sources.strip():
                    self.add_section_title("异常信息")
                    self.add_no_data_label("该日期存在异常记录，但异常来源信息为空")
            else:
                self.add_section_title("无异常记录")
                self.add_no_data_label("该日期未发现异常情况")
                
        except Exception as e:
            self.add_section_title("错误")
            self.add_no_data_label(f"加载详情时出错：{str(e)}")
    
    def add_section_title(self, title):
        """添加章节标题"""
        title_widget = QLabel(title)
        title_widget.setStyleSheet('font-size: 14px; font-weight: bold; color: #2c3e50; margin: 15px 0 5px 0; padding: 5px; background-color: #ecf0f1; border-radius: 3px;')
        self.content_layout.addWidget(title_widget)
    
    def add_no_data_label(self, text="无"):
        """添加无数据标签"""
        no_data_widget = QLabel(text)
        no_data_widget.setStyleSheet('color: #7f8c8d; margin: 5px 0 10px 10px; font-style: italic;')
        self.content_layout.addWidget(no_data_widget)
    
    def add_data_table(self, headers, data):
        """添加数据表格"""
        table = QTableWidget()
        table.setRowCount(len(data))
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # 填充数据
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data) if cell_data else "")
                item.setFlags(item.flags() | Qt.ItemIsEnabled)
                table.setItem(row_idx, col_idx, item)
        
        # 设置表格样式
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                margin: 5px 0 10px 10px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                min-width: 60px;
            }
        """)
        
        # 设置表格属性
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setWordWrap(True)
        
        # 设置水平滚动条策略
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 根据列数和内容调整列宽策略
        total_columns = len(headers)
        
        if total_columns <= 5:
            # 列数较少时，使用拉伸模式填满表格宽度
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            # 列数较多时，使用内容自适应，允许水平滚动
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            
            # 设置最小列宽，确保内容可读
            for i in range(total_columns):
                if i < 5:  # 前5列（日期和基本信息）设置较小的最小宽度
                    table.setColumnWidth(i, max(80, table.columnWidth(i)))
                else:  # 其他列设置较大的最小宽度以显示完整内容
                    table.setColumnWidth(i, max(120, table.columnWidth(i)))
        
        # 设置表格高度
        table.setMaximumHeight(200)
        table.setMinimumHeight(100)
        
        # 根据内容调整行高
        table.resizeRowsToContents()
        
        self.content_layout.addWidget(table)
    
    def load_medical_screening_details(self, show_data=True):
        """加载病史筛查详情"""
        self.add_section_title("病史筛查")
        
        if not show_data:
            self.add_no_data_label()
            return
        
        try:
            record = self.db_manager.get_medical_screening_by_id_card_and_date(self.user_id, self.date_str)
            if record:
                headers = ['筛查日期', '身体', '精神', '筛查情况', '连', '排', '班', '应征地']
                data = [[
                    record[0] if record[0] else '',  # 筛查日期
                    record[1] if record[1] else '',  # 身体
                    record[2] if record[2] else '',  # 精神
                    record[3] if record[3] else '',  # 筛查情况
                    record[4] if record[4] else '',  # 连
                    record[5] if record[5] else '',  # 排
                    record[6] if record[6] else '',  # 班
                    record[7] if record[7] else ''   # 应征地
                ]]
                self.add_data_table(headers, data)
            else:
                self.add_no_data_label()
        except Exception as e:
            self.add_no_data_label(f"加载病史筛查数据时出错：{str(e)}")
    
    def load_political_assessment_details(self, show_data=True):
        """加载政治考核详情"""
        self.add_section_title("政治考核")
        
        if not show_data:
            self.add_no_data_label()
            return
        
        try:
            record = self.db_manager.get_political_assessment_by_id_card_and_date(self.user_id, self.date_str)
            if record:
                headers = ['考核日期', '思想', '精神', '家庭成员信息', '走访调查情况', '政治考核情况', '需重点关注问题', '连', '排', '班', '应征地']
                data = [[
                    record[0] if record[0] else '',   # 考核日期
                    record[1] if record[1] else '',   # 思想
                    record[2] if record[2] else '',   # 精神
                    record[3] if record[3] else '',   # 家庭成员信息
                    record[4] if record[4] else '',   # 走访调查情况
                    record[5] if record[5] else '',   # 政治考核情况
                    record[6] if record[6] else '',   # 需重点关注问题
                    record[7] if record[7] else '',   # 连
                    record[8] if record[8] else '',   # 排
                    record[9] if record[9] else '',   # 班
                    record[10] if record[10] else ''  # 应征地
                ]]
                self.add_data_table(headers, data)
            else:
                self.add_no_data_label()
        except Exception as e:
            self.add_no_data_label(f"加载政治考核数据时出错：{str(e)}")
    
    def load_physical_examination_details(self, show_data=True):
        """加载体检详情"""
        self.add_section_title("体检情况")
        
        if not show_data:
            self.add_no_data_label()
            return
        
        try:
            record = self.db_manager.get_physical_examination_by_id_card_and_date(self.user_id, self.date_str)
            if record:
                headers = ['检查日期', '身体', '跟踪处置意见', '处置意见落实情况', '连', '排', '班', '应征地']
                data = [[
                    record[0] if record[0] else '',  # 检查日期
                    record[1] if record[1] else '',  # 身体
                    record[2] if record[2] else '',  # 跟踪处置意见
                    record[3] if record[3] else '',  # 处置意见落实情况
                    record[4] if record[4] else '',  # 连
                    record[5] if record[5] else '',  # 排
                    record[6] if record[6] else '',  # 班
                    record[7] if record[7] else ''   # 应征地
                ]]
                self.add_data_table(headers, data)
            else:
                self.add_no_data_label()
        except Exception as e:
            self.add_no_data_label(f"加载体检数据时出错：{str(e)}")
    
    def load_daily_stat_details(self, show_data=True):
        """加载每日统计详情"""
        self.add_section_title("每日统计")
        
        if not show_data:
            self.add_no_data_label()
            return
        
        try:
            record = self.db_manager.get_daily_stat_by_id_card_and_date(self.user_id, self.date_str)
            if record:
                headers = ['记录日期', '思想', '身体', '精神', '训练', '管理', '其他', '连', '排', '班', '应征地']
                data = [[
                    record[0] if record[0] else '',   # 记录日期
                    record[1] if record[1] else '',   # 思想
                    record[2] if record[2] else '',   # 身体
                    record[3] if record[3] else '',   # 精神
                    record[4] if record[4] else '',   # 训练
                    record[5] if record[5] else '',   # 管理
                    record[6] if record[6] else '',   # 其他
                    record[7] if record[7] else '',   # 连
                    record[8] if record[8] else '',   # 排
                    record[9] if record[9] else '',   # 班
                    record[10] if record[10] else ''  # 应征地
                ]]
                self.add_data_table(headers, data)
            else:
                self.add_no_data_label()
        except Exception as e:
            self.add_no_data_label(f"加载每日统计数据时出错：{str(e)}")
    
    def load_town_interview_details(self, show_data=True):
        """加载镇街谈心谈话详情"""
        self.add_section_title("镇街谈心谈话")
        
        if not show_data:
            self.add_no_data_label()
            return
        
        try:
            record = self.db_manager.get_town_interview_by_id_card_and_date(self.user_id, self.date_str)
            if record:
                headers = ['谈话日期', '思想', '精神', '连', '排', '班', '应征地']
                data = [[
                    record[0] if record[0] else '',  # 谈话日期
                    record[1] if record[1] else '',  # 思想
                    record[2] if record[2] else '',  # 精神
                    record[3] if record[3] else '',  # 连
                    record[4] if record[4] else '',  # 排
                    record[5] if record[5] else '',  # 班
                    record[6] if record[6] else ''   # 应征地
                ]]
                self.add_data_table(headers, data)
            else:
                self.add_no_data_label()
        except Exception as e:
            self.add_no_data_label(f"加载镇街谈话数据时出错：{str(e)}")
    
    def load_leader_interview_details(self, show_data=True):
        """加载领导谈心谈话详情"""
        self.add_section_title("领导谈心谈话")
        
        if not show_data:
            self.add_no_data_label()
            return
        
        try:
            record = self.db_manager.get_leader_interview_by_id_card_and_date(self.user_id, self.date_str)
            if record:
                headers = ['谈话日期', '思想', '精神', '连', '排', '班', '应征地']
                data = [[
                    record[0] if record[0] else '',  # 谈话日期
                    record[1] if record[1] else '',  # 思想
                    record[2] if record[2] else '',  # 精神
                    record[3] if record[3] else '',  # 连
                    record[4] if record[4] else '',  # 排
                    record[5] if record[5] else '',  # 班
                    record[6] if record[6] else ''   # 应征地
                ]]
                self.add_data_table(headers, data)
            else:
                self.add_no_data_label()
        except Exception as e:
            self.add_no_data_label(f"加载领导谈话数据时出错：{str(e)}")


class CustomChartView(QChartView):
    """自定义图表视图，支持更好的鼠标悬停"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dates = []
        self.source_key = ""
        self.dialog = None
        self.setMouseTracking(True)
    
    def set_hover_data(self, dates, source_key, dialog):
        """设置悬停数据"""
        self.dates = dates
        self.source_key = source_key
        self.dialog = dialog
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，实现容差范围的悬停"""
        super().mouseMoveEvent(event)
        
        if not self.dates or not self.dialog:
            return
        
        try:
            # 获取鼠标在图表中的位置
            chart_pos = self.chart().mapToValue(QPointF(event.position()))
            x_coord = chart_pos.x()
            
            # 使用四舍五入找到最近的日期索引
            x_index = round(x_coord)
            
            # 确保索引在有效范围内
            if 0 <= x_index < len(self.dates):
                date_str = self.dates[x_index]
                
                # 获取该日期的异常状态
                exception_value = self.dialog.get_exception_value_for_date(date_str, self.source_key)
                exception_status = "异常" if exception_value == 1 else "正常"
                
                tooltip_text = f"{date_str} - {exception_status}"
                
                # 显示工具提示
                from PyQt5.QtWidgets import QToolTip
                QToolTip.showText(event.globalPosition().toPoint(), tooltip_text)
            else:
                # 如果超出范围，隐藏提示
                from PyQt5.QtWidgets import QToolTip
                QToolTip.hideText()
                
        except Exception as e:
            print(f"鼠标移动事件处理出错: {e}")
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        from PyQt5.QtWidgets import QToolTip
        QToolTip.hideText()


class ExceptionStatisticsDetailDialog(QDialog):
    def __init__(self, db_manager, parent=None, user_id=None, name=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.name = name
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle(f'异常情况统计-{self.name}')
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        self.setModal(True)
        
        # 允许窗口调整大小，只显示最大化和关闭按钮
        self.setWindowFlags(Qt.Dialog | 
                           Qt.WindowMaximizeButtonHint | 
                           Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部信息和时间筛选器
        top_layout = QHBoxLayout()
        
        # 用户信息
        info_label = QLabel(f'用户：{self.name} ({self.user_id})')
        info_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #2c3e50;')
        top_layout.addWidget(info_label)
        
        top_layout.addStretch()
        
        # 日期筛选器
        # 日期筛选区域
        date_filter_layout = QHBoxLayout()
        
        # 日期筛选标签
        date_filter_layout.addWidget(QLabel('日期筛选: 从:'))
        
        # 开始日期选择器
        from PyQt5.QtWidgets import QDateEdit
        from PyQt5.QtCore import QDate
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))  # 默认30天前
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                min-width: 120px;
                color: #2c3e50;
            }
            QDateEdit:hover {
                border-color: #3498db;
            }
        """)
        date_filter_layout.addWidget(self.start_date)
        
        date_filter_layout.addWidget(QLabel('到:'))
        
        # 结束日期选择器
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())  # 默认今天
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                min-width: 120px;
                color: #2c3e50;
            }
            QDateEdit:hover {
                border-color: #3498db;
            }
        """)
        date_filter_layout.addWidget(self.end_date)
        
        # 筛选按钮
        filter_btn = QPushButton('筛选')
        filter_btn.clicked.connect(self.filter_by_date_range)
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        date_filter_layout.addWidget(filter_btn)
        
        top_layout.addLayout(date_filter_layout)
        
        # 时间范围选择
        top_layout.addWidget(QLabel('时间范围:'))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(['七天内', '半个月内', '一个月内', '无'])
        self.time_range_combo.setCurrentText('七天内')  # 默认选择七天内
        self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
        self.time_range_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                min-width: 100px;
                color: #2c3e50;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bdc3c7;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border: none;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        top_layout.addWidget(self.time_range_combo)
        
        layout.addLayout(top_layout)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # 创建七个图表视图（总异常情况在最上面，然后是六个数据源）
        self.chart_views = {}
        chart_configs = [
            {'key': 'total_exception', 'name': '总异常情况', 'color': QColor(230, 126, 34)},      # 橙色 - 移到最上面
            {'key': 'medical_screening', 'name': '病史筛查异常情况', 'color': QColor(231, 76, 60)},   # 红色
            {'key': 'political_assessment', 'name': '政治考核异常', 'color': QColor(142, 68, 173)},   # 紫色
            {'key': 'physical_examination', 'name': '体检异常', 'color': QColor(39, 174, 96)},       # 绿色
            {'key': 'daily_stat', 'name': '每日统计异常', 'color': QColor(52, 152, 219)},           # 蓝色
            {'key': 'town_interview', 'name': '镇街谈话异常', 'color': QColor(241, 196, 15)},        # 黄色
            {'key': 'leader_interview', 'name': '领导谈话异常', 'color': QColor(155, 89, 182)}       # 浅紫色
        ]
        
        for config in chart_configs:
            # 创建标题标签
            title_label = QLabel(f"{config['name']}异常情况趋势")
            title_label.setStyleSheet('font-size: 14px; font-weight: bold; color: #2c3e50; margin: 10px 0;')
            scroll_layout.addWidget(title_label)
            
            # 创建图表视图
            chart_view = CustomChartView()
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            chart_view.setFixedHeight(250)  # 固定每个图表的高度
            self.chart_views[config['key']] = {
                'view': chart_view,
                'name': config['name'],
                'color': config['color']
            }
            scroll_layout.addWidget(chart_view)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        # 最大化/还原按钮
        self.maximize_btn = QPushButton('最大化')
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        button_layout.addWidget(self.maximize_btn)
        
        close_btn = QPushButton('关闭')
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_x_axis_labels(self, axis_x, dates):
        """设置X轴标签 - 智能间隔显示"""
        # 智能添加日期标签 - 根据日期数量决定显示间隔
        total_dates = len(dates)
        
        if total_dates <= 7:
            # 7天以内，显示所有日期
            step = 1
        elif total_dates <= 15:
            # 15天以内，每2天显示一个
            step = 2
        elif total_dates <= 30:
            # 30天以内，每4天显示一个
            step = 4
        elif total_dates <= 60:
            # 60天以内，每7天显示一个
            step = 7
        elif total_dates <= 120:
            # 120天以内，每15天显示一个
            step = 15
        else:
            # 超过120天，每30天显示一个
            step = 30
        
        # 只添加需要显示的日期标签
        for i, date_str in enumerate(dates):
            if i % step == 0 or i == len(dates) - 1:  # 显示间隔点和最后一个点
                # 只显示月-日部分
                date_label = date_str[5:]  # 去掉年份部分，只保留MM-dd
                axis_x.append(date_label, i)
        
        # 设置X轴范围以包含所有数据点
        if dates:
            axis_x.setRange(-0.5, len(dates) - 0.5)
    
    def get_exception_value_for_date(self, date_str, source_key):
        """获取指定日期和数据源的异常值"""
        try:
            if hasattr(self, 'current_daily_exception_status'):
                if source_key == 'total_exception':
                    # 总异常情况
                    return self.current_daily_exception_status.get(date_str, {}).get('total', 0)
                else:
                    # 单个数据源的异常状态
                    return self.current_daily_exception_status.get(date_str, {}).get(source_key, 0)
            return 0
        except Exception as e:
            print(f"获取异常值时出错: {e}")
            return 0
    
    def on_exception_point_clicked(self, point, source_key, dates):
        """处理异常点点击事件"""
        try:
            # 获取点击的点的X坐标（索引）
            x_index = int(point.x())
            
            if 0 <= x_index < len(dates):
                date_str = dates[x_index]
                
                # 弹出异常详情对话框
                detail_dialog = ExceptionDetailDialog(
                    parent=self,
                    date_str=date_str,
                    source_key=source_key,
                    user_name=self.name,
                    user_id=self.user_id,  # 添加user_id参数
                    db_manager=self.db_manager
                )
                detail_dialog.exec_()
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"显示异常详情时出错：{str(e)}")
    
    def toggle_maximize(self):
        """切换最大化/还原状态"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText('最大化')
        else:
            self.showMaximized()
            self.maximize_btn.setText('还原')
    
    def filter_by_date_range(self):
        """根据日期范围筛选数据"""
        try:
            # 将下拉框选项设置为"无"
            # 临时断开信号连接，避免触发下拉框变化事件
            self.time_range_combo.currentTextChanged.disconnect()
            self.time_range_combo.setCurrentText('无')
            # 重新连接信号
            self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
            
            # 获取日期范围
            start_date = self.start_date.date().toString('yyyy-MM-dd')
            end_date = self.end_date.date().toString('yyyy-MM-dd')
            
            # 验证日期范围
            if start_date > end_date:
                QMessageBox.warning(self, "日期错误", "开始日期不能晚于结束日期")
                return
            
            # 使用日期范围加载数据
            self.load_data_by_date_range(start_date, end_date)
            
        except Exception as e:
            QMessageBox.warning(self, "筛选错误", f"按日期范围筛选数据时发生错误：{str(e)}")
            # 确保信号重新连接
            try:
                self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
            except:
                pass

    def on_time_range_changed(self, selected_range):
        """时间范围变化处理"""
        try:
            # 如果选择的不是"无"，则清空日期筛选器
            if selected_range != '无':
                from PyQt5.QtCore import QDate
                # 重置日期选择器为默认值
                self.start_date.setDate(QDate.currentDate().addDays(-30))
                self.end_date.setDate(QDate.currentDate())
            
            # 如果选择"无"，不进行任何筛选操作，保持当前显示
            if selected_range == '无':
                return
            
            # 使用预设时间范围加载数据
            self.load_data()
            
        except Exception as e:
            QMessageBox.warning(self, "时间范围切换错误", f"切换时间范围时发生错误：{str(e)}")

    def load_data_by_date_range(self, start_date, end_date):
        """根据日期范围加载数据并绘制折线图"""
        try:
            # 从异常统计视图获取该用户在指定日期范围内的数据
            view_records = self.db_manager.get_exception_statistics_view_data(
                start_date=start_date,
                end_date=end_date,
                id_card=self.user_id
            )
            
            self.create_charts_from_view_data(view_records, start_date, end_date)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载异常统计详情时发生错误：{str(e)}")

    def load_data(self):
        """加载数据并绘制四个独立的折线图"""
        try:
            # 获取当前选择的时间范围
            selected_range = self.time_range_combo.currentText()
            
            # 计算日期范围
            from datetime import datetime, timedelta
            if selected_range == '七天内':
                days = 7
            elif selected_range == '半个月内':
                days = 15
            elif selected_range == '一个月内':
                days = 30
            else:
                days = 7
            
            start_date = (datetime.now() - timedelta(days=days-1)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 从异常统计视图获取该用户的数据
            view_records = self.db_manager.get_exception_statistics_view_data(
                start_date=start_date,
                end_date=end_date,
                id_card=self.user_id
            )
            
            self.create_charts_from_view_data(view_records, start_date, end_date, selected_range)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载异常统计详情时发生错误：{str(e)}")
    
    def create_charts_from_view_data(self, view_records, start_date, end_date, time_range=None):
        """基于视图数据创建图表"""
        try:
            from datetime import datetime, timedelta
            
            # 解析开始和结束日期
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 生成完整的日期列表
            dates = []
            current_date = start_datetime
            while current_date <= end_datetime:
                date_str = current_date.strftime('%Y-%m-%d')
                dates.append(date_str)
                current_date += timedelta(days=1)
            
            # 将视图记录按日期组织
            records_by_date = {}
            for record in view_records:
                record_date = record[14]  # 日期字段
                records_by_date[record_date] = record
            
            # 计算每天各类异常状态
            daily_exception_status = {}
            for date_str in dates:
                if date_str in records_by_date:
                    record = records_by_date[date_str]
                    # 视图字段索引：8=思想是否异常, 9=身体是否异常, 10=精神是否异常, 11=训练是否异常, 12=管理是否异常, 13=其他(异常来源)
                    exception_sources = record[13] or ''
                    
                    # 根据异常来源字段判断各个数据源是否异常
                    daily_exception_status[date_str] = {
                        'medical_screening': 1 if ('病史筛查' in exception_sources) else 0,
                        'political_assessment': 1 if ('政治考核' in exception_sources) else 0,
                        'physical_examination': 1 if ('体检' in exception_sources) else 0,
                        'daily_stat': 1 if ('每日统计' in exception_sources) else 0,
                        'town_interview': 1 if ('镇街谈话' in exception_sources) else 0,
                        'leader_interview': 1 if ('领导谈话' in exception_sources) else 0,
                        'total': 1  # 如果有记录就说明有异常
                    }
                else:
                    # 该日期没有异常记录，所有状态都是正常
                    daily_exception_status[date_str] = {
                        'medical_screening': 0,
                        'political_assessment': 0,
                        'physical_examination': 0,
                        'daily_stat': 0,
                        'town_interview': 0,
                        'leader_interview': 0,
                        'total': 0
                    }
            
            # 保存异常状态供悬停使用
            self.current_daily_exception_status = daily_exception_status
            # 保存视图记录供详情弹窗使用
            self.current_view_records = records_by_date
            
            # 为每个数据源创建独立的图表
            for source_key, chart_info in self.chart_views.items():
                chart = QChart()
                
                # 设置图表标题
                if time_range:
                    chart.setTitle(f"{chart_info['name']}异常情况趋势 ({time_range})")
                else:
                    chart.setTitle(f"{chart_info['name']}异常情况趋势 ({start_date} 至 {end_date})")
                
                chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
                
                # 创建折线系列
                series = QLineSeries()
                series.setName(chart_info['name'])
                
                # 设置线条颜色和样式
                pen = QPen(chart_info['color'])
                pen.setWidth(3)
                series.setPen(pen)
                
                # 创建散点系列用于显示异常点
                scatter_series = QScatterSeries()
                scatter_series.setName(f"{chart_info['name']}_异常点")
                scatter_series.setMarkerSize(12)
                scatter_series.setColor(chart_info['color'])
                scatter_series.setBorderColor(QColor(255, 255, 255))
                
                # 为每个日期添加数据点
                for i, date_str in enumerate(dates):
                    if source_key == 'total_exception':
                        exception_value = daily_exception_status[date_str]['total']
                    else:
                        exception_value = daily_exception_status[date_str].get(source_key, 0)
                    
                    # 添加到折线系列
                    series.append(i, exception_value)
                    
                    # 如果是异常日期，添加到散点系列
                    if exception_value == 1:
                        scatter_series.append(i, exception_value)
                
                chart.addSeries(series)
                chart.addSeries(scatter_series)
                
                # 为散点系列添加点击事件
                scatter_series.clicked.connect(lambda point, sk=source_key, d=dates: 
                                             self.on_exception_point_clicked(point, sk, d))
                
                # 设置X轴
                axis_x = QCategoryAxis()
                axis_x.setTitleText("日期")
                self.setup_x_axis_labels(axis_x, dates)
                chart.addAxis(axis_x, Qt.AlignBottom)
                
                # 设置Y轴
                axis_y = QCategoryAxis()
                axis_y.setRange(-0.1, 1.1)
                axis_y.append("正常", 0)
                axis_y.append("异常", 1)
                axis_y.setTitleText("异常状态")
                axis_y.setLabelsPosition(QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
                chart.addAxis(axis_y, Qt.AlignLeft)
                
                # 将系列绑定到坐标轴
                series.attachAxis(axis_x)
                series.attachAxis(axis_y)
                scatter_series.attachAxis(axis_x)
                scatter_series.attachAxis(axis_y)
                
                # 设置图表样式
                chart.setBackgroundBrush(QColor(248, 249, 250))
                chart.legend().setAlignment(Qt.AlignTop)
                
                # 检查是否有数据
                has_data = len(view_records) > 0
                if not has_data:
                    if time_range:
                        chart.setTitle(f"{chart_info['name']}异常情况趋势 ({time_range}) - 暂无数据")
                    else:
                        chart.setTitle(f"{chart_info['name']}异常情况趋势 ({start_date} 至 {end_date}) - 暂无数据")
                
                # 设置图表到视图
                chart_info['view'].setChart(chart)
                
                # 设置悬停数据
                chart_info['view'].set_hover_data(dates, source_key, self)
            
        except Exception as e:
            QMessageBox.warning(self, "图表错误", f"创建折线图时发生错误：{str(e)}")
    
    def refresh_data(self):
        """刷新数据并重置时间筛选器"""
        try:
            # 重置日期筛选器为默认值
            from PyQt5.QtCore import QDate
            self.start_date.setDate(QDate.currentDate().addDays(-30))
            self.end_date.setDate(QDate.currentDate())
            
            # 重置时间范围下拉框为默认值
            # 临时断开信号连接，避免触发下拉框变化事件
            self.time_range_combo.currentTextChanged.disconnect()
            self.time_range_combo.setCurrentText('七天内')
            # 重新连接信号
            self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
            
            # 重新加载数据
            self.load_data()
            
        except Exception as e:
            QMessageBox.warning(self, "刷新错误", f"刷新数据时发生错误：{str(e)}")
            # 确保信号重新连接
            try:
                self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
            except:
                pass