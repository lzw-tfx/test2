"""
数据库管理器
"""
import sqlite3
import hashlib
from datetime import datetime
from .models import Youth, User


class DatabaseManager:
    def __init__(self, db_path='youth_records.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                unit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 青年基本信息表（旧结构）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youth (
                id_card TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                gender TEXT,
                nation TEXT,
                political_status TEXT,
                school TEXT,
                education_level TEXT,
                major TEXT,
                study_status TEXT,
                study_type TEXT,
                phone TEXT,
                household_address TEXT,
                residence_address TEXT,
                family_info TEXT,
                district TEXT,
                street TEXT,
                company TEXT,
                platoon TEXT,
                squad TEXT,
                squad_leader TEXT,
                camp_status TEXT,
                leave_time TEXT,
                situation_note TEXT,
                parent_phone TEXT,
                personal_experience TEXT,
                reference_person TEXT,
                reference_phone TEXT,
                id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 病史调查表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT,
                file_path TEXT,
                upload_date TEXT,
                notes TEXT,
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 病史筛查表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_screening (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT,
                name TEXT,
                gender TEXT,
                id_card TEXT,
                screening_result TEXT,
                screening_date TEXT,
                physical_status TEXT DEFAULT '',
                mental_status TEXT DEFAULT '',
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 迁移：为medical_screening表添加新字段（如果不存在）
        try:
            cursor.execute("PRAGMA table_info(medical_screening)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'recruitment_place' not in columns:
                cursor.execute("ALTER TABLE medical_screening ADD COLUMN recruitment_place TEXT DEFAULT ''")
            if 'company' not in columns:
                cursor.execute("ALTER TABLE medical_screening ADD COLUMN company TEXT DEFAULT ''")
            if 'platoon' not in columns:
                cursor.execute("ALTER TABLE medical_screening ADD COLUMN platoon TEXT DEFAULT ''")
            if 'squad' not in columns:
                cursor.execute("ALTER TABLE medical_screening ADD COLUMN squad TEXT DEFAULT ''")
            if 'remark' not in columns:
                cursor.execute("ALTER TABLE medical_screening ADD COLUMN remark TEXT DEFAULT ''")
        except Exception as e:
            print(f"迁移medical_screening表字段时出错: {e}")
        
        # 镇街谈心谈话情况表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS town_interview (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT NOT NULL,
                youth_name TEXT NOT NULL,
                gender TEXT,
                interview_date TEXT,
                visit_survey_image BLOB,
                thoughts TEXT,
                spirit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 检查并更新镇街谈心谈话表结构
        self._update_town_interview_table(cursor)
        
        # 领导谈心谈话情况表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leader_interview (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT NOT NULL,
                youth_name TEXT NOT NULL,
                gender TEXT,
                interview_date TEXT,
                visit_survey_image BLOB,
                thoughts TEXT,
                spirit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 检查并更新领导谈心谈话表结构
        self._update_leader_interview_table(cursor)
        
        # 走访调查情况表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visit_survey (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT NOT NULL,
                youth_name TEXT NOT NULL,
                gender TEXT,
                survey_date TEXT,
                visit_survey_image BLOB,
                thoughts TEXT,
                spirit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 每日情况统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id INTEGER,
                record_date TEXT,
                mood TEXT,
                physical_condition TEXT,
                mental_state TEXT,
                notes TEXT,
                FOREIGN KEY (youth_id) REFERENCES youth(id)
            )
        ''')
        
        # 检查并更新daily_stat表结构
        self._update_daily_stat_table(cursor)
        
        # 异常情况统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS abnormal_stat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT,
                abnormal_type TEXT,
                description TEXT,
                record_date TEXT,
                handler TEXT,
                status TEXT,
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 健康筛查表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_screening (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT,
                screening_type TEXT,
                result TEXT,
                screening_date TEXT,
                follow_up TEXT,
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 入营点验情况表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS camp_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                user_id TEXT NOT NULL,
                item TEXT,
                usage TEXT,
                Disposal TEXT,
                data TEXT,
                FOREIGN KEY (user_id) REFERENCES youth(id_card)
            )
        ''')
        
        # 迁移：为camp_verification表添加usage字段（如果不存在）
        try:
            cursor.execute("PRAGMA table_info(camp_verification)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'usage' not in columns:
                cursor.execute("ALTER TABLE camp_verification ADD COLUMN usage TEXT DEFAULT ''")
                print("已添加usage字段到camp_verification表")
        except Exception as e:
            print(f"迁移camp_verification表字段时出错: {e}")
        
        # 政治考核情况统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS political_assessment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT NOT NULL,
                name TEXT NOT NULL,
                gender TEXT,
                id_card TEXT NOT NULL,
                family_member_info TEXT,
                visit_survey TEXT,
                political_assessment TEXT,
                key_attention TEXT,
                assessment_date TEXT,
                thoughts TEXT,
                spirit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 体检情况统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS physical_examination (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youth_id_card TEXT NOT NULL,
                name TEXT,
                gender TEXT,
                district_exam TEXT,
                district_positive TEXT,
                district_date TEXT,
                city_exam TEXT,
                city_positive TEXT,
                city_date TEXT,
                special_exam TEXT,
                special_positive TEXT,
                special_date TEXT,
                body_status TEXT,
                psychological_test_type TEXT,
                tracking_opinion TEXT,
                implementation_status TEXT,
                recruitment_place TEXT DEFAULT '',
                company TEXT DEFAULT '',
                platoon TEXT DEFAULT '',
                squad TEXT DEFAULT '',
                squad_leader TEXT DEFAULT '',
                FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
            )
        ''')
        
        # 迁移：为physical_examination表添加新字段（如果不存在）
        try:
            cursor.execute("PRAGMA table_info(physical_examination)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'recruitment_place' not in columns:
                cursor.execute("ALTER TABLE physical_examination ADD COLUMN recruitment_place TEXT DEFAULT ''")
            if 'company' not in columns:
                cursor.execute("ALTER TABLE physical_examination ADD COLUMN company TEXT DEFAULT ''")
            if 'platoon' not in columns:
                cursor.execute("ALTER TABLE physical_examination ADD COLUMN platoon TEXT DEFAULT ''")
            if 'squad' not in columns:
                cursor.execute("ALTER TABLE physical_examination ADD COLUMN squad TEXT DEFAULT ''")
            if 'squad_leader' not in columns:
                cursor.execute("ALTER TABLE physical_examination ADD COLUMN squad_leader TEXT DEFAULT ''")
        except Exception as e:
            print(f"迁移physical_examination表字段时出错: {e}")
        
        conn.commit()
        
        # 升级youth表结构
        self._update_youth_table(cursor)
        
        # 创建默认管理员账户
        self._create_default_admin(cursor)
        
        # 创建异常统计视图
        self._create_exception_statistics_view_if_not_exists(cursor)
        
        conn.commit()
        conn.close()
    
    def _update_youth_table(self, cursor):
        """更新youth表结构，添加完整的青年基本情况统计表字段"""
        try:
            # 检查表是否存在相关字段
            cursor.execute("PRAGMA table_info(youth)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 需要添加的新字段
            new_fields = [
                ('birth_date', 'TEXT'),                    # 出生日期
                ('religion', 'TEXT'),                      # 宗教信仰
                ('native_place', 'TEXT'),                  # 籍贯
                ('camp_entry_time', 'TEXT'),               # 入营时间
                ('recruitment_place', 'TEXT'),             # 征集地
                ('postal_code', 'TEXT'),                   # 邮编
                ('personal_phone', 'TEXT'),                # 本人电话
                ('family_phone', 'TEXT'),                  # 家庭电话
                ('enrollment_time', 'TEXT'),               # 入学时间
                ('initial_hospital', 'TEXT'),              # 初检医院
                ('initial_conclusion', 'TEXT'),            # 初检结论
                ('initial_time', 'TEXT'),                  # 初检时间
                ('physical_conclusion', 'TEXT'),           # 体检结论
                ('physical_time', 'TEXT'),                 # 体检时间
                ('physical_disqualification', 'TEXT'),     # 体检不合格原因
                ('chief_doctor_opinion', 'TEXT'),          # 主检医师意见
                ('graduation_time', 'TEXT'),               # 毕业时间
                ('physical_examination', 'TEXT'),          # 体格检查情况
                ('medical_history_survey', 'TEXT'),        # 病史调查情况
                ('political_assessment', 'TEXT'),          # 政治考核情况
                ('information', 'TEXT'),                   # 信息
                ('item_verification', 'TEXT'),             # 物品点验情况
                ('special_reexamination', 'TEXT'),         # 专项复查情况
                ('leave_reason', 'TEXT'),                  # 离营原因
                ('district_positive', 'TEXT'),             # 区检阳性特征/边缘问题
                ('city_positive', 'TEXT'),                 # 市检阳性特征/边缘问题
                ('special_screening_positive', 'TEXT'),    # 专项筛查阳性特征/边缘问题
                ('psychological_test_type', 'TEXT'),       # 心理检测类型
                ('tracking_opinion', 'TEXT'),              # 跟踪处置意见
                ('implementation_status', 'TEXT'),         # 处置意见落实情况
                ('district_medical_survey', 'TEXT'),       # 区级病史调查情况
                ('city_medical_survey', 'TEXT'),           # 市级病史调查情况
                ('province_medical_survey', 'TEXT'),       # 省级病史调查情况
                ('family_member_info', 'TEXT'),            # 家庭成员信息
                ('visit_survey', 'TEXT'),                  # 走访调查情况
                ('political_assessment2', 'TEXT'),         # 政治考核情况2
                ('key_attention', 'TEXT'),                 # 需重点关注情况
                ('items', 'TEXT'),                         # 物品
                ('usage', 'TEXT'),                         # 用途
                ('disposal_measures', 'TEXT'),             # 处置措施
                ('reexamination_time', 'TEXT'),            # 复查时间
                ('existing_situation', 'TEXT'),            # 存在情况
                ('reexamination_conclusion', 'TEXT'),      # 复查结论
            ]
            
            # 保留原有字段，但可能需要重命名
            field_renames = [
                ('phone', 'personal_phone'),               # 电话 -> 本人电话
                ('parent_phone', 'family_phone'),          # 父母电话 -> 家庭电话
                ('situation_note', 'leave_reason'),        # 情况说明 -> 离营原因
            ]
            
            # 添加新字段
            for field_name, field_type in new_fields:
                if field_name not in columns:
                    cursor.execute(f"ALTER TABLE youth ADD COLUMN {field_name} {field_type}")
                    print(f"已添加{field_name}字段到youth表")
            
            # 处理字段重命名（SQLite不支持直接重命名列，需要通过创建新表的方式）
            # 这里先保留原字段，在数据迁移时处理
                    
        except Exception as e:
            print(f"更新youth表结构时出错: {e}")

    def _update_daily_stat_table(self, cursor):
        """更新daily_stat表结构"""
        try:
            # 检查表是否存在mental_state字段
            cursor.execute("PRAGMA table_info(daily_stat)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'mental_state' not in columns:
                # 如果没有mental_state字段，添加它
                cursor.execute("ALTER TABLE daily_stat ADD COLUMN mental_state TEXT")
                print("已添加mental_state字段到daily_stat表")
            
            # 添加新字段：训练和管理
            if 'training' not in columns:
                cursor.execute("ALTER TABLE daily_stat ADD COLUMN training TEXT DEFAULT '正常'")
                print("已添加training字段到daily_stat表")
            
            if 'management' not in columns:
                cursor.execute("ALTER TABLE daily_stat ADD COLUMN management TEXT DEFAULT '正常'")
                print("已添加management字段到daily_stat表")
            
            # 检查是否使用youth_id_card而不是youth_id
            if 'youth_id_card' in columns and 'youth_id' not in columns:
                # 需要迁移数据结构
                print("正在迁移daily_stat表结构...")
                
                # 创建新表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_stat_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        youth_id INTEGER,
                        record_date TEXT,
                        mood TEXT,
                        physical_condition TEXT,
                        mental_state TEXT,
                        training TEXT DEFAULT '正常',
                        management TEXT DEFAULT '正常',
                        notes TEXT,
                        FOREIGN KEY (youth_id) REFERENCES youth(id)
                    )
                ''')
                
                # 迁移数据 - 通过id_card找到对应的id
                cursor.execute('''
                    INSERT INTO daily_stat_new (id, youth_id, record_date, mood, physical_condition, mental_state, training, management, notes)
                    SELECT d.id, y.id, d.record_date, d.mood, d.physical_condition, 
                           COALESCE(d.training_status, '正常') as mental_state, '正常' as training, '正常' as management, d.notes
                    FROM daily_stat d
                    LEFT JOIN youth y ON d.youth_id_card = y.id_card
                    WHERE y.id IS NOT NULL
                ''')
                
                # 删除旧表，重命名新表
                cursor.execute("DROP TABLE daily_stat")
                cursor.execute("ALTER TABLE daily_stat_new RENAME TO daily_stat")
                
                print("daily_stat表结构迁移完成")
                
        except Exception as e:
            print(f"更新daily_stat表结构时出错: {e}")
            # 如果出错，确保表至少存在基本结构
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youth_id INTEGER,
                    record_date TEXT,
                    mood TEXT,
                    physical_condition TEXT,
                    mental_state TEXT,
                    training TEXT DEFAULT '正常',
                    management TEXT DEFAULT '正常',
                    notes TEXT,
                    FOREIGN KEY (youth_id) REFERENCES youth(id)
                )
            ''')
    
    def _update_town_interview_table(self, cursor):
        """更新镇街谈心谈话表结构"""
        try:
            # 检查表是否存在以及字段结构
            cursor.execute("PRAGMA table_info(town_interview)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 检查是否需要迁移表结构
            required_columns = ['youth_name', 'gender', 'visit_survey_image', 'thoughts', 'spirit']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"正在更新镇街谈心谈话表结构，添加字段: {missing_columns}")
                
                # 备份现有数据
                cursor.execute("SELECT * FROM town_interview")
                existing_data = cursor.fetchall()
                
                # 删除旧表
                cursor.execute("DROP TABLE IF EXISTS town_interview")
                
                # 创建新表
                cursor.execute('''
                    CREATE TABLE town_interview (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        youth_id_card TEXT NOT NULL,
                        youth_name TEXT NOT NULL,
                        gender TEXT,
                        interview_date TEXT,
                        visit_survey_image BLOB,
                        thoughts TEXT,
                        spirit TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
                    )
                ''')
                
                # 如果有现有数据，尝试迁移
                if existing_data:
                    print(f"正在迁移 {len(existing_data)} 条现有记录...")
                    for record in existing_data:
                        try:
                            # 旧表结构可能是: (id, youth_id_card, file_path, interview_date, notes)
                            if len(record) >= 4:
                                youth_id_card = record[1]
                                interview_date = record[3] if len(record) > 3 else None
                                notes = record[4] if len(record) > 4 else None
                                
                                # 从youth表获取姓名和性别
                                cursor.execute("SELECT name, gender FROM youth WHERE id_card = ?", (youth_id_card,))
                                youth_info = cursor.fetchone()
                                
                                if youth_info:
                                    youth_name, gender = youth_info
                                    
                                    # 插入到新表
                                    cursor.execute('''
                                        INSERT INTO town_interview 
                                        (youth_id_card, youth_name, gender, interview_date, thoughts, spirit)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                    ''', (youth_id_card, youth_name, gender, interview_date, notes or '', ''))
                        except Exception as e:
                            print(f"迁移记录时出错: {e}")
                            continue
                
                print("镇街谈心谈话表结构更新完成")
                
        except Exception as e:
            print(f"更新镇街谈心谈话表结构时出错: {e}")
            # 如果出错，确保表至少存在基本结构
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS town_interview (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youth_id_card TEXT NOT NULL,
                    youth_name TEXT NOT NULL,
                    gender TEXT,
                    interview_date TEXT,
                    visit_survey_image BLOB,
                    thoughts TEXT,
                    spirit TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
                )
            ''')
    
    def _update_leader_interview_table(self, cursor):
        """更新领导谈心谈话表结构"""
        try:
            # 检查表是否存在以及字段结构
            cursor.execute("PRAGMA table_info(leader_interview)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 检查是否需要迁移表结构
            required_columns = ['youth_name', 'gender', 'visit_survey_image', 'thoughts', 'spirit']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"正在更新领导谈心谈话表结构，添加字段: {missing_columns}")
                
                # 备份现有数据
                cursor.execute("SELECT * FROM leader_interview")
                existing_data = cursor.fetchall()
                
                # 删除旧表
                cursor.execute("DROP TABLE IF EXISTS leader_interview")
                
                # 创建新表
                cursor.execute('''
                    CREATE TABLE leader_interview (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        youth_id_card TEXT NOT NULL,
                        youth_name TEXT NOT NULL,
                        gender TEXT,
                        interview_date TEXT,
                        visit_survey_image BLOB,
                        thoughts TEXT,
                        spirit TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
                    )
                ''')
                
                # 如果有现有数据，尝试迁移
                if existing_data:
                    print(f"正在迁移 {len(existing_data)} 条现有记录...")
                    for record in existing_data:
                        try:
                            # 旧表结构可能是: (id, youth_id_card, file_path, interview_date, notes)
                            if len(record) >= 4:
                                youth_id_card = record[1]
                                interview_date = record[3] if len(record) > 3 else None
                                notes = record[4] if len(record) > 4 else None
                                
                                # 从youth表获取姓名和性别
                                cursor.execute("SELECT name, gender FROM youth WHERE id_card = ?", (youth_id_card,))
                                youth_info = cursor.fetchone()
                                
                                if youth_info:
                                    youth_name, gender = youth_info
                                    
                                    # 插入到新表
                                    cursor.execute('''
                                        INSERT INTO leader_interview 
                                        (youth_id_card, youth_name, gender, interview_date, thoughts, spirit)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                    ''', (youth_id_card, youth_name, gender, interview_date, notes or '', ''))
                        except Exception as e:
                            print(f"迁移记录时出错: {e}")
                            continue
                
                print("领导谈心谈话表结构更新完成")
                
        except Exception as e:
            print(f"更新领导谈心谈话表结构时出错: {e}")
            # 如果出错，确保表至少存在基本结构
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leader_interview (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youth_id_card TEXT NOT NULL,
                    youth_name TEXT NOT NULL,
                    gender TEXT,
                    interview_date TEXT,
                    visit_survey_image BLOB,
                    thoughts TEXT,
                    spirit TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (youth_id_card) REFERENCES youth(id_card)
                )
            ''')
    
    def _create_default_admin(self, cursor):
        """创建默认管理员账户"""
        cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
        if cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, password, role, unit) VALUES (?, ?, ?, ?)",
                ('admin', password_hash, 'admin', '系统管理员')
            )
    
    def authenticate_user(self, username, password):
        """用户认证"""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute(
            "SELECT id, username, role, unit FROM users WHERE username=? AND password=?",
            (username, password_hash)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return User(id=result[0], username=result[1], role=result[2], unit=result[3])
        return None
    
    def search_youth(self, name='', id_card='', school='', phone='', district='', street='', company='', platoon='', squad=''):
        """搜索青年信息（旧结构）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 明确指定字段顺序（旧结构）
        query = """
            SELECT id_card, name, gender, nation, political_status,
                   school, education_level, major, study_status, study_type,
                   phone, household_address, residence_address, family_info,
                   district, street, company, platoon, squad, squad_leader,
                   camp_status, leave_time, situation_note, parent_phone, 
                   personal_experience, reference_person, reference_phone, id
            FROM youth WHERE 1=1
        """
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f'%{name}%')
        if id_card:
            query += " AND id_card LIKE ?"
            params.append(f'%{id_card}%')
        if school:
            query += " AND school LIKE ?"
            params.append(f'%{school}%')
        if phone:
            query += " AND phone LIKE ?"
            params.append(f'%{phone}%')
        if district:
            query += " AND district LIKE ?"
            params.append(f'%{district}%')
        if street:
            query += " AND street LIKE ?"
            params.append(f'%{street}%')
        if company:
            query += " AND company LIKE ?"
            params.append(f'%{company}%')
        if platoon:
            query += " AND platoon LIKE ?"
            params.append(f'%{platoon}%')
        if squad:
            query += " AND squad LIKE ?"
            params.append(f'%{squad}%')
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_youth_by_id_card(self, id_card):
        """根据身份证号获取青年信息，返回Youth对象"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM youth WHERE id_card=?
        """, (id_card,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # 辅助函数来安全获取字段值
            def get_field(field_name, default=''):
                try:
                    return result[field_name] if result[field_name] is not None else default
                except (KeyError, IndexError):
                    return default
            
            return Youth(
                id_card=get_field('id_card'),
                name=get_field('name'),
                gender=get_field('gender'),
                birth_date=get_field('birth_date'),
                nation=get_field('nation'),
                political_status=get_field('political_status'),
                religion=get_field('religion'),
                native_place=get_field('native_place'),
                education_level=get_field('education_level'),
                study_status=get_field('study_status'),
                study_type=get_field('study_type'),
                camp_entry_time=get_field('camp_entry_time'),
                recruitment_place=get_field('recruitment_place'),
                residence_address=get_field('residence_address'),
                household_address=get_field('household_address'),
                postal_code=get_field('postal_code'),
                personal_phone=get_field('personal_phone') or get_field('phone'),
                family_phone=get_field('family_phone') or get_field('parent_phone'),
                school=get_field('school'),
                major=get_field('major'),
                enrollment_time=get_field('enrollment_time'),
                initial_hospital=get_field('initial_hospital'),
                initial_conclusion=get_field('initial_conclusion'),
                initial_time=get_field('initial_time'),
                physical_conclusion=get_field('physical_conclusion'),
                physical_time=get_field('physical_time'),
                physical_disqualification=get_field('physical_disqualification'),
                chief_doctor_opinion=get_field('chief_doctor_opinion'),
                graduation_time=get_field('graduation_time'),
                physical_examination=get_field('physical_examination'),
                medical_history_survey=get_field('medical_history_survey'),
                political_assessment=get_field('political_assessment'),
                company=get_field('company'),
                platoon=get_field('platoon'),
                squad=get_field('squad'),
                squad_leader=get_field('squad_leader'),
                information=get_field('information'),
                item_verification=get_field('item_verification'),
                special_reexamination=get_field('special_reexamination'),
                camp_status=get_field('camp_status'),
                leave_time=get_field('leave_time'),
                leave_reason=get_field('leave_reason') or get_field('situation_note'),
                district_positive=get_field('district_positive'),
                city_positive=get_field('city_positive'),
                special_screening_positive=get_field('special_screening_positive'),
                psychological_test_type=get_field('psychological_test_type'),
                tracking_opinion=get_field('tracking_opinion'),
                implementation_status=get_field('implementation_status'),
                district_medical_survey=get_field('district_medical_survey'),
                city_medical_survey=get_field('city_medical_survey'),
                province_medical_survey=get_field('province_medical_survey'),
                family_member_info=get_field('family_member_info') or get_field('family_info'),
                visit_survey=get_field('visit_survey'),
                political_assessment2=get_field('political_assessment2'),
                key_attention=get_field('key_attention'),
                items=get_field('items'),
                usage=get_field('usage'),
                disposal_measures=get_field('disposal_measures'),
                reexamination_time=get_field('reexamination_time'),
                existing_situation=get_field('existing_situation'),
                reexamination_conclusion=get_field('reexamination_conclusion'),
                id=get_field('id')
            )
        return None
    
    def get_module_data(self, table_name, youth_id):
        """获取指定模块的数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE youth_id=?", (youth_id,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def insert_youth(self, youth_data):
        """插入或更新青年信息（新结构40字段）
        元组格式：id_card, name, gender, birth_date, nation, political_status, religion, native_place,
                 education_level, study_status, study_type, camp_entry_time, recruitment_place,
                 residence_address, household_address, postal_code, personal_phone, family_phone,
                 school, major, enrollment_time, initial_hospital, initial_conclusion, initial_time,
                 physical_conclusion, physical_time, physical_disqualification, chief_doctor_opinion,
                 graduation_time, company, platoon, squad, squad_leader, camp_status, leave_time, leave_reason
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 元组格式
        id_card = youth_data[0]  # id_card现在在第1个位置
        cursor.execute("SELECT id_card FROM youth WHERE id_card=?", (id_card,))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute('''
                UPDATE youth SET name=?, gender=?, birth_date=?, nation=?, political_status=?,
                               religion=?, native_place=?, education_level=?, study_status=?, study_type=?,
                               camp_entry_time=?, recruitment_place=?, residence_address=?, household_address=?,
                               postal_code=?, personal_phone=?, family_phone=?, school=?, major=?,
                               enrollment_time=?, initial_hospital=?, initial_conclusion=?, initial_time=?,
                               physical_conclusion=?, physical_time=?, physical_disqualification=?,
                               chief_doctor_opinion=?, graduation_time=?, company=?, platoon=?, squad=?,
                               squad_leader=?, camp_status=?, leave_time=?, leave_reason=?
                WHERE id_card=?
            ''', (youth_data[1], youth_data[2], youth_data[3], youth_data[4], youth_data[5],
                  youth_data[6], youth_data[7], youth_data[8], youth_data[9], youth_data[10],
                  youth_data[11], youth_data[12], youth_data[13], youth_data[14], youth_data[15],
                  youth_data[16], youth_data[17], youth_data[18], youth_data[19], youth_data[20],
                  youth_data[21], youth_data[22], youth_data[23], youth_data[24], youth_data[25],
                  youth_data[26], youth_data[27], youth_data[28], youth_data[29], youth_data[30],
                  youth_data[31], youth_data[32], youth_data[33], youth_data[34], youth_data[35], id_card))
        else:
            # 插入新记录，自动分配序号
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM youth")
            next_id = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT INTO youth (id_card, name, gender, birth_date, nation, political_status,
                                 religion, native_place, education_level, study_status, study_type,
                                 camp_entry_time, recruitment_place, residence_address, household_address,
                                 postal_code, personal_phone, family_phone, school, major,
                                 enrollment_time, initial_hospital, initial_conclusion, initial_time,
                                 physical_conclusion, physical_time, physical_disqualification,
                                 chief_doctor_opinion, graduation_time, company, platoon, squad,
                                 squad_leader, camp_status, leave_time, leave_reason, id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (youth_data[0], youth_data[1], youth_data[2], youth_data[3], youth_data[4], youth_data[5],
                  youth_data[6], youth_data[7], youth_data[8], youth_data[9], youth_data[10],
                  youth_data[11], youth_data[12], youth_data[13], youth_data[14], youth_data[15],
                  youth_data[16], youth_data[17], youth_data[18], youth_data[19], youth_data[20],
                  youth_data[21], youth_data[22], youth_data[23], youth_data[24], youth_data[25],
                  youth_data[26], youth_data[27], youth_data[28], youth_data[29], youth_data[30],
                  youth_data[31], youth_data[32], youth_data[33], youth_data[34], youth_data[35], next_id))
        
        conn.commit()
        conn.close()
        return id_card
    
    def insert_daily_stat(self, youth_id, record_date, mood, physical_condition, mental_state, training, management, notes):
        """插入每日统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_stat (youth_id, record_date, mood, physical_condition, 
                                   mental_state, training, management, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (youth_id, record_date, mood, physical_condition, mental_state, training, management, notes))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def update_daily_stat(self, record_id, record_date, mood, physical_condition, mental_state, training, management, notes):
        """更新每日统计"""
        # 先获取原记录信息用于同步
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT y.id_card, d.record_date 
            FROM daily_stat d
            JOIN youth y ON d.youth_id = y.id
            WHERE d.id = ?
        ''', (record_id,))
        old_record = cursor.fetchone()
        
        # 更新记录
        cursor.execute('''
            UPDATE daily_stat 
            SET record_date=?, mood=?, physical_condition=?, mental_state=?, training=?, management=?, notes=?
            WHERE id=?
        ''', (record_date, mood, physical_condition, mental_state, training, management, notes, record_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def delete_daily_stat(self, record_id):
        """删除单个每日统计记录"""
        # 先获取记录信息用于同步
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT y.id_card, d.record_date 
            FROM daily_stat d
            JOIN youth y ON d.youth_id = y.id
            WHERE d.id = ?
        ''', (record_id,))
        record_info = cursor.fetchone()
        
        # 删除记录
        cursor.execute('DELETE FROM daily_stat WHERE id = ?', (record_id,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count > 0
    
    def delete_daily_stats(self, record_ids):
        """批量删除每日统计记录"""
        if not record_ids:
            return 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先获取所有记录信息用于同步
        records_to_sync = []
        for record_id in record_ids:
            cursor.execute('''
                SELECT y.id_card, d.record_date 
                FROM daily_stat d
                JOIN youth y ON d.youth_id = y.id
                WHERE d.id = ?
            ''', (record_id,))
            record_info = cursor.fetchone()
            if record_info:
                records_to_sync.append(record_info)
        
        # 批量删除
        placeholders = ','.join(['?' for _ in record_ids])
        cursor.execute(f'DELETE FROM daily_stat WHERE id IN ({placeholders})', record_ids)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def _get_user_id_card_by_youth_id(self, youth_id):
        """根据youth_id获取身份证号"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id_card FROM youth WHERE id = ?', (youth_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_daily_stats_for_chart(self, youth_id, days=30):
        """获取用于图表显示的每日数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT record_date, mood, physical_condition, training_status
            FROM daily_stat
            WHERE youth_id=?
            ORDER BY record_date DESC
            LIMIT ?
        ''', (youth_id, days))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_town_interviews(self, name='', id_card='', recruitment_place='', company='', platoon='', squad='', time_condition='', time_params=None):
        """搜索镇街谈心谈话记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT t.id, t.youth_id_card, t.youth_name, t.gender, t.interview_date, 
                   y.recruitment_place, y.company, y.platoon, y.squad, y.squad_leader,
                   t.thoughts, t.spirit, t.created_at
            FROM town_interview t
            LEFT JOIN youth y ON t.youth_id_card = y.id_card
            WHERE 1=1
        """
        params = []
        
        # 添加时间筛选条件
        if time_condition:
            query += f" AND {time_condition.replace('interview_date', 't.interview_date')}"
            params.extend(time_params or [])
        
        if name:
            query += " AND t.youth_name LIKE ?"
            params.append(f'%{name}%')
        if id_card:
            query += " AND t.youth_id_card LIKE ?"
            params.append(f'%{id_card}%')
        if recruitment_place:
            query += " AND y.recruitment_place LIKE ?"
            params.append(f'%{recruitment_place}%')
        if company:
            query += " AND y.company LIKE ?"
            params.append(f'%{company}%')
        if platoon:
            query += " AND y.platoon LIKE ?"
            params.append(f'%{platoon}%')
        if squad:
            query += " AND y.squad LIKE ?"
            params.append(f'%{squad}%')
        
        query += " ORDER BY t.interview_date DESC, t.youth_id_card ASC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def insert_town_interview(self, youth_id_card, youth_name, gender, interview_date, 
                             visit_survey_image, thoughts, spirit):
        """插入镇街谈心谈话记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO town_interview (youth_id_card, youth_name, gender, interview_date,
                                      visit_survey_image, thoughts, spirit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (youth_id_card, youth_name, gender, interview_date, visit_survey_image, thoughts, spirit))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def update_town_interview(self, record_id, youth_id_card, youth_name, gender, 
                             interview_date, visit_survey_image, thoughts, spirit):
        """更新镇街谈心谈话记录"""
        # 先获取原记录信息用于同步
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT youth_id_card, interview_date 
            FROM town_interview 
            WHERE id = ?
        ''', (record_id,))
        old_record = cursor.fetchone()
        
        # 更新记录
        if visit_survey_image is not None:
            cursor.execute('''
                UPDATE town_interview 
                SET youth_id_card=?, youth_name=?, gender=?, interview_date=?,
                    visit_survey_image=?, thoughts=?, spirit=?
                WHERE id=?
            ''', (youth_id_card, youth_name, gender, interview_date, 
                  visit_survey_image, thoughts, spirit, record_id))
        else:
            cursor.execute('''
                UPDATE town_interview 
                SET youth_id_card=?, youth_name=?, gender=?, interview_date=?,
                    thoughts=?, spirit=?
                WHERE id=?
            ''', (youth_id_card, youth_name, gender, interview_date, 
                  thoughts, spirit, record_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def delete_town_interviews(self, record_ids):
        """批量删除镇街谈心谈话记录"""
        if not record_ids:
            return 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先获取所有记录信息用于同步
        records_to_sync = []
        for record_id in record_ids:
            cursor.execute('''
                SELECT youth_id_card, interview_date 
                FROM town_interview 
                WHERE id = ?
            ''', (record_id,))
            record_info = cursor.fetchone()
            if record_info:
                records_to_sync.append(record_info)
        
        # 批量删除
        placeholders = ','.join(['?' for _ in record_ids])
        cursor.execute(f'DELETE FROM town_interview WHERE id IN ({placeholders})', record_ids)
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return deleted_count
    
    def get_town_interview_image(self, record_id):
        """获取镇街谈心谈话记录的图片数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT visit_survey_image FROM town_interview WHERE id=?', (record_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_youth_options(self):
        """获取所有青年的姓名和身份证号选项"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id_card, name, gender FROM youth ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def search_leader_interviews(self, name='', id_card='', recruitment_place='', company='', platoon='', squad='', time_condition='', time_params=None):
        """搜索领导谈心谈话记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT l.id, l.youth_id_card, l.youth_name, l.gender, l.interview_date, 
                   y.recruitment_place, y.company, y.platoon, y.squad, y.squad_leader,
                   l.thoughts, l.spirit, l.created_at
            FROM leader_interview l
            LEFT JOIN youth y ON l.youth_id_card = y.id_card
            WHERE 1=1
        """
        params = []
        
        # 添加时间筛选条件
        if time_condition:
            query += f" AND {time_condition.replace('interview_date', 'l.interview_date')}"
            params.extend(time_params or [])
        
        if name:
            query += " AND l.youth_name LIKE ?"
            params.append(f'%{name}%')
        if id_card:
            query += " AND l.youth_id_card LIKE ?"
            params.append(f'%{id_card}%')
        if recruitment_place:
            query += " AND y.recruitment_place LIKE ?"
            params.append(f'%{recruitment_place}%')
        if company:
            query += " AND y.company LIKE ?"
            params.append(f'%{company}%')
        if platoon:
            query += " AND y.platoon LIKE ?"
            params.append(f'%{platoon}%')
        if squad:
            query += " AND y.squad LIKE ?"
            params.append(f'%{squad}%')
        
        query += " ORDER BY l.interview_date DESC, l.youth_id_card ASC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def insert_leader_interview(self, youth_id_card, youth_name, gender, interview_date, 
                               visit_survey_image, thoughts, spirit):
        """插入领导谈心谈话记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO leader_interview (youth_id_card, youth_name, gender, interview_date,
                                        visit_survey_image, thoughts, spirit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (youth_id_card, youth_name, gender, interview_date, visit_survey_image, thoughts, spirit))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def update_leader_interview(self, record_id, youth_id_card, youth_name, gender, 
                               interview_date, visit_survey_image, thoughts, spirit):
        """更新领导谈心谈话记录"""
        # 先获取原记录信息用于同步
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT youth_id_card, interview_date 
            FROM leader_interview 
            WHERE id = ?
        ''', (record_id,))
        old_record = cursor.fetchone()
        
        # 更新记录
        if visit_survey_image is not None:
            cursor.execute('''
                UPDATE leader_interview 
                SET youth_id_card=?, youth_name=?, gender=?, interview_date=?,
                    visit_survey_image=?, thoughts=?, spirit=?
                WHERE id=?
            ''', (youth_id_card, youth_name, gender, interview_date, 
                  visit_survey_image, thoughts, spirit, record_id))
        else:
            cursor.execute('''
                UPDATE leader_interview 
                SET youth_id_card=?, youth_name=?, gender=?, interview_date=?,
                    thoughts=?, spirit=?
                WHERE id=?
            ''', (youth_id_card, youth_name, gender, interview_date, 
                  thoughts, spirit, record_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def delete_leader_interviews(self, record_ids):
        """批量删除领导谈心谈话记录"""
        if not record_ids:
            return 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先获取所有记录信息用于同步
        records_to_sync = []
        for record_id in record_ids:
            cursor.execute('''
                SELECT youth_id_card, interview_date 
                FROM leader_interview 
                WHERE id = ?
            ''', (record_id,))
            record_info = cursor.fetchone()
            if record_info:
                records_to_sync.append(record_info)
        
        # 批量删除
        placeholders = ','.join(['?' for _ in record_ids])
        cursor.execute(f'DELETE FROM leader_interview WHERE id IN ({placeholders})', record_ids)
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return deleted_count
    
    def get_leader_interview_image(self, record_id):
        """获取领导谈心谈话记录的图片数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT visit_survey_image FROM leader_interview WHERE id=?', (record_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def search_visit_surveys(self, youth_id_card='', name='', id_card=''):
        """搜索走访调查记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, youth_id_card, youth_name, gender, survey_date, 
                   thoughts, spirit, created_at
            FROM visit_survey WHERE 1=1
        """
        params = []
        
        if youth_id_card:
            query += " AND youth_id_card = ?"
            params.append(youth_id_card)
        if name:
            query += " AND youth_name LIKE ?"
            params.append(f'%{name}%')
        if id_card:
            query += " AND youth_id_card LIKE ?"
            params.append(f'%{id_card}%')
        
        query += " ORDER BY youth_id_card ASC, survey_date ASC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def insert_visit_survey(self, youth_id_card, youth_name, gender, survey_date, 
                           visit_survey_image, thoughts, spirit):
        """插入走访调查记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO visit_survey (youth_id_card, youth_name, gender, survey_date,
                                    visit_survey_image, thoughts, spirit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (youth_id_card, youth_name, gender, survey_date, visit_survey_image, thoughts, spirit))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def update_visit_survey(self, record_id, youth_id_card, youth_name, gender, 
                           survey_date, visit_survey_image, thoughts, spirit):
        """更新走访调查记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if visit_survey_image is not None:
            cursor.execute('''
                UPDATE visit_survey 
                SET youth_id_card=?, youth_name=?, gender=?, survey_date=?,
                    visit_survey_image=?, thoughts=?, spirit=?
                WHERE id=?
            ''', (youth_id_card, youth_name, gender, survey_date, 
                  visit_survey_image, thoughts, spirit, record_id))
        else:
            cursor.execute('''
                UPDATE visit_survey 
                SET youth_id_card=?, youth_name=?, gender=?, survey_date=?,
                    thoughts=?, spirit=?
                WHERE id=?
            ''', (youth_id_card, youth_name, gender, survey_date, 
                  thoughts, spirit, record_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def delete_visit_surveys(self, record_ids):
        """批量删除走访调查记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in record_ids])
        cursor.execute(f'DELETE FROM visit_survey WHERE id IN ({placeholders})', record_ids)
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return deleted_count
    
    def delete_visit_survey(self, record_id):
        """删除单个走访调查记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM visit_survey WHERE id=?', (record_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def get_visit_survey_image(self, record_id):
        """获取走访调查记录的图片数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT visit_survey_image FROM visit_survey WHERE id=?', (record_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None

    # ==================== 入营点验情况相关方法 ====================
    
    def add_camp_verification(self, username, user_id, item, usage, Disposal, data):
        """添加入营点验记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO camp_verification (username, user_id, item, usage, Disposal, data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, user_id, item, usage, Disposal, data))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_camp_verifications_by_user_id(self, user_id):
        """根据身份证号获取入营点验记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, user_id, item, usage, Disposal, data 
            FROM camp_verification 
            WHERE user_id = ?
            ORDER BY data DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        from .models import CampVerification
        records = []
        for row in results:
            cv = CampVerification(
                id=row[0],
                username=row[1],
                user_id=row[2],
                item=row[3],
                usage=row[4],
                Disposal=row[5],
                data=row[6]
            )
            records.append(cv)
        
        return records
    
    def get_camp_verifications_by_username_and_id(self, username, user_id):
        """根据用户名和身份证号同时查询入营点验记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, user_id, item, usage, Disposal, data 
            FROM camp_verification 
            WHERE username = ? AND user_id = ?
            ORDER BY data DESC
        ''', (username, user_id))
        
        results = cursor.fetchall()
        conn.close()
        
        from .models import CampVerification
        records = []
        for row in results:
            cv = CampVerification(
                id=row[0],
                username=row[1],
                user_id=row[2],
                item=row[3],
                usage=row[4],
                Disposal=row[5],
                data=row[6]
            )
            records.append(cv)
        
        return records
    
    def update_camp_verification(self, record_id, item, usage, Disposal, data):
        """更新入营点验记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE camp_verification 
            SET item = ?, usage = ?, Disposal = ?, data = ?
            WHERE id = ?
        ''', (item, usage, Disposal, data, record_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_camp_verification(self, record_id):
        """删除单个入营点验记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM camp_verification WHERE id = ?', (record_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    
    def delete_camp_verifications(self, record_ids):
        """批量删除入营点验记录"""
        if not record_ids:
            return 0
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in record_ids])
        cursor.execute(f'DELETE FROM camp_verification WHERE id IN ({placeholders})', record_ids)
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        return deleted_count
    
    def check_camp_verification_exists(self, user_id):
        """检查指定身份证号是否已存在入营点验记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM camp_verification WHERE user_id = ?
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def delete_camp_verification_by_user_id(self, user_id):
        """删除指定身份证号的所有入营点验记录（用于覆盖操作）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM camp_verification WHERE user_id = ?', (user_id,))
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        return deleted_count
    
    # ==================== 每日情况统计新方法（基于身份证号） ====================
    
    def insert_daily_stat_by_id_card(self, id_card, record_date, mood, physical_condition, mental_state, training, management, notes):
        """基于身份证号插入每日统计"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先获取youth_id
        cursor.execute('SELECT id FROM youth WHERE id_card = ?', (id_card,))
        youth_result = cursor.fetchone()
        
        if not youth_result:
            conn.close()
            raise ValueError(f"未找到身份证号为 {id_card} 的青年信息")
        
        youth_id = youth_result[0]
        
        # 检查是否已存在相同日期的记录
        cursor.execute('''
            SELECT id FROM daily_stat 
            WHERE youth_id = ? AND record_date = ?
        ''', (youth_id, record_date))
        
        existing = cursor.fetchone()
        if existing:
            conn.close()
            raise ValueError(f"该青年在 {record_date} 已有记录，请使用修改功能")
        
        # 插入新记录
        cursor.execute('''
            INSERT INTO daily_stat (youth_id, record_date, mood, physical_condition, 
                                   mental_state, training, management, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (youth_id, record_date, mood, physical_condition, mental_state, training, management, notes))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_all_daily_stats_with_youth_info(self, time_condition='', time_params=None):
        """获取所有每日统计数据，包含青年基本信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        base_query = '''
            SELECT d.id, y.id_card, y.name, y.recruitment_place, y.company, y.platoon, y.squad, y.squad_leader,
                   d.record_date, d.mood, d.physical_condition, d.mental_state, d.training, d.management, d.notes
            FROM daily_stat d
            JOIN youth y ON d.youth_id = y.id
        '''
        
        if time_condition:
            query = base_query + f" WHERE {time_condition.replace('interview_date', 'd.record_date')} ORDER BY d.record_date DESC, y.id_card ASC"
            cursor.execute(query, time_params or [])
        else:
            query = base_query + " ORDER BY d.record_date DESC, y.id_card ASC"
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_daily_stats_with_youth_info(self, name='', id_card='', recruitment_place='', company='', platoon='', squad=''):
        """搜索每日统计数据，包含青年基本信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT d.id, y.id_card, y.name, y.recruitment_place, y.company, y.platoon, y.squad, y.squad_leader,
                   d.record_date, d.mood, d.physical_condition, d.mental_state, d.training, d.management, d.notes
            FROM daily_stat d
            JOIN youth y ON d.youth_id = y.id
            WHERE 1=1
        '''
        params = []
        
        if name:
            query += " AND y.name LIKE ?"
            params.append(f'%{name}%')
        if id_card:
            query += " AND y.id_card LIKE ?"
            params.append(f'%{id_card}%')
        if recruitment_place:
            query += " AND y.recruitment_place LIKE ?"
            params.append(f'%{recruitment_place}%')
        if company:
            query += " AND y.company LIKE ?"
            params.append(f'%{company}%')
        if platoon:
            query += " AND y.platoon LIKE ?"
            params.append(f'%{platoon}%')
        if squad:
            query += " AND y.squad LIKE ?"
            params.append(f'%{squad}%')
        
        query += " ORDER BY d.record_date DESC, y.id_card ASC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def filter_daily_stats_by_date_range(self, start_date, end_date):
        """按日期范围筛选每日统计数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.id, y.id_card, y.name, y.recruitment_place, y.company, y.platoon, y.squad, y.squad_leader,
                   d.record_date, d.mood, d.physical_condition, d.mental_state, d.training, d.management, d.notes
            FROM daily_stat d
            JOIN youth y ON d.youth_id = y.id
            WHERE d.record_date >= ? AND d.record_date <= ?
            ORDER BY d.record_date DESC, y.id_card ASC
        ''', (start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_youth_options_for_daily_stat(self):
        """获取青年选项，用于每日统计的下拉框"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id_card, name 
            FROM youth 
            ORDER BY name ASC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def batch_update_daily_stats(self, record_ids, updates):
        """批量更新每日统计记录
        
        Args:
            record_ids: 记录ID列表
            updates: 更新字段字典，如 {'mood': '正常', 'training': '异常'}
        """
        if not record_ids or not updates:
            return 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 构建更新语句
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in ['mood', 'physical_condition', 'mental_state', 'training', 'management', 'notes', 'record_date']:
                set_clauses.append(f"{field} = ?")
                params.append(value)
        
        if not set_clauses:
            conn.close()
            return 0
        
        # 执行批量更新
        params.extend(record_ids)
        update_query = f'''
            UPDATE daily_stat 
            SET {', '.join(set_clauses)}
            WHERE id IN ({placeholders})
        '''
        
        cursor.execute(update_query, params)
        updated_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return updated_count

    # ==================== 政治考核情况统计表操作 ====================
    
    def get_political_assessments_by_id_card(self, id_card):
        """根据身份证号获取政治考核情况记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, youth_id_card, name, gender, id_card, family_member_info, 
                   visit_survey, political_assessment, key_attention, assessment_date, 
                   thoughts, spirit, created_at
            FROM political_assessment 
            WHERE youth_id_card = ?
            ORDER BY assessment_date DESC
        ''', (id_card,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def insert_political_assessment(self, youth_id_card, name, gender, id_card, 
                                   family_member_info, visit_survey, political_assessment, 
                                   key_attention, assessment_date, thoughts, spirit):
        """插入政治考核情况记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO political_assessment (youth_id_card, name, gender, id_card,
                                            family_member_info, visit_survey, political_assessment,
                                            key_attention, assessment_date, thoughts, spirit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (youth_id_card, name, gender, id_card, family_member_info, visit_survey, 
              political_assessment, key_attention, assessment_date, thoughts, spirit))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def update_political_assessment(self, record_id, family_member_info, visit_survey, 
                                   political_assessment, key_attention, assessment_date, 
                                   thoughts, spirit):
        """更新政治考核情况记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE political_assessment 
            SET family_member_info=?, visit_survey=?, political_assessment=?, 
                key_attention=?, assessment_date=?, thoughts=?, spirit=?
            WHERE id=?
        ''', (family_member_info, visit_survey, political_assessment, key_attention, 
              assessment_date, thoughts, spirit, record_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def delete_political_assessment(self, record_id):
        """删除单个政治考核情况记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM political_assessment WHERE id = ?', (record_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def delete_political_assessments(self, record_ids):
        """批量删除政治考核情况记录"""
        if not record_ids:
            return 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in record_ids])
        cursor.execute(f'DELETE FROM political_assessment WHERE id IN ({placeholders})', record_ids)
        
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        
        return deleted_count

    def check_political_assessment_exists(self, youth_id_card, name, assessment_date):
        """检查政治考核情况记录是否已存在（根据身份证号、姓名和日期）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM political_assessment 
            WHERE youth_id_card = ? AND name = ? AND assessment_date = ?
        ''', (youth_id_card, name, assessment_date))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def update_political_assessment_by_unique_key(self, youth_id_card, name, assessment_date,
                                                  family_member_info, visit_survey, political_assessment,
                                                  key_attention, thoughts, spirit):
        """根据唯一键（身份证号、姓名、日期）更新政治考核情况记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE political_assessment 
            SET family_member_info=?, visit_survey=?, political_assessment=?, 
                key_attention=?, thoughts=?, spirit=?
            WHERE youth_id_card=? AND name=? AND assessment_date=?
        ''', (family_member_info, visit_survey, political_assessment, key_attention, 
              thoughts, spirit, youth_id_card, name, assessment_date))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success

    # ==================== 异常统计视图相关方法 ====================
    
    def _create_exception_statistics_view_if_not_exists(self, cursor):
        """创建异常统计视图（如果不存在）"""
        try:
            # 检查视图是否已存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='v_exception_statistics'")
            if cursor.fetchone():
                return  # 视图已存在，无需创建
            
            # 删除可能存在的旧视图
            cursor.execute("DROP VIEW IF EXISTS v_exception_statistics")
            
            # 创建新的异常统计视图
            cursor.execute('''
                CREATE VIEW v_exception_statistics AS
                WITH all_dates AS (
                    -- 获取所有相关日期
                    SELECT DISTINCT assessment_date as date FROM political_assessment WHERE assessment_date IS NOT NULL AND assessment_date != ''
                    UNION
                    SELECT DISTINCT screening_date as date FROM medical_screening WHERE screening_date IS NOT NULL AND screening_date != ''
                    UNION
                    SELECT DISTINCT district_date as date FROM physical_examination WHERE district_date IS NOT NULL AND district_date != ''
                    UNION
                    SELECT DISTINCT city_date as date FROM physical_examination WHERE city_date IS NOT NULL AND city_date != ''
                    UNION
                    SELECT DISTINCT special_date as date FROM physical_examination WHERE special_date IS NOT NULL AND special_date != ''
                    UNION
                    SELECT DISTINCT record_date as date FROM daily_stat WHERE record_date IS NOT NULL AND record_date != ''
                    UNION
                    SELECT DISTINCT interview_date as date FROM town_interview WHERE interview_date IS NOT NULL AND interview_date != ''
                    UNION
                    SELECT DISTINCT interview_date as date FROM leader_interview WHERE interview_date IS NOT NULL AND interview_date != ''
                ),
                exception_data AS (
                    SELECT DISTINCT
                        y.id_card,
                        y.name,
                        y.gender,
                        y.company,
                        y.platoon,
                        y.squad,
                        y.squad_leader,
                        y.recruitment_place,
                        dates.date,
                        
                        -- 思想异常判断（政治考核、镇街谈话、领导谈话、每日统计）
                        CASE WHEN 
                            EXISTS(SELECT 1 FROM political_assessment pa WHERE pa.youth_id_card = y.id_card AND pa.assessment_date = dates.date AND pa.thoughts = '异常') OR
                            EXISTS(SELECT 1 FROM town_interview ti WHERE ti.youth_id_card = y.id_card AND ti.interview_date = dates.date AND (ti.thoughts LIKE '%异常%' OR ti.thoughts LIKE '%问题%' OR ti.thoughts LIKE '%消极%' OR ti.thoughts LIKE '%抵触%' OR ti.thoughts LIKE '%不良%' OR ti.thoughts LIKE '%困难%' OR ti.thoughts LIKE '%担心%' OR ti.thoughts LIKE '%焦虑%' OR ti.thoughts LIKE '%抑郁%' OR ti.thoughts LIKE '%差%')) OR
                            EXISTS(SELECT 1 FROM leader_interview li WHERE li.youth_id_card = y.id_card AND li.interview_date = dates.date AND (li.thoughts LIKE '%异常%' OR li.thoughts LIKE '%问题%' OR li.thoughts LIKE '%消极%' OR li.thoughts LIKE '%抵触%' OR li.thoughts LIKE '%不良%' OR li.thoughts LIKE '%困难%' OR li.thoughts LIKE '%担心%' OR li.thoughts LIKE '%焦虑%' OR li.thoughts LIKE '%抑郁%' OR li.thoughts LIKE '%差%')) OR
                            EXISTS(SELECT 1 FROM daily_stat ds JOIN youth y2 ON ds.youth_id = y2.id WHERE y2.id_card = y.id_card AND ds.record_date = dates.date AND ds.mood IN ('异常', '差', '很差', '抑郁', '焦虑'))
                        THEN '异常' ELSE '正常' END AS thought_status,
                        
                        -- 身体异常判断（病史筛查、体检、每日统计）
                        CASE WHEN 
                            EXISTS(SELECT 1 FROM medical_screening ms WHERE ms.id_card = y.id_card AND ms.screening_date = dates.date AND ms.physical_status = '异常') OR
                            EXISTS(SELECT 1 FROM physical_examination pe WHERE pe.youth_id_card = y.id_card AND (pe.district_date = dates.date OR pe.city_date = dates.date OR pe.special_date = dates.date) AND pe.body_status = '异常') OR
                            EXISTS(SELECT 1 FROM daily_stat ds JOIN youth y2 ON ds.youth_id = y2.id WHERE y2.id_card = y.id_card AND ds.record_date = dates.date AND ds.physical_condition IN ('异常', '差', '很差', '生病', '受伤'))
                        THEN '异常' ELSE '正常' END AS body_status,
                        
                        -- 精神异常判断（病史筛查、政治考核、镇街谈话、领导谈话、每日统计）
                        CASE WHEN 
                            EXISTS(SELECT 1 FROM medical_screening ms WHERE ms.id_card = y.id_card AND ms.screening_date = dates.date AND ms.mental_status = '异常') OR
                            EXISTS(SELECT 1 FROM political_assessment pa WHERE pa.youth_id_card = y.id_card AND pa.assessment_date = dates.date AND pa.spirit = '异常') OR
                            EXISTS(SELECT 1 FROM town_interview ti WHERE ti.youth_id_card = y.id_card AND ti.interview_date = dates.date AND (ti.spirit LIKE '%异常%' OR ti.spirit LIKE '%问题%' OR ti.spirit LIKE '%抑郁%' OR ti.spirit LIKE '%焦虑%' OR ti.spirit LIKE '%不良%' OR ti.spirit LIKE '%困难%' OR ti.spirit LIKE '%担心%' OR ti.spirit LIKE '%差%')) OR
                            EXISTS(SELECT 1 FROM leader_interview li WHERE li.youth_id_card = y.id_card AND li.interview_date = dates.date AND (li.spirit LIKE '%异常%' OR li.spirit LIKE '%问题%' OR li.spirit LIKE '%抑郁%' OR li.spirit LIKE '%焦虑%' OR li.spirit LIKE '%不良%' OR li.spirit LIKE '%困难%' OR li.spirit LIKE '%担心%' OR li.spirit LIKE '%差%')) OR
                            EXISTS(SELECT 1 FROM daily_stat ds JOIN youth y2 ON ds.youth_id = y2.id WHERE y2.id_card = y.id_card AND ds.record_date = dates.date AND ds.mental_state IN ('异常', '差', '很差', '抑郁', '焦虑', '紧张'))
                        THEN '异常' ELSE '正常' END AS spirit_status,
                        
                        -- 训练异常判断（仅每日统计）
                        CASE WHEN 
                            EXISTS(SELECT 1 FROM daily_stat ds JOIN youth y2 ON ds.youth_id = y2.id WHERE y2.id_card = y.id_card AND ds.record_date = dates.date AND ds.training IN ('异常', '差', '很差', '不合格', '拒绝'))
                        THEN '异常' ELSE '正常' END AS training_status,
                        
                        -- 管理异常判断（仅每日统计）
                        CASE WHEN 
                            EXISTS(SELECT 1 FROM daily_stat ds JOIN youth y2 ON ds.youth_id = y2.id WHERE y2.id_card = y.id_card AND ds.record_date = dates.date AND ds.management IN ('异常', '差', '很差', '违纪', '冲突'))
                        THEN '异常' ELSE '正常' END AS management_status,
                        
                        -- 异常来源统计
                        (
                            SELECT GROUP_CONCAT(source, '、') FROM (
                                SELECT '政治考核' as source WHERE EXISTS(SELECT 1 FROM political_assessment pa WHERE pa.youth_id_card = y.id_card AND pa.assessment_date = dates.date AND (pa.thoughts = '异常' OR pa.spirit = '异常'))
                                UNION ALL
                                SELECT '病史筛查' as source WHERE EXISTS(SELECT 1 FROM medical_screening ms WHERE ms.id_card = y.id_card AND ms.screening_date = dates.date AND (ms.physical_status = '异常' OR ms.mental_status = '异常'))
                                UNION ALL
                                SELECT '体检' as source WHERE EXISTS(SELECT 1 FROM physical_examination pe WHERE pe.youth_id_card = y.id_card AND (pe.district_date = dates.date OR pe.city_date = dates.date OR pe.special_date = dates.date) AND pe.body_status = '异常')
                                UNION ALL
                                SELECT '每日统计' as source WHERE EXISTS(SELECT 1 FROM daily_stat ds JOIN youth y2 ON ds.youth_id = y2.id WHERE y2.id_card = y.id_card AND ds.record_date = dates.date AND (ds.mood IN ('异常', '差', '很差', '抑郁', '焦虑') OR ds.physical_condition IN ('异常', '差', '很差', '生病', '受伤') OR ds.mental_state IN ('异常', '差', '很差', '抑郁', '焦虑', '紧张') OR ds.training IN ('异常', '差', '很差', '不合格', '拒绝') OR ds.management IN ('异常', '差', '很差', '违纪', '冲突')))
                                UNION ALL
                                SELECT '镇街谈话' as source WHERE EXISTS(SELECT 1 FROM town_interview ti WHERE ti.youth_id_card = y.id_card AND ti.interview_date = dates.date AND (ti.thoughts LIKE '%异常%' OR ti.thoughts LIKE '%问题%' OR ti.thoughts LIKE '%消极%' OR ti.thoughts LIKE '%抵触%' OR ti.thoughts LIKE '%不良%' OR ti.thoughts LIKE '%困难%' OR ti.thoughts LIKE '%担心%' OR ti.thoughts LIKE '%焦虑%' OR ti.thoughts LIKE '%抑郁%' OR ti.thoughts LIKE '%差%' OR ti.spirit LIKE '%异常%' OR ti.spirit LIKE '%问题%' OR ti.spirit LIKE '%抑郁%' OR ti.spirit LIKE '%焦虑%' OR ti.spirit LIKE '%不良%' OR ti.spirit LIKE '%困难%' OR ti.spirit LIKE '%担心%' OR ti.spirit LIKE '%差%'))
                                UNION ALL
                                SELECT '领导谈话' as source WHERE EXISTS(SELECT 1 FROM leader_interview li WHERE li.youth_id_card = y.id_card AND li.interview_date = dates.date AND (li.thoughts LIKE '%异常%' OR li.thoughts LIKE '%问题%' OR li.thoughts LIKE '%消极%' OR li.thoughts LIKE '%抵触%' OR li.thoughts LIKE '%不良%' OR li.thoughts LIKE '%困难%' OR li.thoughts LIKE '%担心%' OR li.thoughts LIKE '%焦虑%' OR li.thoughts LIKE '%抑郁%' OR li.thoughts LIKE '%差%' OR li.spirit LIKE '%异常%' OR li.spirit LIKE '%问题%' OR li.spirit LIKE '%抑郁%' OR li.spirit LIKE '%焦虑%' OR li.spirit LIKE '%不良%' OR li.spirit LIKE '%困难%' OR li.spirit LIKE '%担心%' OR li.spirit LIKE '%差%'))
                            )
                        ) AS exception_sources
                        
                    FROM youth y
                    CROSS JOIN all_dates dates
                )
                SELECT 
                    id_card AS 公民身份号码,
                    name AS 姓名,
                    gender AS 性别,
                    company AS 连,
                    platoon AS 排,
                    squad AS 班,
                    squad_leader AS 带训班长,
                    recruitment_place AS 应征地,
                    thought_status AS 思想是否异常,
                    body_status AS 身体是否异常,
                    spirit_status AS 精神是否异常,
                    training_status AS 训练是否异常,
                    management_status AS 管理是否异常,
                    exception_sources AS 其他,
                    date AS 日期
                FROM exception_data
                WHERE 
                    thought_status = '异常' OR 
                    body_status = '异常' OR 
                    spirit_status = '异常' OR 
                    training_status = '异常' OR 
                    management_status = '异常'
                ORDER BY date DESC, name ASC
            ''')
            
        except Exception as e:
            print(f"创建异常统计视图时出错: {e}")

    def create_exception_statistics_view(self):
        """创建异常统计视图（保留此方法以兼容现有代码）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        self._create_exception_statistics_view_if_not_exists(cursor)
        conn.commit()
        conn.close()

    
    def get_exception_statistics_view_data(self, start_date=None, end_date=None, name=None, id_card=None, recruitment_place=None, company=None, platoon=None, squad=None):
        """查询异常统计视图数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM v_exception_statistics WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND 日期 >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND 日期 <= ?"
            params.append(end_date)
        
        if name:
            query += " AND 姓名 LIKE ?"
            params.append(f'%{name}%')
        
        if id_card:
            query += " AND 公民身份号码 LIKE ?"
            params.append(f'%{id_card}%')
        
        if recruitment_place:
            query += " AND 应征地 LIKE ?"
            params.append(f'%{recruitment_place}%')
        
        if company:
            query += " AND 连 LIKE ?"
            params.append(f'%{company}%')
        
        if platoon:
            query += " AND 排 LIKE ?"
            params.append(f'%{platoon}%')
        
        if squad:
            query += " AND 班 LIKE ?"
            params.append(f'%{squad}%')
            query += " AND 班 LIKE ?"
            params.append(f'%{squad}%')
        
        query += " ORDER BY 日期 DESC, 姓名 ASC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_medical_screening_by_id_card_and_date(self, id_card, date):
        """根据身份证号和日期获取病史筛查记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT screening_date, physical_status, mental_status, screening_result, 
                   company, platoon, squad, recruitment_place
            FROM medical_screening 
            WHERE id_card = ? AND screening_date = ?
        ''', (id_card, date))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_political_assessment_by_id_card_and_date(self, id_card, date):
        """根据身份证号和日期获取政治考核记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT assessment_date, thoughts, spirit, family_member_info, 
                   visit_survey, political_assessment, key_attention,
                   (SELECT company FROM youth WHERE id_card = ?) as company,
                   (SELECT platoon FROM youth WHERE id_card = ?) as platoon,
                   (SELECT squad FROM youth WHERE id_card = ?) as squad,
                   (SELECT recruitment_place FROM youth WHERE id_card = ?) as recruitment_place
            FROM political_assessment 
            WHERE youth_id_card = ? AND assessment_date = ?
        ''', (id_card, id_card, id_card, id_card, id_card, date))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_physical_examination_by_id_card_and_date(self, id_card, date):
        """根据身份证号和日期获取体检记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COALESCE(district_date, city_date, special_date) as exam_date,
                   body_status, tracking_opinion, implementation_status,
                   company, platoon, squad, recruitment_place
            FROM physical_examination 
            WHERE youth_id_card = ? AND (district_date = ? OR city_date = ? OR special_date = ?)
        ''', (id_card, date, date, date))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_daily_stat_by_id_card_and_date(self, id_card, date):
        """根据身份证号和日期获取每日统计记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ds.record_date, ds.mood, ds.physical_condition, ds.mental_state, 
                   ds.training, ds.management, ds.notes,
                   y.company, y.platoon, y.squad, y.recruitment_place
            FROM daily_stat ds
            JOIN youth y ON ds.youth_id = y.id
            WHERE y.id_card = ? AND ds.record_date = ?
        ''', (id_card, date))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_town_interview_by_id_card_and_date(self, id_card, date):
        """根据身份证号和日期获取镇街谈心谈话记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT interview_date, thoughts, spirit,
                   (SELECT company FROM youth WHERE id_card = ?) as company,
                   (SELECT platoon FROM youth WHERE id_card = ?) as platoon,
                   (SELECT squad FROM youth WHERE id_card = ?) as squad,
                   (SELECT recruitment_place FROM youth WHERE id_card = ?) as recruitment_place
            FROM town_interview 
            WHERE youth_id_card = ? AND interview_date = ?
        ''', (id_card, id_card, id_card, id_card, id_card, date))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_leader_interview_by_id_card_and_date(self, id_card, date):
        """根据身份证号和日期获取领导谈心谈话记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT interview_date, thoughts, spirit,
                   (SELECT company FROM youth WHERE id_card = ?) as company,
                   (SELECT platoon FROM youth WHERE id_card = ?) as platoon,
                   (SELECT squad FROM youth WHERE id_card = ?) as squad,
                   (SELECT recruitment_place FROM youth WHERE id_card = ?) as recruitment_place
            FROM leader_interview 
            WHERE youth_id_card = ? AND interview_date = ?
        ''', (id_card, id_card, id_card, id_card, id_card, date))
        
        result = cursor.fetchone()
        conn.close()
        return result

    def get_exception_statistics_summary(self, start_date=None, end_date=None):
        """获取异常统计汇总数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                COUNT(*) as 总记录数,
                COUNT(CASE WHEN 思想是否异常 = '异常' THEN 1 END) as 思想异常数,
                COUNT(CASE WHEN 身体是否异常 = '异常' THEN 1 END) as 身体异常数,
                COUNT(CASE WHEN 精神是否异常 = '异常' THEN 1 END) as 精神异常数,
                COUNT(CASE WHEN 训练是否异常 = '异常' THEN 1 END) as 训练异常数,
                COUNT(CASE WHEN 管理是否异常 = '异常' THEN 1 END) as 管理异常数,
                COUNT(DISTINCT 公民身份号码) as 涉及人数,
                COUNT(DISTINCT 日期) as 涉及天数
            FROM v_exception_statistics
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND 日期 >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND 日期 <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        return result

    def sync_recruitment_fields_for_physical_examination(self):
        """同步体检情况统计表中所有记录的应征地、连、排、班、带训班长信息字段"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 批量更新：从youth表获取应征地、连、排、班、带训班长信息并更新到physical_examination表
            cursor.execute('''
                UPDATE physical_examination
                SET recruitment_place = (SELECT recruitment_place FROM youth WHERE youth.id_card = physical_examination.youth_id_card),
                    company = (SELECT company FROM youth WHERE youth.id_card = physical_examination.youth_id_card),
                    platoon = (SELECT platoon FROM youth WHERE youth.id_card = physical_examination.youth_id_card),
                    squad = (SELECT squad FROM youth WHERE youth.id_card = physical_examination.youth_id_card),
                    squad_leader = (SELECT squad_leader FROM youth WHERE youth.id_card = physical_examination.youth_id_card)
                WHERE youth_id_card IN (SELECT id_card FROM youth)
            ''')
            
            updated_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"体检情况统计表同步完成，更新了 {updated_count} 条记录的应征地、连、排、班、带训班长信息字段")
            return updated_count
        except Exception as e:
            print(f"同步体检情况统计表应征地、连、排、班、带训班长信息字段时出错: {e}")
            return 0
