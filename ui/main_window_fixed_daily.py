    def load_daily_stats_data(self):
        """加载每日情况统计数据"""
        try:
            if '每日情况统计' not in self.tab_tables:
                return
                
            table = self.tab_tables['每日情况统计']
            
            # 设置表头 - 在姓名后面添加应征地
            headers = ['选择', '公民身份证号码', '姓名', '应征地', '连', '排', '班', '带训班长信息', '日期', '思想', '身体', '精神', '训练', '管理', '其他', '修改', '删除']
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            # 获取数据 - 包含应征地字段
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT d.id, y.id_card, y.name, y.recruitment_place, y.company, y.platoon, y.squad, y.squad_leader,
                       d.record_date, d.mood, d.physical_condition, d.mental_state, d.training, d.management, d.notes, d.youth_id
                FROM daily_stat d
                JOIN youth y ON d.youth_id = y.id
                ORDER BY d.id ASC
            ''')
            results = cursor.fetchall()
            conn.close()
            
            # 显示数据
            table.setRowCount(len(results))
            for row, data in enumerate(results):
                # 数据库返回字段顺序：
                # 0:d.id, 1:y.id_card, 2:y.name, 3:y.recruitment_place, 4:y.company, 5:y.platoon, 6:y.squad, 7:y.squad_leader,
                # 8:d.record_date, 9:d.mood, 10:d.physical_condition, 11:d.mental_state, 12:d.training, 13:d.management, 14:d.notes, 15:d.youth_id
                
                # 检查是否有异常状态
                has_abnormal = any(str(data[i]) == '异常' for i in [9, 10, 11, 12, 13])  # mood, physical, mental, training, management
                
                # 第一列：复选框
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
                checkbox.stateChanged.connect(self.update_daily_select_all_state)
                
                checkbox_layout = QHBoxLayout()
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(5, 5, 5, 5)
                checkbox_layout.addWidget(checkbox)
                checkbox_container = QWidget()
                checkbox_container.setLayout(checkbox_layout)
                table.setCellWidget(row, 0, checkbox_container)
                
                # 第二列：公民身份证号码
                item = QTableWidgetItem(str(data[1] or ''))
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 1, item)
                
                # 第三列：姓名
                item = QTableWidgetItem(str(data[2] or ''))
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 2, item)
                
                # 第四列：应征地
                item = QTableWidgetItem(str(data[3] or ''))
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 3, item)
                
                # 第五列：连
                item = QTableWidgetItem(str(data[4] or ''))
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 4, item)
                
                # 第六列：排
                item = QTableWidgetItem(str(data[5] or ''))
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 5, item)
                
                # 第七列：班
                item = QTableWidgetItem(str(data[6] or ''))
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 6, item)
                
                # 第八列：带训班长信息
                item = QTableWidgetItem(str(data[7] or ''))
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 7, item)
                
                # 第九列：日期
                date_value = data[8]
                if date_value:
                    try:
                        from datetime import datetime
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                        else:
                            formatted_date = str(date_value)
                        item = QTableWidgetItem(formatted_date)
                    except:
                        item = QTableWidgetItem(str(date_value or ''))
                else:
                    item = QTableWidgetItem('')
                
                if has_abnormal:
                    from PyQt5.QtGui import QColor
                    item.setForeground(QColor('red'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                table.setItem(row, 8, item)
                
                # 第十到十五列：状态字段 (思想、身体、精神、训练、管理、其他)
                status_fields = [data[9], data[10], data[11], data[12], data[13], data[14]]  # mood, physical, mental, training, management, notes
                for col, value in enumerate(status_fields, 9):
                    item = QTableWidgetItem(str(value or ''))
                    if has_abnormal:
                        from PyQt5.QtGui import QColor
                        item.setForeground(QColor('red'))
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    table.setItem(row, col, item)
                
                # 第十六列：修改按钮
                edit_btn = QPushButton('修改')
                edit_btn.setStyleSheet('background-color: #ADD8E6;')  # 淡蓝色
                edit_btn.clicked.connect(lambda checked, record_id=data[0], youth_id=data[15]: self.edit_daily_record(record_id, youth_id))
                edit_btn_layout = QHBoxLayout()
                edit_btn_layout.setAlignment(Qt.AlignCenter)
                edit_btn_layout.setContentsMargins(5, 5, 5, 5)
                edit_btn_layout.addWidget(edit_btn)
                edit_btn_container = QWidget()
                edit_btn_container.setLayout(edit_btn_layout)
                table.setCellWidget(row, 15, edit_btn_container)
                
                # 第十七列：删除按钮
                del_btn = QPushButton('删除')
                del_btn.setStyleSheet('background-color: #FFB6C1;')  # 淡红色
                del_btn.clicked.connect(lambda checked, record_id=data[0]: self.delete_daily_record(record_id))
                del_btn_layout = QHBoxLayout()
                del_btn_layout.setAlignment(Qt.AlignCenter)
                del_btn_layout.setContentsMargins(5, 5, 5, 5)
                del_btn_layout.addWidget(del_btn)
                del_btn_container = QWidget()
                del_btn_container.setLayout(del_btn_layout)
                table.setCellWidget(row, 16, del_btn_container)
            
            # 设置表格自适应屏幕
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Interactive)  # 允许手动调整
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 选择列
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # 公民身份证号码列
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 姓名列
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 应征地列
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 连列
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 排列
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 班列
            header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 带训班长信息列
            header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # 日期列
            header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # 思想列
            header.setSectionResizeMode(10, QHeaderView.ResizeToContents)  # 身体列
            header.setSectionResizeMode(11, QHeaderView.ResizeToContents)  # 精神列
            header.setSectionResizeMode(12, QHeaderView.ResizeToContents)  # 训练列
            header.setSectionResizeMode(13, QHeaderView.ResizeToContents)  # 管理列
            header.setSectionResizeMode(14, QHeaderView.Stretch)  # 其他列
            header.setSectionResizeMode(15, QHeaderView.ResizeToContents)  # 修改列
            header.setSectionResizeMode(16, QHeaderView.ResizeToContents)  # 删除列
            header.setStretchLastSection(False)
            
        except Exception as e:
            QMessageBox.warning(self, "加载错误", f"加载每日情况统计数据时发生错误：{str(e)}")