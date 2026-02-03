"""
数据模型定义
"""

class Youth:
    """青年基本信息（完整版）"""
    def __init__(self, id_card='', name='', gender='', birth_date='', nation='',
                 political_status='', religion='', native_place='', education_level='', 
                 study_status='', study_type='', camp_entry_time='', recruitment_place='', 
                 residence_address='', household_address='', postal_code='', personal_phone='', 
                 family_phone='', school='', major='', enrollment_time='', initial_hospital='', 
                 initial_conclusion='', initial_time='', physical_conclusion='', physical_time='', 
                 physical_disqualification='', chief_doctor_opinion='', graduation_time='', 
                 physical_examination='', medical_history_survey='', political_assessment='', 
                 company='', platoon='', squad='', squad_leader='', information='', 
                 item_verification='', special_reexamination='', camp_status='', leave_time='', 
                 leave_reason='', district_positive='', city_positive='', special_screening_positive='',
                 psychological_test_type='', tracking_opinion='', implementation_status='',
                 district_medical_survey='', city_medical_survey='', province_medical_survey='',
                 family_member_info='', visit_survey='', political_assessment2='', key_attention='',
                 items='', usage='', disposal_measures='', reexamination_time='', existing_situation='',
                 reexamination_conclusion='', id=None):
        self.id_card = id_card  # 主键：身份证号
        self.name = name
        self.gender = gender
        self.birth_date = birth_date  # 出生日期
        self.nation = nation
        self.political_status = political_status
        self.religion = religion  # 宗教信仰
        self.native_place = native_place  # 籍贯
        self.education_level = education_level
        self.study_status = study_status  # 学业情况
        self.study_type = study_type  # 学习类型
        self.camp_entry_time = camp_entry_time  # 入营时间
        self.recruitment_place = recruitment_place  # 应征地
        self.residence_address = residence_address  # 经常居住地址
        self.household_address = household_address  # 户籍所在地
        self.postal_code = postal_code  # 邮编
        self.personal_phone = personal_phone  # 本人电话
        self.family_phone = family_phone  # 家庭电话
        self.school = school  # 毕业(就读)学校
        self.major = major  # 所学专业
        self.enrollment_time = enrollment_time  # 入学时间
        self.initial_hospital = initial_hospital  # 初检医院
        self.initial_conclusion = initial_conclusion  # 初检结论
        self.initial_time = initial_time  # 初检时间
        self.physical_conclusion = physical_conclusion  # 体检结论
        self.physical_time = physical_time  # 体检时间
        self.physical_disqualification = physical_disqualification  # 体检不合格原因
        self.chief_doctor_opinion = chief_doctor_opinion  # 主检医师意见
        self.graduation_time = graduation_time  # 毕业时间
        self.physical_examination = physical_examination  # 体格检查情况
        self.medical_history_survey = medical_history_survey  # 病史调查情况
        self.political_assessment = political_assessment  # 政治考核情况
        self.company = company  # 连
        self.platoon = platoon  # 排
        self.squad = squad  # 班
        self.squad_leader = squad_leader  # 带训班长
        self.information = information  # 信息
        self.item_verification = item_verification  # 物品点验情况
        self.special_reexamination = special_reexamination  # 专项复查情况
        self.camp_status = camp_status  # 在营状态
        self.leave_time = leave_time  # 离营时间
        self.leave_reason = leave_reason  # 离营原因
        self.district_positive = district_positive  # 区检阳性特征/边缘问题
        self.city_positive = city_positive  # 市检阳性特征/边缘问题
        self.special_screening_positive = special_screening_positive  # 专项筛查阳性特征/边缘问题
        self.psychological_test_type = psychological_test_type  # 心理检测类型
        self.tracking_opinion = tracking_opinion  # 跟踪处置意见
        self.implementation_status = implementation_status  # 处置意见落实情况
        self.district_medical_survey = district_medical_survey  # 区级病史调查情况
        self.city_medical_survey = city_medical_survey  # 市级病史调查情况
        self.province_medical_survey = province_medical_survey  # 省级病史调查情况
        self.family_member_info = family_member_info  # 家庭成员信息
        self.visit_survey = visit_survey  # 走访调查情况
        self.political_assessment2 = political_assessment2  # 政治考核情况2
        self.key_attention = key_attention  # 需重点关注情况
        self.items = items  # 物品
        self.usage = usage  # 用途
        self.disposal_measures = disposal_measures  # 处置措施
        self.reexamination_time = reexamination_time  # 复查时间
        self.existing_situation = existing_situation  # 存在情况
        self.reexamination_conclusion = reexamination_conclusion  # 复查结论
        self.id = id  # 序号字段（保留但不显示）


class MedicalHistory:
    """病史调查"""
    def __init__(self, id=None, youth_id=None, file_path='', upload_date='', notes=''):
        self.id = id
        self.youth_id = youth_id
        self.file_path = file_path
        self.upload_date = upload_date
        self.notes = notes


class MedicalScreening:
    """病史筛查"""
    def __init__(self, id=None, youth_id_card='', name='', gender='', id_card='',
                 screening_result='', screening_date='', physical_status='', mental_status='',
                 recruitment_place='', company='', platoon='', squad='', remark=''):
        self.id = id
        self.youth_id_card = youth_id_card  # 关联青年身份证号
        self.name = name
        self.gender = gender
        self.id_card = id_card
        self.screening_result = screening_result
        self.screening_date = screening_date
        self.physical_status = physical_status
        self.mental_status = mental_status
        self.recruitment_place = recruitment_place  # 应征地
        self.company = company  # 连
        self.platoon = platoon  # 排
        self.squad = squad  # 班
        self.remark = remark  # 备注


class TownInterview:
    """镇街谈心谈话情况"""
    def __init__(self, id=None, youth_id_card='', youth_name='', gender='', 
                 interview_date='', visit_survey_image=None, thoughts='', spirit=''):
        self.id = id  # 序号（自动生成）
        self.youth_id_card = youth_id_card  # 公民身份号码（外键）
        self.youth_name = youth_name  # 姓名
        self.gender = gender  # 性别
        self.interview_date = interview_date  # 日期
        self.visit_survey_image = visit_survey_image  # 走访调查情况（二进制图片数据）
        self.thoughts = thoughts  # 思想
        self.spirit = spirit  # 精神


class LeaderInterview:
    """领导谈心谈话情况"""
    def __init__(self, id=None, youth_id_card='', youth_name='', gender='', 
                 interview_date='', visit_survey_image=None, thoughts='', spirit=''):
        self.id = id  # 序号（自动生成）
        self.youth_id_card = youth_id_card  # 公民身份号码（外键）
        self.youth_name = youth_name  # 姓名
        self.gender = gender  # 性别
        self.interview_date = interview_date  # 日期
        self.visit_survey_image = visit_survey_image  # 走访调查情况（二进制图片数据）
        self.thoughts = thoughts  # 思想
        self.spirit = spirit  # 精神


class VisitSurvey:
    """走访调查情况"""
    def __init__(self, id=None, youth_id_card='', youth_name='', gender='', 
                 survey_date='', visit_survey_image=None, thoughts='', spirit=''):
        self.id = id  # 序号（自动生成）
        self.youth_id_card = youth_id_card  # 公民身份号码（外键）
        self.youth_name = youth_name  # 姓名
        self.gender = gender  # 性别
        self.survey_date = survey_date  # 日期
        self.visit_survey_image = visit_survey_image  # 走访调查情况（二进制图片数据）
        self.thoughts = thoughts  # 思想
        self.spirit = spirit  # 精神


class DailyStat:
    """每日情况统计"""
    def __init__(self, id=None, youth_id=None, record_date='', mood='', 
                 physical_condition='', training_status='', notes=''):
        self.id = id
        self.youth_id = youth_id
        self.record_date = record_date
        self.mood = mood
        self.physical_condition = physical_condition
        self.training_status = training_status
        self.notes = notes


class AbnormalStat:
    """异常情况统计"""
    def __init__(self, id=None, youth_id=None, abnormal_type='', 
                 description='', record_date='', handler='', status=''):
        self.id = id
        self.youth_id = youth_id
        self.abnormal_type = abnormal_type
        self.description = description
        self.record_date = record_date
        self.handler = handler
        self.status = status


class HealthScreening:
    """隐性疾病及心理问题筛查"""
    def __init__(self, id=None, youth_id=None, screening_type='',
                 result='', screening_date='', follow_up=''):
        self.id = id
        self.youth_id = youth_id
        self.screening_type = screening_type
        self.result = result
        self.screening_date = screening_date
        self.follow_up = follow_up


class CampVerification:
    """入营点验情况"""
    def __init__(self, id=None, username='', user_id='', item='', 
                 usage='', Disposal='', data=''):
        self.id = id
        self.username = username
        self.user_id = user_id  # 身份证号，类型为text，非空
        self.item = item  # text类型
        self.usage = usage  # 用途，text类型
        self.Disposal = Disposal  # text类型
        self.data = data  # 日期


class ExceptionStatistics:
    """异常情况统计"""
    def __init__(self, id=None, name='', gender='', user_id='', thought=False,
                 body=False, Spirit=False, other=False, data='', created_at='', updated_at=''):
        self.id = id
        self.name = name  # 姓名
        self.gender = gender  # 性别
        self.user_id = user_id  # 身份证号，类型为text，非空
        self.thought = thought  # 思想问题，布尔类型
        self.body = body  # 身体问题，布尔类型
        self.Spirit = Spirit  # 精神问题，布尔类型
        self.other = other  # 其他问题，布尔类型
        self.data = data  # 日期，格式为2025/8/8
        self.created_at = created_at  # 创建时间
        self.updated_at = updated_at  # 更新时间


class PoliticalAssessment:
    """政治考核情况统计表"""
    def __init__(self, id=None, youth_id_card='', name='', gender='', id_card='',
                 family_member_info='', visit_survey='', political_assessment='', 
                 key_attention='', assessment_date='', thoughts='', spirit=''):
        self.id = id  # 序号（自动生成）
        self.youth_id_card = youth_id_card  # 公民身份号码（外键）
        self.name = name  # 姓名
        self.gender = gender  # 性别
        self.id_card = id_card  # 公民身份号码
        self.family_member_info = family_member_info  # 家庭成员信息
        self.visit_survey = visit_survey  # 走访调查情况
        self.political_assessment = political_assessment  # 政治考核情况
        self.key_attention = key_attention  # 需重点关注问题
        self.assessment_date = assessment_date  # 日期
        self.thoughts = thoughts  # 思想
        self.spirit = spirit  # 精神


class PhysicalExamination:
    """体检情况统计表"""
    def __init__(self, id=None, youth_id_card='', name='', gender='',
                 district_exam='', district_positive='', district_date='',
                 city_exam='', city_positive='', city_date='',
                 special_exam='', special_positive='', special_date='',
                 body_status='', psychological_test_type='',
                 tracking_opinion='', implementation_status='',
                 recruitment_place='', company='', platoon='', squad='', squad_leader=''):
        self.id = id
        self.youth_id_card = youth_id_card  # 公民身份号码
        self.name = name  # 姓名
        self.gender = gender  # 性别
        self.district_exam = district_exam  # 区体检
        self.district_positive = district_positive  # 区检阳性特征/边缘问题
        self.district_date = district_date  # 区体检日期
        self.city_exam = city_exam  # 市体检
        self.city_positive = city_positive  # 市检阳性特征/边缘问题
        self.city_date = city_date  # 市体检日期
        self.special_exam = special_exam  # 专项复查
        self.special_positive = special_positive  # 专项筛查阳性特征/边缘问题
        self.special_date = special_date  # 专项复查日期
        self.body_status = body_status  # 身体状况（正常或异常）
        self.psychological_test_type = psychological_test_type  # 心理检测类型
        self.tracking_opinion = tracking_opinion  # 跟踪处置意见
        self.implementation_status = implementation_status  # 处置意见落实情况
        self.recruitment_place = recruitment_place  # 应征地
        self.company = company  # 连
        self.platoon = platoon  # 排
        self.squad = squad  # 班
        self.squad_leader = squad_leader  # 带训班长


class User:
    """用户账户"""
    def __init__(self, id=None, username='', password='', role='', unit=''):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.unit = unit
