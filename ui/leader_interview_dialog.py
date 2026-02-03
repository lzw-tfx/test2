"""
领导谈心谈话情况对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QDateEdit,
                             QComboBox, QMessageBox, QFrame, QFileDialog,
                             QWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime
import os


class LeaderInterviewDialog(QDialog):
    def __init__(self, db_manager, parent=None, record_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.record_data = record_data
        self.image_data = None
        
        self.init_ui()
        
        if record_data:
            self.load_record_data()
    
    def init_ui(self):
        title = "编辑领导谈心谈话记录" if self.record_data else "添加领导谈心谈话记录"
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
        
        # 姓名选择
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("姓名:"))
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)  # 允许输入
        self.name_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # 不插入新项
        self.name_combo.currentTextChanged.connect(self.on_name_changed)
        name_layout.addWidget(self.name_combo)
        name_layout.addStretch()
        form_layout.addLayout(name_layout)
        
        # 公民身份号码选择
        id_card_layout = QHBoxLayout()
        id_card_layout.addWidget(QLabel("公民身份号码:"))
        self.id_card_combo = QComboBox()
        self.id_card_combo.setEditable(True)  # 允许输入
        self.id_card_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # 不插入新项
        self.id_card_combo.currentTextChanged.connect(self.on_id_card_changed)
        id_card_layout.addWidget(self.id_card_combo)
        id_card_layout.addStretch()
        form_layout.addLayout(id_card_layout)
        
        # 性别（自动填充）
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("性别:"))
        self.gender_input = QLineEdit()
        self.gender_input.setReadOnly(True)
        gender_layout.addWidget(self.gender_input)
        gender_layout.addStretch()
        form_layout.addLayout(gender_layout)
        
        # 走访调查情况（图片）
        image_layout = QVBoxLayout()
        image_label_layout = QHBoxLayout()
        image_label_layout.addWidget(QLabel("走访调查情况:"))
        image_label_layout.addStretch()
        image_layout.addLayout(image_label_layout)
        
        # 图片按钮
        image_btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("导入图片")
        import_btn.clicked.connect(self.import_image)
        image_btn_layout.addWidget(import_btn)
        
        view_btn = QPushButton("查看图片")
        view_btn.clicked.connect(self.view_image)
        image_btn_layout.addWidget(view_btn)
        
        delete_btn = QPushButton("删除图片")
        delete_btn.clicked.connect(self.delete_image)
        image_btn_layout.addWidget(delete_btn)
        
        image_btn_layout.addStretch()
        image_layout.addLayout(image_btn_layout)
        
        # 图片状态标签
        self.image_status_label = QLabel("未选择图片")
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
            self.name_to_id_card = {}
            self.id_card_to_name = {}
            
            names = []
            id_cards = []
            
            for option in youth_options:
                id_card, name, gender = option
                self.youth_data[id_card] = {'name': name, 'gender': gender}
                self.name_to_id_card[name] = id_card
                self.id_card_to_name[id_card] = name
                names.append(name)
                id_cards.append(id_card)
            
            # 按拼音排序姓名
            try:
                import pypinyin
                names.sort(key=lambda x: ''.join(pypinyin.lazy_pinyin(x)))
            except ImportError:
                # 如果没有pypinyin，按字符排序
                names.sort()
            
            # 按数字排序身份证号
            id_cards.sort()
            
            self.name_combo.addItems(names)
            self.id_card_combo.addItems(id_cards)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载青年信息失败: {str(e)}")
    
    def on_name_changed(self, name):
        """姓名改变事件"""
        if name in self.name_to_id_card:
            id_card = self.name_to_id_card[name]
            self.id_card_combo.setCurrentText(id_card)
            self.gender_input.setText(self.youth_data[id_card]['gender'])
    
    def on_id_card_changed(self, id_card):
        """身份证号改变事件"""
        if id_card in self.youth_data:
            name = self.youth_data[id_card]['name']
            self.name_combo.setCurrentText(name)
            self.gender_input.setText(self.youth_data[id_card]['gender'])
    
    def import_image(self):
        """导入图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.tiff);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    self.image_data = f.read()
                
                filename = os.path.basename(file_path)
                self.image_status_label.setText(f"已选择: {filename}")
                self.image_status_label.setStyleSheet("color: green;")
                QMessageBox.information(self, "成功", "图片导入成功！")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入图片失败: {str(e)}")
    
    def view_image(self):
        """查看图片"""
        if not self.image_data:
            QMessageBox.warning(self, "提示", "没有可查看的图片")
            return
        
        try:
            from ui.image_viewer_dialog import ImageViewerDialog
            dialog = ImageViewerDialog(self.image_data, "走访调查图片", self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查看图片失败: {str(e)}")
    
    def delete_image(self):
        """删除图片"""
        if self.image_data:
            reply = QMessageBox.question(
                self, "确认", "确定要删除当前图片吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.image_data = None
                self.image_status_label.setText("未选择图片")
                self.image_status_label.setStyleSheet("color: gray;")
                QMessageBox.information(self, "成功", "图片已删除")
        else:
            QMessageBox.information(self, "提示", "没有可删除的图片")
    
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
            
            # 设置姓名和身份证号
            if self.record_data[1]:  # youth_id_card
                self.id_card_combo.setCurrentText(self.record_data[1])
            if self.record_data[2]:  # youth_name
                self.name_combo.setCurrentText(self.record_data[2])
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
            
            # 加载图片数据
            try:
                self.image_data = self.db_manager.get_leader_interview_image(self.record_data[0])
                if self.image_data:
                    self.image_status_label.setText("已有图片")
                    self.image_status_label.setStyleSheet("color: green;")
                else:
                    self.image_status_label.setText("未选择图片")
                    self.image_status_label.setStyleSheet("color: gray;")
            except Exception as e:
                print(f"加载图片数据失败: {e}")
                self.image_status_label.setText("未选择图片")
                self.image_status_label.setStyleSheet("color: gray;")
    
    def save_record(self):
        """保存记录"""
        # 验证必填字段
        if not self.name_combo.currentText():
            QMessageBox.warning(self, "错误", "请选择姓名")
            return
        
        if not self.id_card_combo.currentText():
            QMessageBox.warning(self, "错误", "请选择公民身份号码")
            return
        
        try:
            # 获取表单数据
            youth_id_card = self.id_card_combo.currentText()
            youth_name = self.name_combo.currentText()
            gender = self.gender_input.text()
            interview_date = self.date_edit.date().toString('yyyy-MM-dd')
            thoughts = self.thoughts_combo.currentText()
            spirit = self.spirit_combo.currentText()
            
            if self.record_data:
                # 更新现有记录
                self.db_manager.update_leader_interview(
                    self.record_data[0], youth_id_card, youth_name, gender,
                    interview_date, self.image_data, thoughts, spirit
                )
                QMessageBox.information(self, "成功", "记录更新成功！")
            else:
                # 插入新记录
                self.db_manager.insert_leader_interview(
                    youth_id_card, youth_name, gender, interview_date,
                    self.image_data, thoughts, spirit
                )
                QMessageBox.information(self, "成功", "记录添加成功！")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存记录失败: {str(e)}")