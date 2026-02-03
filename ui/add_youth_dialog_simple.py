"""
简化的添加青年信息对话框 - 单页面布局
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QFormLayout, QComboBox, QScrollArea, QWidget, QDateEdit
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
        self.resize(1000, 800)  # 改为resize，允许调整大小
        self.setModal(True)
        # 允许最大化和调整大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title_label = QLabel('添加青年信息')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 滚动内容
        scroll_content = QWidget()
        form_layout = QFormLayout(scroll_content)
        form_layout.setSpacing(8)
        
        # 所有字段按顺序添加
        # 1. 姓名
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入姓名')
        form_layout.addRow('姓名 *:', self.name_input)
        
        # 2. 公民身份号码
        self.id_card_input = QLineEdit()
        self.id_card_input.setPlaceholderText('请输入18位身份证号')
        self.id_card_input.setMaxLength(18)
        form_layout.addRow('公民身份号码 *:', self.id_card_input)
        
        # 3. 性别
        self.gender_input = QComboBox()
        self.gender_input.addItems(['', '男', '女'])
        form_layout.addRow('性别 *:', self.gender_input)
        
        # 4. 出生日期
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setDate(QDate.currentDate().addYears(-20))
        self.birth_date_input.setCalendarPopup(True)
        form_layout.addRow('出生日期:', self.birth_date_input)
        
        # 5. 民族
        self.nation_input = QLineEdit()
        self.nation_input.setPlaceholderText('如：汉族')
        form_layout.addRow('民族:', self.nation_input)
        
        # 6. 政治面貌
        self.political_status_input = QComboBox()
        self.political_status_input.addItems(['', '群众', '共青团员', '中共党员', '民主党派', '其他'])
        form_layout.addRow('政治面貌:', self.political_status_input)
        
        # 7. 宗教信仰
        self.religion_input = QLineEdit()
        self.religion_input.setPlaceholderText('如：无')
        form_layout.addRow('宗教信仰:', self.religion_input)
        
        # 8. 籍贯
        self.native_place_input = QLineEdit()
        self.native_place_input.setPlaceholderText('如：山东省济南市')
        form_layout.addRow('籍贯:', self.native_place_input)
        
        # 9. 文化程度
        self.education_level_input = QComboBox()
        self.education_level_input.addItems(['', '小学', '初中', '高中', '中专', '大专', '本科', '硕士', '博士'])
        form_layout.addRow('文化程度:', self.education_level_input)
        
        # 10. 学业情况
        self.study_status_input = QComboBox()
        self.study_status_input.addItems(['', '在读', '毕业', '肄业', '其他'])
        form_layout.addRow('学业情况:', self.study_status_input)
        
        # 11. 学习类型
        self.study_type_input = QComboBox()
        self.study_type_input.addItems(['', '全日制', '非全日制', '函授', '自考', '其他'])
        form_layout.addRow('学习类型:', self.study_type_input)
        
        # 12. 入营时间
        self.camp_entry_time_input = QDateEdit()
        self.camp_entry_time_input.setDate(QDate.currentDate())
        self.camp_entry_time_input.setCalendarPopup(True)
        form_layout.addRow('入营时间:', self.camp_entry_time_input)
        
        # 13. 应征地
        self.recruitment_place_input = QLineEdit()
        self.recruitment_place_input.setPlaceholderText('请输入应征地')
        form_layout.addRow('应征地:', self.recruitment_place_input)
        
        # 14. 经常居住地址
        self.residence_address_input = QLineEdit()
        self.residence_address_input.setPlaceholderText('请输入经常居住地址')
        form_layout.addRow('经常居住地址:', self.residence_address_input)
        
        # 15. 户籍所在地
        self.household_address_input = QLineEdit()
        self.household_address_input.setPlaceholderText('请输入户籍所在地')
        form_layout.addRow('户籍所在地:', self.household_address_input)
        
        # 16. 邮编
        self.postal_code_input = QLineEdit()
        self.postal_code_input.setPlaceholderText('请输入邮编')
        self.postal_code_input.setMaxLength(6)
        form_layout.addRow('邮编:', self.postal_code_input)
        
        # 17. 本人电话
        self.personal_phone_input = QLineEdit()
        self.personal_phone_input.setPlaceholderText('请输入本人电话')
        form_layout.addRow('本人电话:', self.personal_phone_input)
        
        # 18. 家庭电话
        self.family_phone_input = QLineEdit()
        self.family_phone_input.setPlaceholderText('请输入家庭电话')
        form_layout.addRow('家庭电话:', self.family_phone_input)
        
        # 19. 毕业(就读)学校
        self.school_input = QLineEdit()
        self.school_input.setPlaceholderText('请输入学校名称')
        form_layout.addRow('毕业(就读)学校:', self.school_input)
        
        # 20. 所学专业
        self.major_input = QLineEdit()
        self.major_input.setPlaceholderText('请输入专业名称')
        form_layout.addRow('所学专业:', self.major_input)
        
        # 21. 入学时间
        self.enrollment_time_input = QDateEdit()
        self.enrollment_time_input.setDate(QDate.currentDate().addYears(-4))
        self.enrollment_time_input.setCalendarPopup(True)
        form_layout.addRow('入学时间:', self.enrollment_time_input)
        
        # 22. 初检医院
        self.initial_hospital_input = QLineEdit()
        self.initial_hospital_input.setPlaceholderText('请输入初检医院')
        form_layout.addRow('初检医院:', self.initial_hospital_input)
        
        # 23. 初检结论
        self.initial_conclusion_input = QComboBox()
        self.initial_conclusion_input.addItems(['', '合格', '不合格', '待复查'])
        form_layout.addRow('初检结论:', self.initial_conclusion_input)
        
        # 24. 初检时间
        self.initial_time_input = QDateEdit()
        self.initial_time_input.setDate(QDate.currentDate())
        self.initial_time_input.setCalendarPopup(True)
        form_layout.addRow('初检时间:', self.initial_time_input)
        
        # 25. 体检结论
        self.physical_conclusion_input = QComboBox()
        self.physical_conclusion_input.addItems(['', '合格', '不合格', '待复查'])
        form_layout.addRow('体检结论:', self.physical_conclusion_input)
        
        # 26. 体检时间
        self.physical_time_input = QDateEdit()
        self.physical_time_input.setDate(QDate.currentDate())
        self.physical_time_input.setCalendarPopup(True)
        form_layout.addRow('体检时间:', self.physical_time_input)
        
        # 27. 体检不合格原因
        self.physical_disqualification_input = QLineEdit()
        self.physical_disqualification_input.setPlaceholderText('如体检不合格请填写原因')
        form_layout.addRow('体检不合格原因:', self.physical_disqualification_input)
        
        # 28. 主检医师意见
        self.chief_doctor_opinion_input = QLineEdit()
        self.chief_doctor_opinion_input.setPlaceholderText('请输入主检医师意见')
        form_layout.addRow('主检医师意见:', self.chief_doctor_opinion_input)
        
        # 29. 毕业时间
        self.graduation_time_input = QDateEdit()
        self.graduation_time_input.setDate(QDate.currentDate())
        self.graduation_time_input.setCalendarPopup(True)
        form_layout.addRow('毕业时间:', self.graduation_time_input)
        
        # 30. 连
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText('如：一连')
        form_layout.addRow('连:', self.company_input)
        
        # 31. 排
        self.platoon_input = QLineEdit()
        self.platoon_input.setPlaceholderText('如：一排')
        form_layout.addRow('排:', self.platoon_input)
        
        # 32. 班
        self.squad_input = QLineEdit()
        self.squad_input.setPlaceholderText('如：一班')
        form_layout.addRow('班:', self.squad_input)
        
        # 33. 带训班长信息
        self.squad_leader_input = QLineEdit()
        self.squad_leader_input.setPlaceholderText('请输入带训班长信息')
        form_layout.addRow('带训班长信息:', self.squad_leader_input)
        
        # 34. 在营状态
        self.camp_status_input = QComboBox()
        self.camp_status_input.addItems(['在营', '离营'])
        self.camp_status_input.setCurrentText('在营')  # 默认选择在营
        form_layout.addRow('在营状态:', self.camp_status_input)
        
        # 35. 离营时间
        self.leave_time_input = QDateEdit()
        self.leave_time_input.setDate(QDate.currentDate())
        self.leave_time_input.setCalendarPopup(True)
        form_layout.addRow('离营时间:', self.leave_time_input)
        
        # 36. 离营原因
        self.leave_reason_input = QLineEdit()
        self.leave_reason_input.setPlaceholderText('如有离营请填写原因')
        form_layout.addRow('离营原因:', self.leave_reason_input)
        
        # 设置滚动区域
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

    def save_youth(self):
        try:
            name = self.name_input.text().strip()
            gender = self.gender_input.currentText()
            id_card = self.id_card_input.text().strip()
            
            if not name or not gender or not id_card:
                QMessageBox.warning(self, '输入错误', '请填写必填字段！')
                return
            
            # 在营状态验证
            camp_status = self.camp_status_input.currentText()
            leave_time = self.leave_time_input.date().toString('yyyy-MM-dd') if camp_status == '离营' else ''
            leave_reason = self.leave_reason_input.text().strip()
            
            if camp_status == '在营':
                # 在营时，离营时间和离营原因必须为空
                if leave_reason:
                    QMessageBox.warning(self, '数据验证失败', 
                                      '当"在营状态"为"在营"时，"离营原因"必须为空。')
                    return
            elif camp_status == '离营':
                # 离营时，离营时间和离营原因必须不为空
                if not leave_reason:
                    QMessageBox.warning(self, '数据验证失败', 
                                      '当"在营状态"为"离营"时，"离营时间"和"离营原因"必须填写。')
                    return
            
            # 收集所有字段数据，按照insert_youth方法的36字段顺序
            youth_data = (
                id_card,  # 0: id_card
                name,     # 1: name
                gender,   # 2: gender
                self.birth_date_input.date().toString('yyyy-MM-dd'),  # 3: birth_date
                self.nation_input.text().strip(),  # 4: nation
                self.political_status_input.currentText(),  # 5: political_status
                self.religion_input.text().strip(),  # 6: religion
                self.native_place_input.text().strip(),  # 7: native_place
                self.education_level_input.currentText(),  # 8: education_level
                self.study_status_input.currentText(),  # 9: study_status
                self.study_type_input.currentText(),  # 10: study_type
                self.camp_entry_time_input.date().toString('yyyy-MM-dd'),  # 11: camp_entry_time
                self.recruitment_place_input.text().strip(),  # 12: recruitment_place
                self.residence_address_input.text().strip(),  # 13: residence_address
                self.household_address_input.text().strip(),  # 14: household_address
                self.postal_code_input.text().strip(),  # 15: postal_code
                self.personal_phone_input.text().strip(),  # 16: personal_phone
                self.family_phone_input.text().strip(),  # 17: family_phone
                self.school_input.text().strip(),  # 18: school
                self.major_input.text().strip(),  # 19: major
                self.enrollment_time_input.date().toString('yyyy-MM-dd'),  # 20: enrollment_time
                self.initial_hospital_input.text().strip(),  # 21: initial_hospital
                self.initial_conclusion_input.currentText(),  # 22: initial_conclusion
                self.initial_time_input.date().toString('yyyy-MM-dd'),  # 23: initial_time
                self.physical_conclusion_input.currentText(),  # 24: physical_conclusion
                self.physical_time_input.date().toString('yyyy-MM-dd'),  # 25: physical_time
                self.physical_disqualification_input.text().strip(),  # 26: physical_disqualification
                self.chief_doctor_opinion_input.text().strip(),  # 27: chief_doctor_opinion
                self.graduation_time_input.date().toString('yyyy-MM-dd'),  # 28: graduation_time
                self.company_input.text().strip(),  # 29: company
                self.platoon_input.text().strip(),  # 30: platoon
                self.squad_input.text().strip(),  # 31: squad
                self.squad_leader_input.text().strip(),  # 32: squad_leader
                camp_status,  # 33: camp_status
                leave_time,  # 34: leave_time
                leave_reason  # 35: leave_reason
            )
            
            # 保存到数据库
            result_id_card = self.db_manager.insert_youth(youth_data)
            
            QMessageBox.information(self, '添加成功', 
                                  f'青年信息已成功添加！\n\n'
                                  f'姓名：{name}\n'
                                  f'性别：{gender}\n'
                                  f'身份证号：{id_card}')
            
            # 发出数据更新信号
            self.data_updated.emit()
            
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, '添加失败', f'添加青年信息时发生错误：{str(e)}')