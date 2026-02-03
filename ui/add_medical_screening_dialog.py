"""
添加病史筛查记录对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton, QFormLayout,
                             QMessageBox, QDateEdit, QComboBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
import sqlite3
from datetime import datetime


class AddMedicalScreeningDialog(QDialog):
    # 定义信号，当数据更新时发出
    data_updated = pyqtSignal()
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('添加病史筛查记录')
        self.setFixedSize(500, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel('添加病史筛查记录')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 姓名输入框
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('请输入姓名或通过身份证自动填写')
        form_layout.addRow('姓名 *:', self.name_edit)
        
        # 性别下拉选择框
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['', '男', '女'])
        self.gender_combo.setCurrentText('')
        form_layout.addRow('性别 *:', self.gender_combo)
        
        # 公民身份号码输入框
        self.id_card_edit = QLineEdit()
        self.id_card_edit.setPlaceholderText('请输入18位身份证号码')
        self.id_card_edit.setMaxLength(18)
        # 连接文本变化信号，实现自动填写功能
        self.id_card_edit.textChanged.connect(self.on_id_card_changed)
        form_layout.addRow('公民身份号码 *:', self.id_card_edit)
        
        # 筛查情况输入框（多行文本）
        self.screening_result_edit = QTextEdit()
        self.screening_result_edit.setPlaceholderText('请输入筛查情况详细信息...')
        self.screening_result_edit.setMaximumHeight(120)
        form_layout.addRow('筛查情况 *:', self.screening_result_edit)
        
        # 日期选择器
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        form_layout.addRow('筛查日期 *:', self.date_edit)
        
        # 备注选择
        self.remark_combo = QComboBox()
        self.remark_combo.addItems(['', '区调查情况', '市调查情况', '省调查情况'])
        self.remark_combo.setCurrentText('')
        form_layout.addRow('备注:', self.remark_combo)
        
        # 身体状况选择
        self.physical_status_combo = QComboBox()
        self.physical_status_combo.addItems(['', '正常', '异常'])
        self.physical_status_combo.setCurrentText('')
        form_layout.addRow('身体状况 *:', self.physical_status_combo)
        
        # 精神状况选择
        self.mental_status_combo = QComboBox()
        self.mental_status_combo.addItems(['', '正常', '异常'])
        self.mental_status_combo.setCurrentText('')
        form_layout.addRow('精神状况 *:', self.mental_status_combo)
        
        layout.addLayout(form_layout)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 保存按钮
        save_btn = QPushButton('保存')
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
        save_btn.clicked.connect(self.save_record)
        
        # 取消按钮
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
            QPushButton:pressed {
                background-color: #566573;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_id_card_changed(self, text):
        """身份证号码变化时的处理"""
        if len(text) == 18:
            # 查询基本信息数据库
            youth = self.db_manager.get_youth_by_id_card(text)
            if youth:
                # 自动填写姓名和性别
                self.name_edit.setText(youth.name)
                self.gender_combo.setCurrentText(youth.gender)
            else:
                # 清空自动填写的内容
                self.name_edit.clear()
                self.gender_combo.setCurrentText('')
                QMessageBox.information(self, '提示', '未在基本信息中找到该身份证号对应的人员信息')
    
    def save_record(self):
        """保存病史筛查记录"""
        # 验证必填字段
        name = self.name_edit.text().strip()
        gender = self.gender_combo.currentText()
        id_card = self.id_card_edit.text().strip()
        screening_result = self.screening_result_edit.toPlainText().strip()
        screening_date = self.date_edit.date().toString('yyyy-MM-dd')
        remark = self.remark_combo.currentText()
        physical_status = self.physical_status_combo.currentText()
        mental_status = self.mental_status_combo.currentText()
        
        # 验证必填字段
        if not all([name, gender, id_card, screening_result, physical_status, mental_status]):
            QMessageBox.warning(self, '输入错误', '请填写所有必填字段！')
            return
        
        # 验证1：身份证号码格式（18位）
        if len(id_card) != 18:
            QMessageBox.warning(self, '公民身份号码错误', '身份证号码必须是18位！\n请检查输入的身份证号码是否正确。')
            return
        
        # 验证2：检查基本信息中是否存在该人员，并获取应征地、连、排、班信息
        youth = self.db_manager.get_youth_by_id_card(id_card)
        if not youth:
            QMessageBox.warning(self, '此人在基本信息库中不存在', 
                              f'身份证号 {id_card} 在基本信息库中不存在！\n\n'
                              '请先在基本信息模块中添加该人员的基本信息，\n'
                              '然后再添加病史筛查记录。')
            return
        
        # 从基本信息中获取应征地、连、排、班
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT recruitment_place, company, platoon, squad 
                FROM youth WHERE id_card = ?
            """, (id_card,))
            youth_info = cursor.fetchone()
            
            recruitment_place = youth_info[0] if youth_info and youth_info[0] else ''
            company = youth_info[1] if youth_info and youth_info[1] else ''
            platoon = youth_info[2] if youth_info and youth_info[2] else ''
            squad = youth_info[3] if youth_info and youth_info[3] else ''
            
            # 验证3：检查数据是否重复（同一个人在同一天的筛查记录）
            cursor.execute('''
                SELECT COUNT(*) FROM medical_screening 
                WHERE id_card = ? AND screening_date = ?
            ''', (id_card, screening_date))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                conn.close()
                QMessageBox.warning(self, '数据重复', 
                                  f'{name} ({id_card}) 在 {screening_date} 已有筛查记录！\n\n'
                                  '同一个人在同一天只能有一条筛查记录。\n'
                                  '如需修改，请在列表中找到该记录进行编辑。')
                return
            
            # 插入病史筛查记录
            cursor.execute('''
                INSERT INTO medical_screening (youth_id_card, name, gender, id_card,
                                             screening_result, screening_date, remark,
                                             physical_status, mental_status,
                                             recruitment_place, company, platoon, squad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id_card, name, gender, id_card, screening_result, screening_date, remark,
                  physical_status, mental_status, recruitment_place, company, platoon, squad))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, '保存成功', '病史筛查记录已成功保存！')
            
            # 发出数据更新信号
            self.data_updated.emit()
            
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, '保存失败', f'保存病史筛查记录时发生错误：{str(e)}')
