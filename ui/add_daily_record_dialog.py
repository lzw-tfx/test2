"""
添加每日记录对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit,
                             QTextEdit, QScrollArea, QWidget, QMessageBox,
                             QFormLayout, QCompleter)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QStringListModel
from PyQt5.QtGui import QFont
from datetime import datetime


class AddDailyRecordDialog(QDialog):
    # 定义信号，用于通知父窗口数据已更新
    data_updated = pyqtSignal()
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.youth_data = {}  # 存储青年数据
        self.init_ui()
        self.load_youth_options()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('添加每日记录')
        self.setModal(True)
        self.resize(500, 650)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容widget
        content_widget = QWidget()
        content_layout = QFormLayout()
        
        # 设置字体
        font = QFont()
        font.setPointSize(11)
        
        # 青年选择
        self.youth_combo = QComboBox()
        self.youth_combo.setEditable(True)  # 允许输入
        self.youth_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # 不插入新项
        self.youth_combo.setFont(font)
        
        # 设置自动完成
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.youth_combo.setCompleter(self.completer)
        
        content_layout.addRow('选择青年:', self.youth_combo)
        
        # 日期选择
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFont(font)
        content_layout.addRow('日期:', self.date_edit)
        
        # 思想状态
        self.mood_combo = QComboBox()
        self.mood_combo.addItems(['正常', '异常'])
        self.mood_combo.setFont(font)
        content_layout.addRow('思想:', self.mood_combo)
        
        # 身体状态
        self.physical_combo = QComboBox()
        self.physical_combo.addItems(['正常', '异常'])
        self.physical_combo.setFont(font)
        content_layout.addRow('身体:', self.physical_combo)
        
        # 精神状态
        self.mental_combo = QComboBox()
        self.mental_combo.addItems(['正常', '异常'])
        self.mental_combo.setFont(font)
        content_layout.addRow('精神:', self.mental_combo)
        
        # 训练状态
        self.training_combo = QComboBox()
        self.training_combo.addItems(['正常', '异常'])
        self.training_combo.setFont(font)
        content_layout.addRow('训练:', self.training_combo)
        
        # 管理状态
        self.management_combo = QComboBox()
        self.management_combo.addItems(['正常', '异常'])
        self.management_combo.setFont(font)
        content_layout.addRow('管理:', self.management_combo)
        
        # 其他备注
        self.notes_edit = QTextEdit()
        self.notes_edit.setFont(font)
        self.notes_edit.setMaximumHeight(120)
        self.notes_edit.setPlaceholderText('请输入其他备注信息...')
        content_layout.addRow('其他:', self.notes_edit)
        
        # 设置内容widget的布局
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # 添加滚动区域到主布局
        main_layout.addWidget(scroll_area)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 保存按钮
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_record)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11pt;
                min-height: 35px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
        button_layout.addWidget(save_btn)
        
        # 取消按钮
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2C3E50;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11pt;
                min-height: 35px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ECF0F1;
                border-color: #95A5A6;
            }
            QPushButton:pressed {
                background-color: #D5DBDB;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def load_youth_options(self):
        """加载青年选项"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id_card, name 
                FROM youth 
                ORDER BY name
            ''')
            results = cursor.fetchall()
            conn.close()
            
            # 清空现有选项
            self.youth_combo.clear()
            self.youth_data.clear()
            
            # 构建选项列表
            options = []
            for id_card, name in results:
                if name and id_card:
                    option_text = f"{name}（{id_card}）"
                    options.append(option_text)
                    self.youth_data[option_text] = {
                        'id_card': id_card,
                        'name': name
                    }
            
            # 按字符顺序排序选项
            options.sort()
            
            # 存储所有选项用于过滤
            self.all_options = options.copy()
            
            # 添加选项到下拉框
            self.youth_combo.addItems(options)
            
            # 设置自动完成模型
            model = QStringListModel(options)
            self.completer.setModel(model)
            
            # 连接文本变化事件，实现动态过滤
            self.youth_combo.lineEdit().textChanged.connect(self.filter_youth_options)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载青年信息失败：{str(e)}')
    
    def filter_youth_options(self, text):
        """根据输入文本过滤青年选项"""
        if not text:
            return
        
        try:
            # 获取所有选项
            all_options = list(self.youth_data.keys())
            
            # 过滤选项
            filtered_options = [
                option for option in all_options 
                if text.lower() in option.lower()
            ]
            
            # 更新自动完成模型
            model = QStringListModel(filtered_options)
            self.completer.setModel(model)
            
        except Exception as e:
            print(f"过滤青年选项时出错: {e}")
    
    def get_selected_youth_info(self):
        """获取选中的青年信息"""
        current_text = self.youth_combo.currentText()
        if current_text in self.youth_data:
            return self.youth_data[current_text]
        
        # 如果是手动输入的文本，尝试解析
        if '（' in current_text and '）' in current_text:
            try:
                name = current_text.split('（')[0]
                id_card = current_text.split('（')[1].split('）')[0]
                return {'name': name, 'id_card': id_card}
            except:
                pass
        
        return None
    
    def save_record(self):
        """保存记录"""
        try:
            # 获取青年信息
            youth_info = self.get_selected_youth_info()
            if not youth_info:
                QMessageBox.warning(self, '错误', '请选择一个有效的青年')
                return
            
            # 数据校验：验证青年是否存在于基本信息表中
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM youth WHERE id_card = ?', (youth_info['id_card'],))
            youth_record = cursor.fetchone()
            
            if not youth_record:
                conn.close()
                QMessageBox.warning(self, '数据校验失败', 
                                  f'公民身份号码 {youth_info["id_card"]} 在基本信息表中不存在，无法添加每日记录。\n\n'
                                  f'请先在基本信息模块中添加该人员的基本信息。')
                return
            
            youth_id = youth_record[0]
            
            # 获取表单数据
            record_date = self.date_edit.date().toString('yyyy-MM-dd')
            mood = self.mood_combo.currentText()
            physical_condition = self.physical_combo.currentText()
            mental_state = self.mental_combo.currentText()
            training = self.training_combo.currentText()
            management = self.management_combo.currentText()
            notes = self.notes_edit.toPlainText().strip()
            
            # 异常数据验证：如果任一状态为异常，其他列不能为空
            is_abnormal = any(status == '异常' for status in [mood, physical_condition, mental_state, training, management])
            if is_abnormal and not notes:
                QMessageBox.warning(self, '数据验证失败', 
                                  '当思想、身体、精神、训练或管理任一项为异常时，"其他"列不能为空。\n\n'
                                  '请在"其他"栏中填写相关说明。')
                return
            
            # 检查是否已存在相同日期的记录
            cursor.execute('''
                SELECT id FROM daily_stat 
                WHERE youth_id = ? AND record_date = ?
            ''', (youth_id, record_date))
            
            existing_record = cursor.fetchone()
            if existing_record:
                conn.close()
                reply = QMessageBox.question(
                    self, '记录已存在', 
                    f'该青年在 {record_date} 已有记录，是否要覆盖？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                
                # 更新现有记录
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE daily_stat 
                    SET mood = ?, physical_condition = ?, mental_state = ?, 
                        training = ?, management = ?, notes = ?
                    WHERE youth_id = ? AND record_date = ?
                ''', (mood, physical_condition, mental_state, training, 
                      management, notes, youth_id, record_date))
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO daily_stat (youth_id, record_date, mood, physical_condition, 
                                          mental_state, training, management, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (youth_id, record_date, mood, physical_condition, mental_state, 
                      training, management, notes))
            
            conn.commit()
            conn.close()
            
            # 发送数据更新信号
            self.data_updated.emit()
            
            QMessageBox.information(self, '成功', '记录已成功保存')
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存记录时发生错误：{str(e)}')