"""
入营点验情况对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QDateEdit, QMessageBox,
                             QFrame, QWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime


class CampVerificationDialog(QDialog):
    def __init__(self, db_manager, parent=None, record_data=None, youth_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.record_data = record_data
        self.youth_data = youth_data  # 青年数据对象
        
        self.init_ui()
        
        if record_data:
            self.load_record_data()
    
    def init_ui(self):
        title = "编辑入营点验记录" if self.record_data else "添加入营点验记录"
        self.setWindowTitle(title)
        self.setGeometry(200, 100, 600, 350)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 表单框架
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Shape.Box)
        form_layout = QVBoxLayout()
        
        # 日期
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        form_layout.addLayout(date_layout)
        
        # 姓名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("姓名:"))
        self.name_input = QLineEdit()
        if self.youth_data:
            self.name_input.setReadOnly(True)
            self.name_input.setText(self.youth_data.name)
        name_layout.addWidget(self.name_input)
        name_layout.addStretch()
        form_layout.addLayout(name_layout)
        
        # 身份证号
        id_card_layout = QHBoxLayout()
        id_card_layout.addWidget(QLabel("身份证号:"))
        self.id_card_input = QLineEdit()
        if self.youth_data:
            self.id_card_input.setReadOnly(True)
            self.id_card_input.setText(self.youth_data.id_card)
        id_card_layout.addWidget(self.id_card_input)
        id_card_layout.addStretch()
        form_layout.addLayout(id_card_layout)
        
        # 携带物品 (item)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel("携带物品:"))
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("请输入携带物品")
        item_layout.addWidget(self.item_input)
        item_layout.addStretch()
        form_layout.addLayout(item_layout)
        
        # 用途 (usage)
        usage_layout = QHBoxLayout()
        usage_layout.addWidget(QLabel("用途:"))
        self.usage_input = QLineEdit()
        self.usage_input.setPlaceholderText("请输入物品用途")
        usage_layout.addWidget(self.usage_input)
        usage_layout.addStretch()
        form_layout.addLayout(usage_layout)
        
        # 处置措施 (Disposal)
        disposal_layout = QHBoxLayout()
        disposal_layout.addWidget(QLabel("处置措施:"))
        self.disposal_input = QLineEdit()
        self.disposal_input.setPlaceholderText("请输入处置措施")
        disposal_layout.addWidget(self.disposal_input)
        disposal_layout.addStretch()
        form_layout.addLayout(disposal_layout)
        
        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_record)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_record_data(self):
        """加载现有记录数据"""
        if not self.record_data:
            return
        
        # 记录结构: CampVerification 对象
        self.name_input.setText(self.record_data.username)
        self.id_card_input.setText(self.record_data.user_id)
        self.item_input.setText(self.record_data.item)
        self.usage_input.setText(self.record_data.usage if hasattr(self.record_data, 'usage') else '')
        self.disposal_input.setText(self.record_data.Disposal)
        
        # 设置日期
        try:
            date = QDate.fromString(self.record_data.data, "yyyy-MM-dd")
            if date.isValid():
                self.date_edit.setDate(date)
        except:
            pass
    
    def save_record(self):
        """保存记录"""
        # 验证必填项
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "警告", "请输入姓名")
            return
        
        if not self.id_card_input.text().strip():
            QMessageBox.warning(self, "警告", "请输入身份证号")
            return
        
        if not self.item_input.text().strip():
            QMessageBox.warning(self, "警告", "请输入携带物品")
            return
        
        try:
            username = self.name_input.text().strip()
            user_id = self.id_card_input.text().strip()
            item = self.item_input.text().strip()
            usage = self.usage_input.text().strip()
            Disposal = self.disposal_input.text().strip()
            data = self.date_edit.date().toString("yyyy-MM-dd")
            
            if self.record_data:
                # 更新现有记录
                success = self.db_manager.update_camp_verification(
                    self.record_data.id, item, usage, Disposal, data
                )
                if success:
                    QMessageBox.information(self, "成功", "入营点验记录已更新")
                    self.accept()
                else:
                    QMessageBox.warning(self, "失败", "更新记录失败")
            else:
                # 添加新记录 - 检查是否已存在该身份证号的记录
                if self.db_manager.check_camp_verification_exists(user_id):
                    # 弹出确认对话框
                    reply = QMessageBox.question(
                        self, 
                        "重复数据确认", 
                        f"身份证号 {user_id} 已存在入营点验数据。\n\n是否覆盖现有数据？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # 用户选择覆盖，先删除现有记录
                        self.db_manager.delete_camp_verification_by_user_id(user_id)
                        
                        # 添加新记录
                        record_id = self.db_manager.add_camp_verification(
                            username, user_id, item, usage, Disposal, data
                        )
                        if record_id:
                            QMessageBox.information(self, "成功", "入营点验记录已覆盖保存")
                            self.accept()
                        else:
                            QMessageBox.warning(self, "失败", "覆盖记录失败")
                    else:
                        # 用户选择取消，不保存
                        return
                else:
                    # 没有重复记录，直接添加
                    record_id = self.db_manager.add_camp_verification(
                        username, user_id, item, usage, Disposal, data
                    )
                    if record_id:
                        QMessageBox.information(self, "成功", "入营点验记录已添加")
                        self.accept()
                    else:
                        QMessageBox.warning(self, "失败", "添加记录失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存记录时发生错误: {str(e)}")
