#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析EXE文件的导入表，找出缺少的序数函数
"""

import subprocess
import os
import sys


def analyze_exe_imports(exe_path):
    """
    分析EXE文件的导入表
    
    Args:
        exe_path (str): EXE文件路径
    """
    print(f"正在分析EXE文件: {exe_path}")
    
    # 检查EXE文件是否存在
    if not os.path.exists(exe_path):
        print(f"错误: 找不到文件 {exe_path}")
        return 1
    
    # 使用LLVM工具
    llvm_objdump = r"C:\Program Files\LLVM\bin\llvm-objdump.exe"
    if not os.path.exists(llvm_objdump):
        print(f"错误: 找不到LLVM工具 {llvm_objdump}")
        return 1
    
    try:
        # 执行llvm-objdump命令查看导入表
        cmd = [llvm_objdump, "-p", exe_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"错误: 执行llvm-objdump失败: {result.stderr}")
            return 1
        
        print("使用LLVM工具分析导入表...")
        
        lines = result.stdout.split('\n')
        current_dll = ""
        
        print("\n=== 导入表分析 ===")
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 查找DLL名称
            if "DLL Name:" in line:
                current_dll = line.split("DLL Name:")[-1].strip()
                print(f"\n--- DLL: {current_dll} ---")
            
            # 查找包含序数的导入函数
            if current_dll and "Ordinal:" in line:
                # 提取序数
                if "Ordinal: " in line:
                    ordinal_part = line.split("Ordinal: ")[-1]
                    # 查找数字部分
                    import sys
                    if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
                        from re import findall
                        ordinals = findall(r'\d+', ordinal_part)
                        if ordinals:
                            ordinal = int(ordinals[0])
                            print(f"   序数导入: {ordinal}")
                            
                            # 检查是否是我们要找的序数381
                            if ordinal == 381:
                                print(f"\n✅ 找到问题! EXE文件尝试从 {current_dll} 导入序数 {ordinal} 的函数")
                                return 0
        
        print("\n❌ 未找到导入序数381的函数")
        print("\n=== 可能的原因 ===")
        print("1. 导入表中可能没有直接列出序数")
        print("2. 可能需要使用其他工具分析")
        
        # 尝试使用另一种方法：查找所有"[Ordinal]"的引用
        print("\n=== 尝试查找所有序数引用 ===")
        for i, line in enumerate(lines):
            if "[Ordinal]" in line:
                print(f"行 {i+1}: {line.strip()}")
                # 检查是否包含381
                if "381" in line:
                    print(f"\n✅ 找到序数381的引用: {line.strip()}")
                    return 0
        
        return 1
        
    except Exception as e:
        print(f"错误: 分析过程中发生异常: {str(e)}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python analyze_imports.py <EXE路径>")
        print("示例: python analyze_imports.py bin\\notepad_abc.exe")
        sys.exit(1)
    
    exe_path = sys.argv[1]
    sys.exit(analyze_exe_imports(exe_path))
