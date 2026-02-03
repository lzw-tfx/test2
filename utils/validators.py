"""
数据验证工具
"""
import re


def validate_id_card(id_card):
    """验证身份证号 - 必须是18位（可含英文字符X）"""
    if not id_card:
        return False, "身份证号不能为空"
    
    # 18位身份证号验证：17位数字 + 1位数字或X
    if len(id_card) != 18:
        return False, f"身份证号必须是18位，当前为{len(id_card)}位"
    
    pattern = r'^\d{17}[\dXx]$'
    if not re.match(pattern, id_card):
        return False, "身份证号格式不正确（应为17位数字+1位数字或X）"
    
    return True, ""


def validate_phone(phone):
    """验证手机号 - 必须是11位数字"""
    if not phone:
        return True, ""  # 允许为空
    
    # 移除可能的空格和分隔符
    phone_clean = phone.replace(' ', '').replace('-', '')
    
    if len(phone_clean) != 11:
        return False, f"电话号码必须是11位数字，当前为{len(phone_clean)}位"
    
    pattern = r'^1[3-9]\d{9}$'
    if not re.match(pattern, phone_clean):
        return False, "电话号码格式不正确（应为1开头的11位数字）"
    
    return True, ""


def validate_required_fields(data, required_fields):
    """验证必填字段"""
    for field in required_fields:
        if not data.get(field):
            return False, f"字段 {field} 不能为空"
    return True, ""


def validate_date(date_str):
    """验证日期格式 YYYY-MM-DD"""
    if not date_str:
        return True, ""  # 允许为空
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False, "日期格式不正确（应为YYYY-MM-DD）"
    
    return True, ""


def validate_youth_data(youth_data):
    """验证青年基本信息数据（新结构40字段）
    数据顺序：id_card, name, gender, birth_date, nation, political_status, religion, native_place,
             education_level, study_status, study_type, camp_entry_time, recruitment_place,
             residence_address, household_address, postal_code, personal_phone, family_phone,
             school, major, enrollment_time, initial_hospital, initial_conclusion, initial_time,
             physical_conclusion, physical_time, physical_disqualification, chief_doctor_opinion,
             graduation_time, company, platoon, squad, squad_leader, camp_status, leave_time, leave_reason
    """
    errors = []
    
    # 验证姓名 (索引1)
    if not youth_data[1] or not youth_data[1].strip():
        errors.append("姓名不能为空")
    
    # 验证身份证号 (索引0)
    if len(youth_data) > 0:
        is_valid, error_msg = validate_id_card(youth_data[0])
        if not is_valid:
            errors.append(error_msg)
    else:
        errors.append("身份证号不能为空")
    
    # 验证在营状态和离营时间、离营原因的业务逻辑
    if len(youth_data) > 35:
        camp_status = youth_data[33] if len(youth_data) > 33 else ''
        leave_time = youth_data[34] if len(youth_data) > 34 else ''
        leave_reason = youth_data[35] if len(youth_data) > 35 else ''
        
        if camp_status == '在营':
            # 在营时，离营时间和离营原因必须为空
            if leave_time and leave_time.strip():
                errors.append('当"在营状态"为"在营"时，"离营时间"必须为空')
            if leave_reason and leave_reason.strip():
                errors.append('当"在营状态"为"在营"时，"离营原因"必须为空')
        elif camp_status == '离营':
            # 离营时，离营时间和离营原因必须不为空
            if not leave_time or not leave_time.strip():
                errors.append('当"在营状态"为"离营"时，"离营时间"必须填写')
            if not leave_reason or not leave_reason.strip():
                errors.append('当"在营状态"为"离营"时，"离营原因"必须填写')
        elif camp_status and camp_status not in ['在营', '离营', '其他']:
            errors.append('"在营状态"只能为"在营"、"离营"或"其他"')
    
    # 验证本人电话 (索引16 - personal_phone字段)
    if len(youth_data) > 16 and youth_data[16]:
        is_valid, error_msg = validate_phone(youth_data[16])
        if not is_valid:
            errors.append(f"本人电话: {error_msg}")
    
    # 验证家庭电话 (索引17 - family_phone字段)
    if len(youth_data) > 17 and youth_data[17]:
        # 家庭电话可能包含多个号码，用逗号分隔
        family_phones = str(youth_data[17]).replace('，', ',').split(',')
        for i, phone in enumerate(family_phones, 1):
            phone = phone.strip()
            if phone:
                is_valid, error_msg = validate_phone(phone)
                if not is_valid:
                    errors.append(f"家庭电话{i}: {error_msg}")
    
    if errors:
        return False, "; ".join(errors)
    
    return True, ""
