"""
测试添加青年信息对话框
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QFormLayout, QComboBox, QScrollArea, QWidget, QGroupBox, QDateEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont
from utils.validators import validate_id_card, validate_phone


class AddYouthDialog(QDialog):
    data_updated = pyqtSignal()
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle('添加青年信息')
        self.setFixedSize(900, 700)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel('添加青年信息')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 滚动内容
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 基本信息组
        self.create_basic_info_group(scroll_layout)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_youth)
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def create_basic_info_group(self, parent_layout):
        group = QGroupBox('基本信息')
        layout = QFormLayout()
        
        # 姓名
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入姓名')
        layout.addRow('姓名 *:', self.name_input)
        
        # 性别
        self.gender_input = QComboBox()
        self.gender_input.addItems(['', '男', '女'])
        layout.addRow('性别 *:', self.gender_input)
        
        # 身份证号
        self.id_card_input = QLineEdit()
        self.id_card_input.setPlaceholderText('请输入18位身份证号')
        layout.addRow('公民身份号码 *:', self.id_card_input)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def save_youth(self):
        try:
            name = self.name_input.text().strip()
            gender = self.gender_input.currentText()
            id_card = self.id_card_input.text().strip()
            
            if not name or not gender or not id_card:
                QMessageBox.warning(self, '输入错误', '请填写必填字段！')
                return
            
            QMessageBox.information(self, '测试', '对话框工作正常！')
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'发生错误：{str(e)}')