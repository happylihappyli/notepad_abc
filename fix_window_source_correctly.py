#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复窗口显示问题的源代码修正脚本
正确地修复隐藏窗口逻辑
"""

import os
import shutil
import re
from datetime import datetime

def fix_window_source_code():
    """修复窗口显示问题的源代码"""
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始修复窗口显示源代码...")
    
    # 定义文件路径
    notepad_window_file = "PowerEditor\\src\\Notepad_plus_Window.cpp"
    winmain_file = "PowerEditor\\src\\winmain.cpp"
    
    # 备份原始文件
    backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    files_to_fix = [
        (notepad_window_file, f"Notepad_plus_Window.cpp.backup_{backup_timestamp}"),
        (winmain_file, f"winmain.cpp.backup_{backup_timestamp}")
    ]
    
    print("正在备份原始文件...")
    for src_file, backup_name in files_to_fix:
        if os.path.exists(src_file):
            backup_path = backup_name
            shutil.copy2(src_file, backup_path)
            print(f"已备份: {src_file} -> {backup_path}")
        else:
            print(f"警告: 文件不存在 {src_file}")
    
    # 修复 Notepad_plus_Window.cpp 文件
    if os.path.exists(notepad_window_file):
        print(f"正在修复 {notepad_window_file}...")
        
        with open(notepad_window_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复隐藏窗口的逻辑
        # 找到包含 doFunctionListExport 或 doPrintAndExit 的条件判断，并将其禁用
        original_pattern = r'if\s*\(\s*(doFunctionListExport\(\)|doPrintAndExit\(\)|doFunctionListExport\s*\(\s*\)\s*\|\|\s*doPrintAndExit\s*\(\s*\))\s*\)\s*\{\s*::ShowWindow\s*\(\s*_hSelf\s*,\s*SW_HIDE\s*\)\s*;'
        
        def disable_hide_window(match):
            return match.group(0).replace('if (', 'if (false && ')
        
        content = re.sub(original_pattern, disable_hide_window, content)
        
        # 如果上面的正则匹配不到，尝试更简单的匹配方式
        content = content.replace(
            'if (doFunctionListExport() || doPrintAndExit())\n\t{\n\t\t::ShowWindow(_hSelf, SW_HIDE);',
            'if (false && (doFunctionListExport() || doPrintAndExit()))\n\t{\n\t\t::ShowWindow(_hSelf, SW_HIDE);'
        )
        
        content = content.replace(
            'if (doPrintAndExit())\n\t{\n\t\t::ShowWindow(_hSelf, SW_HIDE);',
            'if (false && doPrintAndExit())\n\t{\n\t\t::ShowWindow(_hSelf, SW_HIDE);'
        )
        
        content = content.replace(
            'if (doFunctionListExport())\n\t{\n\t\t::ShowWindow(_hSelf, SW_HIDE);',
            'if (false && doFunctionListExport())\n\t{\n\t\t::ShowWindow(_hSelf, SW_HIDE);'
        )
        
        with open(notepad_window_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已修复 {notepad_window_file} 的隐藏窗口逻辑")
    
    # 修复 winmain.cpp 文件
    if os.path.exists(winmain_file):
        print(f"正在修复 {winmain_file}...")
        
        with open(winmain_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复命令行参数解析逻辑，防止设置 doFunctionListExport 和 doPrintAndExit
        # 通常这些值是通过命令行参数设置的，我们需要找到设置这些值的地方
        
        # 查找设置 doFunctionListExport 的地方
        content = re.sub(
            r'(\s*)nppParameters\.setFunctionListExportBoolean\(.*?\);',
            r'\1// 禁用 FunctionListExport: nppParameters.setFunctionListExportBoolean(false);',
            content
        )
        
        # 查找设置 doPrintAndExit 的地方
        content = re.sub(
            r'(\s*)nppParameters\.setPrintAndExitBoolean\(.*?\);',
            r'\1// 禁用 PrintAndExit: nppParameters.setPrintAndExitBoolean(false);',
            content
        )
        
        # 强制设置这些值为 false
        content = content.replace(
            'nppParameters.setFunctionListExportBoolean(doFunctionListExport);',
            'nppParameters.setFunctionListExportBoolean(false); // 强制禁用以显示窗口'
        )
        
        content = content.replace(
            'nppParameters.setPrintAndExitBoolean(doPrintAndQuit);',
            'nppParameters.setPrintAndExitBoolean(false); // 强制禁用以显示窗口'
        )
        
        with open(winmain_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已修复 {winmain_file} 的命令行参数处理逻辑")
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 源代码修复完成!")
    print("修复内容:")
    print("1. 禁用了隐藏窗口的条件判断（通过false && 条件）")
    print("2. 强制设置相关标志为false")
    print("3. 备份了原始文件到备份文件")
    print("\n请重新编译项目以应用修改。")

if __name__ == "__main__":
    fix_window_source_code()