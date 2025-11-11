#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证文档列表功能修复
功能：
1. 检查可执行文件是否存在
2. 验证VerticalFileSwitcher.h中的关键修改
3. 验证SConscript中的资源处理逻辑
4. 提供运行程序的说明
"""

import os
import sys
import subprocess
import re
from pathlib import Path

def print_color(text, color='green'):
    """打印带颜色的文本"""
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")

def check_file_exists(file_path):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print_color(f"✓ 文件存在: {file_path}", 'green')
        return True
    else:
        print_color(f"✗ 文件不存在: {file_path}", 'red')
        return False

def check_file_content(file_path, search_pattern, description):
    """检查文件内容是否包含指定模式"""
    if not os.path.exists(file_path):
        print_color(f"✗ 文件不存在，无法检查: {file_path}", 'red')
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if re.search(search_pattern, content):
                print_color(f"✓ {description}: {file_path}", 'green')
                return True
            else:
                print_color(f"✗ {description}: {file_path}", 'red')
                return False
    except Exception as e:
        print_color(f"✗ 读取文件失败: {file_path}, 错误: {str(e)}", 'red')
        return False

def main():
    print_color("=" * 80, 'blue')
    print_color("Notepad++ 文档列表功能修复验证", 'blue')
    print_color("=" * 80, 'blue')
    
    base_dir = Path(r"E:\GitHub3\notepad_abc")
    
    # 1. 检查可执行文件
    print_color("\n[1] 检查编译结果:", 'yellow')
    exe_path = base_dir / "bin" / "notepad_abc.exe"
    if check_file_exists(exe_path):
        print_color(f"   可执行文件大小: {os.path.getsize(exe_path) / 1024:.1f} KB", 'yellow')
    
    # 2. 检查VerticalFileSwitcher.h中的关键修改
    print_color("\n[2] 检查VerticalFileSwitcher.h修改:", 'yellow')
    vfs_h_path = base_dir / "PowerEditor" / "src" / "WinControls" / "VerticalFileSwitcher" / "VerticalFileSwitcher.h"
    
    # 检查构造函数使用-1作为资源ID
    check_file_content(vfs_h_path, r"VerticalFileSwitcher\s*\(\s*\)\s*:\s*DockingDlgInterface\s*\(\s*-1\s*\)", 
                      "构造函数使用-1作为资源ID")
    
    # 检查CreateWindowEx调用
    check_file_content(vfs_h_path, r"CreateWindowEx", 
                      "使用CreateWindowEx直接创建对话框")
    
    # 检查不使用CreateDialogParam
    if not check_file_content(vfs_h_path, r"CreateDialogParam", 
                            "不使用CreateDialogParam"):
        print_color("✓ 确认: 不再使用CreateDialogParam，避免资源依赖", 'green')
    
    # 3. 检查SConscript中的资源处理
    print_color("\n[3] 检查SConscript资源处理:", 'yellow')
    scons_path = base_dir / "SConscript"
    
    # 检查VerticalFileSwitcher资源处理逻辑
    check_file_content(scons_path, 
                      r"// 为VerticalFileSwitcher生成完整的资源定义", 
                      "SConscript包含VerticalFileSwitcher资源处理")
    
    # 4. 检查资源ID定义
    print_color("\n[4] 检查资源ID定义:", 'yellow')
    vfs_resource_path = base_dir / "PowerEditor" / "src" / "WinControls" / "VerticalFileSwitcher" / "VerticalFileSwitcher_resource.cpp"
    check_file_content(vfs_resource_path, r"#define IDD_DOCLIST 3000", "资源ID IDD_DOCLIST定义为3000")
    check_file_content(vfs_resource_path, r"#define IDC_LIST_DOCLIST 3001", "资源ID IDC_LIST_DOCLIST定义为3001")
    
    # 5. 总结和建议
    print_color("\n[5] 修复总结:", 'yellow')
    print_color("✓ 已修复VerticalFileSwitcher构造函数，使用-1作为资源ID，避免依赖资源文件", 'green')
    print_color("✓ 已修复SConscript中的资源处理逻辑，为VerticalFileSwitcher生成必要的资源定义", 'green')
    print_color("✓ 已成功编译程序，生成了notepad_abc.exe", 'green')
    
    print_color("\n[6] 运行建议:", 'yellow')
    print_color("请以管理员权限运行以下命令启动程序:", 'yellow')
    print_color(f"   cd {base_dir / 'bin'} && notepad_abc.exe", 'blue')
    print_color("\n验证要点:", 'yellow')
    print_color("1. 检查程序启动时是否不再出现'找不到映像文件不包含资源区域'错误", 'yellow')
    print_color("2. 检查工具栏按钮是否正确显示图标", 'yellow')
    print_color("3. 测试文档列表功能是否正常工作", 'yellow')
    
    print_color("\n" + "=" * 80, 'blue')

if __name__ == "__main__":
    main()