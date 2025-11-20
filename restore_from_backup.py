#!/usr/bin/env python3
"""
从备份文件恢复WinMain.cpp
"""
import os
import glob
from datetime import datetime

def restore_from_backup():
    """从备份恢复WinMain.cpp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始恢复WinMain.cpp...")
    
    winmain_path = "PowerEditor\\src\\winmain.cpp"
    
    # 查找所有备份文件
    backup_files = []
    for backup in glob.glob(f"{winmain_path}.backup*"):
        backup_files.append(backup)
    
    if not backup_files:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 没有找到备份文件")
        return False
    
    # 按时间排序，选择最新的备份
    backup_files.sort(key=os.path.getmtime, reverse=True)
    latest_backup = backup_files[0]
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 使用备份文件: {latest_backup}")
    
    try:
        # 复制备份文件到原位置
        with open(latest_backup, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(winmain_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 恢复完成")
        return True
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 恢复失败: {str(e)}")
        return False

def main():
    """主函数"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 从备份恢复WinMain.cpp...")
    
    if restore_from_backup():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 恢复完成！")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 恢复失败")

if __name__ == "__main__":
    main()