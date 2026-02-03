"""
青年详情对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
                             QPushButton, QTextBrowser, QMessageBox, QFileDialog,
                             QScrollArea, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QFrame, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import os


class YouthDetailDialog(QDialog):
    # 定义信号，当数据更新时发出
    data_updated = pyqtSignal()
    
    def __init__(self, db_manager, export_service, id_card, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.export_service = export_service
        self.id_card = id_card
        self.youth_data = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle('青年详细信息')
        self.setGeometry(150, 50, 1000, 700)
        # 允许最大化和调整大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        layout = QVBoxLayout()
        
        # 标题栏
        header_layout = QHBoxLayout()
        self.title_label = QLabel('青年详细信息')
        self.title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        export_btn = QPushButton('导出PDF')
        export_btn.clicked.connect(self.export_pdf)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # 标签页
        self.tabs = QTabWidget()
        self.create_tabs()
        layout.addWidget(self.tabs)
        
        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def create_tabs(self):
        """创建标签页"""
        tab_configs = [
            ('基本信息', self.create_basic_info_tab),
            ('病史筛查情况', self.create_medical_screening_tab),
            ('体检情况统计表', self.create_physical_examination_tab),
            ('每日情况统计', self.create_daily_stat_tab),
            ('政治考核情况统计', self.create_political_assessment_tab),
            ('入营点验情况', self.create_camp_verification_tab)
        ]
        
        for tab_name, create_func in tab_configs:
            widget = create_func()
            self.tabs.addTab(widget, tab_name)
    
    def create_basic_info_tab(self):
        """创建基本信息标签页 - 可编辑版本"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        form_layout = QFormLayout()
        
        self.edit_fields = {}
        
        field_definitions = [
            ('序号', 'id', False),
            ('姓名', 'name', False),  # 姓名不可修改
            ('公民身份号码', 'id_card', False),  # 公民身份号码不可修改
            ('性别', 'gender', True),
            ('出生日期', 'birth_date', True),
            ('民族', 'nation', True),
            ('政治面貌', 'political_status', True),
            ('宗教信仰', 'religion', True),
            ('籍贯', 'native_place', True),
            ('文化程度', 'education_level', True),
            ('学业情况', 'study_status', True),
            ('学习类型', 'study_type', True),
            ('入营时间', 'camp_entry_time', True),
            ('应征地', 'recruitment_place', True),
            ('经常居住地址', 'residence_address', True),
            ('户籍所在地', 'household_address', True),
            ('邮编', 'postal_code', True),
            ('本人电话', 'personal_phone', True),
            ('家庭电话', 'family_phone', True),
            ('毕业(就读)学校', 'school', True),
            ('所学专业', 'major', True),
            ('入学时间', 'enrollment_time', True),
            ('初检医院', 'initial_hospital', True),
            ('初检结论', 'initial_conclusion', True),
            ('初检时间', 'initial_time', True),
            ('体检结论', 'physical_conclusion', True),
            ('体检时间', 'physical_time', True),
            ('体检不合格原因', 'physical_disqualification', True),
            ('主检医师意见', 'chief_doctor_opinion', True),
            ('毕业时间', 'graduation_time', True),
            ('连', 'company', True),
            ('排', 'platoon', True),
            ('班', 'squad', True),
            ('带训班长信息', 'squad_leader', True),
            ('在营状态', 'camp_status', True),
            ('离营时间', 'leave_time', True),
            ('离营原因', 'leave_reason', True)
        ]
        
        for label, field_name, editable in field_definitions:
            # 对于长文本字段使用QTextEdit
            if field_name in ['physical_disqualification', 'chief_doctor_opinion']:
                edit_widget = QTextEdit()
                edit_widget.setMaximumHeight(80)
            elif field_name == 'gender':
                # 性别使用下拉选项
                edit_widget = QComboBox()
                edit_widget.addItems(['男', '女'])
                edit_widget.setMaxVisibleItems(2)
                edit_widget.setStyleSheet("""
                    QComboBox {
                        padding: 5px;
                    }
                    QComboBox QAbstractItemView {
                        min-height: 60px;
                    }
                    QComboBox QAbstractItemView::item {
                        height: 30px;
                        padding: 5px;
                    }
                """)
            elif field_name == 'camp_status':
                # 在营状态使用下拉选项
                edit_widget = QComboBox()
                edit_widget.addItems(['在营', '离营'])
                edit_widget.setMaxVisibleItems(2)
                edit_widget.setStyleSheet("""
                    QComboBox {
                        padding: 5px;
                    }
                    QComboBox QAbstractItemView {
                        min-height: 60px;
                    }
                    QComboBox QAbstractItemView::item {
                        height: 30px;
                        padding: 5px;
                    }
                """)
            else:
                edit_widget = QLineEdit()
            
            # 对于姓名和身份证号，设置为只读而不是禁用，这样可以复制
            if field_name in ['name', 'id_card']:
                if isinstance(edit_widget, QLineEdit):
                    edit_widget.setReadOnly(True)
                    edit_widget.setStyleSheet("background-color: #F0F0F0;")
            else:
                edit_widget.setEnabled(editable)
                if not editable:
                    edit_widget.setStyleSheet("background-color: #F0F0F0;")
            
            self.edit_fields[field_name] = edit_widget
            form_layout.addRow(label + ':', edit_widget)
        
        scroll_widget.setLayout(form_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存修改')
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
        save_btn.clicked.connect(self.save_basic_info)
        
        cancel_btn = QPushButton('取消修改')
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
        cancel_btn.clicked.connect(self.load_basic_info)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_document_tab(self, table_name):
        """创建文档类标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['文件路径', '日期', '备注', '操作'])
        
        setattr(self, f'{table_name}_table', table)
        layout.addWidget(table)
        
        # 上传按钮
        upload_btn = QPushButton('上传新文档')
        upload_btn.clicked.connect(lambda: self.upload_document(table_name))
        layout.addWidget(upload_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_medical_screening_tab(self):
        """创建病史筛查情况标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建滚动区域来容纳所有记录
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.medical_screening_layout = QVBoxLayout()
        
        scroll_widget.setLayout(self.medical_screening_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 全选复选框
        self.medical_select_all_checkbox = QCheckBox('全选')
        self.medical_select_all_checkbox.stateChanged.connect(self.toggle_medical_select_all)
        button_layout.addWidget(self.medical_select_all_checkbox)
        
        button_layout.addStretch()
        
        add_btn = QPushButton('添加筛查记录')
        add_btn.clicked.connect(self.add_medical_screening)
        button_layout.addWidget(add_btn)
        
        batch_delete_btn = QPushButton('批量删除')
        batch_delete_btn.clicked.connect(self.batch_delete_medical_screening)
        button_layout.addWidget(batch_delete_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_medical_screening_data)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_visit_survey_tab(self):
        """创建走访调查情况标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建滚动区域来容纳所有记录
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.visit_survey_layout = QVBoxLayout()
        
        scroll_widget.setLayout(self.visit_survey_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 全选复选框
        self.visit_select_all_checkbox = QCheckBox('全选')
        self.visit_select_all_checkbox.stateChanged.connect(self.toggle_visit_select_all)
        button_layout.addWidget(self.visit_select_all_checkbox)
        
        button_layout.addStretch()
        
        add_btn = QPushButton('添加信息')
        add_btn.clicked.connect(self.add_visit_survey)
        button_layout.addWidget(add_btn)
        
        export_btn = QPushButton('导出数据')
        export_btn.clicked.connect(self.export_visit_survey_data)
        button_layout.addWidget(export_btn)
        
        batch_delete_btn = QPushButton('批量删除')
        batch_delete_btn.clicked.connect(self.batch_delete_visit_survey)
        button_layout.addWidget(batch_delete_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_visit_survey_data)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_daily_stat_tab(self):
        """创建每日情况统计标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建滚动区域来容纳所有记录
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.daily_stat_layout = QVBoxLayout()
        
        scroll_widget.setLayout(self.daily_stat_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 全选复选框
        self.daily_select_all_checkbox = QCheckBox('全选')
        self.daily_select_all_checkbox.stateChanged.connect(self.toggle_daily_select_all)
        button_layout.addWidget(self.daily_select_all_checkbox)
        
        button_layout.addStretch()
        
        add_btn = QPushButton('添加记录')
        add_btn.clicked.connect(self.add_daily_stat)
        button_layout.addWidget(add_btn)
        
        batch_delete_btn = QPushButton('批量删除')
        batch_delete_btn.clicked.connect(self.batch_delete_daily_stat)
        button_layout.addWidget(batch_delete_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_exception_statistics_tab(self):
        """创建异常情况统计标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(['姓名', '性别', '公民证件号码', '思想', '身体', '精神', '其他', '日期'])
        
        # 设置列宽度
        table.setColumnWidth(0, 80)    # 姓名
        table.setColumnWidth(1, 60)    # 性别
        table.setColumnWidth(2, 150)   # 公民证件号码
        table.setColumnWidth(3, 60)    # 思想
        table.setColumnWidth(4, 60)    # 身体
        table.setColumnWidth(5, 60)    # 精神
        table.setColumnWidth(6, 60)    # 其他
        table.setColumnWidth(7, 100)   # 日期
        
        self.exception_statistics_table = table
        layout.addWidget(table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_exception_statistics_data)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_table_tab(self, table_name, headers):
        """创建通用表格标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        setattr(self, f'{table_name}_table', table)
        layout.addWidget(table)
        
        widget.setLayout(layout)
        return widget
    
    def load_data(self):
        """加载所有数据"""
        try:
            self.youth_data = self.db_manager.get_youth_by_id_card(self.id_card)
            
            if not self.youth_data:
                QMessageBox.warning(self, '错误', '未找到青年信息')
                return
            
            self.title_label.setText(f'青年详细信息 - {self.youth_data.name}')
            
            self.load_basic_info()
            self.load_medical_screening_data()
            self.load_physical_examination_data()
            self.load_daily_stat_data()
            self.load_political_assessment_data()
            self.load_camp_verification_data()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载数据时发生错误: {str(e)}')
    
    def load_basic_info(self):
        """加载基本信息到可编辑输入框"""
        if not self.youth_data or not hasattr(self, 'edit_fields'):
            return
        
        field_mapping = {
            'id': self.youth_data.id,
            'name': self.youth_data.name,
            'id_card': self.youth_data.id_card,
            'gender': self.youth_data.gender,
            'birth_date': getattr(self.youth_data, 'birth_date', ''),
            'nation': self.youth_data.nation,
            'political_status': self.youth_data.political_status,
            'religion': getattr(self.youth_data, 'religion', ''),
            'native_place': getattr(self.youth_data, 'native_place', ''),
            'education_level': self.youth_data.education_level,
            'study_status': self.youth_data.study_status,
            'study_type': self.youth_data.study_type,
            'camp_entry_time': getattr(self.youth_data, 'camp_entry_time', ''),
            'recruitment_place': getattr(self.youth_data, 'recruitment_place', ''),
            'residence_address': self.youth_data.residence_address,
            'household_address': self.youth_data.household_address,
            'postal_code': getattr(self.youth_data, 'postal_code', ''),
            'personal_phone': getattr(self.youth_data, 'personal_phone', getattr(self.youth_data, 'phone', '')),
            'family_phone': getattr(self.youth_data, 'family_phone', getattr(self.youth_data, 'parent_phone', '')),
            'school': self.youth_data.school,
            'major': self.youth_data.major,
            'enrollment_time': getattr(self.youth_data, 'enrollment_time', ''),
            'initial_hospital': getattr(self.youth_data, 'initial_hospital', ''),
            'initial_conclusion': getattr(self.youth_data, 'initial_conclusion', ''),
            'initial_time': getattr(self.youth_data, 'initial_time', ''),
            'physical_conclusion': getattr(self.youth_data, 'physical_conclusion', ''),
            'physical_time': getattr(self.youth_data, 'physical_time', ''),
            'physical_disqualification': getattr(self.youth_data, 'physical_disqualification', ''),
            'chief_doctor_opinion': getattr(self.youth_data, 'chief_doctor_opinion', ''),
            'graduation_time': getattr(self.youth_data, 'graduation_time', ''),
            'company': self.youth_data.company,
            'platoon': self.youth_data.platoon,
            'squad': self.youth_data.squad,
            'squad_leader': self.youth_data.squad_leader,
            'camp_status': self.youth_data.camp_status,
            'leave_time': self.youth_data.leave_time,
            'leave_reason': getattr(self.youth_data, 'leave_reason', getattr(self.youth_data, 'situation_note', ''))
        }
        
        for field_name, value in field_mapping.items():
            if field_name in self.edit_fields:
                widget = self.edit_fields[field_name]
                if isinstance(widget, QComboBox):
                    # 处理下拉框（性别）
                    index = widget.findText(str(value or ''))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif hasattr(widget, 'setPlainText'):
                    widget.setPlainText(str(value or ''))
                else:
                    widget.setText(str(value or ''))
    
    def save_basic_info(self):
        """保存基本信息修改（更新现有记录）"""
        try:
            from utils.validators import validate_phone
            
            # 从输入框获取数据
            updated_data = {}
            for field_name, widget in self.edit_fields.items():
                if field_name == 'id':
                    continue
                
                if isinstance(widget, QComboBox):
                    # 处理下拉框（性别、政治面貌等）
                    value = widget.currentText().strip()
                elif hasattr(widget, 'toPlainText'):
                    value = widget.toPlainText().strip()
                else:
                    value = widget.text().strip()
                
                updated_data[field_name] = value
            
            # 在营状态验证
            camp_status = updated_data.get('camp_status', '')
            leave_time = updated_data.get('leave_time', '')
            leave_reason = updated_data.get('leave_reason', '')
            
            if camp_status == '在营':
                # 在营时，离营时间和离营原因必须为空
                if leave_time or leave_reason:
                    QMessageBox.warning(self, '数据验证失败', 
                                      '当"在营状态"为"在营"时，"离营时间"和"离营原因"必须为空。')
                    return
            elif camp_status == '离营':
                # 离营时，离营时间和离营原因必须不为空
                if not leave_time or not leave_reason:
                    QMessageBox.warning(self, '数据验证失败', 
                                      '当"在营状态"为"离营"时，"离营时间"和"离营原因"必须填写。')
                    return
            elif camp_status and camp_status not in ['在营', '离营']:
                QMessageBox.warning(self, '数据验证失败', 
                                  '"在营状态"只能为"在营"或"离营"。')
                return
            
            # 验证电话号码（如果填写了）
            personal_phone = updated_data.get('personal_phone', '')
            if personal_phone:
                is_valid, error_msg = validate_phone(personal_phone)
                if not is_valid:
                    QMessageBox.warning(self, '验证错误', f'本人电话验证失败：{error_msg}')
                    return
            
            # 验证家庭电话（如果填写了）
            family_phone = updated_data.get('family_phone', '')
            if family_phone:
                # 家庭电话可能包含多个号码，用逗号分隔
                family_phones = family_phone.replace('，', ',').split(',')
                for i, p in enumerate(family_phones, 1):
                    p = p.strip()
                    if p:
                        is_valid, error_msg = validate_phone(p)
                        if not is_valid:
                            QMessageBox.warning(self, '验证错误', f'家庭电话{i}验证失败：{error_msg}')
                            return
            
            # 使用UPDATE语句更新现有记录
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 构建UPDATE SQL语句，包含所有可编辑字段
            cursor.execute('''
                UPDATE youth SET
                    gender=?, birth_date=?, nation=?, political_status=?, religion=?,
                    native_place=?, education_level=?, study_status=?, study_type=?,
                    camp_entry_time=?, recruitment_place=?, residence_address=?,
                    household_address=?, postal_code=?, personal_phone=?, family_phone=?,
                    school=?, major=?, enrollment_time=?, initial_hospital=?,
                    initial_conclusion=?, initial_time=?, physical_conclusion=?,
                    physical_time=?, physical_disqualification=?, chief_doctor_opinion=?,
                    graduation_time=?, company=?, platoon=?, squad=?, squad_leader=?,
                    camp_status=?, leave_time=?, leave_reason=?
                WHERE id_card=?
            ''', (
                updated_data.get('gender', ''),
                updated_data.get('birth_date', ''),
                updated_data.get('nation', ''),
                updated_data.get('political_status', ''),
                updated_data.get('religion', ''),
                updated_data.get('native_place', ''),
                updated_data.get('education_level', ''),
                updated_data.get('study_status', ''),
                updated_data.get('study_type', ''),
                updated_data.get('camp_entry_time', ''),
                updated_data.get('recruitment_place', ''),
                updated_data.get('residence_address', ''),
                updated_data.get('household_address', ''),
                updated_data.get('postal_code', ''),
                updated_data.get('personal_phone', ''),
                updated_data.get('family_phone', ''),
                updated_data.get('school', ''),
                updated_data.get('major', ''),
                updated_data.get('enrollment_time', ''),
                updated_data.get('initial_hospital', ''),
                updated_data.get('initial_conclusion', ''),
                updated_data.get('initial_time', ''),
                updated_data.get('physical_conclusion', ''),
                updated_data.get('physical_time', ''),
                updated_data.get('physical_disqualification', ''),
                updated_data.get('chief_doctor_opinion', ''),
                updated_data.get('graduation_time', ''),
                updated_data.get('company', ''),
                updated_data.get('platoon', ''),
                updated_data.get('squad', ''),
                updated_data.get('squad_leader', ''),
                updated_data.get('camp_status', ''),
                updated_data.get('leave_time', ''),
                updated_data.get('leave_reason', ''),
                self.id_card  # WHERE条件：使用身份证号定位记录
            ))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, '成功', '基本信息已保存')
            
            # 重新加载数据
            self.youth_data = self.db_manager.get_youth_by_id_card(self.id_card)
            self.load_basic_info()
            
            # 发出信号通知主窗口刷新
            self.data_updated.emit()
            
            if self.parent():
                if hasattr(self.parent(), 'refresh_table_data'):
                    self.parent().refresh_table_data()
                elif hasattr(self.parent(), 'load_all_youth_detailed'):
                    self.parent().load_all_youth_detailed()
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存基本信息时发生错误：{str(e)}')
            
        except Exception as e:
            QMessageBox.warning(self, '保存失败', f'保存基本信息时发生错误: {str(e)}')
    
    def load_document_data(self, table_name):
        """加载文档数据"""
        try:
            # 使用 id_card 查询关联数据
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE youth_id_card=?", (self.id_card,))
            data = cursor.fetchall()
            conn.close()
            
            table = getattr(self, f'{table_name}_table')
            
            table.setRowCount(len(data))
            for row, record in enumerate(data):
                table.setItem(row, 0, QTableWidgetItem(record[2] or ''))
                table.setItem(row, 1, QTableWidgetItem(record[3] or ''))
                table.setItem(row, 2, QTableWidgetItem(record[4] or ''))
                
                view_btn = QPushButton('查看')
                view_btn.clicked.connect(lambda checked, path=record[2]: self.view_file(path))
                table.setCellWidget(row, 3, view_btn)
        except Exception as e:
            pass
    
    def load_daily_stat_data(self):
        """加载每日情况统计数据"""
        try:
            # 获取当前青年的每日情况数据
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, youth_id, record_date, mood, physical_condition, mental_state, training, management, notes
                FROM daily_stat 
                WHERE youth_id = (SELECT id FROM youth WHERE id_card = ?)
                ORDER BY record_date DESC
            ''', (self.id_card,))
            records = cursor.fetchall()
            conn.close()
            
            self.display_daily_stat_records(records)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载每日情况统计数据时发生错误：{str(e)}")
    
    def display_daily_stat_records(self, records):
        """显示每日情况统计记录"""
        try:
            # 清空现有布局
            for i in reversed(range(self.daily_stat_layout.count())):
                child = self.daily_stat_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
                    child.deleteLater()  # 确保完全删除
            
            # 重置记录列表
            self.daily_stat_records = []  # 存储记录引用
            
            for record in records:
                # record格式: (id, youth_id, record_date, mood, physical_condition, mental_state, notes)
                
                # 创建记录容器
                record_frame = QFrame()
                record_frame.setFrameStyle(QFrame.Shape.Box)
                record_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        margin: 5px;
                        padding: 10px;
                        background-color: #f9f9f9;
                    }
                """)
                
                record_layout = QVBoxLayout()
                
                # 第一行：基本信息和操作按钮
                info_layout = QHBoxLayout()
                
                # 选择框
                checkbox = QCheckBox()
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border: 2px solid #7F8C8D;
                        border-radius: 2px;
                        background-color: white;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #3498DB;
                        background-color: #ECF0F1;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #3498DB;
                        border-color: #2980B9;
                    }
                """)
                info_layout.addWidget(checkbox)
                
                # 基本信息
                info_text = f"日期: {record[2] or ''} | 思想: {record[3] or ''} | 身体: {record[4] or ''} | 精神: {record[5] or ''} | 训练: {record[6] or '正常'} | 管理: {record[7] or '正常'}"
                info_label = QLabel(info_text)
                info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                info_layout.addWidget(info_label)
                
                info_layout.addStretch()
                
                # 操作按钮
                edit_btn = QPushButton('编辑')
                edit_btn.clicked.connect(lambda checked, record_data=record: self.edit_daily_stat_by_record(record_data))
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                """)
                info_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton('删除')
                delete_btn.clicked.connect(lambda checked, record_data=record: self.delete_single_daily_stat(record_data))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
                info_layout.addWidget(delete_btn)
                
                record_layout.addLayout(info_layout)
                
                # 第二行：备注信息（如果有）
                if record[8]:  # notes (现在是索引8)
                    notes_layout = QVBoxLayout()
                    notes_layout.setSpacing(0)
                    notes_layout.setContentsMargins(0, 5, 0, 0)
                    
                    notes_label = QLabel("备注:")
                    notes_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #666;")
                    notes_layout.addWidget(notes_label)
                    
                    notes_content = QLabel(record[8])
                    notes_content.setWordWrap(True)
                    notes_content.setStyleSheet("""
                        QLabel {
                            background-color: white;
                            border: 1px solid #ddd;
                            border-radius: 3px;
                            padding: 5px;
                            font-size: 12px;
                        }
                    """)
                    notes_layout.addWidget(notes_content)
                    
                    record_layout.addLayout(notes_layout)
                
                record_frame.setLayout(record_layout)
                self.daily_stat_layout.addWidget(record_frame)
                
                # 存储记录和复选框的引用
                self.daily_stat_records.append({
                    'record': record,
                    'checkbox': checkbox,
                    'frame': record_frame
                })
            
            # 添加弹性空间，将所有记录推到顶部
            self.daily_stat_layout.addStretch()
            
            # 如果没有记录，显示提示
            if not records:
                no_data_label = QLabel('暂无每日情况记录')
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: gray; font-size: 16px; padding: 50px;")
                self.daily_stat_layout.addWidget(no_data_label)
            
            # 重置全选复选框状态
            if hasattr(self, 'daily_select_all_checkbox'):
                self.daily_select_all_checkbox.setChecked(False)
            
        except Exception as e:
            QMessageBox.warning(self, "显示错误", f"显示每日情况记录时发生错误：{str(e)}")
    
    def load_table_data(self, table_name, headers):
        """加载表格数据"""
        try:
            # 使用 id_card 查询关联数据
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE youth_id_card=?", (self.id_card,))
            data = cursor.fetchall()
            conn.close()
            
            table = getattr(self, f'{table_name}_table')
            
            table.setRowCount(len(data))
            for row, record in enumerate(data):
                for col in range(len(headers)):
                    value = record[col + 2] if col + 2 < len(record) else ''
                    table.setItem(row, col, QTableWidgetItem(str(value or '')))
        except Exception as e:
            pass
    
    def upload_document(self, table_name):
        """上传文档"""
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文档', '', 
                                                   'All Files (*.pdf *.jpg *.png *.doc *.docx)')
        if not file_path:
            return
        
        # 这里应该复制文件到程序目录
        from services.import_service import ImportService
        import_service = ImportService(self.db_manager)
        
        module_map = {
            'medical_history': 'medical',
            'town_interview': 'town',
            'leader_interview': 'leader'
        }
        
        module_type = module_map.get(table_name)
        if module_type and import_service.save_scanned_document(self.id_card, module_type, file_path):
            QMessageBox.information(self, '成功', '文档上传成功')
            self.load_document_data(table_name)
        else:
            QMessageBox.warning(self, '失败', '文档上传失败')
    
    def view_file(self, file_path):
        """查看文件"""
        if file_path and os.path.exists(file_path):
            os.startfile(file_path)
        else:
            QMessageBox.warning(self, '提示', '文件不存在')
    
    def open_daily_record_dialog(self):
        """打开每日记录对话框"""
        from ui.daily_record_dialog import DailyRecordDialog
        dialog = DailyRecordDialog(self.db_manager, self.id_card, self.youth_data.name, self)
        dialog.exec_()
        self.load_daily_stat_data()
    
    def export_pdf(self):
        """导出PDF - 导出该青年的所有详细信息"""
        file_path, _ = QFileDialog.getSaveFileName(self, '保存PDF', 
                                                   f'{self.youth_data.name}_完整信息.pdf',
                                                   'PDF Files (*.pdf)')
        if file_path:
            success, msg = self.export_service.export_youth_to_pdf(self.id_card, file_path)
            if success:
                QMessageBox.information(self, '成功', msg)
            else:
                QMessageBox.warning(self, '失败', msg)
    
    def load_visit_survey_data(self):
        """加载走访调查情况数据到表格"""
        try:
            # 获取当前青年的走访调查数据
            records = self.db_manager.search_visit_surveys(id_card=self.id_card)
            self.display_visit_survey_records(records)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载走访调查情况数据时发生错误：{str(e)}")
    
    def display_visit_survey_records(self, records):
        """显示走访调查记录"""
        try:
            # 清空现有布局
            for i in reversed(range(self.visit_survey_layout.count())):
                child = self.visit_survey_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            self.visit_survey_records = []  # 存储记录引用
            
            for record in records:
                # record格式: (id, youth_id_card, youth_name, gender, survey_date, thoughts, spirit, created_at)
                
                # 创建记录容器
                record_frame = QFrame()
                record_frame.setFrameStyle(QFrame.Shape.Box)
                record_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        margin: 5px;
                        padding: 10px;
                        background-color: #f9f9f9;
                    }
                """)
                
                record_layout = QVBoxLayout()
                
                # 第一行：基本信息和操作按钮
                info_layout = QHBoxLayout()
                
                # 选择框
                checkbox = QCheckBox()
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border: 2px solid #7F8C8D;
                        border-radius: 2px;
                        background-color: white;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #3498DB;
                        background-color: #ECF0F1;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #3498DB;
                        border-color: #2980B9;
                    }
                """)
                info_layout.addWidget(checkbox)
                
                # 基本信息
                info_text = f"日期: {record[4] or ''} | 思想: {record[5] or ''} | 精神: {record[6] or ''}"
                info_label = QLabel(info_text)
                info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                info_layout.addWidget(info_label)
                
                info_layout.addStretch()
                
                # 操作按钮
                edit_btn = QPushButton('编辑信息')
                edit_btn.clicked.connect(lambda checked, record_data=record: self.edit_visit_survey_by_record(record_data))
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                """)
                info_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton('删除')
                delete_btn.clicked.connect(lambda checked, record_data=record: self.delete_single_visit_survey(record_data))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
                info_layout.addWidget(delete_btn)
                
                record_layout.addLayout(info_layout)
                
                # 第二行：图片
                image_layout = QHBoxLayout()
                image_layout.addStretch()  # 左侧留白
                
                try:
                    image_data = self.db_manager.get_visit_survey_image(record[0])
                    
                    # 计算图片大小（界面宽度的60%）
                    dialog_width = self.width() if self.width() > 0 else 1000  # 默认宽度
                    target_width = int(dialog_width * 0.6)
                    target_height = int(target_width * 0.75)  # 默认4:3比例
                    
                    if image_data:
                        # 创建图片标签
                        image_label = QLabel()
                        pixmap = QPixmap()
                        pixmap.loadFromData(image_data)
                        
                        # 根据原始图片比例计算高度
                        original_width = pixmap.width()
                        original_height = pixmap.height()
                        if original_width > 0:
                            target_height = int(target_width * original_height / original_width)
                        
                        # 缩放图片
                        scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        image_label.setPixmap(scaled_pixmap)
                        image_label.setAlignment(Qt.AlignCenter)
                        image_label.setStyleSheet("""
                            QLabel {
                                border: 2px solid #ccc;
                                border-radius: 5px;
                                padding: 5px;
                                background-color: white;
                                cursor: pointer;
                            }
                            QLabel:hover {
                                border-color: #3498DB;
                            }
                        """)
                        
                        # 添加点击查看大图功能
                        image_label.mousePressEvent = lambda event, rid=record[0]: self.view_visit_survey_image(rid)
                        image_layout.addWidget(image_label)
                    else:
                        no_image_label = QLabel('无图片')
                        no_image_label.setAlignment(Qt.AlignCenter)
                        no_image_label.setStyleSheet(f"""
                            QLabel {{
                                color: gray;
                                border: 2px dashed #ccc;
                                border-radius: 5px;
                                padding: 20px;
                                background-color: white;
                                min-width: {target_width}px;
                                min-height: {target_height}px;
                            }}
                        """)
                        image_layout.addWidget(no_image_label)
                except Exception as e:
                    # 计算错误标签大小
                    dialog_width = self.width() if self.width() > 0 else 1000
                    target_width = int(dialog_width * 0.6)
                    target_height = int(target_width * 0.75)
                    
                    error_label = QLabel('图片加载失败')
                    error_label.setAlignment(Qt.AlignCenter)
                    error_label.setStyleSheet(f"""
                        QLabel {{
                            color: red;
                            border: 2px solid #E74C3C;
                            border-radius: 5px;
                            padding: 20px;
                            background-color: white;
                            min-width: {target_width}px;
                            min-height: {target_height}px;
                        }}
                    """)
                    image_layout.addWidget(error_label)
                
                image_layout.addStretch()  # 右侧留白
                record_layout.addLayout(image_layout)
                
                record_frame.setLayout(record_layout)
                self.visit_survey_layout.addWidget(record_frame)
                
                # 存储记录和复选框的引用
                self.visit_survey_records.append({
                    'record': record,
                    'checkbox': checkbox,
                    'frame': record_frame
                })
            
            # 如果没有记录，显示提示
            if not records:
                no_data_label = QLabel('暂无走访调查记录')
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: gray; font-size: 16px; padding: 50px;")
                self.visit_survey_layout.addWidget(no_data_label)
            
        except Exception as e:
            QMessageBox.warning(self, "显示错误", f"显示走访调查记录时发生错误：{str(e)}")
    
    def toggle_visit_select_all(self, state):
        """走访调查全选/取消全选"""
        is_checked = (state == Qt.CheckState.Checked.value)
        if hasattr(self, 'visit_survey_records'):
            for record_info in self.visit_survey_records:
                record_info['checkbox'].setChecked(is_checked)
    
    def add_visit_survey(self):
        """添加走访调查记录"""
        try:
            from ui.visit_survey_dialog import VisitSurveyDialog
            # 传递当前青年的信息，确保姓名、性别、身份证号不可更改
            dialog = VisitSurveyDialog(self.db_manager, self, None, self.youth_data)
            if dialog.exec_():
                self.load_visit_survey_data()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开添加走访调查对话框时发生错误: {str(e)}')
    
    def edit_visit_survey_by_record(self, record_data):
        """通过记录数据编辑走访调查记录"""
        try:
            from ui.visit_survey_dialog import VisitSurveyDialog
            # 传递记录数据和青年数据，确保姓名、性别、身份证号不可更改
            dialog = VisitSurveyDialog(self.db_manager, self, record_data, self.youth_data)
            if dialog.exec_():
                self.load_visit_survey_data()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'编辑走访调查记录时发生错误: {str(e)}')
    
    def delete_single_visit_survey(self, record_data):
        """删除单个走访调查记录"""
        try:
            reply = QMessageBox.question(self, '确认删除', 
                                       f'确定要删除 {record_data[2]} 的走访调查记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.db_manager.delete_visit_survey(record_data[0])
                if success:
                    QMessageBox.information(self, '删除成功', '记录已删除')
                    self.load_visit_survey_data()
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除记录')
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'删除走访调查记录时发生错误: {str(e)}')
    
    def batch_delete_visit_survey(self):
        """批量删除走访调查记录"""
        try:
            selected_records = []
            if hasattr(self, 'visit_survey_records'):
                for record_info in self.visit_survey_records:
                    if record_info['checkbox'].isChecked():
                        selected_records.append(record_info['record'][0])  # 记录ID
            
            if not selected_records:
                QMessageBox.warning(self, '提示', '请先选择要删除的记录')
                return
            
            reply = QMessageBox.question(self, '确认删除', 
                                       f'确定要删除选中的 {len(selected_records)} 条记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                deleted_count = 0
                for record_id in selected_records:
                    if self.db_manager.delete_visit_survey(record_id):
                        deleted_count += 1
                
                # 取消全选状态
                if hasattr(self, 'visit_select_all_checkbox'):
                    self.visit_select_all_checkbox.setChecked(False)
                
                self.load_visit_survey_data()
                
                if deleted_count > 0:
                    QMessageBox.information(self, '删除成功', f'成功删除 {deleted_count} 条记录')
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除任何记录')
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'批量删除走访调查记录时发生错误: {str(e)}')
    
    def view_visit_survey_image(self, record_id):
        """查看走访调查图片"""
        try:
            image_data = self.db_manager.get_visit_survey_image(record_id)
            if image_data:
                from ui.image_viewer_dialog import ImageViewerDialog
                dialog = ImageViewerDialog(image_data, "走访调查图片", self)
                dialog.exec_()
            else:
                QMessageBox.information(self, '提示', '该记录没有图片')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'查看图片时发生错误: {str(e)}')
    
    def export_visit_survey_data(self):
        """导出走访调查数据"""
        try:
            from datetime import datetime
            import os
            
            # 获取选中的记录
            selected_records = []
            if hasattr(self, 'visit_survey_records'):
                for record_info in self.visit_survey_records:
                    if record_info['checkbox'].isChecked():
                        selected_records.append(record_info['record'])
            
            # 如果没有选中记录，导出当前青年的所有记录
            if not selected_records:
                selected_records = self.db_manager.search_visit_surveys(id_card=self.id_card)
            
            if not selected_records:
                QMessageBox.warning(self, '提示', '没有数据可导出')
                return
            
            # 选择保存位置
            timestamp = datetime.now().strftime("%Y%m%d")
            default_name = f'走访调查情况_{timestamp}_导出'
            
            save_dir = QFileDialog.getExistingDirectory(self, '选择导出位置', default_name)
            if not save_dir:
                return
            
            # 创建导出目录
            export_dir = os.path.join(save_dir, default_name)
            os.makedirs(export_dir, exist_ok=True)
            
            # 导出Excel和图片
            success, message = self.export_service.export_visit_surveys_with_images(
                selected_records, export_dir
            )
            
            if success:
                QMessageBox.information(self, '导出成功', message)
            else:
                QMessageBox.warning(self, '导出失败', message)
                
        except Exception as e:
            QMessageBox.warning(self, '导出错误', f'导出走访调查数据时发生错误: {str(e)}')

    def load_medical_screening_data(self):
        """加载病史筛查情况数据"""
        try:
            # 获取当前青年的病史筛查数据
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, youth_id_card, name, gender, id_card, 
                       screening_result, screening_date, remark, physical_status, mental_status
                FROM medical_screening 
                WHERE youth_id_card=?
                ORDER BY screening_date DESC
            ''', (self.id_card,))
            records = cursor.fetchall()
            conn.close()
            
            self.display_medical_screening_records(records)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载病史筛查情况数据时发生错误：{str(e)}")
    
    def display_medical_screening_records(self, records):
        """显示病史筛查记录"""
        try:
            # 清空现有布局
            for i in reversed(range(self.medical_screening_layout.count())):
                child = self.medical_screening_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            self.medical_screening_records = []  # 存储记录引用
            
            for record in records:
                # record格式: (id, youth_id_card, name, gender, id_card, screening_result, screening_date, remark, physical_status, mental_status)
                
                physical_status = str(record[8] if len(record) > 8 else '') or ''
                mental_status = str(record[9] if len(record) > 9 else '') or ''
                
                # 创建记录容器
                record_frame = QFrame()
                record_frame.setFrameStyle(QFrame.Shape.Box)
                record_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        margin: 5px;
                        padding: 10px;
                        background-color: #f9f9f9;
                    }
                """)
                
                record_layout = QVBoxLayout()
                record_layout.setSpacing(0)
                
                # 第一行：基本信息和操作按钮
                info_layout = QHBoxLayout()
                
                # 选择框
                checkbox = QCheckBox()
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border: 2px solid #7F8C8D;
                        border-radius: 2px;
                        background-color: white;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #3498DB;
                        background-color: #ECF0F1;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #3498DB;
                        border-color: #2980B9;
                    }
                """)
                info_layout.addWidget(checkbox)
                
                # 基本信息
                remark_text = f" | 备注: {record[7]}" if len(record) > 7 and record[7] else ""
                info_text = f"筛查日期: {record[6] or ''} | 身体状况: {physical_status} | 精神状况: {mental_status}{remark_text}"
                info_label = QLabel(info_text)
                info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                info_layout.addWidget(info_label)
                
                info_layout.addStretch()
                
                # 操作按钮
                edit_btn = QPushButton('编辑')
                edit_btn.clicked.connect(lambda checked, record_data=record: self.edit_medical_screening_by_record(record_data))
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                """)
                info_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton('删除')
                delete_btn.clicked.connect(lambda checked, record_data=record: self.delete_single_medical_screening(record_data))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
                info_layout.addWidget(delete_btn)
                
                record_layout.addLayout(info_layout)
                
                # 第二行：筛查情况详细内容
                screening_layout = QVBoxLayout()
                screening_layout.setSpacing(0)
                screening_layout.setContentsMargins(0, 0, 0, 0)
                
                # 筛查情况标签
                screening_label = QLabel("筛查情况:")
                screening_label.setWordWrap(False)
                screening_label.setFixedHeight(25)
                screening_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold;
                        font-size: 14px;
                        padding: 0px;
                        background-color: transparent;
                        border: none;
                    }
                """)
                screening_layout.addWidget(screening_label)
                
                screening_content = QTextBrowser()
                screening_content.setPlainText(record[5] or '')
                screening_content.setFixedHeight(120)
                screening_content.setStyleSheet("""
                    QTextBrowser {
                        border: none;
                        padding: 0px;
                        background-color: white;
                        font-size: 13px;
                        line-height: 1.5;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background: #f0f0f0;
                        width: 10px;
                        margin: 0px;
                    }
                    QScrollBar::handle:vertical {
                        background: #c0c0c0;
                        min-height: 20px;
                        border-radius: 5px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background: #a0a0a0;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                """)
                screening_layout.addWidget(screening_content)
                
                record_layout.addLayout(screening_layout)
                
                record_frame.setLayout(record_layout)
                self.medical_screening_layout.addWidget(record_frame)
                
                # 存储记录和复选框的引用
                self.medical_screening_records.append({
                    'record': record,
                    'checkbox': checkbox,
                    'frame': record_frame
                })
            
            # 添加弹性空间，将所有记录推到顶部
            self.medical_screening_layout.addStretch()
            
            # 如果没有记录，显示提示
            if not records:
                no_data_label = QLabel('暂无病史筛查记录')
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: gray; font-size: 16px; padding: 50px;")
                self.medical_screening_layout.addWidget(no_data_label)
            
        except Exception as e:
            QMessageBox.warning(self, "显示错误", f"显示病史筛查记录时发生错误：{str(e)}")
    
    def toggle_medical_select_all(self, state):
        """病史筛查全选/取消全选"""
        is_checked = (state == Qt.CheckState.Checked.value)
        if hasattr(self, 'medical_screening_records'):
            for record_info in self.medical_screening_records:
                record_info['checkbox'].setChecked(is_checked)
    
    def add_medical_screening(self):
        """添加病史筛查记录"""
        try:
            from ui.add_medical_screening_dialog import AddMedicalScreeningDialog
            dialog = AddMedicalScreeningDialog(self.db_manager, self)
            # 预填充当前青年的信息
            dialog.name_edit.setText(self.youth_data.name)
            dialog.gender_combo.setCurrentText(self.youth_data.gender)
            dialog.id_card_edit.setText(self.youth_data.id_card)
            # 禁用这些字段的编辑
            dialog.name_edit.setEnabled(False)
            dialog.gender_combo.setEnabled(False)
            dialog.id_card_edit.setEnabled(False)
            
            # 连接信号 - 刷新详情页面
            dialog.data_updated.connect(self.load_medical_screening_data)
            
            # 连接信号 - 通知主窗口刷新
            def on_data_updated():
                self.data_updated.emit()
                if self.parent() and hasattr(self.parent(), 'load_medical_screening_data'):
                    self.parent().load_medical_screening_data()
            
            dialog.data_updated.connect(on_data_updated)
            
            dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开添加病史筛查对话框时发生错误: {str(e)}')
    
    def edit_medical_screening_by_record(self, record_data):
        """编辑病史筛查记录"""
        try:
            from ui.add_medical_screening_dialog import AddMedicalScreeningDialog
            from PyQt5.QtCore import QDate
            
            dialog = AddMedicalScreeningDialog(self.db_manager, self)
            dialog.setWindowTitle('编辑病史筛查记录')
            
            # 填充现有数据
            dialog.name_edit.setText(record_data[2] or '')
            dialog.gender_combo.setCurrentText(record_data[3] or '')
            dialog.id_card_edit.setText(record_data[4] or '')
            dialog.screening_result_edit.setPlainText(record_data[5] or '')
            
            # 设置日期
            if record_data[6]:
                date_parts = record_data[6].split('-')
                if len(date_parts) == 3:
                    dialog.date_edit.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            
            # 设置备注
            if len(record_data) > 7 and record_data[7]:
                dialog.remark_combo.setCurrentText(record_data[7] or '')
            
            dialog.physical_status_combo.setCurrentText(record_data[8] if len(record_data) > 8 else '')
            dialog.mental_status_combo.setCurrentText(record_data[9] if len(record_data) > 9 else '')
            
            # 禁用身份证、姓名、性别编辑
            dialog.name_edit.setEnabled(False)
            dialog.gender_combo.setEnabled(False)
            dialog.id_card_edit.setEnabled(False)
            
            # 修改保存方法为更新
            record_id = record_data[0]
            original_save = dialog.save_record
            
            def update_record():
                # 验证必填字段
                screening_result = dialog.screening_result_edit.toPlainText().strip()
                screening_date = dialog.date_edit.date().toString('yyyy-MM-dd')
                remark = dialog.remark_combo.currentText()
                physical_status = dialog.physical_status_combo.currentText()
                mental_status = dialog.mental_status_combo.currentText()
                
                if not all([screening_result, physical_status, mental_status]):
                    QMessageBox.warning(dialog, '输入错误', '请填写所有必填字段！')
                    return
                
                try:
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE medical_screening 
                        SET screening_result=?, screening_date=?, remark=?,
                            physical_status=?, mental_status=?
                        WHERE id=?
                    ''', (screening_result, screening_date, remark, physical_status, mental_status, record_id))
                    
                    conn.commit()
                    conn.close()
                    
                    # 异常统计已通过视图自动更新，无需手动同步
                    
                    QMessageBox.information(dialog, '保存成功', '病史筛查记录已成功更新！')
                    dialog.data_updated.emit()
                    dialog.accept()
                    
                    # 通知主窗口刷新病史筛查数据
                    self.data_updated.emit()
                    if self.parent() and hasattr(self.parent(), 'load_medical_screening_data'):
                        self.parent().load_medical_screening_data()
                    
                except Exception as e:
                    QMessageBox.warning(dialog, '保存失败', f'更新病史筛查记录时发生错误：{str(e)}')
            
            dialog.save_record = update_record
            dialog.data_updated.connect(self.load_medical_screening_data)
            
            dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'编辑病史筛查记录时发生错误: {str(e)}')
    
    def delete_single_medical_screening(self, record_data):
        """删除单个病史筛查记录"""
        try:
            reply = QMessageBox.question(self, '确认删除', 
                                       f'确定要删除 {record_data[2]} 的病史筛查记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM medical_screening WHERE id=?', (record_data[0],))
                conn.commit()
                conn.close()
                
                # 异常统计已通过视图自动更新，无需手动同步
                
                QMessageBox.information(self, '删除成功', '记录已删除')
                self.load_medical_screening_data()
                
                # 发出信号通知主窗口刷新
                self.data_updated.emit()
                
                # 如果父窗口有刷新病史筛查数据的方法，调用它
                if self.parent() and hasattr(self.parent(), 'load_medical_screening_data'):
                    self.parent().load_medical_screening_data()
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'删除病史筛查记录时发生错误: {str(e)}')
    
    def batch_delete_medical_screening(self):
        """批量删除病史筛查记录"""
        try:
            selected_records = []
            if hasattr(self, 'medical_screening_records'):
                for record_info in self.medical_screening_records:
                    if record_info['checkbox'].isChecked():
                        selected_records.append(record_info['record'][0])  # 记录ID
            
            if not selected_records:
                QMessageBox.warning(self, '提示', '请先选择要删除的记录')
                return
            
            reply = QMessageBox.question(self, '确认删除', 
                                       f'确定要删除选中的 {len(selected_records)} 条记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                # 在删除前收集需要同步的记录信息
                records_to_sync = []
                
                if hasattr(self, 'medical_screening_records'):
                    for record_info in self.medical_screening_records:
                        if record_info['checkbox'].isChecked():
                            record_data = record_info['record']
                            records_to_sync.append({
                                'id': record_data[0],
                                'user_id': record_data[4] if len(record_data) > 4 else '',
                                'screening_date': record_data[6] if len(record_data) > 6 else ''
                            })
                
                # 执行删除
                deleted_count = 0
                for record_id in selected_records:
                    cursor.execute('DELETE FROM medical_screening WHERE id=?', (record_id,))
                    deleted_count += 1
                
                conn.commit()
                conn.close()
                
                # 取消全选状态
                if hasattr(self, 'medical_select_all_checkbox'):
                    self.medical_select_all_checkbox.setChecked(False)
                
                self.load_medical_screening_data()
                
                if deleted_count > 0:
                    QMessageBox.information(self, '删除成功', f'成功删除 {deleted_count} 条记录')
                    
                    # 发出信号通知主窗口刷新
                    self.data_updated.emit()
                    
                    # 如果父窗口有刷新病史筛查数据的方法，调用它
                    if self.parent() and hasattr(self.parent(), 'load_medical_screening_data'):
                        self.parent().load_medical_screening_data()
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除任何记录')
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'批量删除病史筛查记录时发生错误: {str(e)}')
    
    def create_physical_examination_tab(self):
        """创建体检情况统计表标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建表格
        self.physical_exam_table = QTableWidget()
        
        # 设置表格样式
        self.physical_exam_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # 设置表格属性
        self.physical_exam_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.physical_exam_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.physical_exam_table.setAlternatingRowColors(True)
        
        # 连接双击事件
        self.physical_exam_table.cellDoubleClicked.connect(self.on_physical_exam_double_click)
        
        layout.addWidget(self.physical_exam_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加体检记录')
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        add_btn.clicked.connect(self.add_physical_examination_record)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton('修改选中记录')
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #F39C12;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #E67E22;
            }
        """)
        edit_btn.clicked.connect(self.edit_selected_physical_examination)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('删除选中记录')
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_physical_examination)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 加载数据
        self.load_physical_examination_data()
        
        widget.setLayout(layout)
        return widget
    
    def load_physical_examination_data(self):
        """加载体检情况数据"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, gender, youth_id_card,
                       district_exam, district_positive, district_date,
                       city_exam, city_positive, city_date,
                       special_exam, special_positive, special_date,
                       body_status, psychological_test_type, tracking_opinion, implementation_status
                FROM physical_examination 
                WHERE youth_id_card=?
                ORDER BY id
            ''', (self.id_card,))
            records = cursor.fetchall()
            conn.close()
            
            self.display_physical_examination_records(records)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载体检情况数据时发生错误：{str(e)}")
    
    def display_physical_examination_records(self, records):
        """显示体检情况记录 - 每条记录占3行"""
        # 清空表格内容和所有widget
        self.physical_exam_table.clearContents()
        self.physical_exam_table.setRowCount(0)
        
        # 设置表头
        headers = ['选择', '序号', '姓名', '性别', '公民身份号码', '检查阶段', '阳性特征/边缘问题', 
                   '日期', '身体状况', '士兵职业基本适应性检测机检类型', '跟踪处置意见', '处置意见落实情况']
        self.physical_exam_table.setColumnCount(len(headers))
        self.physical_exam_table.setHorizontalHeaderLabels(headers)
        
        # 每条记录占3行
        self.physical_exam_table.setRowCount(len(records) * 3)
        
        for idx, record in enumerate(records):
            base_row = idx * 3
            
            # 先设置所有需要合并的单元格
            self.physical_exam_table.setSpan(base_row, 0, 3, 1)  # 选择框列
            self.physical_exam_table.setSpan(base_row, 1, 3, 1)  # 序号
            self.physical_exam_table.setSpan(base_row, 2, 3, 1)  # 姓名
            self.physical_exam_table.setSpan(base_row, 3, 3, 1)  # 性别
            self.physical_exam_table.setSpan(base_row, 4, 3, 1)  # 公民身份号码
            self.physical_exam_table.setSpan(base_row, 8, 3, 1)  # 身体状况
            self.physical_exam_table.setSpan(base_row, 9, 3, 1)  # 士兵职业基本适应性检测机检类型
            self.physical_exam_table.setSpan(base_row, 10, 3, 1) # 跟踪处置意见
            self.physical_exam_table.setSpan(base_row, 11, 3, 1) # 处置意见落实情况
            
            # 选择框 - 在合并后的单元格中设置
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #7F8C8D;
                    border-radius: 2px;
                    background-color: white;
                }
                QCheckBox::indicator:hover {
                    border-color: #3498DB;
                    background-color: #ECF0F1;
                }
                QCheckBox::indicator:checked {
                    background-color: #3498DB;
                    border-color: #2980B9;
                }
            """)
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.addWidget(checkbox)
            checkbox_container = QWidget()
            checkbox_container.setLayout(checkbox_layout)
            self.physical_exam_table.setCellWidget(base_row, 0, checkbox_container)
            
            # 序号
            item = QTableWidgetItem(str(idx + 1))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            item.setData(Qt.ItemDataRole.UserRole, record[0])  # 存储记录ID
            self.physical_exam_table.setItem(base_row, 1, item)
            
            # 姓名
            item = QTableWidgetItem(str(record[1] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 2, item)
            
            # 性别
            item = QTableWidgetItem(str(record[2] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 3, item)
            
            # 公民身份号码
            item = QTableWidgetItem(str(record[3] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 4, item)
            
            # 第一行：区体检
            item = QTableWidgetItem('区体检')
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 5, item)
            
            item = QTableWidgetItem(str(record[5] or ''))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 6, item)
            
            item = QTableWidgetItem(str(record[6] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 7, item)
            
            # 第二行：市体检
            item = QTableWidgetItem('市体检')
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row + 1, 5, item)
            
            item = QTableWidgetItem(str(record[8] or ''))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row + 1, 6, item)
            
            item = QTableWidgetItem(str(record[9] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row + 1, 7, item)
            
            # 第三行：专项复查
            item = QTableWidgetItem('专项复查')
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row + 2, 5, item)
            
            item = QTableWidgetItem(str(record[11] or ''))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row + 2, 6, item)
            
            item = QTableWidgetItem(str(record[12] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row + 2, 7, item)
            
            # 身体状况
            item = QTableWidgetItem(str(record[13] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 8, item)
            
            # 士兵职业基本适应性检测机检类型
            item = QTableWidgetItem(str(record[14] or ''))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 9, item)
            
            # 跟踪处置意见
            item = QTableWidgetItem(str(record[15] or ''))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 10, item)
            
            # 处置意见落实情况
            item = QTableWidgetItem(str(record[16] or ''))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.physical_exam_table.setItem(base_row, 11, item)
        
        # 设置列宽
        self.physical_exam_table.setColumnWidth(0, 50)   # 选择
        self.physical_exam_table.setColumnWidth(1, 60)   # 序号
        self.physical_exam_table.setColumnWidth(2, 80)   # 姓名
        self.physical_exam_table.setColumnWidth(3, 60)   # 性别
        self.physical_exam_table.setColumnWidth(4, 150)  # 公民身份号码
        self.physical_exam_table.setColumnWidth(5, 100)  # 检查阶段
        self.physical_exam_table.setColumnWidth(6, 200)  # 阳性特征/边缘问题
        self.physical_exam_table.setColumnWidth(7, 100)  # 日期
        self.physical_exam_table.setColumnWidth(8, 100)  # 身体状况
        self.physical_exam_table.setColumnWidth(9, 200)  # 士兵职业基本适应性检测机检类型
        self.physical_exam_table.setColumnWidth(10, 200) # 跟踪处置意见
        self.physical_exam_table.setColumnWidth(11, 200) # 处置意见落实情况
        
        # 设置行高
        for row in range(self.physical_exam_table.rowCount()):
            self.physical_exam_table.setRowHeight(row, 40)
    
    def on_physical_exam_double_click(self, row, column):
        """双击体检记录时编辑"""
        try:
            # 计算记录索引
            record_index = row // 3
            base_row = record_index * 3
            
            # 获取记录ID
            id_item = self.physical_exam_table.item(base_row, 1)
            if id_item:
                physical_id = id_item.data(Qt.ItemDataRole.UserRole)
                self.edit_physical_examination_record(physical_id)
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开编辑对话框时发生错误: {str(e)}')
    
    def add_physical_examination_record(self):
        """添加体检记录"""
        try:
            from ui.physical_examination_detail_dialog import PhysicalExaminationDetailDialog
            
            dialog = PhysicalExaminationDetailDialog(self.db_manager, self)
            dialog.id_card_input.setText(self.id_card)
            dialog.id_card_input.setReadOnly(True)
            
            # 触发身份证号变化事件以自动填充姓名和性别
            dialog.on_id_card_changed(self.id_card)
            
            # 连接数据更新信号
            dialog.data_updated.connect(self.on_physical_exam_data_updated)
            
            dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开添加对话框时发生错误: {str(e)}')
    
    def edit_physical_examination_record(self, physical_id):
        """编辑体检记录"""
        try:
            from ui.physical_examination_detail_dialog import PhysicalExaminationDetailDialog
            
            # 查询记录数据
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, youth_id_card, name, gender,
                       district_exam, district_positive, district_date,
                       city_exam, city_positive, city_date,
                       special_exam, special_positive, special_date,
                       body_status, psychological_test_type, tracking_opinion, implementation_status
                FROM physical_examination 
                WHERE id = ?
            ''', (physical_id,))
            
            record = cursor.fetchone()
            conn.close()
            
            if record:
                dialog = PhysicalExaminationDetailDialog(self.db_manager, self, record_data=record)
                
                # 连接数据更新信号
                dialog.data_updated.connect(self.on_physical_exam_data_updated)
                
                dialog.exec_()
            else:
                QMessageBox.warning(self, '错误', '未找到该记录')
                
        except Exception as e:
            QMessageBox.warning(self, '错误', f'查看详情时发生错误: {str(e)}')
    
    def edit_selected_physical_examination(self):
        """修改选中的体检记录"""
        try:
            selected_ids = []
            
            # 获取选中的记录
            for i in range(0, self.physical_exam_table.rowCount(), 3):
                checkbox_widget = self.physical_exam_table.cellWidget(i, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        id_item = self.physical_exam_table.item(i, 1)
                        if id_item:
                            physical_id = id_item.data(Qt.ItemDataRole.UserRole)
                            selected_ids.append(physical_id)
            
            if not selected_ids:
                QMessageBox.warning(self, '提示', '请先选择要修改的记录')
                return
            
            if len(selected_ids) > 1:
                QMessageBox.warning(self, '提示', '一次只能修改一条记录，请只选择一条记录')
                return
            
            # 编辑选中的记录
            self.edit_physical_examination_record(selected_ids[0])
            
        except Exception as e:
            QMessageBox.critical(self, '修改失败', f'修改体检记录时发生错误：{str(e)}')
    
    def delete_selected_physical_examination(self):
        """删除选中的体检记录"""
        try:
            selected_ids = []
            
            # 获取选中的记录
            for i in range(0, self.physical_exam_table.rowCount(), 3):
                checkbox_widget = self.physical_exam_table.cellWidget(i, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        id_item = self.physical_exam_table.item(i, 1)
                        if id_item:
                            physical_id = id_item.data(Qt.ItemDataRole.UserRole)
                            selected_ids.append(physical_id)
            
            if not selected_ids:
                QMessageBox.warning(self, '提示', '请先选择要删除的记录')
                return
            
            reply = QMessageBox.question(
                self, 
                '确认删除', 
                f'确定要删除选中的 {len(selected_ids)} 条体检记录吗？\n删除后无法恢复！',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                for physical_id in selected_ids:
                    cursor.execute("DELETE FROM physical_examination WHERE id = ?", (physical_id,))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, '删除成功', f'成功删除 {len(selected_ids)} 条体检记录')
                
                # 刷新数据
                self.on_physical_exam_data_updated()
                
        except Exception as e:
            QMessageBox.critical(self, '删除失败', f'删除体检记录时发生错误：{str(e)}')
    
    def on_physical_exam_data_updated(self):
        """体检数据更新时的回调"""
        # 刷新当前对话框的体检数据
        self.load_physical_examination_data()
        
        # 通知主窗口刷新体检情况统计表
        try:
            if self.parent():
                main_window = self.parent()
                if hasattr(main_window, 'load_physical_examination_data'):
                    main_window.load_physical_examination_data()
        except Exception as e:
            print(f"刷新主窗口体检数据时出错: {str(e)}")
    
    def create_camp_verification_tab(self):
        """创建入营点验情况标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建滚动区域来容纳所有记录
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.camp_verification_layout = QVBoxLayout()
        
        scroll_widget.setLayout(self.camp_verification_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 全选复选框
        self.camp_select_all_checkbox = QCheckBox('全选')
        self.camp_select_all_checkbox.stateChanged.connect(self.toggle_camp_select_all)
        button_layout.addWidget(self.camp_select_all_checkbox)
        
        button_layout.addStretch()
        
        add_btn = QPushButton('添加记录')
        add_btn.clicked.connect(self.add_camp_verification)
        button_layout.addWidget(add_btn)
        
        batch_delete_btn = QPushButton('批量删除')
        batch_delete_btn.clicked.connect(self.batch_delete_camp_verification)
        button_layout.addWidget(batch_delete_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_camp_verification_data)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def load_exception_statistics_data(self):
        """加载异常情况统计数据"""
        if not hasattr(self, 'exception_statistics_table'):
            return
        
        try:
            # 使用异常统计视图获取该青年相关的数据
            all_records = self.db_manager.get_exception_statistics_view_data()
            
            # 过滤出属于当前青年的记录
            filtered_records = [record for record in all_records if record[0] == self.id_card]
            
            # 清空表格
            self.exception_statistics_table.setRowCount(0)
            
            if not filtered_records:
                return
            
            # 填充表格数据
            self.exception_statistics_table.setRowCount(len(filtered_records))
            
            for row, record in enumerate(filtered_records):
                # 姓名
                name_item = QTableWidgetItem(record[1])  # 姓名
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 0, name_item)
                
                # 性别
                gender_item = QTableWidgetItem(record[2] or '')  # 性别
                gender_item.setFlags(gender_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 1, gender_item)
                
                # 公民证件号码
                user_id_item = QTableWidgetItem(record[0])  # 公民身份号码
                user_id_item.setFlags(user_id_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 2, user_id_item)
                
                # 思想
                thought_text = record[8] if record[8] == '异常' else '正常'
                thought_item = QTableWidgetItem(thought_text)
                thought_item.setFlags(thought_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 3, thought_item)
                
                # 身体
                body_text = record[9] if record[9] == '异常' else '正常'
                body_item = QTableWidgetItem(body_text)
                body_item.setFlags(body_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 4, body_item)
                
                # 精神
                spirit_text = record[10] if record[10] == '异常' else '正常'
                spirit_item = QTableWidgetItem(spirit_text)
                spirit_item.setFlags(spirit_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 5, spirit_item)
                
                # 其他（异常来源）
                other_text = record[13] or ''  # 其他
                other_item = QTableWidgetItem(other_text)
                other_item.setFlags(other_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 6, other_item)
                
                # 日期
                date_item = QTableWidgetItem(record[14] or '')  # 日期
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.exception_statistics_table.setItem(row, 7, date_item)
                
        except Exception as e:
            print(f"加载异常情况统计数据时出错: {e}")
    
    def load_camp_verification_data(self):
        """加载入营点验情况数据"""
        if not self.youth_data:
            return
        
        try:
            # 清空布局
            while self.camp_verification_layout.count():
                item = self.camp_verification_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 根据用户名和身份证号查询入营点验记录
            records = self.db_manager.get_camp_verifications_by_username_and_id(
                self.youth_data.name, 
                self.youth_data.id_card
            )
            
            if not records:
                empty_label = QLabel('暂无入营点验记录')
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("color: gray; padding: 20px;")
                self.camp_verification_layout.addWidget(empty_label)
            else:
                # 创建表格
                table = QTableWidget()
                table.setColumnCount(8)
                table.setHorizontalHeaderLabels(['', '用户名', '公民身份号码', '携带物品', '用途', '处置措施', '日期', '操作'])
                table.setColumnWidth(0, 30)
                table.setColumnWidth(1, 80)
                table.setColumnWidth(2, 150)  # 公民身份号码列
                table.setColumnWidth(3, 120)  # 携带物品
                table.setColumnWidth(4, 100)  # 用途
                table.setColumnWidth(5, 120)  # 处置措施
                table.setColumnWidth(6, 100)  # 日期
                table.setColumnWidth(7, 80)   # 操作
                
                table.setRowCount(len(records))
                
                self.camp_verification_checkboxes = []
                self.camp_verification_record_ids = {}  # 存储复选框对应的记录ID
                
                for row, record in enumerate(records):
                    # 复选框
                    checkbox = QCheckBox()
                    self.camp_verification_checkboxes.append(checkbox)
                    self.camp_verification_record_ids[id(checkbox)] = record.id  # 保存checkbox对应的record.id
                    table.setCellWidget(row, 0, checkbox)
                    
                    # 用户名
                    table.setItem(row, 1, QTableWidgetItem(record.username))
                    
                    # 公民身份号码
                    table.setItem(row, 2, QTableWidgetItem(record.user_id))
                    
                    # 携带物品（验证项目）
                    table.setItem(row, 3, QTableWidgetItem(record.item))
                    
                    # 用途
                    usage_text = record.usage if hasattr(record, 'usage') else ''
                    table.setItem(row, 4, QTableWidgetItem(usage_text))
                    
                    # 处置措施
                    table.setItem(row, 5, QTableWidgetItem(record.Disposal))
                    
                    # 日期
                    table.setItem(row, 6, QTableWidgetItem(record.data))
                    
                    # 编辑和删除按钮
                    op_layout = QHBoxLayout()
                    op_widget = QWidget()
                    
                    edit_btn = QPushButton('编辑')
                    edit_btn.setMaximumWidth(40)
                    edit_btn.clicked.connect(lambda checked, r=record: self.edit_camp_verification(r))
                    op_layout.addWidget(edit_btn)
                    
                    delete_btn = QPushButton('删除')
                    delete_btn.setMaximumWidth(40)
                    delete_btn.clicked.connect(lambda checked, r_id=record.id: self.delete_single_camp_verification(r_id))
                    op_layout.addWidget(delete_btn)
                    
                    op_layout.setContentsMargins(0, 0, 0, 0)
                    op_widget.setLayout(op_layout)
                    table.setCellWidget(row, 7, op_widget)
                
                self.camp_verification_layout.addWidget(table)
                self.camp_verification_table = table
        except Exception as e:
            QMessageBox.warning(self, '加载失败', f'加载入营点验数据时发生错误: {str(e)}')
    
    def add_camp_verification(self):
        """添加入营点验记录"""
        from ui.camp_verification_dialog import CampVerificationDialog
        
        dialog = CampVerificationDialog(self.db_manager, self, youth_data=self.youth_data)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            self.load_camp_verification_data()
            self.data_updated.emit()
    
    def edit_camp_verification(self, record):
        """编辑入营点验记录"""
        from ui.camp_verification_dialog import CampVerificationDialog
        
        dialog = CampVerificationDialog(self.db_manager, self, record_data=record, youth_data=self.youth_data)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            self.load_camp_verification_data()
            self.data_updated.emit()
    
    def delete_single_camp_verification(self, record_id):
        """删除单个入营点验记录"""
        reply = QMessageBox.question(self, '确认删除', '确定要删除这条记录吗？')
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.db_manager.delete_camp_verification(record_id)
                if success:
                    QMessageBox.information(self, '删除成功', '记录已删除')
                    self.load_camp_verification_data()
                    self.data_updated.emit()
                else:
                    QMessageBox.warning(self, '删除失败', '删除记录失败')
            except Exception as e:
                QMessageBox.warning(self, '删除错误', f'删除记录时发生错误: {str(e)}')
    
    def toggle_camp_select_all(self):
        """切换全选状态"""
        if not hasattr(self, 'camp_verification_checkboxes'):
            return
        
        is_checked = self.camp_select_all_checkbox.isChecked()
        for checkbox in self.camp_verification_checkboxes:
            checkbox.setChecked(is_checked)
    
    def batch_delete_camp_verification(self):
        """批量删除入营点验记录"""
        if not hasattr(self, 'camp_verification_checkboxes'):
            return
        
        selected_records = [
            self.camp_verification_record_ids[id(checkbox)]
            for checkbox in self.camp_verification_checkboxes 
            if checkbox.isChecked() and id(checkbox) in self.camp_verification_record_ids
        ]
        
        if not selected_records:
            QMessageBox.warning(self, '警告', '请选择要删除的记录')
            return
        
        reply = QMessageBox.question(self, '确认删除', f'确定要删除选中的 {len(selected_records)} 条记录吗？')
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted_count = self.db_manager.delete_camp_verifications(selected_records)
                if deleted_count > 0:
                    QMessageBox.information(self, '删除成功', f'成功删除 {deleted_count} 条记录')
                    
                    if hasattr(self, 'camp_select_all_checkbox'):
                        self.camp_select_all_checkbox.setChecked(False)
                    
                    self.load_camp_verification_data()
                    self.data_updated.emit()
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除任何记录')
            except Exception as e:
                QMessageBox.warning(self, '删除错误', f'批量删除记录时发生错误: {str(e)}')
    def toggle_daily_select_all(self, state):
        """每日情况统计全选/取消全选"""
        is_checked = (state == Qt.CheckState.Checked.value)
        if hasattr(self, 'daily_stat_records'):
            for record_info in self.daily_stat_records:
                record_info['checkbox'].setChecked(is_checked)
    
    def add_daily_stat(self):
        """添加每日情况记录"""
        try:
            from ui.daily_record_dialog import DailyRecordDialog
            # 创建对话框，传递当前青年的ID和姓名
            youth_id = self.youth_data.id if self.youth_data else None
            dialog = DailyRecordDialog(self.db_manager, self, youth_id, self.youth_data.name)
            
            def on_data_updated():
                # 重新加载数据并刷新显示
                self.load_daily_stat_data()
                # 通知主窗口刷新
                self.data_updated.emit()
                # 如果父窗口有相关刷新方法，也调用它
                if self.parent() and hasattr(self.parent(), 'load_daily_stats_data'):
                    self.parent().load_daily_stats_data()
            
            dialog.data_updated.connect(on_data_updated)
            dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开添加每日记录对话框时发生错误: {str(e)}')
    
    def edit_daily_stat_by_record(self, record_data):
        """编辑每日情况记录"""
        try:
            from ui.edit_daily_record_dialog import EditDailyRecordDialog
            
            # record_data[0] 是记录ID
            dialog = EditDailyRecordDialog(self.db_manager, record_data[0], self)
            
            # 连接数据更新信号
            def on_data_updated():
                self.load_daily_stat_data()
                self.data_updated.emit()
                # 如果父窗口有相关刷新方法，也调用它
                if self.parent() and hasattr(self.parent(), 'load_daily_stats_data'):
                    self.parent().load_daily_stats_data()
            
            dialog.data_updated.connect(on_data_updated)
            
            # 显示对话框
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开编辑对话框时发生错误: {str(e)}')
    
    def delete_single_daily_stat(self, record_data):
        """删除单个每日情况记录"""
        try:
            reply = QMessageBox.question(self, '确认删除', 
                                       f'确定要删除 {record_data[2]} 的每日情况记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.db_manager.delete_daily_stat(record_data[0])
                if success:
                    QMessageBox.information(self, '删除成功', '记录已删除')
                    # 重新加载数据并刷新显示
                    self.load_daily_stat_data()
                    # 通知主窗口刷新
                    self.data_updated.emit()
                    # 如果父窗口有相关刷新方法，也调用它
                    if self.parent() and hasattr(self.parent(), 'load_daily_stats_data'):
                        self.parent().load_daily_stats_data()
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除记录')
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'删除每日情况记录时发生错误: {str(e)}')
    
    def batch_delete_daily_stat(self):
        """批量删除每日情况记录"""
        try:
            selected_records = []
            if hasattr(self, 'daily_stat_records'):
                for record_info in self.daily_stat_records:
                    if record_info['checkbox'].isChecked():
                        selected_records.append(record_info['record'][0])  # 记录ID
            
            if not selected_records:
                QMessageBox.warning(self, '提示', '请先选择要删除的记录')
                return
            
            reply = QMessageBox.question(self, '确认删除', 
                                       f'确定要删除选中的 {len(selected_records)} 条记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                deleted_count = self.db_manager.delete_daily_stats(selected_records)
                
                if deleted_count > 0:
                    QMessageBox.information(self, '删除成功', f'成功删除 {deleted_count} 条记录')
                    
                    # 取消全选状态
                    if hasattr(self, 'daily_select_all_checkbox'):
                        self.daily_select_all_checkbox.setChecked(False)
                    
                    # 重新加载数据并刷新显示
                    self.load_daily_stat_data()
                    # 通知主窗口刷新
                    self.data_updated.emit()
                    # 如果父窗口有相关刷新方法，也调用它
                    if self.parent() and hasattr(self.parent(), 'load_daily_stats_data'):
                        self.parent().load_daily_stats_data()
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除任何记录')
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'批量删除每日情况记录时发生错误: {str(e)}')
    def update_single_daily_stat_record(self, old_record_data, new_data):
        """更新单个每日情况记录的显示，不重新加载整个列表"""
        try:
            if not hasattr(self, 'daily_stat_records'):
                return
            
            # 找到要更新的记录
            for record_info in self.daily_stat_records:
                if record_info['record'][0] == old_record_data[0]:  # 通过ID匹配
                    # 更新记录数据
                    updated_record = list(old_record_data)
                    updated_record[2] = new_data['record_date']  # 日期
                    updated_record[3] = new_data['mood']  # 思想
                    updated_record[4] = new_data['physical_condition']  # 身体
                    updated_record[5] = new_data['mental_state']  # 精神
                    updated_record[6] = new_data['notes']  # 备注
                    
                    # 更新存储的记录数据
                    record_info['record'] = tuple(updated_record)
                    
                    # 更新界面显示
                    frame = record_info['frame']
                    layout = frame.layout()
                    
                    # 更新第一行的基本信息标签
                    info_layout = layout.itemAt(0).layout()  # 第一行布局
                    info_label = info_layout.itemAt(1).widget()  # 基本信息标签
                    info_text = f"日期: {new_data['record_date']} | 思想: {new_data['mood']} | 身体: {new_data['physical_condition']} | 精神: {new_data['mental_state']}"
                    info_label.setText(info_text)
                    
                    # 更新备注信息（如果有）
                    if new_data['notes']:
                        # 检查是否已经有备注布局
                        notes_layout_exists = False
                        for i in range(layout.count()):
                            item = layout.itemAt(i)
                            if item and item.layout():
                                child_layout = item.layout()
                                if child_layout.count() > 0:
                                    first_widget = child_layout.itemAt(0).widget()
                                    if first_widget and isinstance(first_widget, QLabel) and first_widget.text() == "备注:":
                                        # 更新现有备注
                                        notes_content = child_layout.itemAt(1).widget()
                                        notes_content.setText(new_data['notes'])
                                        notes_layout_exists = True
                                        break
                        
                        # 如果没有备注布局，创建新的
                        if not notes_layout_exists:
                            notes_layout = QVBoxLayout()
                            notes_layout.setSpacing(0)
                            notes_layout.setContentsMargins(0, 5, 0, 0)
                            
                            notes_label = QLabel("备注:")
                            notes_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #666;")
                            notes_layout.addWidget(notes_label)
                            
                            notes_content = QLabel(new_data['notes'])
                            notes_content.setWordWrap(True)
                            notes_content.setStyleSheet("""
                                QLabel {
                                    background-color: white;
                                    border: 1px solid #ddd;
                                    border-radius: 3px;
                                    padding: 5px;
                                    font-size: 12px;
                                }
                            """)
                            notes_layout.addWidget(notes_content)
                            
                            layout.addLayout(notes_layout)
                    else:
                        # 如果新数据没有备注，删除现有的备注布局
                        for i in range(layout.count()):
                            item = layout.itemAt(i)
                            if item and item.layout():
                                child_layout = item.layout()
                                if child_layout.count() > 0:
                                    first_widget = child_layout.itemAt(0).widget()
                                    if first_widget and isinstance(first_widget, QLabel) and first_widget.text() == "备注:":
                                        # 删除备注布局
                                        while child_layout.count():
                                            child = child_layout.takeAt(0)
                                            if child.widget():
                                                child.widget().deleteLater()
                                        layout.removeItem(item)
                                        break
                    
                    break
                    
        except Exception as e:
            print(f"更新单个记录显示时出错: {e}")
            # 如果更新失败，回退到重新加载整个列表
            self.load_daily_stat_data()

    # ==================== 政治考核情况统计相关方法 ====================
    
    def create_political_assessment_tab(self):
        """创建政治考核情况统计标签页"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 创建滚动区域来容纳所有记录
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.political_assessment_layout = QVBoxLayout()
        
        scroll_widget.setLayout(self.political_assessment_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 全选复选框
        self.political_select_all_checkbox = QCheckBox('全选')
        self.political_select_all_checkbox.stateChanged.connect(self.toggle_political_select_all)
        self.political_select_all_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #7F8C8D;
                border-radius: 2px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3498DB;
                background-color: #ECF0F1;
            }
            QCheckBox::indicator:checked {
                background-color: #3498DB;
                border-color: #2980B9;
            }
        """)
        button_layout.addWidget(self.political_select_all_checkbox)
        
        button_layout.addStretch()
        
        add_btn = QPushButton('添加记录')
        add_btn.clicked.connect(self.add_political_assessment)
        button_layout.addWidget(add_btn)
        
        batch_delete_btn = QPushButton('批量删除')
        batch_delete_btn.clicked.connect(self.batch_delete_political_assessment)
        button_layout.addWidget(batch_delete_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_political_assessment_data)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def load_political_assessment_data(self):
        """加载政治考核情况数据"""
        try:
            # 获取当前青年的政治考核情况数据
            records = self.db_manager.get_political_assessments_by_id_card(self.id_card)
            self.display_political_assessment_records(records)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载政治考核情况数据时发生错误：{str(e)}")
    
    def display_political_assessment_records(self, records):
        """显示政治考核情况记录"""
        try:
            # 清空现有布局
            for i in reversed(range(self.political_assessment_layout.count())):
                child = self.political_assessment_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
                    child.deleteLater()
            
            # 重置记录列表
            self.political_assessment_records = []
            
            for record in records:
                # record格式: (id, youth_id_card, name, gender, id_card, family_member_info, 
                #             visit_survey, political_assessment, key_attention, assessment_date, 
                #             thoughts, spirit, created_at)
                
                # 创建记录容器
                record_frame = QFrame()
                record_frame.setFrameStyle(QFrame.Shape.Box)
                record_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        margin: 5px;
                        padding: 10px;
                        background-color: #f9f9f9;
                    }
                """)
                
                record_layout = QVBoxLayout()
                
                # 第一行：基本信息和操作按钮
                info_layout = QHBoxLayout()
                
                # 选择框
                checkbox = QCheckBox()
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border: 2px solid #7F8C8D;
                        border-radius: 2px;
                        background-color: white;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #3498DB;
                        background-color: #ECF0F1;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #3498DB;
                        border-color: #2980B9;
                    }
                """)
                info_layout.addWidget(checkbox)
                
                # 基本信息
                info_text = f"日期: {record[9] or ''} | 姓名: {record[2] or ''} | 性别: {record[3] or ''}"
                info_label = QLabel(info_text)
                info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                info_layout.addWidget(info_label)
                
                info_layout.addStretch()
                
                # 操作按钮
                edit_btn = QPushButton('编辑')
                edit_btn.clicked.connect(lambda checked, record_data=record: self.edit_political_assessment(record_data))
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                """)
                info_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton('删除')
                delete_btn.clicked.connect(lambda checked, record_id=record[0]: self.delete_political_assessment(record_id))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E74C3C;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #C0392B;
                    }
                """)
                info_layout.addWidget(delete_btn)
                
                record_layout.addLayout(info_layout)
                
                # 详细信息
                details_layout = QVBoxLayout()
                details_layout.setSpacing(5)
                details_layout.setContentsMargins(25, 5, 0, 0)
                
                if record[5]:  # family_member_info
                    details_layout.addWidget(QLabel(f"<b>家庭成员信息:</b> {record[5]}"))
                
                if record[6]:  # visit_survey
                    details_layout.addWidget(QLabel(f"<b>走访调查情况:</b> {record[6]}"))
                
                if record[7]:  # political_assessment
                    details_layout.addWidget(QLabel(f"<b>政治考核情况:</b> {record[7]}"))
                
                if record[8]:  # key_attention
                    details_layout.addWidget(QLabel(f"<b>需重点关注问题:</b> {record[8]}"))
                
                if record[10]:  # thoughts
                    details_layout.addWidget(QLabel(f"<b>思想:</b> {record[10]}"))
                
                if record[11]:  # spirit
                    details_layout.addWidget(QLabel(f"<b>精神:</b> {record[11]}"))
                
                record_layout.addLayout(details_layout)
                
                record_frame.setLayout(record_layout)
                self.political_assessment_layout.addWidget(record_frame)
                
                # 保存记录引用
                self.political_assessment_records.append({
                    'checkbox': checkbox,
                    'record': record,
                    'frame': record_frame
                })
            
            if not records:
                no_data_label = QLabel('暂无政治考核情况记录')
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: #999; font-size: 14px; padding: 20px;")
                self.political_assessment_layout.addWidget(no_data_label)
            
        except Exception as e:
            QMessageBox.warning(self, "显示错误", f"显示政治考核情况记录时发生错误：{str(e)}")
    
    def toggle_political_select_all(self, state):
        """切换政治考核情况记录的全选状态"""
        if hasattr(self, 'political_assessment_records'):
            for record_info in self.political_assessment_records:
                record_info['checkbox'].setChecked(state == Qt.CheckState.Checked.value)
    
    def add_political_assessment(self):
        """添加政治考核情况记录"""
        from ui.add_political_assessment_dialog import AddPoliticalAssessmentDialog
        
        dialog = AddPoliticalAssessmentDialog(self.db_manager, self.id_card, self)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            self.load_political_assessment_data()
            self.data_updated.emit()
    
    def edit_political_assessment(self, record_data):
        """编辑政治考核情况记录"""
        from ui.add_political_assessment_dialog import AddPoliticalAssessmentDialog
        
        dialog = AddPoliticalAssessmentDialog(self.db_manager, self.id_card, self, record_data)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            self.load_political_assessment_data()
            self.data_updated.emit()
    
    def delete_political_assessment(self, record_id):
        """删除单个政治考核情况记录"""
        try:
            reply = QMessageBox.question(self, '确认删除', 
                                       '确定要删除这条政治考核情况记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                success = self.db_manager.delete_political_assessment(record_id)
                
                if success:
                    QMessageBox.information(self, '删除成功', '记录已删除')
                    self.load_political_assessment_data()
                    self.data_updated.emit()
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除记录')
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'删除政治考核情况记录时发生错误: {str(e)}')
    
    def batch_delete_political_assessment(self):
        """批量删除政治考核情况记录"""
        try:
            selected_records = []
            if hasattr(self, 'political_assessment_records'):
                for record_info in self.political_assessment_records:
                    if record_info['checkbox'].isChecked():
                        selected_records.append(record_info['record'][0])  # 记录ID
            
            if not selected_records:
                QMessageBox.warning(self, '提示', '请先选择要删除的记录')
                return
            
            reply = QMessageBox.question(self, '确认删除', 
                                       f'确定要删除选中的 {len(selected_records)} 条记录吗？',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                deleted_count = self.db_manager.delete_political_assessments(selected_records)
                
                if deleted_count > 0:
                    QMessageBox.information(self, '删除成功', f'成功删除 {deleted_count} 条记录')
                    
                    # 取消全选状态
                    if hasattr(self, 'political_select_all_checkbox'):
                        self.political_select_all_checkbox.setChecked(False)
                    
                    self.load_political_assessment_data()
                    self.data_updated.emit()
                else:
                    QMessageBox.warning(self, '删除失败', '未能删除任何记录')
        except Exception as e:
            QMessageBox.warning(self, '删除错误', f'批量删除政治考核情况记录时发生错误: {str(e)}')
