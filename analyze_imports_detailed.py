#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用llvm-readobj工具详细分析EXE文件的导入表，找出缺少的序数函数
"""

import subprocess
import os
import sys


def analyze_exe_imports_detailed(exe_path):
    """
    使用llvm-readobj详细分析EXE文件的导入表
    
    Args:
        exe_path (str): EXE文件路径
    """
    print(f"正在详细分析EXE文件: {exe_path}")
    
    # 检查EXE文件是否存在
    if not os.path.exists(exe_path):
        print(f"错误: 找不到文件 {exe_path}")
        return 1
    
    # 使用LLVM工具
    llvm_readobj = r"C:\Program Files\LLVM\bin\llvm-readobj.exe"
    if not os.path.exists(llvm_readobj):
        print(f"错误: 找不到LLVM工具 {llvm_readobj}")
        return 1
    
    try:
        # 执行llvm-readobj命令查看详细的导入表
        cmd = [llvm_readobj, "--coff-imports", exe_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"错误: 执行llvm-readobj失败: {result.stderr}")
            return 1
        
        print("使用llvm-readobj分析详细导入表...")
        
        output = result.stdout
        print("\n=== 详细导入表分析结果 ===")
        
        # 查找包含"Import"的部分
        import_blocks = []
        current_block = ""
        
        lines = output.split('\n')
        in_import_block = False
        
        for line in lines:
            if "Import {" in line:
                in_import_block = True
                current_block = line + '\n'
            elif in_import_block:
                current_block += line + '\n'
                if "}" in line:
                    import_blocks.append(current_block)
                    in_import_block = False
                    current_block = ""
        
        print(f"找到 {len(import_blocks)} 个导入块")
        
        found_ordinal_381 = False
        
        for i, block in enumerate(import_blocks):
            # 查找DLL名称
            dll_name = ""
            for line in block.split('\n'):
                if "Name: " in line and ".dll" in line:
                    dll_name = line.split("Name: ")[-1].strip()
                    break
            
            if dll_name:
                print(f"\n--- 导入块 {i+1} (DLL: {dll_name}) ---")
                
                # 查找序数信息
                lines_in_block = block.split('\n')
                for line in lines_in_block:
                    if "Ordinal: " in line:
                        # 提取序数
                        ordinal_part = line.split("Ordinal: ")[-1].strip()
                        try:
                            ordinal = int(ordinal_part)
                            print(f"   序数导入: {ordinal}")
                            
                            # 检查是否是我们要找的序数381
                            if ordinal == 381:
                                print(f"\n✅ 找到问题! EXE文件尝试从 {dll_name} 导入序数 {ordinal} 的函数")
                                found_ordinal_381 = True
                                
                                # 显示整个导入块以获取更多信息
                                print("\n导入块详细信息:")
                                print(block)
                                return 0
                        except ValueError:
                            print(f"   序数信息: {ordinal_part}")
        
        if not found_ordinal_381:
            print("\n❌ 未找到导入序数381的函数")
            print("\n=== 可能的解决方案 ===")
            print("1. 检查是否链接了错误版本的库")
            print("2. 检查是否使用了不兼容的Windows API函数")
            print("3. 尝试重新编译项目，确保使用正确的SDK版本")
            
            # 显示所有USER32.dll的导入信息
            print("\n=== USER32.dll 导入信息 ===")
            for i, block in enumerate(import_blocks):
                if "USER32.dll" in block:
                    print(f"\n--- USER32.dll 导入块 {i+1} ---")
                    print(block)
        
        return 1
        
    except Exception as e:
        print(f"错误: 分析过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python analyze_imports_detailed.py <EXE路径>")
        print("示例: python analyze_imports_detailed.py bin\\notepad_abc.exe")
        sys.exit(1)
    
    exe_path = sys.argv[1]
    sys.exit(analyze_exe_imports_detailed(exe_path))
