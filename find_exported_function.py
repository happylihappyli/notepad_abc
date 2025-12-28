#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找DLL中指定序数的导出函数
使用Python替代PowerShell脚本，更可靠且用户更倾向于使用Python
"""

import subprocess
import os
import sys


def main(dll_path, ordinal):
    """
    查找DLL中指定序数的导出函数
    
    Args:
        dll_path (str): DLL文件路径
        ordinal (int): 要查找的函数序数
    """
    print(f"正在分析DLL: {dll_path}")
    print(f"查找序数: {ordinal}")
    
    # 检查DLL文件是否存在
    if not os.path.exists(dll_path):
        print(f"错误: 找不到文件 {dll_path}")
        return 1
    
    # 使用LLVM工具（如果可用）
    llvm_objdump = r"C:\Program Files\LLVM\bin\llvm-objdump.exe"
    if not os.path.exists(llvm_objdump):
        print(f"错误: 找不到LLVM工具 {llvm_objdump}")
        return 1
    
    try:
        # 执行llvm-objdump命令并捕获输出
        cmd = [llvm_objdump, "-p", dll_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"错误: 执行llvm-objdump失败: {result.stderr}")
            return 1
        
        print("使用LLVM工具分析...")
        
        # 查找指定序数的函数
        found = False
        lines = result.stdout.split('\n')
        
        print("\n=== 详细导出表分析 ===")
        
        # 查找所有Export相关部分
        in_export_address_table = False
        in_name_pointer_table = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if "Export Address Table:" in line:
                in_export_address_table = True
                in_name_pointer_table = False
                print(f"\n--- 导出地址表 (行 {i+1}) ---")
                continue
            elif "Name Pointer Table:" in line:
                in_name_pointer_table = True
                in_export_address_table = False
                print(f"\n--- 名称指针表 (行 {i+1}) ---")
                continue
            elif "Import Address Table:" in line:
                in_export_address_table = False
                in_name_pointer_table = False
                break
            
            if in_export_address_table and line:
                print(f"行 {i+1}: {line}")
                # 查找序数
                if f"[{ordinal}]" in line:
                    print(f"\n✅ 找到序数 {ordinal} 在导出地址表中")
                    print(f"   行内容: {line}")
                    found = True
                    
                    # 检查是否有相关的函数名信息
                    # 查找Name Pointer Table中的对应条目
                    if in_name_pointer_table:
                        continue
        
        if not found:
            print(f"\n❌ 未找到序数 {ordinal} 对应的函数")
            
            # 尝试另一种方法：使用dumpbin的替代方案
            print("\n=== 尝试使用dumpbin风格的解析 ===")
            
            # 查找包含"[Ordinal/Name Pointer] Table"的行
            ordinal_table_start = -1
            for i, line in enumerate(lines):
                if "[Ordinal/Name Pointer] Table" in line:
                    ordinal_table_start = i
                    break
            
            if ordinal_table_start != -1:
                print(f"找到序数表开始位置: 行 {ordinal_table_start+1}")
                
                # 查看序数表的内容
                for i in range(ordinal_table_start + 1, min(ordinal_table_start + 100, len(lines))):
                    line = lines[i].strip()
                    if not line:
                        continue
                    print(f"行 {i+1}: {line}")
                    if f"[{ordinal}]" in line:
                        print(f"\n✅ 找到序数 {ordinal}")
                        found = True
                        break
        
        if not found:
            print(f"\n❌ 仍然未找到序数 {ordinal} 对应的函数")
            print("\n=== 可能的原因 ===")
            print("1. USER32.dll中确实没有这个序数的函数")
            print("2. 可能是其他DLL中的序数错误")
            print("3. 可能是编译时链接了错误的库版本")
                    
    except Exception as e:
        print(f"错误: 分析过程中发生异常: {str(e)}")
        return 1
    
    print("分析完成")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python find_exported_function.py <DLL路径> <序数>")
        print("示例: python find_exported_function.py C:\\Windows\\System32\\user32.dll 381")
        sys.exit(1)
    
    dll_path = sys.argv[1]
    ordinal = int(sys.argv[2])
    
    sys.exit(main(dll_path, ordinal))
