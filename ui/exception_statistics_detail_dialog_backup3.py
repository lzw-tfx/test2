"""
异常情况统计详情对话框 - 四个独立坐标系折线图显示
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QMessageBox, QScrollArea, QWidget)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis, QCategoryAxis
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QDateTime
from datetime import datetime, timedelta


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
        self.setMinimumSize(800, 600)  # 设置最小尺寸
        self.resize(1200, 800)  # 设置初始尺寸，但允许调整
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
        else:
            # 超过30天，每7天显示一个
            step = 7
        
        # 添加日期标签，但只显示部分
        for i, date_str in enumerate(dates):
            if i % step == 0 or i == len(dates) - 1:  # 显示间隔点和最后一个点
                # 只显示月-日部分
                date_label = date_str[5:]  # 去掉年份部分，只保留MM-dd
                axis_x.append(date_label, i)
            else:
                # 不显示标签，但保留位置
                axis_x.append("", i)
    
    def get_exception_value_for_date(self, date_str, source_key):
        """获取指定日期和数据源的异常值"""
        try:
            if hasattr(self, 'current_data_sources') and hasattr(self, 'current_daily_exception_status'):
                if source_key == 'total_exception':
                    # 总异常情况：只要任何一个数据源异常，就为1
                    return 1 if any(self.current_daily_exception_status.get(date_str, {}).values()) else 0
                else:
                    # 单个数据源的异常状态
                    return self.calculate_exception_for_date(
                        self.current_data_sources.get(source_key, []), date_str, source_key
                    )
            return 0
        except Exception as e:
            print(f"获取异常值时出错: {e}")
            return 0
    
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
            # 获取各个数据源在指定日期范围内的原始数据
            data_sources = self.db_manager.get_user_data_sources_by_date_range(
                self.user_id, start_date, end_date
            )
            
            self.create_individual_charts_by_date_range(data_sources, start_date, end_date)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载异常统计详情时发生错误：{str(e)}")

    def load_data(self):
        """加载数据并绘制四个独立的折线图"""
        try:
            # 获取当前选择的时间范围
            selected_range = self.time_range_combo.currentText()
            
            # 获取各个数据源的原始数据
            data_sources = self.db_manager.get_user_data_sources_by_time_range(
                self.user_id, selected_range
            )
            
            self.create_individual_charts(data_sources, selected_range)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载异常统计详情时发生错误：{str(e)}")
    
    def create_individual_charts(self, data_sources, time_range):
        """为每个数据源创建独立的折线图"""
        try:
            from datetime import datetime, timedelta
            
            # 保存当前数据源供悬停使用
            self.current_data_sources = data_sources
            
            # 计算日期范围
            if time_range == '七天内':
                days = 7
            elif time_range == '半个月内':
                days = 15
            elif time_range == '一个月内':
                days = 30
            else:
                days = 7
            
            # 生成日期列表
            dates = []
            for i in range(days):
                date = datetime.now() - timedelta(days=days-1-i)
                date_str = date.strftime('%Y-%m-%d')
                dates.append(date_str)
            
            # 收集所有数据源中实际存在的日期
            all_actual_dates = set()
            for source_key, source_data in data_sources.items():
                for record in source_data:
                    if record and len(record) > 0:
                        actual_date = record[0]  # 第一个字段是日期
                        if actual_date:
                            all_actual_dates.add(actual_date)
            
            # 合并生成的日期和实际存在的日期，确保所有相关日期都被包含
            all_dates = set(dates) | all_actual_dates
            
            # 过滤出在时间范围内的日期并排序
            start_date = (datetime.now() - timedelta(days=days-1)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            filtered_dates = []
            for date_str in sorted(all_dates):
                if start_date <= date_str <= end_date:
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                        filtered_dates.append(date_str)
                    except ValueError:
                        continue
            
            # 使用过滤后的日期
            dates = filtered_dates
            
            # 先计算每天各数据源的异常状态，用于总异常情况计算
            daily_exception_status = {}
            for date_str in dates:
                daily_exception_status[date_str] = {
                    'medical_screening': self.calculate_exception_for_date(data_sources['medical_screening'], date_str, 'medical_screening'),
                    'political_assessment': self.calculate_exception_for_date(data_sources['political_assessment'], date_str, 'political_assessment'),
                    'physical_examination': self.calculate_exception_for_date(data_sources['physical_examination'], date_str, 'physical_examination'),
                    'daily_stat': self.calculate_exception_for_date(data_sources['daily_stat'], date_str, 'daily_stat'),
                    'town_interview': self.calculate_exception_for_date(data_sources['town_interview'], date_str, 'town_interview'),
                    'leader_interview': self.calculate_exception_for_date(data_sources['leader_interview'], date_str, 'leader_interview')
                }
            
            # 保存异常状态供悬停使用
            self.current_daily_exception_status = daily_exception_status
            
            # 为每个数据源创建独立的图表
            for source_key, chart_info in self.chart_views.items():
                chart = QChart()
                chart.setTitle(f"{chart_info['name']}异常情况趋势 ({time_range})")
                chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
                
                # 创建折线系列
                series = QLineSeries()
                series.setName(chart_info['name'])
                
                # 设置线条颜色和样式
                pen = QPen(chart_info['color'])
                pen.setWidth(3)
                series.setPen(pen)
                
                # 为每个日期计算异常状态并添加数据点
                for i, date_str in enumerate(dates):
                    if source_key == 'total_exception':
                        # 总异常情况：只要任何一个数据源异常，就为1
                        exception_value = 1 if any(daily_exception_status[date_str].values()) else 0
                    else:
                        # 单个数据源的异常状态
                        exception_value = self.calculate_exception_for_date(
                            data_sources[source_key], date_str, source_key
                        )
                    
                    # 使用索引作为X轴值，确保精确对齐
                    series.append(i, exception_value)
                
                chart.addSeries(series)
                
                # 设置X轴 - 使用分类轴显示日期
                axis_x = QCategoryAxis()
                axis_x.setTitleText("日期")
                
                # 添加日期标签
                for i, date_str in enumerate(dates):
                    # 只显示月-日部分
                    date_label = date_str[5:]  # 去掉年份部分，只保留MM-dd
                    axis_x.append(date_label, i)
                
                chart.addAxis(axis_x, Qt.AlignBottom)
                
                # 设置Y轴 - 异常状态 (0=正常, 1=异常)
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
                
                # 设置图表样式
                chart.setBackgroundBrush(QColor(248, 249, 250))
                chart.legend().setAlignment(Qt.AlignTop)
                
                # 检查是否有数据
                if source_key == 'total_exception':
                    # 总异常情况：检查是否有任何数据源有数据
                    has_data = any(len(data_sources[key]) > 0 for key in ['medical_screening', 'political_assessment', 'physical_examination', 'daily_stat', 'town_interview', 'leader_interview'])
                else:
                    # 单个数据源：检查该数据源是否有数据
                    has_data = len(data_sources[source_key]) > 0
                
                if not has_data:
                    chart.setTitle(f"{chart_info['name']}异常情况趋势 ({time_range}) - 暂无数据")
                
                # 设置图表到视图
                chart_info['view'].setChart(chart)
                
                # 设置悬停数据
                chart_info['view'].set_hover_data(dates, source_key, self)
            
        except Exception as e:
            QMessageBox.warning(self, "图表错误", f"创建折线图时发生错误：{str(e)}")
    
    def create_individual_charts_by_date_range(self, data_sources, start_date, end_date):
        """根据日期范围为每个数据源创建独立的折线图"""
        try:
            from datetime import datetime, timedelta
            
            # 保存当前数据源供悬停使用
            self.current_data_sources = data_sources
            
            # 解析开始和结束日期
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 生成完整的日期列表（基于日期范围）
            base_dates = []
            current_date = start_datetime
            while current_date <= end_datetime:
                date_str = current_date.strftime('%Y-%m-%d')
                base_dates.append(date_str)
                current_date += timedelta(days=1)
            
            # 收集所有数据源中实际存在的日期
            all_actual_dates = set()
            for source_key, source_data in data_sources.items():
                for record in source_data:
                    if record and len(record) > 0:
                        actual_date = record[0]  # 第一个字段是日期
                        if actual_date and start_date <= actual_date <= end_date:
                            all_actual_dates.add(actual_date)
            
            # 合并基础日期和实际存在的日期
            all_dates = set(base_dates) | all_actual_dates
            
            # 过滤并排序日期
            filtered_dates = []
            for date_str in sorted(all_dates):
                if start_date <= date_str <= end_date:
                    try:
                        datetime.strptime(date_str, '%Y-%m-%d')
                        filtered_dates.append(date_str)
                    except ValueError:
                        continue
            
            # 使用过滤后的日期
            dates = filtered_dates
            
            # 先计算每天各数据源的异常状态，用于总异常情况计算
            daily_exception_status = {}
            for date_str in dates:
                daily_exception_status[date_str] = {
                    'medical_screening': self.calculate_exception_for_date(data_sources['medical_screening'], date_str, 'medical_screening'),
                    'political_assessment': self.calculate_exception_for_date(data_sources['political_assessment'], date_str, 'political_assessment'),
                    'physical_examination': self.calculate_exception_for_date(data_sources['physical_examination'], date_str, 'physical_examination'),
                    'daily_stat': self.calculate_exception_for_date(data_sources['daily_stat'], date_str, 'daily_stat'),
                    'town_interview': self.calculate_exception_for_date(data_sources['town_interview'], date_str, 'town_interview'),
                    'leader_interview': self.calculate_exception_for_date(data_sources['leader_interview'], date_str, 'leader_interview')
                }
            
            # 保存异常状态供悬停使用
            self.current_daily_exception_status = daily_exception_status
            
            # 为每个数据源创建独立的图表
            for source_key, chart_info in self.chart_views.items():
                chart = QChart()
                chart.setTitle(f"{chart_info['name']}异常情况趋势 ({start_date} 至 {end_date})")
                chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
                
                # 创建折线系列
                series = QLineSeries()
                series.setName(chart_info['name'])
                
                # 设置线条颜色和样式
                pen = QPen(chart_info['color'])
                pen.setWidth(3)
                series.setPen(pen)
                
                # 为每个日期计算异常状态并添加数据点
                for i, date_str in enumerate(dates):
                    if source_key == 'total_exception':
                        # 总异常情况：只要任何一个数据源异常，就为1
                        exception_value = 1 if any(daily_exception_status[date_str].values()) else 0
                    else:
                        # 单个数据源的异常状态
                        exception_value = self.calculate_exception_for_date(
                            data_sources[source_key], date_str, source_key
                        )
                    
                    # 使用索引作为X轴值，确保精确对齐
                    series.append(i, exception_value)
                
                chart.addSeries(series)
                
                # 设置X轴 - 使用分类轴显示日期
                axis_x = QCategoryAxis()
                axis_x.setTitleText("日期")
                
                # 添加日期标签
                for i, date_str in enumerate(dates):
                    # 只显示月-日部分
                    date_label = date_str[5:]  # 去掉年份部分，只保留MM-dd
                    axis_x.append(date_label, i)
                
                chart.addAxis(axis_x, Qt.AlignBottom)
                
                # 设置Y轴 - 异常状态 (0=正常, 1=异常)
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
                
                # 设置图表样式
                chart.setBackgroundBrush(QColor(248, 249, 250))
                chart.legend().setAlignment(Qt.AlignTop)
                
                # 检查是否有数据
                if source_key == 'total_exception':
                    # 总异常情况：检查是否有任何数据源有数据
                    has_data = any(len(data_sources[key]) > 0 for key in ['medical_screening', 'political_assessment', 'physical_examination', 'daily_stat', 'town_interview', 'leader_interview'])
                else:
                    # 单个数据源：检查该数据源是否有数据
                    has_data = len(data_sources[source_key]) > 0
                
                if not has_data:
                    chart.setTitle(f"{chart_info['name']}异常情况趋势 ({start_date} 至 {end_date}) - 暂无数据")
                
                # 设置图表到视图
                chart_info['view'].setChart(chart)
                
                # 设置悬停数据
                chart_info['view'].set_hover_data(dates, source_key, self)
            
        except Exception as e:
            QMessageBox.warning(self, "图表错误", f"创建折线图时发生错误：{str(e)}")
    
    def calculate_exception_for_date(self, source_data, target_date, source_type):
        """计算指定日期的异常状态"""
        try:
            # 查找该日期的数据
            for record in source_data:
                record_date = record[0]  # 第一个字段是日期
                
                if record_date == target_date:
                    if source_type == 'medical_screening':
                        # 病史筛查：physical_status, mental_status
                        physical_status = record[1]
                        mental_status = record[2]
                        return 1 if (physical_status == '异常' or mental_status == '异常') else 0
                    
                    elif source_type == 'political_assessment':
                        # 政治考核：thoughts, spirit
                        thoughts = record[1]
                        spirit = record[2]
                        
                        # 检查是否有异常关键词
                        exception_keywords = ['异常', '问题', '消极', '抵触', '不良', '困难', '担心', '焦虑', '抑郁', '差']
                        for field in [thoughts, spirit]:
                            if field and any(keyword in str(field) for keyword in exception_keywords):
                                return 1
                        return 0
                    
                    elif source_type == 'physical_examination':
                        # 体检：body_status
                        body_status = record[1]
                        return 1 if (body_status == '异常' or body_status == '不合格') else 0
                    
                    elif source_type == 'daily_stat':
                        # 每日统计：mood, physical_condition, mental_state, training, management
                        mood = record[1]
                        physical_condition = record[2]
                        mental_state = record[3]
                        training = record[4] if len(record) > 4 else '正常'
                        management = record[5] if len(record) > 5 else '正常'
                        
                        # 检查是否有异常关键词或异常状态
                        exception_keywords = ['异常', '差', '很差', '抑郁', '焦虑', '生病', '受伤', '紧张']
                        for field in [mood, physical_condition, mental_state]:
                            if field and any(keyword in str(field) for keyword in exception_keywords):
                                return 1
                        
                        # 检查训练和管理状态
                        if training == '异常' or management == '异常':
                            return 1
                        
                        return 0
                    
                    elif source_type in ['town_interview', 'leader_interview']:
                        # 谈话：thoughts, spirit
                        thoughts = record[1]
                        spirit = record[2]
                        
                        # 检查是否有异常关键词
                        exception_keywords = ['异常', '问题', '消极', '抵触', '不良', '困难', '担心', '焦虑', '抑郁', '差']
                        for field in [thoughts, spirit]:
                            if field and any(keyword in str(field) for keyword in exception_keywords):
                                return 1
                        return 0
            
            # 如果没有找到该日期的数据，返回0（正常）
            return 0
            
        except Exception as e:
            print(f"计算异常状态时出错: {e}")
            return 0
    
    def on_point_hovered_fixed(self, point, state, series, source_key, dates):
        """处理鼠标悬停在数据点上的事件 - 修复版本，支持容差范围"""
        try:
            if state:  # 鼠标进入点
                # 获取点的X坐标（可能是小数）
                x_coord = point.x()
                
                # 使用四舍五入找到最近的日期索引，这样每个日期点左右0.5的范围都会显示该日期
                x_index = round(x_coord)
                
                # 确保索引在有效范围内
                if 0 <= x_index < len(dates):
                    date_str = dates[x_index]
                    exception_status = "异常" if point.y() == 1 else "正常"
                    tooltip_text = f"{date_str} - {exception_status}"
                    
                    # 显示工具提示
                    from PyQt5.QtWidgets import QToolTip
                    from PyQt5.QtGui import QCursor
                    QToolTip.showText(QCursor.pos(), tooltip_text)
                else:
                    # 如果超出范围，隐藏提示
                    from PyQt5.QtWidgets import QToolTip
                    QToolTip.hideText()
            else:  # 鼠标离开点
                from PyQt5.QtWidgets import QToolTip
                QToolTip.hideText()
        except Exception as e:
            print(f"处理悬停事件时出错: {e}")
    
    def on_point_hovered(self, point, state, series, source_key):
        """处理鼠标悬停在数据点上的事件"""
        try:
            if state:  # 鼠标进入点
                # 将时间戳转换为日期
                timestamp = point.x()
                date_time = QDateTime.fromMSecsSinceEpoch(int(timestamp))
                date_str = date_time.toString('yyyy-MM-dd')
                
                # 只显示日期
                tooltip_text = date_str
                
                # 显示工具提示
                from PyQt5.QtWidgets import QToolTip
                from PyQt5.QtGui import QCursor
                QToolTip.showText(QCursor.pos(), tooltip_text)
            else:  # 鼠标离开点
                from PyQt5.QtWidgets import QToolTip
                QToolTip.hideText()
        except Exception as e:
            print(f"处理悬停事件时出错: {e}")
    
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