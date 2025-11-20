#!/usr/bin/env python3
"""
简单修复WinMain.cpp中的代码缩进问题
"""
from datetime import datetime

def fix_simple_indentation():
    """简单修复缩进问题"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始修复代码缩进...")
    
    winmain_path = "PowerEditor\\src\\winmain.cpp"
    
    try:
        # 读取文件
        with open(winmain_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 创建备份
        backup_path = f"{winmain_path}.backup_simple_fix"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建备份文件: {backup_path}")
        
        # 查找并修复有问题的行
        fixed_lines = []
        for i, line in enumerate(lines):
            # 查找问题行
            if ('notepad_plus_plus.init(' in line and 
                line.strip() and 
                not line.startswith('\t') and 
                not line.startswith('    ')):
                # 这行缺少缩进，添加正确的缩进
                fixed_lines.append('\t\tnotepad_plus_plus.init(hInstance, NULL, quotFileName.c_str(), &cmdLineParams);\n')
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 修复第{i+1}行的缩进: notepad_plus_plus.init")
            elif ('allowPrivilegeMessages(' in line and 
                  line.strip() and 
                  not line.startswith('\t') and 
                  not line.startswith('    ')):
                # 这行缺少缩进，添加正确的缩进
                fixed_lines.append('\t\tallowPrivilegeMessages(notepad_plus_plus, ver);\n')
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 修复第{i+1}行的缩进: allowPrivilegeMessages")
            elif ('bool going = true;' in line and 
                  line.strip() and 
                  not line.startswith('\t') and 
                  not line.startswith('    ')):
                # 这行缺少缩进，添加正确的缩进
                fixed_lines.append('\t\tbool going = true;\n')
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 修复第{i+1}行的缩进: bool going = true;")
            else:
                fixed_lines.append(line)
        
        # 写入修复后的内容
        with open(winmain_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 代码缩进修复完成")
        return True
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 修复失败: {str(e)}")
        return False

def main():
    """主函数"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始简单缩进修复...")
    
    if fix_simple_indentation():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 修复完成！")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 修复失败")

if __name__ == "__main__":
    main()