"""
谈心谈话基类 - 用于镇街谈心谈话和领导谈心谈话的通用功能
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QCheckBox, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class InterviewBase:
    """谈心谈话基类，提供通用的界面创建和数据操作方法"""
    
    def __init__(self, main_window, interview_type):
        """
        初始化基类
        
        Args:
            main_window: 主窗口实例
            interview_type: 谈话类型 ('town' 或 'leader')
        """
        self.main_window = main_window
        self.interview_type = interview_type
        self.db_manager = main_window.db_manager
        
        # 根据类型设置属性名前缀
        self.prefix = interview_type
        
        # 设置表格和输入框的属性名
        self.table_attr = f'{self.prefix}_interview_table'
        self.name_input_attr = f'{self.prefix}_name_input'
        self.id_card_input_attr = f'{self.prefix}_id_card_input'
        self.select_all_checkbox_attr = f'{self.prefix}_select_all_checkbox'
        
        # 设置方法名
        self.search_method = f'search_{self.prefix}_interview'
        self.reset_search_method = f'reset_{self.prefix}_interview_search'
        self.load_data_method = f'load_{self.prefix}_interview_data'
        self.display_records_method = f'display_{self.prefix}_interview_records'
        self.toggle_select_all_method = f'toggle_{self.prefix}_select_all'
        self.update_select_all_state_method = f'update_{self.prefix}_select_all_state'
        self.add_interview_method = f'add_{self.prefix}_interview'
        self.edit_interview_method = f'edit_{self.prefix}_interview_by_record'
        self.delete_single_method = f'delete_single_{self.prefix}_interview'
        self.batch_delete_method = f'batch_delete_{self.prefix}_interview'
        self.view_image_method = f'view_{self.prefix}_interview_image'
        self.get_selected_data_method = f'get_selected_{self.prefix}_interview_data'
        
        # 设置数据库方法名
        self.db_search_method = f'search_{self.prefix}_interviews'
        self.db_delete_method = f'delete_{self.prefix}_interviews'
        self.db_get_image_method = f'get_{self.prefix}_interview_image'
        
        # 设置显示名称
        if interview_type == 'town':
            self.display_name = '镇街谈心谈话'
        else:
            self.display_name = '领导谈心谈话'
    
    def create_interview_tab(self):
        """创建谈心谈话标签页"""
        tab_widget = QWidget()
        layout = QVBoxLayout()
        
        # 搜索栏
        search_layout = self._create_search_layout()
        layout.addLayout(search_layout)
        
        # 全选按钮行
        select_all_layout = self._create_select_all_layout()
        layout.addLayout(select_all_layout)
        
        # 表格
        table = self._create_table()
        layout.addWidget(table)
        
        # 操作按钮
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)
        
        tab_widget.setLayout(layout)
        return tab_widget
    
    def _create_search_layout(self):
        """创建搜索栏布局"""
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel('搜索:'))
        
        # 姓名输入框
        name_input = QLineEdit()
        name_input.setStyleSheet("""
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                min-height: 30px;
            }
        """)
        name_input.setPlaceholderText('姓名')
        name_input.returnPressed.connect(getattr(self.main_window, self.search_method))
        setattr(self.main_window, self.name_input_attr, name_input)
        search_layout.addWidget(name_input)
        
        # 身份证输入框
        id_card_input = QLineEdit()
        id_card_input.setStyleSheet("""
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                min-height: 30px;
            }
        """)
        id_card_input.setPlaceholderText('身份证号')
        id_card_input.returnPressed.connect(getattr(self.main_window, self.search_method))
        setattr(self.main_window, self.id_card_input_attr, id_card_input)
        search_layout.addWidget(id_card_input)
        
        # 应征地输入框
        recruitment_place_input = QLineEdit()
        recruitment_place_input.setStyleSheet("""
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                min-height: 30px;
            }
        """)
        recruitment_place_input.setPlaceholderText('应征地')
        recruitment_place_input.returnPressed.connect(getattr(self.main_window, self.search_method))
        recruitment_place_input_attr = f'{self.prefix}_recruitment_place_input'
        setattr(self.main_window, recruitment_place_input_attr, recruitment_place_input)
        search_layout.addWidget(recruitment_place_input)
        
        # 连输入框
        company_input = QLineEdit()
        company_input.setStyleSheet("""
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                min-height: 30px;
            }
        """)
        company_input.setPlaceholderText('连')
        company_input.returnPressed.connect(getattr(self.main_window, self.search_method))
        company_input_attr = f'{self.prefix}_company_input'
        setattr(self.main_window, company_input_attr, company_input)
        search_layout.addWidget(company_input)
        
        # 排输入框
        platoon_input = QLineEdit()
        platoon_input.setStyleSheet("""
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                min-height: 30px;
            }
        """)
        platoon_input.setPlaceholderText('排')
        platoon_input.returnPressed.connect(getattr(self.main_window, self.search_method))
        platoon_input_attr = f'{self.prefix}_platoon_input'
        setattr(self.main_window, platoon_input_attr, platoon_input)
        search_layout.addWidget(platoon_input)
        
        # 班输入框
        squad_input = QLineEdit()
        squad_input.setStyleSheet("""
            QLineEdit {
                font-size: 11pt;
                padding: 8px;
                min-height: 30px;
            }
        """)
        squad_input.setPlaceholderText('班')
        squad_input.returnPressed.connect(getattr(self.main_window, self.search_method))
        squad_input_attr = f'{self.prefix}_squad_input'
        setattr(self.main_window, squad_input_attr, squad_input)
        search_layout.addWidget(squad_input)
        
        # 搜索按钮
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(getattr(self.main_window, self.search_method))
        self.main_window.setup_button_style(search_btn, 'primary')
        search_layout.addWidget(search_btn)
        
        # 重置按钮
        reset_btn = QPushButton('重置')
        reset_btn.clicked.connect(getattr(self.main_window, self.reset_search_method))
        self.main_window.setup_button_style(reset_btn, 'normal')
        search_layout.addWidget(reset_btn)
        
        return search_layout
    
    def _create_select_all_layout(self):
        """创建全选按钮布局"""
        select_all_layout = QHBoxLayout()
        
        select_all_checkbox = QCheckBox('全选')
        select_all_checkbox.stateChanged.connect(getattr(self.main_window, self.toggle_select_all_method))
        select_all_checkbox.setStyleSheet("""
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
        setattr(self.main_window, self.select_all_checkbox_attr, select_all_checkbox)
        select_all_layout.addWidget(select_all_checkbox)
        select_all_layout.addStretch()
        
        return select_all_layout
    
    def _create_table(self):
        """创建表格"""
        from PyQt5.QtWidgets import QHeaderView
        
        table = QTableWidget()
        headers = ['选择', '日期', '姓名', '性别', '公民身份号码', '应征地', '连', '排', '班', '带训班长信息', '思想', '精神', '走访调查情况', '操作', '删除']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 应用统一的表格样式
        self.main_window.setup_table_style(table)
        
        # 设置表格列宽策略 - 采用与病史筛查情况相同的设置
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # 允许手动调整
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 选择列
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 日期列
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 姓名列
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 性别列
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 身份证列
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 应征地列
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 连列
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 排列
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # 班列
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # 带训班长信息列
        header.setSectionResizeMode(10, QHeaderView.Stretch)  # 思想列自动拉伸
        header.setSectionResizeMode(11, QHeaderView.ResizeToContents)  # 精神列
        header.setSectionResizeMode(12, QHeaderView.ResizeToContents)  # 走访调查情况列
        header.setSectionResizeMode(13, QHeaderView.ResizeToContents)  # 操作列
        header.setSectionResizeMode(14, QHeaderView.ResizeToContents)  # 删除列
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 设置表格属性到主窗口
        setattr(self.main_window, self.table_attr, table)
        
        return table
    
    def _create_button_layout(self):
        """创建操作按钮布局"""
        button_layout = QHBoxLayout()
        
        # 添加信息按钮
        add_btn = QPushButton('添加信息')
        add_btn.clicked.connect(getattr(self.main_window, self.add_interview_method))
        self.main_window.setup_button_style(add_btn, 'normal')
        button_layout.addWidget(add_btn)
        
        # 导入文件按钮
        import_btn = QPushButton('批量导入文件')
        import_method_name = f'import_{self.prefix}_interview_files'
        import_btn.clicked.connect(getattr(self.main_window, import_method_name))
        self.main_window.setup_button_style(import_btn, 'normal')
        button_layout.addWidget(import_btn)
        
        # 导出数据按钮
        export_btn = QPushButton('导出数据')
        export_btn.clicked.connect(lambda: self.main_window.export_data(f'{self.display_name}情况'))
        self.main_window.setup_button_style(export_btn, 'normal')
        button_layout.addWidget(export_btn)
        
        # 批量删除按钮
        batch_delete_btn = QPushButton('批量删除')
        self.main_window.setup_button_style(batch_delete_btn, 'danger')
        batch_delete_btn.clicked.connect(getattr(self.main_window, self.batch_delete_method))
        button_layout.addWidget(batch_delete_btn)
        
        # 刷新按钮
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(getattr(self.main_window, self.load_data_method))
        self.main_window.setup_button_style(refresh_btn, 'normal')
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        return button_layout
    
    def load_interview_data(self):
        """加载谈心谈话数据到表格"""
        try:
            # 获取时间筛选条件
            time_condition, time_params = self.main_window.get_time_filter_condition("interview_date")
            
            # 获取数据
            db_method = getattr(self.db_manager, self.db_search_method)
            records = db_method(time_condition=time_condition, time_params=time_params)
            
            # 显示数据
            display_method = getattr(self.main_window, self.display_records_method)
            display_method(records)
            
        except Exception as e:
            QMessageBox.warning(self.main_window, "加载错误", f"加载{self.display_name}数据时发生错误：{str(e)}")
    
    def search_interview(self):
        """搜索谈心谈话记录"""
        try:
            # 重置全选按钮状态
            select_all_checkbox = getattr(self.main_window, self.select_all_checkbox_attr)
            if hasattr(self.main_window, self.select_all_checkbox_attr):
                # 临时断开信号连接，避免触发全选操作
                select_all_checkbox.stateChanged.disconnect()
                select_all_checkbox.setCheckState(Qt.CheckState.Unchecked)
                # 重新连接信号
                select_all_checkbox.stateChanged.connect(getattr(self.main_window, self.toggle_select_all_method))
            
            # 获取搜索条件
            name_input = getattr(self.main_window, self.name_input_attr)
            id_card_input = getattr(self.main_window, self.id_card_input_attr)
            recruitment_place_input = getattr(self.main_window, f'{self.prefix}_recruitment_place_input')
            company_input = getattr(self.main_window, f'{self.prefix}_company_input')
            platoon_input = getattr(self.main_window, f'{self.prefix}_platoon_input')
            squad_input = getattr(self.main_window, f'{self.prefix}_squad_input')
            
            name = name_input.text().strip()
            id_card = id_card_input.text().strip()
            recruitment_place = recruitment_place_input.text().strip()
            company = company_input.text().strip()
            platoon = platoon_input.text().strip()
            squad = squad_input.text().strip()
            
            db_method = getattr(self.db_manager, self.db_search_method)
            records = db_method(name=name, id_card=id_card, recruitment_place=recruitment_place, 
                              company=company, platoon=platoon, squad=squad)
            
            display_method = getattr(self.main_window, self.display_records_method)
            display_method(records)
            
        except Exception as e:
            QMessageBox.warning(self.main_window, "搜索错误", f"搜索{self.display_name}记录时发生错误：{str(e)}")
            # 确保信号重新连接
            try:
                select_all_checkbox = getattr(self.main_window, self.select_all_checkbox_attr)
                if hasattr(self.main_window, self.select_all_checkbox_attr):
                    select_all_checkbox.stateChanged.connect(getattr(self.main_window, self.toggle_select_all_method))
            except:
                pass
    
    def reset_interview_search(self):
        """重置谈心谈话搜索"""
        try:
            # 重置全选按钮状态
            select_all_checkbox = getattr(self.main_window, self.select_all_checkbox_attr)
            if hasattr(self.main_window, self.select_all_checkbox_attr):
                # 临时断开信号连接，避免触发全选操作
                select_all_checkbox.stateChanged.disconnect()
                select_all_checkbox.setCheckState(Qt.CheckState.Unchecked)
                # 重新连接信号
                select_all_checkbox.stateChanged.connect(getattr(self.main_window, self.toggle_select_all_method))
            
            # 清空所有搜索输入框
            name_input = getattr(self.main_window, self.name_input_attr)
            id_card_input = getattr(self.main_window, self.id_card_input_attr)
            recruitment_place_input = getattr(self.main_window, f'{self.prefix}_recruitment_place_input')
            company_input = getattr(self.main_window, f'{self.prefix}_company_input')
            platoon_input = getattr(self.main_window, f'{self.prefix}_platoon_input')
            squad_input = getattr(self.main_window, f'{self.prefix}_squad_input')
            
            name_input.clear()
            id_card_input.clear()
            recruitment_place_input.clear()
            company_input.clear()
            platoon_input.clear()
            squad_input.clear()
            
            load_method = getattr(self.main_window, self.load_data_method)
            load_method()
            
        except Exception as e:
            QMessageBox.warning(self.main_window, "重置错误", f"重置搜索时发生错误：{str(e)}")
            # 确保信号重新连接
            try:
                select_all_checkbox = getattr(self.main_window, self.select_all_checkbox_attr)
                if hasattr(self.main_window, self.select_all_checkbox_attr):
                    select_all_checkbox.stateChanged.connect(getattr(self.main_window, self.toggle_select_all_method))
            except:
                pass
    
    def display_interview_records(self, records):
        """显示谈心谈话记录"""
        try:
            table = getattr(self.main_window, self.table_attr)
            table.setRowCount(len(records))
            
            for row, record in enumerate(records):
                # record格式: (id, youth_id_card, youth_name, gender, interview_date, 
                #              enlistment_place, company, platoon, squad, squad_leader,
                #              thoughts, spirit, created_at)
                
                # 检查是否为异常数据（思想或精神任一个为异常）
                thoughts_status = str(record[10] or '').strip()
                spirit_status = str(record[11] or '').strip()
                is_abnormal = '异常' in thoughts_status or '异常' in spirit_status
                
                # 选择框
                checkbox = QCheckBox()
                checkbox.setStyleSheet("""
                    QCheckBox {
                        spacing: 0px;
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
                checkbox.setMinimumSize(24, 24)
                
                # 添加状态变化监听
                checkbox.stateChanged.connect(getattr(self.main_window, self.update_select_all_state_method))
                
                checkbox_layout = QHBoxLayout()
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(5, 5, 5, 5)
                checkbox_layout.addWidget(checkbox)
                checkbox_container = QWidget()
                checkbox_container.setLayout(checkbox_layout)
                table.setCellWidget(row, 0, checkbox_container)
                
                # 日期
                item = QTableWidgetItem(str(record[4] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))  # 淡红色背景
                table.setItem(row, 1, item)
                
                # 姓名
                item = QTableWidgetItem(str(record[2] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 2, item)
                
                # 性别
                item = QTableWidgetItem(str(record[3] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 3, item)
                
                # 公民身份号码
                item = QTableWidgetItem(str(record[1] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 4, item)
                
                # 应征地
                item = QTableWidgetItem(str(record[5] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 5, item)
                
                # 连
                item = QTableWidgetItem(str(record[6] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 6, item)
                
                # 排
                item = QTableWidgetItem(str(record[7] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 7, item)
                
                # 班
                item = QTableWidgetItem(str(record[8] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 8, item)
                
                # 带训班长信息
                item = QTableWidgetItem(str(record[9] or ''))
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 9, item)
                
                # 思想（截断长文本）
                thoughts = record[10][:50] + "..." if record[10] and len(record[10]) > 50 else (record[10] or "")
                item = QTableWidgetItem(thoughts)
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 10, item)
                
                # 精神（截断长文本）
                spirit = record[11][:50] + "..." if record[11] and len(record[11]) > 50 else (record[11] or "")
                item = QTableWidgetItem(spirit)
                if is_abnormal:
                    item.setBackground(QColor(255, 182, 193, 100))
                table.setItem(row, 11, item)
                
                # 走访调查情况（查看文件按钮）
                try:
                    db_get_image_method = getattr(self.db_manager, self.db_get_image_method)
                    image_data = db_get_image_method(record[0])
                    if image_data:
                        view_image_btn = QPushButton('查看文件')
                        view_image_btn.setStyleSheet('background-color: #ADD8E6;')  # 淡蓝色
                        view_image_btn.clicked.connect(lambda checked, rid=record[0]: getattr(self.main_window, self.view_image_method)(rid))
                    else:
                        view_image_btn = QPushButton('无文件')
                        view_image_btn.setEnabled(False)
                        view_image_btn.setStyleSheet("color: gray;")
                except:
                    view_image_btn = QPushButton('无文件')
                    view_image_btn.setEnabled(False)
                    view_image_btn.setStyleSheet("color: gray;")
                
                view_image_btn_layout = QHBoxLayout()
                view_image_btn_layout.setAlignment(Qt.AlignCenter)
                view_image_btn_layout.setContentsMargins(2, 2, 2, 2)
                view_image_btn_layout.addWidget(view_image_btn, 1)
                view_image_btn_container = QWidget()
                view_image_btn_container.setLayout(view_image_btn_layout)
                
                # 如果是异常数据，给按钮容器也设置背景色
                if is_abnormal:
                    view_image_btn_container.setStyleSheet("background-color: rgba(255, 182, 193, 100);")
                
                table.setCellWidget(row, 12, view_image_btn_container)
                
                # 操作按钮（编辑信息）
                edit_btn = QPushButton('编辑信息')
                edit_btn.setStyleSheet("background-color: #ADD8E6;")  # 淡蓝色
                edit_btn.clicked.connect(lambda checked, record_data=record: getattr(self.main_window, self.edit_interview_method)(record_data))
                edit_btn_layout = QHBoxLayout()
                edit_btn_layout.setAlignment(Qt.AlignCenter)
                edit_btn_layout.setContentsMargins(5, 5, 5, 5)
                edit_btn_layout.addWidget(edit_btn)
                edit_btn_container = QWidget()
                edit_btn_container.setLayout(edit_btn_layout)
                
                # 如果是异常数据，给按钮容器也设置背景色
                if is_abnormal:
                    edit_btn_container.setStyleSheet("background-color: rgba(255, 182, 193, 100);")
                
                table.setCellWidget(row, 13, edit_btn_container)
                
                # 删除按钮
                delete_btn = QPushButton('删除')
                delete_btn.setStyleSheet("background-color: #FFB6C1;")  # 淡红色
                delete_btn.clicked.connect(lambda checked, record_data=record: getattr(self.main_window, self.delete_single_method)(record_data))
                delete_btn_layout = QHBoxLayout()
                delete_btn_layout.setAlignment(Qt.AlignCenter)
                delete_btn_layout.setContentsMargins(5, 5, 5, 5)
                delete_btn_layout.addWidget(delete_btn)
                delete_btn_container = QWidget()
                delete_btn_container.setLayout(delete_btn_layout)
                
                # 如果是异常数据，给按钮容器也设置背景色
                if is_abnormal:
                    delete_btn_container.setStyleSheet("background-color: rgba(255, 182, 193, 100);")
                
                table.setCellWidget(row, 14, delete_btn_container)
            
        except Exception as e:
            QMessageBox.warning(self.main_window, "显示错误", f"显示{self.display_name}记录时发生错误：{str(e)}")

    
    def toggle_select_all(self, state):
        """全选/取消全选"""
        is_checked = (state == Qt.CheckState.Checked.value)
        
        # 临时标记，防止在全选操作时触发单个复选框的状态更新
        setattr(self.main_window, f'_updating_{self.prefix}_select_all', True)
        
        table = getattr(self.main_window, self.table_attr)
        for row in range(table.rowCount()):
            checkbox_widget = table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(is_checked)
        
        # 重置标记
        setattr(self.main_window, f'_updating_{self.prefix}_select_all', False)
    
    def update_select_all_state(self):
        """更新全选按钮状态"""
        # 如果正在执行全选操作，则不更新全选按钮状态
        if getattr(self.main_window, f'_updating_{self.prefix}_select_all', False):
            return
        
        try:
            table = getattr(self.main_window, self.table_attr)
            select_all_checkbox = getattr(self.main_window, self.select_all_checkbox_attr)
            
            total_rows = table.rowCount()
            if total_rows == 0:
                return
            
            checked_count = 0
            for row in range(total_rows):
                checkbox_widget = table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        checked_count += 1
            
            # 临时断开全选按钮的信号连接
            select_all_checkbox.stateChanged.disconnect()
            
            # 更新全选按钮状态
            if checked_count == 0:
                select_all_checkbox.setCheckState(Qt.CheckState.Unchecked)
            elif checked_count == total_rows:
                select_all_checkbox.setCheckState(Qt.CheckState.Checked)
            else:
                select_all_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
            
            # 重新连接信号
            select_all_checkbox.stateChanged.connect(getattr(self.main_window, self.toggle_select_all_method))
            
        except Exception as e:
            print(f"更新{self.display_name}全选按钮状态时出错: {e}")
            # 确保信号重新连接
            try:
                select_all_checkbox = getattr(self.main_window, self.select_all_checkbox_attr)
                select_all_checkbox.stateChanged.connect(getattr(self.main_window, self.toggle_select_all_method))
            except:
                pass
    
    def add_interview(self):
        """添加谈心谈话记录"""
        try:
            from ui.interview_dialog import InterviewDialog
            dialog = InterviewDialog(self.db_manager, self.main_window, None, self.interview_type)
            if dialog.exec_():
                load_method = getattr(self.main_window, self.load_data_method)
                load_method()
        except Exception as e:
            QMessageBox.warning(self.main_window, '错误', f'打开添加{self.display_name}对话框时发生错误: {str(e)}')
    
    def edit_interview_by_record(self, record_data):
        """根据记录数据编辑谈心谈话记录"""
        try:
            from ui.interview_dialog import InterviewDialog
            dialog = InterviewDialog(self.db_manager, self.main_window, record_data, self.interview_type)
            if dialog.exec_():
                load_method = getattr(self.main_window, self.load_data_method)
                load_method()
        except Exception as e:
            QMessageBox.warning(self.main_window, '错误', f'编辑{self.display_name}记录时发生错误: {str(e)}')
    
    def delete_single_interview(self, record_data):
        """删除单个谈心谈话记录"""
        try:
            # record_data格式: (id, youth_id_card, youth_name, gender, interview_date, thoughts, spirit, created_at)
            record_id = record_data[0]
            youth_name = record_data[2]
            
            reply = QMessageBox.question(
                self.main_window,
                '确认删除',
                f'确定要删除 {youth_name} 的{self.display_name}记录吗？\n删除后无法恢复！',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                db_delete_method = getattr(self.db_manager, self.db_delete_method)
                deleted_count = db_delete_method([record_id])
                if deleted_count > 0:
                    QMessageBox.information(self.main_window, '删除成功', '记录已删除')
                    load_method = getattr(self.main_window, self.load_data_method)
                    load_method()
                else:
                    QMessageBox.warning(self.main_window, '删除失败', '未能删除记录')
                    
        except Exception as e:
            QMessageBox.critical(self.main_window, '删除失败', f'删除{self.display_name}记录时发生错误：{str(e)}')
    
    def batch_delete_interview(self):
        """批量删除谈心谈话记录"""
        try:
            table = getattr(self.main_window, self.table_attr)
            
            # 获取选中的记录
            selected_rows = []
            for row in range(table.rowCount()):
                checkbox_widget = table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        selected_rows.append(row)
            
            if not selected_rows:
                QMessageBox.warning(self.main_window, "提示", "请选择要删除的记录")
                return
            
            # 获取所有记录，根据选中行号找到对应的记录ID
            db_search_method = getattr(self.db_manager, self.db_search_method)
            records = db_search_method()
            selected_ids = []
            selected_names = []
            
            for row in selected_rows:
                if row < len(records):
                    record = records[row]
                    selected_ids.append(record[0])  # record[0] 是 id
                    selected_names.append(record[2])  # record[2] 是 youth_name
            
            if not selected_ids:
                QMessageBox.warning(self.main_window, "错误", "找不到要删除的记录")
                return
            
            # 确认删除
            names_text = '、'.join(selected_names[:5])
            if len(selected_names) > 5:
                names_text += f' 等{len(selected_names)}人'
            
            reply = QMessageBox.question(
                self.main_window,
                '确认批量删除',
                f'确定要删除以下{self.display_name}记录吗？\n{names_text}\n\n共{len(selected_ids)}条记录，删除后无法恢复！',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                db_delete_method = getattr(self.db_manager, self.db_delete_method)
                deleted_count = db_delete_method(selected_ids)
                QMessageBox.information(self.main_window, '删除成功', f'成功删除 {deleted_count} 条记录')
                
                # 取消全选
                select_all_checkbox = getattr(self.main_window, self.select_all_checkbox_attr)
                if hasattr(self.main_window, self.select_all_checkbox_attr):
                    select_all_checkbox.setChecked(False)
                
                load_method = getattr(self.main_window, self.load_data_method)
                load_method()
                
        except Exception as e:
            QMessageBox.critical(self.main_window, '批量删除失败', f'批量删除{self.display_name}记录时发生错误：{str(e)}')
    
    def view_interview_image(self, record_id):
        """查看谈心谈话文件"""
        try:
            db_get_image_method = getattr(self.db_manager, self.db_get_image_method)
            image_data = db_get_image_method(record_id)
            if not image_data:
                QMessageBox.information(self.main_window, "提示", "该记录没有文件")
                return
            
            from ui.image_viewer_dialog import ImageViewerDialog
            dialog = ImageViewerDialog(image_data, "走访调查文件", self.main_window)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"查看文件失败: {str(e)}")
    
    def get_selected_interview_data(self):
        """获取选中的谈心谈话数据"""
        try:
            selected_data = []
            table = getattr(self.main_window, self.table_attr)
            
            # 获取所有数据用于对照
            db_search_method = getattr(self.db_manager, self.db_search_method)
            all_records = db_search_method()
            
            # 检查选中的行
            for row in range(table.rowCount()):
                checkbox_widget = table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and checkbox.isChecked():
                        if row < len(all_records):
                            selected_data.append(all_records[row])
            
            return selected_data
            
        except Exception as e:
            print(f"获取选中{self.display_name}数据时出错: {e}")
            return []