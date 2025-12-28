#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试资源编译器命令生成
"""

import os
import sys

# 测试llvm-rc的命令格式
print("测试llvm-rc命令格式...")

# 设置参数
rc_compiler = r"C:\Program Files\LLVM\bin\llvm-rc.exe"
source = r"E:\GitHub3\cpp\notepad_abc\PowerEditor\src\WinControls\VerticalFileSwitcher\VerticalFileSwitcher.rc"
target = r"E:\GitHub3\cpp\notepad_abc\test.res"

# 测试不同的命令格式
commands = [
    f'"{rc_compiler}" "{source}" -o "{target}"',
    f'{rc_compiler} {source} -o {target}',
    f'"{rc_compiler}" "{source}" -o "{target}" --verbose',
    f'"{rc_compiler}" "{source}" /fo "{target}"'
]

print("生成的命令:")
for i, cmd in enumerate(commands):
    print(f"命令 {i+1}: {cmd}")
    
    # 测试命令是否可以执行
    try:
        print(f"执行命令 {i+1}...")
        # 使用subprocess模块来正确处理带空格的路径
        import subprocess
        # 将命令拆分为参数列表
        if '"' in cmd:
            # 如果有引号，使用shlex解析
            import shlex
            args = shlex.split(cmd)
        else:
            # 否则简单拆分
            args = cmd.split()
        print(f"解析后的参数: {args}")
        result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
        print(f"命令 {i+1}执行结果: {result.returncode}")
        if result.stdout:
            print(f"标准输出: {result.stdout}")
        if result.stderr:
            print(f"标准错误: {result.stderr}")
        print("---")
    except Exception as e:
        print(f"执行命令 {i+1}出错: {e}")
        print("---")

# 检查是否生成了.res文件
if os.path.exists(target):
    print(f"✅ 成功生成了资源文件: {target}")
    print(f"文件大小: {os.path.getsize(target)} 字节")
    os.remove(target)  # 清理测试文件
    print("已清理测试文件")
else:
    print(f"❌ 没有生成资源文件: {target}")
