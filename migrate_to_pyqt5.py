#!/usr/bin/env python3
"""
PyQt6 到 PyQt5 自动迁移脚本
用于将项目从 PyQt6 迁移到 PyQt5（兼容 Python 3.8.2）
"""
import os
import re
import shutil
from datetime import datetime

def backup_file(filepath):
    """备份文件"""
    backup_dir = "backup_before_migration"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 保持目录结构
    rel_path = os.path.relpath(filepath)
    backup_path = os.path.join(backup_dir, rel_path)
    backup_dir_path = os.path.dirname(backup_path)
    
    if not os.path.exists(backup_dir_path):
        os.makedirs(backup_dir_path)
    
    shutil.copy2(filepath, backup_path)

def replace_in_file(filepath):
    """替换文件中的 PyQt6 导入为 PyQt5"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换导入语句
        content = content.replace('from PyQt5.QtWidgets', 'from PyQt5.QtWidgets')
        content = content.replace('from PyQt5.QtCore', 'from PyQt5.QtCore')
        content = content.replace('from PyQt5.QtGui', 'from PyQt5.QtGui')
        content = content.replace('from PyQt5.QtChart', 'from PyQt5.QtChart')
        content = content.replace('from PyQt5 import', 'from PyQt5 import')
        
        content = content.replace('import PyQt5.QtWidgets', 'import PyQt5.QtWidgets')
        content = content.replace('import PyQt5.QtCore', 'import PyQt5.QtCore')
        content = content.replace('import PyQt5.QtGui', 'import PyQt5.QtGui')
        content = content.replace('import PyQt5.QtChart', 'import PyQt5.QtChart')
        content = content.replace('import PyQt5', 'import PyQt5')
        
        # 替换常见的枚举用法（PyQt6 → PyQt5）
        # Qt.AlignCenter → Qt.AlignCenter
        content = re.sub(r'Qt\.AlignmentFlag\.(\w+)', r'Qt.\1', content)
        
        # QHeaderView.Interactive → QHeaderView.Interactive
        content = re.sub(r'QHeaderView\.ResizeMode\.(\w+)', r'QHeaderView.\1', content)
        
        # Qt.Dialog → Qt.Dialog
        content = re.sub(r'Qt\.WindowType\.(\w+)', r'Qt.\1', content)
        
        # Qt.ItemIsEnabled → Qt.ItemIsEnabled
        content = re.sub(r'Qt\.ItemFlag\.(\w+)', r'Qt.\1', content)
        
        # 替换 exec() 为 exec_()（如果有）
        content = re.sub(r'\.exec\(\)', r'.exec_()', content)
        
        # 只有内容发生变化时才写入
        if content != original_content:
            # 备份原文件
            backup_file(filepath)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ 已处理: {filepath}")
            return True
        else:
            print(f"- 跳过（无需修改）: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ 错误处理 {filepath}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("PyQt6 → PyQt5 自动迁移脚本")
    print("=" * 80)
    print()
    
    # 统计
    total_files = 0
    modified_files = 0
    
    # 遍历项目目录
    for root, dirs, files in os.walk('.'):
        # 跳过不需要处理的目录
        skip_dirs = ['venv', 'venv_package', '__pycache__', '.git', 'backup_before_migration', 
                     'build', 'dist', '.conda']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_files += 1
                
                if replace_in_file(filepath):
                    modified_files += 1
    
    print()
    print("=" * 80)
    print("迁移完成！")
    print("=" * 80)
    print(f"总共扫描文件: {total_files}")
    print(f"修改的文件: {modified_files}")
    print(f"未修改的文件: {total_files - modified_files}")
    print()
    print("备份位置: ./backup_before_migration/")
    print()
    print("下一步:")
    print("1. 更新 requirements.txt（使用 requirements_pyqt5.txt）")
    print("2. 重新安装依赖: pip install -r requirements.txt")
    print("3. 测试程序: python main.py")
    print("4. 如果有问题，可以从 backup_before_migration/ 恢复文件")
    print()

if __name__ == '__main__':
    # 确认操作
    print("=" * 80)
    print("警告：此脚本将修改项目中的所有 Python 文件")
    print("=" * 80)
    print()
    print("操作内容：")
    print("1. 将所有 PyQt6 导入替换为 PyQt5")
    print("2. 调整枚举用法（PyQt6 → PyQt5）")
    print("3. 替换 exec() 为 exec_()")
    print("4. 自动备份所有修改的文件到 backup_before_migration/")
    print()
    
    response = input("是否继续？(yes/no): ").strip().lower()
    
    if response in ['yes', 'y', '是']:
        print()
        main()
    else:
        print("操作已取消")
