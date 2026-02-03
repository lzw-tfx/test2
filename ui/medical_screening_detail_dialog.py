"""
病史筛查详情对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton, QFormLayout,
                             QMessageBox, QDateEdit, QComboBox, QFrame, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont


class MedicalScreeningDetailDialog(QDialog):
    # 定义信号，当数据更新时发出
    data_updated = pyqtSignal()
    
    def __init__(self, db_manager, record_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.record_data = record_data
        self.is_edit_mode = False
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('病史筛查详情')
        self.setMinimumSize(600, 550)  # 设置最小尺寸
        self.resize(600, 550)  # 设置初始尺寸，但允许调整
        self.setModal(True)
        
        # 允许窗口调整大小，只显示最大化和关闭按钮
        self.setWindowFlags(Qt.Dialog | 
                           Qt.WindowMaximizeButtonHint | 
                           Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel('病史筛查详情')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 表单布局
        self.form_layout = QFormLayout()
        
        # 姓名输入框
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        self.form_layout.addRow('姓名:', self.name_edit)
        
        # 性别单选按钮组
        gender_layout = QHBoxLayout()
        self.gender_button_group = QButtonGroup()
        self.gender_male_radio = QRadioButton('男')
        self.gender_female_radio = QRadioButton('女')
        self.gender_button_group.addButton(self.gender_male_radio, 1)
        self.gender_button_group.addButton(self.gender_female_radio, 2)
        self.gender_male_radio.setEnabled(False)
        self.gender_female_radio.setEnabled(False)
        gender_layout.addWidget(self.gender_male_radio)
        gender_layout.addWidget(self.gender_female_radio)
        gender_layout.addStretch()
        self.form_layout.addRow('性别:', gender_layout)
        
        # 公民身份号码输入框
        self.id_card_edit = QLineEdit()
        self.id_card_edit.setReadOnly(True)
        self.form_layout.addRow('公民身份号码:', self.id_card_edit)
        
        # 筛查情况输入框（多行文本）
        self.screening_result_edit = QTextEdit()
        self.screening_result_edit.setReadOnly(True)
        self.screening_result_edit.setMinimumHeight(150)
        self.form_layout.addRow('筛查情况:', self.screening_result_edit)
        
        # 日期选择器
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setReadOnly(True)
        self.date_edit.setEnabled(False)
        self.form_layout.addRow('筛查日期:', self.date_edit)
        
        # 备注下拉选择框
        self.remark_combo = QComboBox()
        self.remark_combo.addItems(['', '区调查情况', '市调查情况', '省调查情况'])
        self.remark_combo.setEnabled(False)
        self.form_layout.addRow('备注:', self.remark_combo)
        
        # 身体状况单选按钮组
        physical_layout = QHBoxLayout()
        self.physical_button_group = QButtonGroup()
        self.physical_normal_radio = QRadioButton('正常')
        self.physical_abnormal_radio = QRadioButton('异常')
        self.physical_button_group.addButton(self.physical_normal_radio, 1)
        self.physical_button_group.addButton(self.physical_abnormal_radio, 2)
        self.physical_normal_radio.setEnabled(False)
        self.physical_abnormal_radio.setEnabled(False)
        physical_layout.addWidget(self.physical_normal_radio)
        physical_layout.addWidget(self.physical_abnormal_radio)
        physical_layout.addStretch()
        self.form_layout.addRow('身体状况:', physical_layout)
        
        # 精神状况单选按钮组
        mental_layout = QHBoxLayout()
        self.mental_button_group = QButtonGroup()
        self.mental_normal_radio = QRadioButton('正常')
        self.mental_abnormal_radio = QRadioButton('异常')
        self.mental_button_group.addButton(self.mental_normal_radio, 1)
        self.mental_button_group.addButton(self.mental_abnormal_radio, 2)
        self.mental_normal_radio.setEnabled(False)
        self.mental_abnormal_radio.setEnabled(False)
        mental_layout.addWidget(self.mental_normal_radio)
        mental_layout.addWidget(self.mental_abnormal_radio)
        mental_layout.addStretch()
        self.form_layout.addRow('精神状况:', mental_layout)
        
        layout.addLayout(self.form_layout)
        
        # 按钮布局
        self.button_layout = QHBoxLayout()
        
        # 编辑按钮
        self.edit_btn = QPushButton('编辑')
        self.edit_btn.setStyleSheet("""
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
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        
        # 保存按钮（初始隐藏）
        self.save_btn = QPushButton('保存')
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.hide()
        
        # 取消按钮
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.setStyleSheet("""
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
        self.cancel_btn.clicked.connect(self.handle_cancel)
        
        self.button_layout.addWidget(self.edit_btn)
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.cancel_btn)
        layout.addLayout(self.button_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """加载数据到表单"""
        # record_data格式: (id, youth_id_card, name, gender, id_card, screening_result, 
        #                   screening_date, remark, physical_status, mental_status)
        self.name_edit.setText(str(self.record_data[2] or ''))
        
        # 设置性别单选按钮
        gender = str(self.record_data[3] or '男')
        if gender == '女':
            self.gender_female_radio.setChecked(True)
        else:
            self.gender_male_radio.setChecked(True)
        
        self.id_card_edit.setText(str(self.record_data[4] or ''))
        self.screening_result_edit.setPlainText(str(self.record_data[5] or ''))
        
        # 设置日期
        if self.record_data[6]:
            date_parts = str(self.record_data[6]).split('-')
            if len(date_parts) == 3:
                self.date_edit.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
        
        # 设置备注
        remark = str(self.record_data[7] or '')
        if remark in ['区调查情况', '市调查情况', '省调查情况']:
            self.remark_combo.setCurrentText(remark)
        else:
            self.remark_combo.setCurrentIndex(0)
        
        # 设置身体状况单选按钮
        physical_status = str(self.record_data[8] or '正常')
        if physical_status == '异常':
            self.physical_abnormal_radio.setChecked(True)
        else:
            self.physical_normal_radio.setChecked(True)
        
        # 设置精神状况单选按钮
        mental_status = str(self.record_data[9] or '正常')
        if mental_status == '异常':
            self.mental_abnormal_radio.setChecked(True)
        else:
            self.mental_normal_radio.setChecked(True)
    
    def toggle_edit_mode(self):
        """切换编辑模式"""
        self.is_edit_mode = True
        
        # 设置可编辑字段
        self.gender_male_radio.setEnabled(True)
        self.gender_female_radio.setEnabled(True)
        self.screening_result_edit.setReadOnly(False)
        self.date_edit.setReadOnly(False)
        self.date_edit.setEnabled(True)
        self.remark_combo.setEnabled(True)
        self.physical_normal_radio.setEnabled(True)
        self.physical_abnormal_radio.setEnabled(True)
        self.mental_normal_radio.setEnabled(True)
        self.mental_abnormal_radio.setEnabled(True)
        
        # 修改样式
        editable_style = """
            QTextEdit {
                background-color: white;
                border: 1px solid #3498DB;
            }
        """
        radio_style = """
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #3498DB;
                border-radius: 9px;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #3498DB;
                border-radius: 9px;
                background-color: #3498DB;
            }
        """
        self.gender_male_radio.setStyleSheet(radio_style)
        self.gender_female_radio.setStyleSheet(radio_style)
        self.screening_result_edit.setStyleSheet(editable_style)
        self.physical_normal_radio.setStyleSheet(radio_style)
        self.physical_abnormal_radio.setStyleSheet(radio_style)
        self.mental_normal_radio.setStyleSheet(radio_style)
        self.mental_abnormal_radio.setStyleSheet(radio_style)
        
        # 切换按钮显示
        self.edit_btn.hide()
        self.save_btn.show()
        self.cancel_btn.setText('取消编辑')
        
        # 修改标题
        self.setWindowTitle('编辑病史筛查记录')
    
    def handle_cancel(self):
        """处理取消操作"""
        if self.is_edit_mode:
            # 如果在编辑模式，退出编辑模式
            reply = QMessageBox.question(self, '确认取消', 
                                       '确定要取消编辑吗？未保存的修改将丢失。',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.exit_edit_mode()
        else:
            # 如果在查看模式，关闭对话框
            self.reject()
    
    def exit_edit_mode(self):
        """退出编辑模式"""
        self.is_edit_mode = False
        
        # 重新加载数据
        self.load_data()
        
        # 设置为只读
        self.gender_male_radio.setEnabled(False)
        self.gender_female_radio.setEnabled(False)
        self.screening_result_edit.setReadOnly(True)
        self.date_edit.setReadOnly(True)
        self.date_edit.setEnabled(False)
        self.remark_combo.setEnabled(False)
        self.physical_normal_radio.setEnabled(False)
        self.physical_abnormal_radio.setEnabled(False)
        self.mental_normal_radio.setEnabled(False)
        self.mental_abnormal_radio.setEnabled(False)
        
        # 恢复样式
        self.gender_male_radio.setStyleSheet("")
        self.gender_female_radio.setStyleSheet("")
        self.screening_result_edit.setStyleSheet("")
        self.physical_normal_radio.setStyleSheet("")
        self.physical_abnormal_radio.setStyleSheet("")
        self.mental_normal_radio.setStyleSheet("")
        self.mental_abnormal_radio.setStyleSheet("")
        
        # 切换按钮显示
        self.save_btn.hide()
        self.edit_btn.show()
        self.cancel_btn.setText('取消')
        
        # 恢复标题
        self.setWindowTitle('病史筛查详情')
    
    def save_changes(self):
        """保存修改"""
        # 获取修改后的数据
        gender = '男' if self.gender_male_radio.isChecked() else '女'
        screening_result = self.screening_result_edit.toPlainText().strip()
        screening_date = self.date_edit.date().toString('yyyy-MM-dd')
        remark = self.remark_combo.currentText()
        physical_status = '正常' if self.physical_normal_radio.isChecked() else '异常'
        mental_status = '正常' if self.mental_normal_radio.isChecked() else '异常'
        
        # 验证必填字段
        if not screening_result:
            QMessageBox.warning(self, '输入错误', '筛查情况不能为空！')
            return
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 更新病史筛查记录
            cursor.execute('''
                UPDATE medical_screening 
                SET gender=?, screening_result=?, screening_date=?, remark=?,
                    physical_status=?, mental_status=?
                WHERE id=?
            ''', (gender, screening_result, screening_date, remark, physical_status, mental_status, self.record_data[0]))
            
            conn.commit()
            conn.close()
            
            # 异常统计已通过视图自动更新，无需手动同步
            
            QMessageBox.information(self, '保存成功', '病史筛查记录已成功更新！')
            
            # 更新本地数据
            self.record_data = (
                self.record_data[0],  # id
                self.record_data[1],  # youth_id_card
                self.record_data[2],  # name
                gender,               # gender - 更新
                self.record_data[4],  # id_card
                screening_result,     # screening_result - 更新
                screening_date,       # screening_date - 更新
                remark,               # remark - 更新
                physical_status,      # physical_status - 更新
                mental_status         # mental_status - 更新
            )
            
            # 发出数据更新信号
            self.data_updated.emit()
            
            # 退出编辑模式
            self.exit_edit_mode()
            
        except Exception as e:
            QMessageBox.warning(self, '保存失败', f'更新病史筛查记录时发生错误：{str(e)}')
