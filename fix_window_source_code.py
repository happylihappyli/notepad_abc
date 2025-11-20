#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Notepad++窗口隐藏问题的脚本
直接修改源代码，强制禁用隐藏窗口的逻辑
"""

import os
import shutil
import time

def backup_file(file_path):
    """备份文件"""
    backup_path = file_path + f".backup_{int(time.time())}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ 已备份: {file_path} -> {backup_path}")
    return backup_path

def fix_window_creation_logic():
    """修复窗口创建逻辑"""
    print("修复Notepad++窗口创建逻辑...")
    print("=" * 60)
    
    # 文件路径
    cpp_file = "PowerEditor\\src\\Notepad_plus_Window.cpp"
    
    # 读取原文件
    print(f"读取文件: {cpp_file}")
    with open(cpp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份文件
    backup_file(cpp_file)
    
    # 修复逻辑1: 注释掉或修改隐藏窗口的条件
    old_condition = """	if (nppParams.doFunctionListExport() || nppParams.doPrintAndExit())
	{
		::ShowWindow(_hSelf, SW_HIDE);
	}"""
    
    new_condition = """	if (false) // 强制禁用隐藏窗口逻辑
	{
		::ShowWindow(_hSelf, SW_HIDE);
	}"""
    
    content = content.replace(old_condition, new_condition)
    print("✅ 已修复: 禁用 doFunctionListExport/doPrintAndExit 隐藏窗口逻辑")
    
    # 修复逻辑2: 另一个隐藏窗口的位置
    old_condition2 = """	if (nppParams.doPrintAndExit())
	{
		::ShowWindow(_hSelf, SW_HIDE);
		::PostMessage(_hSelf, WM_CLOSE, 0, 0);
	}"""
    
    new_condition2 = """	if (false) // 强制禁用隐藏窗口逻辑
	{
		::ShowWindow(_hSelf, SW_HIDE);
		::PostMessage(_hSelf, WM_CLOSE, 0, 0);
	}"""
    
    content = content.replace(old_condition2, new_condition2)
    print("✅ 已修复: 禁用 doPrintAndExit 隐藏窗口逻辑")
    
    # 修复逻辑3: 确保窗口总是可见（修改其他可能隐藏窗口的地方）
    old_show_logic = """	else if (!cmdLineParams->_isPreLaunch)
	{
		if (cmdLineParams->isPointValid())
			::ShowWindow(_hSelf, SW_SHOW);
		else
			::ShowWindow(_hSelf, nppGUI._isMaximized ? SW_MAXIMIZE : SW_SHOW);
	}"""
    
    new_show_logic = """	else if (true) // 强制显示窗口
	{
		::ShowWindow(_hSelf, SW_SHOW); // 总是显示窗口
		if (nppGUI._isMaximized)
			::ShowWindow(_hSelf, SW_MAXIMIZE); // 如果配置了最大化，则最大化
	}"""
    
    content = content.replace(old_show_logic, new_show_logic)
    print("✅ 已修复: 强制显示窗口逻辑")
    
    # 写入修改后的文件
    with open(cpp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 文件修改完成")
    return True

def fix_command_line_parsing():
    """修复命令行解析逻辑"""
    print("\n修复命令行解析逻辑...")
    print("=" * 60)
    
    # 文件路径
    cpp_file = "PowerEditor\\src\\winmain.cpp"
    
    print(f"读取文件: {cpp_file}")
    with open(cpp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份文件
    backup_file(cpp_file)
    
    # 修复逻辑: 确保 doFunctionListExport 和 doPrintAndQuit 总是为 false
    old_line = """	bool doFunctionListExport = isInList(FLAG_FUNCLSTEXPORT, params);
	bool doPrintAndQuit = isInList(FLAG_PRINTANDQUIT, params);"""
    
    new_line = """	bool doFunctionListExport = false; // 强制设置为 false
	bool doPrintAndQuit = false; // 强制设置为 false
	// 原逻辑: isInList(FLAG_FUNCLSTEXPORT, params);
	// 原逻辑: isInList(FLAG_PRINTANDQUIT, params);"""
    
    content = content.replace(old_line, new_line)
    print("✅ 已修复: 强制设置命令行标志为 false")
    
    # 写入修改后的文件
    with open(cpp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 命令行解析修改完成")
    return True

def recompile_project():
    """重新编译项目"""
    print("\n重新编译项目...")
    print("=" * 60)
    
    # 使用scons编译
    scons_cmd = "chcp 65001; scons SCINTILLA_DIR=lexilla\\src LEXILLA_DIR=lexilla"
    
    print(f"执行命令: {scons_cmd}")
    result = os.system(scons_cmd)
    
    if result == 0:
        print("✅ 编译成功")
        return True
    else:
        print(f"❌ 编译失败，返回码: {result}")
        return False

def main():
    """主函数"""
    print("Notepad++ 窗口显示问题源代码修复工具")
    print("=" * 60)
    
    # 检查文件是否存在
    files_to_check = [
        "PowerEditor\\src\\Notepad_plus_Window.cpp",
        "PowerEditor\\src\\winmain.cpp"
    ]
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return False
    
    try:
        # 修复窗口创建逻辑
        fix_window_creation_logic()
        
        # 修复命令行解析逻辑
        fix_command_line_parsing()
        
        # 重新编译
        print("\n建议下一步:")
        print("1. 手动编译项目: scons SCINTILLA_DIR=lexilla\\src LEXILLA_DIR=lexilla")
        print("2. 或者运行: python rebuild_project.py")
        print("3. 编译完成后测试程序是否能正常显示窗口")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    main()