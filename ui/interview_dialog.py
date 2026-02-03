"""
通用谈心谈话对话框 - 支持镇街谈心谈话和领导谈心谈话
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QDateEdit,
                             QComboBox, QMessageBox, QFrame, QFileDialog,
                             QWidget, QCompleter)
from PyQt5.QtCore import Qt, QDate, QStringListModel
from PyQt5.QtGui import QFont
from datetime import datetime
import os


class InterviewDialog(QDialog):
    """通用谈心谈话对话框"""
    
    def __init__(self, db_manager, parent=None, record_data=None, interview_type='town'):
        """
        初始化对话框
        
        Args:
            db_manager: 数据库管理器
            parent: 父窗口
            record_data: 记录数据（编辑模式时使用）
            interview_type: 谈话类型 ('town' 或 'leader')
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.record_data = record_data
        self.interview_type = interview_type
        self.image_data = None
        
        # 根据类型设置相关属性
        if interview_type == 'town':
            self.display_name = '镇街谈心谈话'
            self.db_get_image_method = 'get_town_interview_image'
            self.db_update_method = 'update_town_interview'
            self.db_insert_method = 'insert_town_interview'
        else:  # leader
            self.display_name = '领导谈心谈话'
            self.db_get_image_method = 'get_leader_interview_image'
            self.db_update_method = 'update_leader_interview'
            self.db_insert_method = 'insert_leader_interview'
        
        self.init_ui()
        
        if record_data:
            self.load_record_data()
    
    def init_ui(self):
        """初始化用户界面"""
        title = f"编辑{self.display_name}记录" if self.record_data else f"添加{self.display_name}记录"
        self.setWindowTitle(title)
        self.setGeometry(200, 100, 600, 500)
        
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
        
        # 青年选择
        youth_layout = QHBoxLayout()
        youth_layout.addWidget(QLabel("选择青年:"))
        self.youth_combo = QComboBox()
        self.youth_combo.setEditable(True)  # 允许输入
        self.youth_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # 不插入新项
        
        # 设置下拉框宽度
        self.youth_combo.setMinimumWidth(400)  # 设置最小宽度
        self.youth_combo.setMaximumWidth(500)  # 设置最大宽度
        
        # 设置自动完成
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.youth_combo.setCompleter(self.completer)
        
        self.youth_combo.currentTextChanged.connect(self.on_youth_changed)
        youth_layout.addWidget(self.youth_combo)
        youth_layout.addStretch()
        form_layout.addLayout(youth_layout)
        
        # 性别（自动填充）
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("性别:"))
        self.gender_input = QLineEdit()
        self.gender_input.setReadOnly(True)
        gender_layout.addWidget(self.gender_input)
        gender_layout.addStretch()
        form_layout.addLayout(gender_layout)
        
        # 走访调查情况（文件）
        image_layout = QVBoxLayout()
        image_label_layout = QHBoxLayout()
        image_label_layout.addWidget(QLabel("走访调查情况:"))
        
        # 添加文件格式说明
        format_label = QLabel("(支持格式: .pdf, .jpg, .png, .bmp, .gif, .tiff)")
        format_label.setStyleSheet("color: #666666; font-size: 9pt;")
        image_label_layout.addWidget(format_label)
        
        image_label_layout.addStretch()
        image_layout.addLayout(image_label_layout)
        
        # 文件按钮
        image_btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("导入文件")
        import_btn.clicked.connect(self.import_file)
        image_btn_layout.addWidget(import_btn)
        
        view_btn = QPushButton("查看文件")
        view_btn.clicked.connect(self.view_image)
        image_btn_layout.addWidget(view_btn)
        
        delete_btn = QPushButton("删除文件")
        delete_btn.clicked.connect(self.delete_image)
        image_btn_layout.addWidget(delete_btn)
        
        image_btn_layout.addStretch()
        image_layout.addLayout(image_btn_layout)
        
        # 文件状态标签
        self.image_status_label = QLabel("未选择文件")
        self.image_status_label.setStyleSheet("color: gray;")
        image_layout.addWidget(self.image_status_label)
        
        form_layout.addLayout(image_layout)
        
        # 思想
        form_layout.addWidget(QLabel("思想:"))
        self.thoughts_combo = QComboBox()
        self.thoughts_combo.addItems(["正常", "异常"])
        form_layout.addWidget(self.thoughts_combo)
        
        # 精神
        form_layout.addWidget(QLabel("精神:"))
        self.spirit_combo = QComboBox()
        self.spirit_combo.addItems(["正常", "异常"])
        form_layout.addWidget(self.spirit_combo)
        
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
        
        # 加载青年选项
        self.load_youth_options()
    
    def load_youth_options(self):
        """加载青年选项"""
        try:
            youth_options = self.db_manager.get_youth_options()
            
            # 存储完整的青年信息
            self.youth_data = {}
            
            options = []
            
            for option in youth_options:
                id_card, name, gender = option
                if name and id_card:
                    option_text = f"{name}（{id_card}）"
                    options.append(option_text)
                    self.youth_data[option_text] = {
                        'id_card': id_card,
                        'name': name,
                        'gender': gender
                    }
            
            # 按拼音排序选项
            try:
                import pypinyin
                options.sort(key=lambda x: ''.join(pypinyin.lazy_pinyin(x.split('（')[0])))
            except ImportError:
                # 如果没有pypinyin，按字符排序
                options.sort()
            
            # 存储所有选项用于过滤
            self.all_options = options.copy()
            
            self.youth_combo.addItems(options)
            
            # 设置自动完成模型
            model = QStringListModel(options)
            self.completer.setModel(model)
            
            # 连接文本变化事件，实现动态过滤
            self.youth_combo.lineEdit().textChanged.connect(self.filter_youth_options)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载青年信息失败: {str(e)}")
    
    def filter_youth_options(self, text):
        """根据输入文本过滤青年选项"""
        if not text:
            return
        
        try:
            # 获取所有选项
            all_options = list(self.youth_data.keys())
            
            # 过滤选项
            filtered_options = [
                option for option in all_options 
                if text.lower() in option.lower()
            ]
            
            # 更新自动完成模型
            model = QStringListModel(filtered_options)
            self.completer.setModel(model)
            
        except Exception as e:
            print(f"过滤青年选项时出错: {e}")
    
    def on_youth_changed(self, option_text):
        """青年选择改变事件"""
        if option_text in self.youth_data:
            youth_info = self.youth_data[option_text]
            self.gender_input.setText(youth_info['gender'])
    
    def import_file(self):
        """导入文件（支持图片和PDF）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "",
            "支持的文件 (*.pdf *.jpg *.jpeg *.png *.bmp *.gif *.tiff);;PDF文件 (*.pdf);;图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.tiff);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                filename = os.path.basename(file_path)
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext == '.pdf':
                    # 处理PDF文件
                    self.image_data = self.convert_pdf_to_jpg(file_path)
                    if self.image_data:
                        self.image_status_label.setText(f"已选择: {filename}")
                        self.image_status_label.setStyleSheet("color: green;")
                        QMessageBox.information(self, "成功", "文件导入成功！")
                    else:
                        QMessageBox.critical(self, "错误", "PDF文件转换失败！")
                        return
                else:
                    # 处理图片文件
                    with open(file_path, 'rb') as f:
                        self.image_data = f.read()
                    
                    self.image_status_label.setText(f"已选择: {filename}")
                    self.image_status_label.setStyleSheet("color: green;")
                    QMessageBox.information(self, "成功", "文件导入成功！")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入文件失败: {str(e)}")
    
    def convert_pdf_to_jpg(self, pdf_path):
        """将PDF文件转换为JPG图片"""
        try:
            # 尝试导入pdf2image库
            try:
                from pdf2image import convert_from_path
            except ImportError:
                QMessageBox.critical(self, "错误", 
                    "缺少pdf2image库，无法处理PDF文件。\n"
                    "请安装：pip install pdf2image\n"
                    "注意：还需要安装poppler工具。")
                return None
            
            # 转换PDF的第一页为图片
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=200)
            
            if not images:
                return None
            
            # 将PIL图片转换为字节数据
            import io
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr = img_byte_arr.getvalue()
            
            return img_byte_arr
            
        except Exception as e:
            print(f"PDF转换错误: {e}")
            return None
    
    def view_image(self):
        """查看文件"""
        if not self.image_data:
            QMessageBox.warning(self, "提示", "没有可查看的文件")
            return
        
        try:
            from ui.image_viewer_dialog import ImageViewerDialog
            dialog = ImageViewerDialog(self.image_data, "走访调查文件", self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查看文件失败: {str(e)}")
    
    def delete_image(self):
        """删除文件"""
        if self.image_data:
            reply = QMessageBox.question(
                self, "确认", "确定要删除当前文件吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.image_data = None
                self.image_status_label.setText("未选择文件")
                self.image_status_label.setStyleSheet("color: gray;")
                QMessageBox.information(self, "成功", "文件已删除")
        else:
            QMessageBox.information(self, "提示", "没有可删除的文件")
    
    def load_record_data(self):
        """加载记录数据（编辑模式）"""
        if self.record_data:
            # record_data格式: (id, youth_id_card, youth_name, gender, interview_date, thoughts, spirit, created_at)
            
            # 设置日期
            if self.record_data[4]:  # interview_date
                try:
                    date_obj = datetime.strptime(self.record_data[4], '%Y-%m-%d')
                    self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                except:
                    pass
            
            # 设置青年选择
            if self.record_data[1] and self.record_data[2]:  # youth_id_card and youth_name
                option_text = f"{self.record_data[2]}（{self.record_data[1]}）"
                self.youth_combo.setCurrentText(option_text)
            if self.record_data[3]:  # gender
                self.gender_input.setText(self.record_data[3])
            
            # 设置思想和精神
            if self.record_data[5]:  # thoughts
                thoughts_value = self.record_data[5]
                if thoughts_value in ["正常", "异常"]:
                    self.thoughts_combo.setCurrentText(thoughts_value)
                else:
                    # 如果是旧数据，根据内容判断
                    self.thoughts_combo.setCurrentText("异常" if thoughts_value and thoughts_value.strip() and thoughts_value != "正常" else "正常")
            
            if self.record_data[6]:  # spirit
                spirit_value = self.record_data[6]
                if spirit_value in ["正常", "异常"]:
                    self.spirit_combo.setCurrentText(spirit_value)
                else:
                    # 如果是旧数据，根据内容判断
                    self.spirit_combo.setCurrentText("异常" if spirit_value and spirit_value.strip() and spirit_value != "正常" else "正常")
            
            # 加载文件数据
            try:
                db_get_image_method = getattr(self.db_manager, self.db_get_image_method)
                self.image_data = db_get_image_method(self.record_data[0])
                if self.image_data:
                    self.image_status_label.setText("已有文件")
                    self.image_status_label.setStyleSheet("color: green;")
                else:
                    self.image_status_label.setText("未选择文件")
                    self.image_status_label.setStyleSheet("color: gray;")
            except Exception as e:
                print(f"加载文件数据失败: {e}")
                self.image_status_label.setText("未选择文件")
                self.image_status_label.setStyleSheet("color: gray;")
    
    def save_record(self):
        """保存记录"""
        # 验证必填字段
        if not self.youth_combo.currentText():
            QMessageBox.warning(self, "错误", "请选择青年")
            return
        
        # 检查选择的青年是否有效
        selected_option = self.youth_combo.currentText()
        if selected_option not in self.youth_data:
            QMessageBox.warning(self, "错误", "请选择有效的青年")
            return
        
        try:
            # 获取表单数据
            youth_info = self.youth_data[selected_option]
            youth_id_card = youth_info['id_card']
            youth_name = youth_info['name']
            gender = youth_info['gender']
            interview_date = self.date_edit.date().toString('yyyy-MM-dd')
            thoughts = self.thoughts_combo.currentText()
            spirit = self.spirit_combo.currentText()
            
            if self.record_data:
                # 更新现有记录
                db_update_method = getattr(self.db_manager, self.db_update_method)
                db_update_method(
                    self.record_data[0], youth_id_card, youth_name, gender,
                    interview_date, self.image_data, thoughts, spirit
                )
                QMessageBox.information(self, "成功", "记录更新成功！")
            else:
                # 检查是否已存在相同身份证号和日期的记录
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                if self.interview_type == 'town':
                    cursor.execute('''
                        SELECT id, youth_name FROM town_interview 
                        WHERE youth_id_card = ? AND interview_date = ?
                    ''', (youth_id_card, interview_date))
                else:  # leader
                    cursor.execute('''
                        SELECT id, youth_name FROM leader_interview 
                        WHERE youth_id_card = ? AND interview_date = ?
                    ''', (youth_id_card, interview_date))
                
                existing_record = cursor.fetchone()
                conn.close()
                
                if existing_record:
                    # 存在记录，询问是否覆盖
                    reply = QMessageBox.question(
                        self, '确认覆盖数据', 
                        f"已存在 {existing_record[1]} 在 {interview_date} 的{self.display_name}记录。\n\n是否覆盖现有数据？",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # 覆盖现有记录
                        db_update_method = getattr(self.db_manager, self.db_update_method)
                        db_update_method(
                            existing_record[0], youth_id_card, youth_name, gender,
                            interview_date, self.image_data, thoughts, spirit
                        )
                        QMessageBox.information(self, "成功", "记录覆盖成功！")
                    else:
                        return
                else:
                    # 插入新记录
                    db_insert_method = getattr(self.db_manager, self.db_insert_method)
                    db_insert_method(
                        youth_id_card, youth_name, gender, interview_date,
                        self.image_data, thoughts, spirit
                    )
                    QMessageBox.information(self, "成功", "记录添加成功！")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存记录失败: {str(e)}")


# 为了保持向后兼容性，创建别名类
class TownInterviewDialog(InterviewDialog):
    """镇街谈心谈话对话框（向后兼容）"""
    def __init__(self, db_manager, parent=None, record_data=None):
        super().__init__(db_manager, parent, record_data, 'town')


class LeaderInterviewDialog(InterviewDialog):
    """领导谈心谈话对话框（向后兼容）"""
    def __init__(self, db_manager, parent=None, record_data=None):
        super().__init__(db_manager, parent, record_data, 'leader')