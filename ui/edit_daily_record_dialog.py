"""
编辑每日记录对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit,
                             QTextEdit, QScrollArea, QWidget, QMessageBox,
                             QFormLayout)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime


class EditDailyRecordDialog(QDialog):
    # 定义信号，用于通知父窗口数据已更新
    data_updated = pyqtSignal()
    
    def __init__(self, db_manager, record_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.record_id = record_id
        self.record_data = None
        self.init_ui()
        self.load_record_data()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('编辑每日记录')
        self.setModal(True)
        self.resize(500, 600)
        
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
    
    def load_record_data(self):
        """加载记录数据"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT record_date, mood, physical_condition, mental_state, 
                       training, management, notes
                FROM daily_stat 
                WHERE id = ?
            ''', (self.record_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.record_data = result
                # 设置日期
                if result[0]:
                    try:
                        if isinstance(result[0], str):
                            date_obj = datetime.strptime(result[0], '%Y-%m-%d')
                            self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                        else:
                            # 如果是其他日期格式，尝试直接转换
                            self.date_edit.setDate(QDate.fromString(str(result[0]), 'yyyy-MM-dd'))
                    except:
                        # 如果转换失败，使用当前日期
                        self.date_edit.setDate(QDate.currentDate())
                
                # 设置状态字段
                self.mood_combo.setCurrentText(str(result[1] or '正常'))
                self.physical_combo.setCurrentText(str(result[2] or '正常'))
                self.mental_combo.setCurrentText(str(result[3] or '正常'))
                self.training_combo.setCurrentText(str(result[4] or '正常'))
                self.management_combo.setCurrentText(str(result[5] or '正常'))
                
                # 设置备注
                self.notes_edit.setPlainText(str(result[6] or ''))
            else:
                QMessageBox.warning(self, '错误', '未找到指定的记录')
                self.reject()
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载记录数据时发生错误：{str(e)}')
            self.reject()
    
    def save_record(self):
        """保存记录"""
        try:
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
            
            # 更新数据库
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE daily_stat 
                SET record_date = ?, mood = ?, physical_condition = ?, 
                    mental_state = ?, training = ?, management = ?, notes = ?
                WHERE id = ?
            ''', (record_date, mood, physical_condition, mental_state, 
                  training, management, notes, self.record_id))
            
            conn.commit()
            conn.close()
            
            # 发送数据更新信号
            self.data_updated.emit()
            
            QMessageBox.information(self, '成功', '记录已成功更新')
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存记录时发生错误：{str(e)}')