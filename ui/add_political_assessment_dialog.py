"""
添加/编辑政治考核情况对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton, QMessageBox, QDateEdit, QComboBox)
from PyQt5.QtCore import Qt, QDate


class AddPoliticalAssessmentDialog(QDialog):
    def __init__(self, db_manager, youth_id_card, parent=None, record_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.youth_id_card = youth_id_card
        self.record_data = record_data  # 如果是编辑模式，包含现有记录数据
        
        self.init_ui()
        
        # 如果是编辑模式，加载现有数据
        if self.record_data:
            self.load_record_data()
    
    def init_ui(self):
        title = '编辑政治考核情况' if self.record_data else '添加政治考核情况'
        self.setWindowTitle(title)
        self.setGeometry(200, 100, 600, 700)
        
        # 允许最大化和调整大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        layout = QVBoxLayout()
        
        # 获取青年基本信息
        youth = self.db_manager.get_youth_by_id_card(self.youth_id_card)
        if youth:
            info_label = QLabel(f'姓名: {youth.name}  |  性别: {youth.gender}  |  身份证号: {youth.id_card}')
            info_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
            layout.addWidget(info_label)
        
        # 日期
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel('日期:'))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
        """)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # 家庭成员信息
        layout.addWidget(QLabel('家庭成员信息:'))
        self.family_member_info_edit = QTextEdit()
        self.family_member_info_edit.setMaximumHeight(80)
        self.family_member_info_edit.setPlaceholderText('请输入家庭成员信息...')
        layout.addWidget(self.family_member_info_edit)
        
        # 走访调查情况
        layout.addWidget(QLabel('走访调查情况:'))
        self.visit_survey_edit = QTextEdit()
        self.visit_survey_edit.setMaximumHeight(80)
        self.visit_survey_edit.setPlaceholderText('请输入走访调查情况...')
        layout.addWidget(self.visit_survey_edit)
        
        # 政治考核情况
        layout.addWidget(QLabel('政治考核情况:'))
        self.political_assessment_edit = QTextEdit()
        self.political_assessment_edit.setMaximumHeight(80)
        self.political_assessment_edit.setPlaceholderText('请输入政治考核情况...')
        layout.addWidget(self.political_assessment_edit)
        
        # 需重点关注问题
        layout.addWidget(QLabel('需重点关注问题:'))
        self.key_attention_edit = QTextEdit()
        self.key_attention_edit.setMaximumHeight(80)
        self.key_attention_edit.setPlaceholderText('请输入需重点关注问题...')
        layout.addWidget(self.key_attention_edit)
        
        # 思想
        layout.addWidget(QLabel('思想:'))
        self.thoughts_combo = QComboBox()
        self.thoughts_combo.addItems(['正常', '异常'])
        layout.addWidget(self.thoughts_combo)
        
        # 精神
        layout.addWidget(QLabel('精神:'))
        self.spirit_combo = QComboBox()
        self.spirit_combo.addItems(['正常', '异常'])
        layout.addWidget(self.spirit_combo)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_record)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_record_data(self):
        """加载现有记录数据到表单"""
        if not self.record_data:
            return
        
        # record_data格式: (id, youth_id_card, name, gender, id_card, family_member_info, 
        #                   visit_survey, political_assessment, key_attention, assessment_date, 
        #                   thoughts, spirit, created_at)
        
        # 日期
        if self.record_data[9]:
            date_str = self.record_data[9]
            try:
                date_parts = date_str.split('-')
                if len(date_parts) == 3:
                    year, month, day = map(int, date_parts)
                    self.date_edit.setDate(QDate(year, month, day))
            except:
                pass
        
        # 家庭成员信息
        if self.record_data[5]:
            self.family_member_info_edit.setPlainText(self.record_data[5])
        
        # 走访调查情况
        if self.record_data[6]:
            self.visit_survey_edit.setPlainText(self.record_data[6])
        
        # 政治考核情况
        if self.record_data[7]:
            self.political_assessment_edit.setPlainText(self.record_data[7])
        
        # 需重点关注问题
        if self.record_data[8]:
            self.key_attention_edit.setPlainText(self.record_data[8])
        
        # 思想
        if self.record_data[10]:
            index = self.thoughts_combo.findText(self.record_data[10])
            if index >= 0:
                self.thoughts_combo.setCurrentIndex(index)
        
        # 精神
        if self.record_data[11]:
            index = self.spirit_combo.findText(self.record_data[11])
            if index >= 0:
                self.spirit_combo.setCurrentIndex(index)
    
    def save_record(self):
        """保存记录"""
        try:
            # 获取表单数据
            assessment_date = self.date_edit.date().toString('yyyy-MM-dd')
            family_member_info = self.family_member_info_edit.toPlainText().strip()
            visit_survey = self.visit_survey_edit.toPlainText().strip()
            political_assessment = self.political_assessment_edit.toPlainText().strip()
            key_attention = self.key_attention_edit.toPlainText().strip()
            thoughts = self.thoughts_combo.currentText()
            spirit = self.spirit_combo.currentText()
            
            # 获取青年基本信息
            youth = self.db_manager.get_youth_by_id_card(self.youth_id_card)
            if not youth:
                QMessageBox.warning(self, '错误', '未找到青年信息')
                return
            
            if self.record_data:
                # 编辑模式：更新现有记录
                record_id = self.record_data[0]
                success = self.db_manager.update_political_assessment(
                    record_id, family_member_info, visit_survey, political_assessment,
                    key_attention, assessment_date, thoughts, spirit
                )
                
                if success:
                    QMessageBox.information(self, '成功', '政治考核情况记录已更新')
                    self.accept()
                else:
                    QMessageBox.warning(self, '失败', '更新记录失败')
            else:
                # 添加模式：检查是否已存在相同记录
                existing_id = self.db_manager.check_political_assessment_exists(
                    self.youth_id_card, youth.name, assessment_date
                )
                
                if existing_id:
                    # 发现重复记录，询问用户
                    reply = QMessageBox.question(
                        self, '发现重复记录',
                        f'该人员在 {assessment_date} 已有政治考核情况记录。\n\n是否覆盖更新现有记录？',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # 覆盖更新
                        success = self.db_manager.update_political_assessment_by_unique_key(
                            self.youth_id_card, youth.name, assessment_date,
                            family_member_info, visit_survey, political_assessment,
                            key_attention, thoughts, spirit
                        )
                        
                        if success:
                            QMessageBox.information(self, '成功', '政治考核情况记录已覆盖更新')
                            self.accept()
                        else:
                            QMessageBox.warning(self, '失败', '覆盖更新记录失败')
                    # 如果选择No，则不做任何操作，对话框保持打开
                else:
                    # 插入新记录
                    record_id = self.db_manager.insert_political_assessment(
                        self.youth_id_card, youth.name, youth.gender, self.youth_id_card,
                        family_member_info, visit_survey, political_assessment,
                        key_attention, assessment_date, thoughts, spirit
                    )
                    
                    if record_id:
                        QMessageBox.information(self, '成功', '政治考核情况记录已添加')
                        self.accept()
                    else:
                        QMessageBox.warning(self, '失败', '添加记录失败')
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存记录时发生错误：{str(e)}')
