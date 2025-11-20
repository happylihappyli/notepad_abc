#!/usr/bin/env python3
"""
修复WinMain.cpp中未定义的log_message函数调用
"""
import os
import re
from datetime import datetime

def fix_log_message_calls():
    """移除未定义的log_message函数调用"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始修复WinMain.cpp中的log_message调用...")
    
    # 读取WinMain.cpp文件
    winmain_path = "PowerEditor\\src\\winmain.cpp"
    backup_path = f"{winmain_path}.backup_log_fix"
    
    try:
        # 创建备份
        if os.path.exists(winmain_path):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建备份文件: {backup_path}")
            with open(winmain_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # 读取当前内容
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 读取WinMain.cpp文件...")
        with open(winmain_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 计算修复前的log_message调用数量
        log_calls = re.findall(r'log_message\([^)]+\);?', content)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 发现 {len(log_calls)} 个log_message调用需要移除")
        
        # 移除所有log_message调用
        # 匹配 log_message("..."); 模式
        pattern = r'\s*log_message\([^)]+\);\s*'
        fixed_content = re.sub(pattern, '\n', content)
        
        # 清理多余的空行
        fixed_content = re.sub(r'\n\s*\n\s*\n', '\n\n', fixed_content)
        
        # 写入修复后的内容
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 移除log_message调用...")
        with open(winmain_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] WinMain文件修复完成")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 已移除 {len(log_calls)} 个log_message调用")
        
        return True
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 修复失败: {str(e)}")
        return False

def compile_project():
    """编译项目"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始编译项目...")
    
    # 设置编码
    os.system("chcp 65001 >nul 2>&1")
    
    # 清理旧文件
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 清理旧文件...")
    os.system("rmdir /s /q obj >nul 2>&1")
    os.system("rmdir /s /q bin >nul 2>&1")
    
    # 编译项目
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行scons编译...")
    result = os.system("scons")
    
    if result == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 编译成功！")
        return True
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 编译失败，返回码: {result}")
        return False

def main():
    """主函数"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始log_message修复...")
    
    # 修复log_message调用
    if fix_log_message_calls():
        # 编译项目
        if compile_project():
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 修复完成！")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 现在可以测试程序是否能正常显示GUI窗口")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 编译仍然失败")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 修复失败")

if __name__ == "__main__":
    main()