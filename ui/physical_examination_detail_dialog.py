"""
体检情况详情对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QMessageBox,
                             QFormLayout, QGroupBox, QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont


class PhysicalExaminationDetailDialog(QDialog):
    """体检情况详情对话框"""
    
    data_updated = pyqtSignal()  # 数据更新信号
    
    def __init__(self, db_manager, parent=None, record_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.record_data = record_data
        self.is_edit_mode = record_data is not None
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.load_record_data()
    
    def init_ui(self):
        """初始化界面"""
        if self.is_edit_mode:
            self.setWindowTitle('查看/编辑体检情况')
        else:
            self.setWindowTitle('添加体检情况')
        
        # 设置固定的初始尺寸和位置，确保在任何地方打开都是相同大小
        self.setGeometry(200, 100, 900, 900)
        self.setMinimumWidth(900)
        self.setMinimumHeight(900)
        
        # 允许最大化和调整大小
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        layout = QVBoxLayout()
        
        # 基本信息组
        basic_group = QGroupBox('基本信息')
        basic_layout = QFormLayout()
        
        self.id_card_input = QLineEdit()
        self.id_card_input.setPlaceholderText('请输入身份证号')
        self.id_card_input.textChanged.connect(self.on_id_card_changed)
        self.id_card_input.setMinimumHeight(35)
        basic_layout.addRow('公民身份号码*:', self.id_card_input)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('请输入姓名')
        self.name_input.setReadOnly(True)  # 自动填充，不允许手动修改
        self.name_input.setMinimumHeight(35)
        basic_layout.addRow('姓名*:', self.name_input)
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(['', '男', '女'])
        self.gender_input.setEditable(False)
        self.gender_input.setEnabled(False)  # 自动填充，不允许手动修改
        self.gender_input.setMinimumHeight(35)
        basic_layout.addRow('性别*:', self.gender_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 区体检组
        district_group = QGroupBox('区体检')
        district_layout = QFormLayout()
        
        self.district_positive_input = QTextEdit()
        self.district_positive_input.setPlaceholderText('请输入区检阳性特征或边缘问题')
        self.district_positive_input.setMinimumHeight(100)
        self.district_positive_input.setMaximumHeight(120)
        district_layout.addRow('区检阳性特征/边缘问题:', self.district_positive_input)
        
        self.district_date_input = QDateEdit()
        self.district_date_input.setCalendarPopup(True)
        self.district_date_input.setDisplayFormat('yyyy-MM-dd')
        self.district_date_input.setDate(QDate.currentDate())
        self.district_date_input.setSpecialValueText('未设置')
        self.district_date_input.setMinimumHeight(35)
        district_layout.addRow('区体检日期:', self.district_date_input)
        
        district_group.setLayout(district_layout)
        layout.addWidget(district_group)
        
        # 市体检组
        city_group = QGroupBox('市体检')
        city_layout = QFormLayout()
        
        self.city_positive_input = QTextEdit()
        self.city_positive_input.setPlaceholderText('请输入市检阳性特征或边缘问题')
        self.city_positive_input.setMinimumHeight(100)
        self.city_positive_input.setMaximumHeight(120)
        city_layout.addRow('市检阳性特征/边缘问题:', self.city_positive_input)
        
        self.city_date_input = QDateEdit()
        self.city_date_input.setCalendarPopup(True)
        self.city_date_input.setDisplayFormat('yyyy-MM-dd')
        self.city_date_input.setDate(QDate.currentDate())
        self.city_date_input.setSpecialValueText('未设置')
        self.city_date_input.setMinimumHeight(35)
        city_layout.addRow('市体检日期:', self.city_date_input)
        
        city_group.setLayout(city_layout)
        layout.addWidget(city_group)
        
        # 专项复查组
        special_group = QGroupBox('专项复查')
        special_layout = QFormLayout()
        
        self.special_positive_input = QTextEdit()
        self.special_positive_input.setPlaceholderText('请输入专项筛查阳性特征或边缘问题')
        self.special_positive_input.setMinimumHeight(100)
        self.special_positive_input.setMaximumHeight(120)
        special_layout.addRow('专项筛查阳性特征/边缘问题:', self.special_positive_input)
        
        self.special_date_input = QDateEdit()
        self.special_date_input.setCalendarPopup(True)
        self.special_date_input.setDisplayFormat('yyyy-MM-dd')
        self.special_date_input.setDate(QDate.currentDate())
        self.special_date_input.setSpecialValueText('未设置')
        self.special_date_input.setMinimumHeight(35)
        special_layout.addRow('专项复查日期:', self.special_date_input)
        
        special_group.setLayout(special_layout)
        layout.addWidget(special_group)
        
        # 身体状况组
        status_group = QGroupBox('身体状况')
        status_layout = QFormLayout()
        
        self.body_status_input = QComboBox()
        self.body_status_input.addItems(['', '正常', '异常'])
        self.body_status_input.setEditable(False)
        self.body_status_input.setMinimumHeight(35)
        status_layout.addRow('身体状况*:', self.body_status_input)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 心理测试和处置意见组
        follow_group = QGroupBox('心理测试与处置意见')
        follow_layout = QFormLayout()
        
        self.psychological_test_input = QLineEdit()
        self.psychological_test_input.setPlaceholderText('如：SCL-90、MMPI、EPQ等')
        self.psychological_test_input.setMinimumWidth(600)
        self.psychological_test_input.setMinimumHeight(35)
        follow_layout.addRow('士兵职业基本适应性检测机检类型:', self.psychological_test_input)
        
        self.tracking_opinion_input = QTextEdit()
        self.tracking_opinion_input.setPlaceholderText('请输入跟踪处置意见')
        self.tracking_opinion_input.setMinimumHeight(100)
        self.tracking_opinion_input.setMaximumHeight(120)
        self.tracking_opinion_input.setMinimumWidth(600)
        follow_layout.addRow('跟踪处置意见:', self.tracking_opinion_input)
        
        self.implementation_status_input = QTextEdit()
        self.implementation_status_input.setPlaceholderText('如：已落实、正在落实等')
        self.implementation_status_input.setMinimumHeight(100)
        self.implementation_status_input.setMaximumHeight(120)
        self.implementation_status_input.setMinimumWidth(600)
        follow_layout.addRow('处置意见落实情况:', self.implementation_status_input)
        
        follow_group.setLayout(follow_layout)
        layout.addWidget(follow_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_record)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11pt;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 11pt;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_id_card_changed(self, text):
        """身份证号变化时自动查询并填充姓名和性别"""
        id_card = text.strip()
        
        # 只有在编辑模式下才允许修改身份证号，查看模式下不处理
        if self.is_edit_mode:
            return
        
        # 清空姓名和性别
        self.name_input.clear()
        self.gender_input.setCurrentIndex(0)
        
        # 如果身份证号长度不是18位，不查询
        if len(id_card) != 18:
            return
        
        try:
            # 查询基本信息数据库
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, gender FROM youth WHERE id_card = ?
            """, (id_card,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # 找到对应的青年信息，自动填充
                name, gender = result
                self.name_input.setText(name or '')
                if gender in ['男', '女']:
                    self.gender_input.setCurrentText(gender)
                else:
                    self.gender_input.setCurrentIndex(0)
            else:
                # 未找到对应的青年信息
                self.name_input.setPlaceholderText('未找到该身份证号对应的青年信息')
                
        except Exception as e:
            print(f"查询青年信息时出错: {str(e)}")
    
    def load_record_data(self):
        """加载记录数据"""
        if not self.record_data:
            return
        
        # record_data 是一个元组，按照查询的顺序
        # (id, youth_id_card, name, gender, 
        #  district_exam, district_positive, district_date,
        #  city_exam, city_positive, city_date,
        #  special_exam, special_positive, special_date,
        #  body_status, psychological_test_type, tracking_opinion, implementation_status)
        
        self.id_card_input.setText(str(self.record_data[1] or ''))
        self.id_card_input.setReadOnly(True)  # 身份证号不允许修改
        
        self.name_input.setText(str(self.record_data[2] or ''))
        self.name_input.setReadOnly(True)  # 编辑模式下不允许修改姓名
        
        # 性别下拉框
        gender = str(self.record_data[3] or '')
        if gender in ['男', '女']:
            self.gender_input.setCurrentText(gender)
        else:
            self.gender_input.setCurrentIndex(0)
        self.gender_input.setEnabled(False)  # 编辑模式下不允许修改性别
        
        # 跳过district_exam (index 4)，直接读取district_positive (index 5)
        self.district_positive_input.setPlainText(str(self.record_data[5] or ''))
        
        # 区体检日期
        district_date_str = str(self.record_data[6] or '')
        if district_date_str:
            try:
                date_parts = district_date_str.split('-')
                if len(date_parts) == 3:
                    self.district_date_input.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            except:
                self.district_date_input.setDate(QDate.currentDate())
        
        # 跳过city_exam (index 7)，直接读取city_positive (index 8)
        self.city_positive_input.setPlainText(str(self.record_data[8] or ''))
        
        # 市体检日期
        city_date_str = str(self.record_data[9] or '')
        if city_date_str:
            try:
                date_parts = city_date_str.split('-')
                if len(date_parts) == 3:
                    self.city_date_input.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            except:
                self.city_date_input.setDate(QDate.currentDate())
        
        # 跳过special_exam (index 10)，直接读取special_positive (index 11)
        self.special_positive_input.setPlainText(str(self.record_data[11] or ''))
        
        # 专项复查日期
        special_date_str = str(self.record_data[12] or '')
        if special_date_str:
            try:
                date_parts = special_date_str.split('-')
                if len(date_parts) == 3:
                    self.special_date_input.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            except:
                self.special_date_input.setDate(QDate.currentDate())
        
        # 身体状况下拉框
        body_status = str(self.record_data[13] or '')
        if body_status in ['正常', '异常']:
            self.body_status_input.setCurrentText(body_status)
        else:
            self.body_status_input.setCurrentIndex(0)
        
        self.psychological_test_input.setText(str(self.record_data[14] or ''))
        self.tracking_opinion_input.setPlainText(str(self.record_data[15] or ''))
        self.implementation_status_input.setPlainText(str(self.record_data[16] or ''))
    
    def save_record(self):
        """保存记录"""
        # 验证必填字段
        id_card = self.id_card_input.text().strip()
        name = self.name_input.text().strip()
        gender = self.gender_input.currentText().strip()
        body_status = self.body_status_input.currentText().strip()
        
        if not id_card:
            QMessageBox.warning(self, '提示', '请输入公民身份号码')
            return
        
        if not name:
            QMessageBox.warning(self, '提示', '请输入姓名')
            return
        
        if not gender:
            QMessageBox.warning(self, '提示', '请选择性别')
            return
        
        if not body_status:
            QMessageBox.warning(self, '提示', '请选择身体状况')
            return
        
        # 验证身份证号是否存在于基本信息中，并获取应征地、连、排、班、带训班长信息
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_card, recruitment_place, company, platoon, squad, squad_leader 
            FROM youth WHERE id_card = ?
        """, (id_card,))
        youth_info = cursor.fetchone()
        
        if not youth_info:
            conn.close()
            QMessageBox.warning(self, '提示', f'身份证号 {id_card} 不存在于基本信息中，请先添加基本信息')
            return
        
        # 获取青年的应征地、连、排、班、带训班长信息
        recruitment_place = youth_info[1] or ''
        company = youth_info[2] or ''
        platoon = youth_info[3] or ''
        squad = youth_info[4] or ''
        squad_leader = youth_info[5] or ''
        
        try:
            # 获取所有字段值
            district_positive = self.district_positive_input.toPlainText().strip()
            district_date = self.district_date_input.date().toString('yyyy-MM-dd')
            city_positive = self.city_positive_input.toPlainText().strip()
            city_date = self.city_date_input.date().toString('yyyy-MM-dd')
            special_positive = self.special_positive_input.toPlainText().strip()
            special_date = self.special_date_input.date().toString('yyyy-MM-dd')
            body_status = self.body_status_input.currentText().strip()
            psychological_test_type = self.psychological_test_input.text().strip()
            tracking_opinion = self.tracking_opinion_input.toPlainText().strip()
            implementation_status = self.implementation_status_input.toPlainText().strip()
            
            # 检查结果字段设为空（不再使用）
            district_exam = ''
            city_exam = ''
            special_exam = ''
            
            if self.is_edit_mode:
                # 更新记录
                record_id = self.record_data[0]
                cursor.execute("""
                    UPDATE physical_examination 
                    SET name = ?, gender = ?, 
                        district_exam = ?, district_positive = ?, district_date = ?,
                        city_exam = ?, city_positive = ?, city_date = ?,
                        special_exam = ?, special_positive = ?, special_date = ?,
                        body_status = ?, psychological_test_type = ?, tracking_opinion = ?, implementation_status = ?,
                        recruitment_place = ?, company = ?, platoon = ?, squad = ?, squad_leader = ?
                    WHERE id = ?
                """, (name, gender, 
                      district_exam, district_positive, district_date,
                      city_exam, city_positive, city_date,
                      special_exam, special_positive, special_date,
                      body_status, psychological_test_type, tracking_opinion, implementation_status,
                      recruitment_place, company, platoon, squad, squad_leader, record_id))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, '成功', '体检情况记录已更新')
                self.data_updated.emit()
                self.accept()
            else:
                # 新增记录
                cursor.execute("""
                    INSERT INTO physical_examination 
                    (youth_id_card, name, gender, 
                     district_exam, district_positive, district_date,
                     city_exam, city_positive, city_date,
                     special_exam, special_positive, special_date,
                     body_status, psychological_test_type, tracking_opinion, implementation_status,
                     recruitment_place, company, platoon, squad, squad_leader)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (id_card, name, gender, 
                      district_exam, district_positive, district_date,
                      city_exam, city_positive, city_date,
                      special_exam, special_positive, special_date,
                      body_status, psychological_test_type, tracking_opinion, implementation_status,
                      recruitment_place, company, platoon, squad, squad_leader))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, '成功', '体检情况记录已添加')
                self.data_updated.emit()
                self.accept()
                
        except Exception as e:
            if conn:
                conn.close()
            QMessageBox.critical(self, '错误', f'保存失败：{str(e)}')
