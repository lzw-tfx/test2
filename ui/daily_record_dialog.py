"""
每日记录对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QDateEdit,
                             QComboBox, QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QPainter
from datetime import datetime, timedelta

# 尝试导入QtCharts，如果失败则禁用图表功能
QTCHARTS_AVAILABLE = True
try:
    from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
except ImportError:
    QTCHARTS_AVAILABLE = False
    print("警告: PyQt6.QtCharts 未安装，图表功能将被禁用")


class DailyRecordDialog(QDialog):
    data_updated = pyqtSignal()  # 数据更新信号
    
    def __init__(self, db_manager, parent=None, youth_id=None, youth_name=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.youth_id = youth_id
        self.youth_name = youth_name
        self.init_ui()
        if self.youth_id:
            self.load_records()
    
    def init_ui(self):
        if self.youth_id:
            self.setWindowTitle(f'每日情况记录 - {self.youth_name}')
        else:
            self.setWindowTitle('添加每日情况记录')
        self.setMinimumSize(600, 400)  # 设置最小尺寸
        self.resize(600, 400)  # 设置初始尺寸，但允许调整
        
        # 允许窗口调整大小，只显示最大化和关闭按钮
        self.setWindowFlags(Qt.Dialog | 
                           Qt.WindowMaximizeButtonHint | 
                           Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)  # 减小间隔
        layout.setContentsMargins(20, 15, 20, 15)
        
        # 如果没有指定青年，显示青年选择
        if not self.youth_id:
            # 标题
            title = QLabel('添加每日情况记录')
            title.setStyleSheet('font-size: 14px; font-weight: bold; padding: 3px;')
            layout.addWidget(title)
            
            youth_layout = QHBoxLayout()
            youth_layout.setSpacing(8)
            youth_layout.addWidget(QLabel('选择青年:'))
            
            self.youth_combo = QComboBox()
            self.load_youth_list()
            youth_layout.addWidget(self.youth_combo)
            
            layout.addLayout(youth_layout)
        else:
            # 标题
            title = QLabel(f'青年: {self.youth_name}')
            title.setStyleSheet('font-size: 16px; font-weight: bold; padding: 3px;')
            layout.addWidget(title)
        
        # 录入表单 - 使用FormLayout更紧凑
        from PyQt5.QtWidgets import QFormLayout
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 5, 0, 5)
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow('日期:', self.date_input)
        
        self.mood_input = QComboBox()
        self.mood_input.addItems(['正常', '异常'])
        form_layout.addRow('思想:', self.mood_input)
        
        self.physical_input = QComboBox()
        self.physical_input.addItems(['正常', '异常'])
        form_layout.addRow('身体:', self.physical_input)
        
        self.mental_input = QComboBox()
        self.mental_input.addItems(['正常', '异常'])
        form_layout.addRow('精神:', self.mental_input)
        
        self.training_input = QComboBox()
        self.training_input.addItems(['正常', '异常'])
        form_layout.addRow('训练:', self.training_input)
        
        self.management_input = QComboBox()
        self.management_input.addItems(['正常', '异常'])
        form_layout.addRow('管理:', self.management_input)
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText('请输入其他备注信息')
        form_layout.addRow('其他:', self.notes_input)
        
        layout.addLayout(form_layout)
        
        # 如果有指定青年，显示历史记录
        if self.youth_id:
            # 历史记录表格
            self.records_table = QTableWidget()
            self.records_table.setColumnCount(9)
            self.records_table.setHorizontalHeaderLabels(['日期', '思想', '身体', '精神', '训练', '管理', '其他', '修改', '删除'])
            
            # 设置表格属性
            self.records_table.setAlternatingRowColors(True)
            self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.records_table.horizontalHeader().setStretchLastSection(False)
            self.records_table.verticalHeader().setVisible(False)  # 隐藏行号
            
            layout.addWidget(self.records_table)
            
            # 趋势图表（仅在QtCharts可用时显示）
            if QTCHARTS_AVAILABLE:
                chart_label = QLabel('情况趋势图 (最近30天)')
                chart_label.setStyleSheet('font-weight: bold; margin-top: 3px; padding: 3px;')
                layout.addWidget(chart_label)
                
                self.chart_view = self.create_chart()
                layout.addWidget(self.chart_view)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        ok_btn = QPushButton('确定')
        ok_btn.setStyleSheet("""
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
        ok_btn.clicked.connect(self.on_ok_clicked)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet("""
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
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_youth_list(self):
        """加载青年列表"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, id_card FROM youth ORDER BY name")
            results = cursor.fetchall()
            conn.close()
            
            self.youth_combo.clear()
            self.youth_combo.addItem("请选择青年", None)
            
            for youth in results:
                display_text = f"{youth[1]} ({youth[2]})"
                self.youth_combo.addItem(display_text, youth[0])
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载青年列表失败: {str(e)}")
    
    def create_chart(self):
        """创建趋势图表"""
        if not QTCHARTS_AVAILABLE:
            return QLabel('图表功能不可用')
        
        chart = QChart()
        chart.setTitle('每日情况趋势')
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(250)
        
        return chart_view
    
    def update_chart(self):
        """更新趋势图表"""
        if not QTCHARTS_AVAILABLE or not self.youth_id:
            return
        
        data = self.db_manager.get_daily_stats_for_chart(self.youth_id, 30)
        
        if not data:
            return
        
        # 创建数据系列
        mood_series = QLineSeries()
        mood_series.setName('思想状态')
        
        physical_series = QLineSeries()
        physical_series.setName('身体状况')
        
        mental_series = QLineSeries()
        mental_series.setName('精神状态')
        
        # 评分映射
        mood_map = {'正常': 3, '下拉': 2, '异常': 1}
        physical_map = {'正常': 2, '异常': 1}
        mental_map = {'正常': 2, '异常': 1}
        
        for i, record in enumerate(reversed(data)):
            mood_series.append(i, mood_map.get(record[1], 2))
            physical_series.append(i, physical_map.get(record[2], 1))
            mental_series.append(i, mental_map.get(record[3], 1))
        
        # 创建新图表
        chart = QChart()
        chart.addSeries(mood_series)
        chart.addSeries(physical_series)
        chart.addSeries(mental_series)
        
        # 设置坐标轴
        axis_x = QValueAxis()
        axis_x.setTitleText('天数')
        axis_x.setLabelFormat('%d')
        axis_x.setRange(0, len(data))
        
        axis_y = QValueAxis()
        axis_y.setTitleText('评分')
        axis_y.setRange(0, 4)
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        mood_series.attachAxis(axis_x)
        mood_series.attachAxis(axis_y)
        physical_series.attachAxis(axis_x)
        physical_series.attachAxis(axis_y)
        mental_series.attachAxis(axis_x)
        mental_series.attachAxis(axis_y)
        
        chart.setTitle('每日情况趋势 (最近30天)')
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view.setChart(chart)
    
    def load_records(self):
        """加载历史记录"""
        if not self.youth_id:
            return
            
        data = self.db_manager.get_module_data('daily_stat', self.youth_id)
        
        self.records_table.setRowCount(len(data))
        
        # 设置表格列宽，确保显示正确
        self.records_table.setColumnWidth(0, 100)  # 日期
        self.records_table.setColumnWidth(1, 60)   # 思想
        self.records_table.setColumnWidth(2, 60)   # 身体
        self.records_table.setColumnWidth(3, 60)   # 精神
        self.records_table.setColumnWidth(4, 60)   # 训练
        self.records_table.setColumnWidth(5, 60)   # 管理
        self.records_table.setColumnWidth(6, 120)  # 其他
        self.records_table.setColumnWidth(7, 70)   # 编辑
        self.records_table.setColumnWidth(8, 70)   # 删除
        
        for row, record in enumerate(data):
            # 记录结构：id, youth_id, record_date, mood, physical_condition, mental_state, training, management, notes
            self.records_table.setItem(row, 0, QTableWidgetItem(str(record[2]) if record[2] else ''))  # date
            self.records_table.setItem(row, 1, QTableWidgetItem(str(record[3]) if record[3] else '正常'))  # mood
            self.records_table.setItem(row, 2, QTableWidgetItem(str(record[4]) if record[4] else '正常'))  # physical
            self.records_table.setItem(row, 3, QTableWidgetItem(str(record[5]) if record[5] else '正常'))  # mental
            self.records_table.setItem(row, 4, QTableWidgetItem(str(record[6]) if record[6] else '正常'))  # training
            self.records_table.setItem(row, 5, QTableWidgetItem(str(record[7]) if record[7] else '正常'))  # management
            self.records_table.setItem(row, 6, QTableWidgetItem(str(record[8]) if record[8] else ''))  # notes
            
            # 编辑按钮
            edit_btn = QPushButton('修改')
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, r=record: self.edit_record(r))
            self.records_table.setCellWidget(row, 7, edit_btn)
            
            # 删除按钮
            del_btn = QPushButton('删除')
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
            """)
            del_btn.clicked.connect(lambda checked, r_id=record[0]: self.delete_record(r_id))
            self.records_table.setCellWidget(row, 8, del_btn)
        
        self.update_chart()
    
    def edit_record(self, record):
        """编辑记录"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDateEdit, QComboBox, QMessageBox
        from PyQt5.QtCore import QDate
        
        dialog = QDialog(self)
        dialog.setWindowTitle('编辑每日记录')
        dialog.setFixedSize(500, 350)
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 标题
        title = QLabel('编辑每日记录')
        title.setStyleSheet('font-size: 14px; font-weight: bold;')
        layout.addWidget(title)
        
        # 表单
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)
        
        # 日期
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel('日期:'))
        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        if record[2]:
            date_parts = record[2].split('-')
            if len(date_parts) == 3:
                date_input.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
        date_layout.addWidget(date_input)
        form_layout.addLayout(date_layout)
        
        # 思想
        mood_layout = QHBoxLayout()
        mood_layout.addWidget(QLabel('思想:'))
        mood_input = QComboBox()
        mood_input.addItems(['正常', '异常'])
        mood_input.setCurrentText(record[3] or '正常')
        mood_layout.addWidget(mood_input)
        form_layout.addLayout(mood_layout)
        
        # 身体
        physical_layout = QHBoxLayout()
        physical_layout.addWidget(QLabel('身体:'))
        physical_input = QComboBox()
        physical_input.addItems(['正常', '异常'])
        physical_input.setCurrentText(record[4] or '正常')
        physical_layout.addWidget(physical_input)
        form_layout.addLayout(physical_layout)
        
        # 精神
        mental_layout = QHBoxLayout()
        mental_layout.addWidget(QLabel('精神:'))
        mental_input = QComboBox()
        mental_input.addItems(['正常', '异常'])
        mental_input.setCurrentText(record[5] or '正常')
        mental_layout.addWidget(mental_input)
        form_layout.addLayout(mental_layout)
        
        # 训练
        training_layout = QHBoxLayout()
        training_layout.addWidget(QLabel('训练:'))
        training_input = QComboBox()
        training_input.addItems(['正常', '异常'])
        training_input.setCurrentText(record[6] or '正常')
        training_layout.addWidget(training_input)
        form_layout.addLayout(training_layout)
        
        # 管理
        management_layout = QHBoxLayout()
        management_layout.addWidget(QLabel('管理:'))
        management_input = QComboBox()
        management_input.addItems(['正常', '异常'])
        management_input.setCurrentText(record[7] or '正常')
        management_layout.addWidget(management_input)
        form_layout.addLayout(management_layout)
        
        # 其他
        notes_layout = QHBoxLayout()
        notes_layout.addWidget(QLabel('其他:'))
        notes_input = QLineEdit()
        notes_input.setText(record[8] or '')
        notes_layout.addWidget(notes_input)
        form_layout.addLayout(notes_layout)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        
        def save_changes():
            # 验证：当有任何状态为"异常"时，"其他"字段必须填写
            abnormal_statuses = []
            if mood_input.currentText() == '异常':
                abnormal_statuses.append('思想')
            if physical_input.currentText() == '异常':
                abnormal_statuses.append('身体')
            if mental_input.currentText() == '异常':
                abnormal_statuses.append('精神')
            if training_input.currentText() == '异常':
                abnormal_statuses.append('训练')
            if management_input.currentText() == '异常':
                abnormal_statuses.append('管理')
            
            notes_text = notes_input.text().strip()
            if abnormal_statuses and not notes_text:
                status_text = '、'.join(abnormal_statuses)
                QMessageBox.warning(dialog, '验证失败', f'当{status_text}状态为"异常"时，"其他"字段必须填写说明信息！')
                return
            
            try:
                # 更新数据库记录
                self.db_manager.update_daily_stat(
                    record[0],  # record_id
                    date_input.date().toString('yyyy-MM-dd'),
                    mood_input.currentText(),
                    physical_input.currentText(),
                    mental_input.currentText(),
                    training_input.currentText(),
                    management_input.currentText(),
                    notes_text
                )
                
                QMessageBox.information(dialog, '成功', '记录已更新')
                self.data_updated.emit()
                self.load_records()
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(dialog, '错误', f'更新失败: {str(e)}')
        
        save_btn.clicked.connect(save_changes)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def on_ok_clicked(self):
        """确定按钮点击事件 - 添加记录"""
        # 如果没有指定青年，从下拉框获取
        if not self.youth_id:
            current_youth_id = self.youth_combo.currentData()
            if not current_youth_id:
                QMessageBox.warning(self, '提示', '请选择一个青年')
                return
            target_youth_id = current_youth_id
            
            # 验证青年是否存在（通过youth_id查询）
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_card, name FROM youth WHERE id=?", (target_youth_id,))
            youth_info = cursor.fetchone()
            conn.close()
            
            if not youth_info:
                QMessageBox.warning(self, '青年不存在', '该青年信息不存在，请重新选择！')
                return
        else:
            target_youth_id = self.youth_id
        
        date = self.date_input.date().toString('yyyy-MM-dd')
        mood = self.mood_input.currentText()
        physical = self.physical_input.currentText()
        mental = self.mental_input.currentText()
        training = self.training_input.currentText()
        management = self.management_input.currentText()
        notes = self.notes_input.text().strip()
        
        # 验证：当有任何状态为"异常"时，"其他"字段必须填写
        abnormal_statuses = []
        if mood == '异常':
            abnormal_statuses.append('思想')
        if physical == '异常':
            abnormal_statuses.append('身体')
        if mental == '异常':
            abnormal_statuses.append('精神')
        if training == '异常':
            abnormal_statuses.append('训练')
        if management == '异常':
            abnormal_statuses.append('管理')
        
        if abnormal_statuses and not notes:
            status_text = '、'.join(abnormal_statuses)
            QMessageBox.warning(self, '验证失败', f'当{status_text}状态为"异常"时，"其他"字段必须填写说明信息！')
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 检查是否存在重复记录（相同的 youth_id 和 record_date）
            cursor.execute("""
                SELECT d.id, y.name, y.id_card
                FROM daily_stat d
                JOIN youth y ON d.youth_id = y.id
                WHERE d.youth_id = ? AND d.record_date = ?
            """, (target_youth_id, date))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # 存在重复记录，询问是否覆盖
                existing_id = existing_record[0]
                youth_name = existing_record[1]
                youth_id_card = existing_record[2]
                
                reply = QMessageBox.question(
                    self,
                    '重复数据',
                    f'已存在 {youth_name}（{youth_id_card}）在 {date} 的记录。\n\n是否覆盖原有数据？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # 覆盖：更新现有记录，使用新的数据库方法
                    self.db_manager.update_daily_stat(
                        existing_id,
                        date,
                        mood,
                        physical,
                        mental,
                        training,
                        management,
                        notes
                    )
                    
                    QMessageBox.information(self, '成功', '记录已更新')
                    
                    # 发送数据更新信号
                    self.data_updated.emit()
                    
                    # 关闭对话框
                    self.accept()
                else:
                    # 不覆盖，关闭连接并返回
                    conn.close()
                    return
            else:
                # 不存在重复记录，使用新的数据库方法插入
                conn.close()  # 先关闭查询连接
                
                self.db_manager.insert_daily_stat(
                    target_youth_id, date, mood, physical, mental, training, management, notes
                )
                
                QMessageBox.information(self, '成功', '记录添加成功')
                
                # 发送数据更新信号
                self.data_updated.emit()
                
                # 关闭对话框
                self.accept()
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')
    
    def add_record(self):
        """添加记录"""
        # 如果没有指定青年，从下拉框获取
        if not self.youth_id:
            current_youth_id = self.youth_combo.currentData()
            if not current_youth_id:
                QMessageBox.warning(self, '提示', '请选择一个青年')
                return
            target_youth_id = current_youth_id
        else:
            target_youth_id = self.youth_id
        
        date = self.date_input.date().toString('yyyy-MM-dd')
        mood = self.mood_input.currentText()
        physical = self.physical_input.currentText()
        mental = self.mental_input.currentText()
        training = self.training_input.currentText()
        management = self.management_input.currentText()
        notes = self.notes_input.text().strip()
        
        # 验证：当有任何状态为"异常"时，"其他"字段必须填写
        abnormal_statuses = []
        if mood == '异常':
            abnormal_statuses.append('思想')
        if physical == '异常':
            abnormal_statuses.append('身体')
        if mental == '异常':
            abnormal_statuses.append('精神')
        if training == '异常':
            abnormal_statuses.append('训练')
        if management == '异常':
            abnormal_statuses.append('管理')
        
        if abnormal_statuses and not notes:
            status_text = '、'.join(abnormal_statuses)
            QMessageBox.warning(self, '验证失败', f'当{status_text}状态为"异常"时，"其他"字段必须填写说明信息！')
            return
        
        try:
            # 插入数据库记录
            self.db_manager.insert_daily_stat(
                target_youth_id, date, mood, physical, mental, training, management, notes
            )
            
            QMessageBox.information(self, '成功', '记录添加成功')
            self.notes_input.clear()
            
            # 发送数据更新信号
            self.data_updated.emit()
            
            if self.youth_id:
                self.load_records()
            else:
                # 如果是添加模式，添加成功后可以关闭对话框
                self.accept()
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'添加失败: {str(e)}')
    
    def delete_record(self, record_id):
        """删除记录"""
        reply = QMessageBox.question(self, '确认', '确定要删除这条记录吗?',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # 删除数据库记录
            success = self.db_manager.delete_daily_stat(record_id)
            
            if success:
                QMessageBox.information(self, '成功', '记录已删除')
                self.data_updated.emit()
                self.load_records()
            else:
                QMessageBox.warning(self, '错误', '删除失败，记录可能不存在')
