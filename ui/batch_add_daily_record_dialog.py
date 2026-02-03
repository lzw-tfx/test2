"""
批量添加每日记录对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QDateEdit, QTextEdit, 
                             QScrollArea, QWidget, QMessageBox, QFormLayout,
                             QProgressBar, QApplication)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from datetime import datetime


class BatchAddWorker(QThread):
    """批量添加工作线程"""
    progress_updated = pyqtSignal(int, int)  # 当前进度, 总数
    record_processed = pyqtSignal(str, bool, str)  # 青年姓名, 是否成功, 消息
    finished = pyqtSignal(int, int)  # 成功数量, 失败数量
    
    def __init__(self, db_manager, youth_list, record_data):
        super().__init__()
        self.db_manager = db_manager
        self.youth_list = youth_list
        self.record_data = record_data
        self.success_count = 0
        self.fail_count = 0
    
    def run(self):
        """执行批量添加"""
        total = len(self.youth_list)
        
        for i, youth_info in enumerate(self.youth_list):
            try:
                youth_id = youth_info['youth_id']
                youth_name = youth_info['name']
                youth_id_card = youth_info.get('id_card', '')
                
                # 数据校验：验证青年是否存在于基本信息表中
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM youth WHERE id = ?', (youth_id,))
                youth_exists = cursor.fetchone()
                
                if not youth_exists:
                    conn.close()
                    self.record_processed.emit(youth_name, False, f"公民身份号码 {youth_id_card} 在基本信息表中不存在")
                    self.fail_count += 1
                    self.progress_updated.emit(i + 1, total)
                    continue
                
                # 检查是否已存在记录
                cursor.execute('''
                    SELECT id FROM daily_stat 
                    WHERE youth_id = ? AND record_date = ?
                ''', (youth_id, self.record_data['date']))
                
                existing_record = cursor.fetchone()
                
                if existing_record:
                    # 如果用户选择了覆盖，则更新记录
                    if self.record_data.get('overwrite', False):
                        cursor.execute('''
                            UPDATE daily_stat 
                            SET mood = ?, physical_condition = ?, mental_state = ?, 
                                training = ?, management = ?, notes = ?
                            WHERE youth_id = ? AND record_date = ?
                        ''', (self.record_data['mood'], self.record_data['physical_condition'], 
                              self.record_data['mental_state'], self.record_data['training'], 
                              self.record_data['management'], self.record_data['notes'], 
                              youth_id, self.record_data['date']))
                        conn.commit()
                        self.record_processed.emit(youth_name, True, "记录已更新")
                        self.success_count += 1
                    else:
                        self.record_processed.emit(youth_name, False, "记录已存在，跳过")
                        self.fail_count += 1
                else:
                    # 插入新记录
                    cursor.execute('''
                        INSERT INTO daily_stat (youth_id, record_date, mood, physical_condition, 
                                              mental_state, training, management, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (youth_id, self.record_data['date'], self.record_data['mood'], 
                          self.record_data['physical_condition'], self.record_data['mental_state'], 
                          self.record_data['training'], self.record_data['management'], 
                          self.record_data['notes']))
                    conn.commit()
                    self.record_processed.emit(youth_name, True, "记录已添加")
                    self.success_count += 1
                
                conn.close()
                
            except Exception as e:
                self.record_processed.emit(youth_name, False, f"错误: {str(e)}")
                self.fail_count += 1
            
            # 更新进度
            self.progress_updated.emit(i + 1, total)
        
        # 完成
        self.finished.emit(self.success_count, self.fail_count)


class BatchAddDailyRecordDialog(QDialog):
    # 定义信号，用于通知父窗口数据已更新
    data_updated = pyqtSignal()
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('批量添加每日记录')
        self.setModal(True)
        self.resize(650, 700)  # 增加窗口宽度
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 标题和说明
        title_label = QLabel('批量添加每日记录')
        title_font = QFont("Arial", 12)  # 使用Arial字体，12pt
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # 设置字体
        font = QFont("Arial", 11)  # 使用Arial字体，11pt
        
        # 筛选条件区域
        filter_label = QLabel('筛选条件:')
        filter_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # 使用Arial字体
        content_layout.addWidget(filter_label)
        
        # 连、排、班筛选 - 放在同一行
        filter_row_layout = QHBoxLayout()
        
        # 应征地筛选
        filter_row_layout.addWidget(QLabel('应征地:'))
        self.recruitment_place_combo = QComboBox()
        self.recruitment_place_combo.setFont(font)
        self.recruitment_place_combo.setMinimumWidth(120)
        self.recruitment_place_combo.currentTextChanged.connect(self.on_recruitment_place_changed)
        filter_row_layout.addWidget(self.recruitment_place_combo)
        
        # 连筛选
        filter_row_layout.addWidget(QLabel('连:'))
        self.company_combo = QComboBox()
        self.company_combo.setFont(font)
        self.company_combo.setMinimumWidth(120)
        self.company_combo.currentTextChanged.connect(self.on_company_changed)
        filter_row_layout.addWidget(self.company_combo)
        
        # 排筛选
        filter_row_layout.addWidget(QLabel('排:'))
        self.platoon_combo = QComboBox()
        self.platoon_combo.setFont(font)
        self.platoon_combo.setMinimumWidth(120)
        self.platoon_combo.currentTextChanged.connect(self.on_platoon_changed)
        filter_row_layout.addWidget(self.platoon_combo)
        
        # 班筛选
        filter_row_layout.addWidget(QLabel('班:'))
        self.squad_combo = QComboBox()
        self.squad_combo.setFont(font)
        self.squad_combo.setMinimumWidth(120)
        filter_row_layout.addWidget(self.squad_combo)
        
        filter_row_layout.addStretch()  # 添加弹性空间
        content_layout.addLayout(filter_row_layout)
        
        # 加载初始数据
        self.load_recruitment_place_options()
        
        # 分隔线
        separator_label = QLabel('记录信息:')
        separator_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # 使用Arial字体
        separator_label.setContentsMargins(0, 20, 0, 0)  # 添加上边距
        content_layout.addWidget(separator_label)
        
        # 记录信息表单
        form_layout = QFormLayout()
        
        # 日期选择
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFont(font)
        form_layout.addRow('日期:', self.date_edit)
        
        # 思想状态
        self.mood_combo = QComboBox()
        self.mood_combo.addItems(['正常', '异常'])
        self.mood_combo.setFont(font)
        form_layout.addRow('思想:', self.mood_combo)
        
        # 身体状态
        self.physical_combo = QComboBox()
        self.physical_combo.addItems(['正常', '异常'])
        self.physical_combo.setFont(font)
        form_layout.addRow('身体:', self.physical_combo)
        
        # 精神状态
        self.mental_combo = QComboBox()
        self.mental_combo.addItems(['正常', '异常'])
        self.mental_combo.setFont(font)
        form_layout.addRow('精神:', self.mental_combo)
        
        # 训练状态
        self.training_combo = QComboBox()
        self.training_combo.addItems(['正常', '异常'])
        self.training_combo.setFont(font)
        form_layout.addRow('训练:', self.training_combo)
        
        # 管理状态
        self.management_combo = QComboBox()
        self.management_combo.addItems(['正常', '异常'])
        self.management_combo.setFont(font)
        form_layout.addRow('管理:', self.management_combo)
        
        # 其他备注
        self.notes_edit = QTextEdit()
        self.notes_edit.setFont(font)
        self.notes_edit.setMaximumHeight(120)
        self.notes_edit.setPlaceholderText('请输入其他备注信息...')
        form_layout.addRow('其他:', self.notes_edit)
        
        content_layout.addLayout(form_layout)
        
        # 设置内容widget的布局
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # 添加滚动区域到主布局
        main_layout.addWidget(scroll_area)
        
        # 进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 状态标签（初始隐藏）
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 开始批量添加按钮
        self.start_btn = QPushButton('开始批量添加')
        self.start_btn.clicked.connect(self.start_batch_add)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11pt;
                min-height: 35px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        button_layout.addWidget(self.start_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
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
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def natural_sort_key(self, text):
        """自然排序键函数，专门处理中文数字排序"""
        import re
        
        # 中文数字映射
        chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20
        }
        
        # 提取数字部分
        # 匹配模式：中文数字 + 连/排/班
        match = re.match(r'([一二三四五六七八九十]+)([连排班])', text)
        if match:
            chinese_num = match.group(1)
            unit = match.group(2)
            
            # 转换中文数字为阿拉伯数字
            if chinese_num in chinese_numbers:
                return (chinese_numbers[chinese_num], unit)
            else:
                # 处理复杂的中文数字（如二十一、三十二等）
                try:
                    if '十' in chinese_num:
                        if chinese_num.startswith('十'):
                            # 十、十一、十二等
                            if len(chinese_num) == 1:
                                num = 10
                            else:
                                num = 10 + chinese_numbers.get(chinese_num[1:], 0)
                        else:
                            # 二十、三十等
                            parts = chinese_num.split('十')
                            if len(parts) == 2:
                                tens = chinese_numbers.get(parts[0], 0) * 10
                                ones = chinese_numbers.get(parts[1], 0) if parts[1] else 0
                                num = tens + ones
                            else:
                                num = chinese_numbers.get(chinese_num, 999)
                    else:
                        num = chinese_numbers.get(chinese_num, 999)
                    return (num, unit)
                except:
                    return (999, unit)
        
        # 如果不匹配模式，使用原始字符串排序
        return (999, text)
    
    def load_recruitment_place_options(self):
        """加载应征地的选项"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT recruitment_place FROM youth WHERE recruitment_place IS NOT NULL AND recruitment_place != ""')
            recruitment_places = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # 使用自然排序
            recruitment_places.sort(key=self.natural_sort_key)
            
            self.recruitment_place_combo.clear()
            self.recruitment_place_combo.addItem('全部')
            self.recruitment_place_combo.addItems(recruitment_places)
        except Exception as e:
            print(f"加载应征地选项时出错: {e}")
            self.recruitment_place_combo.clear()
            self.recruitment_place_combo.addItem('全部')
    
    def load_company_options(self, recruitment_place_filter='全部'):
        """加载连的选项"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if recruitment_place_filter == '全部':
                cursor.execute('SELECT DISTINCT company FROM youth WHERE company IS NOT NULL AND company != ""')
            else:
                cursor.execute('SELECT DISTINCT company FROM youth WHERE recruitment_place = ? AND company IS NOT NULL AND company != ""', (recruitment_place_filter,))
            
            companies = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # 使用自然排序
            companies.sort(key=self.natural_sort_key)
            
            self.company_combo.clear()
            self.company_combo.addItem('全部')
            self.company_combo.addItems(companies)
        except Exception as e:
            print(f"加载连选项时出错: {e}")
            self.company_combo.clear()
            self.company_combo.addItem('全部')
    
    def load_platoon_options(self, recruitment_place_filter='全部', company_filter='全部'):
        """加载排的选项，根据应征地和连进行筛选"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if recruitment_place_filter != '全部':
                conditions.append('recruitment_place = ?')
                params.append(recruitment_place_filter)
            
            if company_filter != '全部':
                conditions.append('company = ?')
                params.append(company_filter)
            
            conditions.append('platoon IS NOT NULL AND platoon != ""')
            
            where_clause = ' AND '.join(conditions)
            cursor.execute(f'SELECT DISTINCT platoon FROM youth WHERE {where_clause}', params)
            
            platoons = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # 使用自然排序
            platoons.sort(key=self.natural_sort_key)
            
            self.platoon_combo.clear()
            self.platoon_combo.addItem('全部')
            self.platoon_combo.addItems(platoons)
        except Exception as e:
            print(f"加载排选项时出错: {e}")
            self.platoon_combo.clear()
            self.platoon_combo.addItem('全部')
    
    def load_squad_options(self, recruitment_place_filter='全部', company_filter='全部', platoon_filter='全部'):
        """加载班的选项，根据应征地、连和排进行筛选"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if recruitment_place_filter != '全部':
                conditions.append('recruitment_place = ?')
                params.append(recruitment_place_filter)
            
            if company_filter != '全部':
                conditions.append('company = ?')
                params.append(company_filter)
            
            if platoon_filter != '全部':
                conditions.append('platoon = ?')
                params.append(platoon_filter)
            
            sql = 'SELECT DISTINCT squad FROM youth WHERE squad IS NOT NULL AND squad != ""'
            if conditions:
                sql += ' AND ' + ' AND '.join(conditions)
            
            cursor.execute(sql, params)
            squads = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # 使用自然排序
            squads.sort(key=self.natural_sort_key)
            
            self.squad_combo.clear()
            self.squad_combo.addItem('全部')
            self.squad_combo.addItems(squads)
        except Exception as e:
            print(f"加载班选项时出错: {e}")
            self.squad_combo.clear()
            self.squad_combo.addItem('全部')
    
    def on_recruitment_place_changed(self):
        """应征地选择改变时的处理"""
        recruitment_place = self.recruitment_place_combo.currentText()
        # 重新加载连的选项
        self.load_company_options(recruitment_place)
        # 重新加载排的选项
        self.load_platoon_options(recruitment_place, '全部')
        # 重新加载班的选项
        self.load_squad_options(recruitment_place, '全部', '全部')
    
    def on_company_changed(self):
        """连选择改变时的处理"""
        recruitment_place = self.recruitment_place_combo.currentText()
        company = self.company_combo.currentText()
        # 重新加载排的选项
        self.load_platoon_options(recruitment_place, company)
        # 重新加载班的选项
        self.load_squad_options(recruitment_place, company, '全部')
    
    def on_platoon_changed(self):
        """排选择改变时的处理"""
        recruitment_place = self.recruitment_place_combo.currentText()
        company = self.company_combo.currentText()
        platoon = self.platoon_combo.currentText()
        # 重新加载班的选项
        self.load_squad_options(recruitment_place, company, platoon)
    
    def get_filtered_youth_list(self):
        """根据筛选条件获取青年列表"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # 构建查询条件
            conditions = []
            params = []
            
            # 应征地筛选
            if self.recruitment_place_combo.currentText() != '全部':
                conditions.append('recruitment_place = ?')
                params.append(self.recruitment_place_combo.currentText())
            
            # 连筛选
            if self.company_combo.currentText() != '全部':
                conditions.append('company = ?')
                params.append(self.company_combo.currentText())
            
            # 排筛选
            if self.platoon_combo.currentText() != '全部':
                conditions.append('platoon = ?')
                params.append(self.platoon_combo.currentText())
            
            # 班筛选
            if self.squad_combo.currentText() != '全部':
                conditions.append('squad = ?')
                params.append(self.squad_combo.currentText())
            
            # 构建SQL查询
            sql = 'SELECT id, id_card, name FROM youth'
            if conditions:
                sql += ' WHERE ' + ' AND '.join(conditions)
            sql += ' ORDER BY recruitment_place, company, platoon, squad, name'
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            conn.close()
            
            # 转换为所需格式
            youth_list = []
            for row in results:
                youth_info = {
                    'youth_id': row[0],
                    'id_card': row[1],
                    'name': row[2]
                }
                youth_list.append(youth_info)
            
            return youth_list
            
        except Exception as e:
            print(f"获取筛选青年列表时出错: {e}")
            return []
    
    def start_batch_add(self):
        """开始批量添加"""
        try:
            # 根据筛选条件获取青年列表
            selected_youth_list = self.get_filtered_youth_list()
            
            if not selected_youth_list:
                QMessageBox.warning(self, '提示', '根据当前筛选条件没有找到符合条件的青年')
                return
            
            # 获取表单数据
            record_data = {
                'date': self.date_edit.date().toString('yyyy-MM-dd'),
                'mood': self.mood_combo.currentText(),
                'physical_condition': self.physical_combo.currentText(),
                'mental_state': self.mental_combo.currentText(),
                'training': self.training_combo.currentText(),
                'management': self.management_combo.currentText(),
                'notes': self.notes_edit.toPlainText().strip(),
                'overwrite': False  # 默认不覆盖
            }
            
            # 异常数据验证：如果任一状态为异常，其他列不能为空
            is_abnormal = any(status == '异常' for status in [
                record_data['mood'], record_data['physical_condition'], 
                record_data['mental_state'], record_data['training'], 
                record_data['management']
            ])
            if is_abnormal and not record_data['notes']:
                QMessageBox.warning(self, '数据验证失败', 
                                  '当思想、身体、精神、训练或管理任一项为异常时，"其他"列不能为空。\n\n'
                                  '请在"其他"栏中填写相关说明。')
                return
            
            # 检查是否有重复记录
            duplicate_youth = self.check_duplicate_records(record_data['date'], selected_youth_list)
            
            if duplicate_youth:
                # 询问是否覆盖
                duplicate_names = [youth['name'] for youth in duplicate_youth]
                reply = QMessageBox.question(
                    self, '发现重复记录', 
                    f'以下青年在 {record_data["date"]} 已有记录：\n\n' + 
                    '\n'.join(duplicate_names[:10]) + 
                    (f'\n... 等共 {len(duplicate_names)} 人' if len(duplicate_names) > 10 else '') +
                    '\n\n是否要覆盖现有记录？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Cancel:
                    return
                elif reply == QMessageBox.StandardButton.Yes:
                    record_data['overwrite'] = True
            
            # 显示进度条和状态
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(selected_youth_list))
            self.progress_bar.setValue(0)
            self.status_label.setVisible(True)
            self.status_label.setText(f'准备开始批量添加 {len(selected_youth_list)} 个青年的记录...')
            
            # 禁用按钮
            self.start_btn.setEnabled(False)
            self.start_btn.setText('正在处理...')
            
            # 创建并启动工作线程
            self.worker = BatchAddWorker(self.db_manager, selected_youth_list, record_data)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.record_processed.connect(self.record_processed)
            self.worker.finished.connect(self.batch_add_finished)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'开始批量添加时发生错误：{str(e)}')
    
    def check_duplicate_records(self, date, selected_youth_list):
        """检查重复记录"""
        try:
            duplicate_youth = []
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            for youth_info in selected_youth_list:
                cursor.execute('''
                    SELECT id FROM daily_stat 
                    WHERE youth_id = ? AND record_date = ?
                ''', (youth_info['youth_id'], date))
                
                if cursor.fetchone():
                    duplicate_youth.append(youth_info)
            
            conn.close()
            return duplicate_youth
            
        except Exception as e:
            print(f"检查重复记录时出错: {e}")
            return []
    
    def update_progress(self, current, total):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f'正在处理: {current}/{total}')
        QApplication.processEvents()  # 更新界面
    
    def record_processed(self, youth_name, success, message):
        """记录处理完成"""
        # 可以在这里添加详细的处理日志
        pass
    
    def batch_add_finished(self, success_count, fail_count):
        """批量添加完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f'批量添加完成！成功: {success_count}, 失败: {fail_count}')
        
        # 恢复按钮状态
        self.start_btn.setEnabled(True)
        self.start_btn.setText('开始批量添加')
        
        # 发送数据更新信号
        if success_count > 0:
            self.data_updated.emit()
        
        # 显示结果
        if fail_count == 0:
            QMessageBox.information(self, '成功', f'批量添加完成！\n成功添加 {success_count} 条记录。')
        else:
            QMessageBox.warning(self, '部分成功', 
                              f'批量添加完成！\n成功: {success_count} 条\n失败: {fail_count} 条')
        
        if success_count > 0:
            self.accept()
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, '确认关闭', 
                '批量添加正在进行中，确定要关闭吗？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.terminate()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()