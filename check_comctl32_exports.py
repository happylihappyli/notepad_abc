#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查COMCTL32.dll中是否包含序数381的函数
"""

import subprocess
import os


def check_comctl32_exports():
    """
    检查COMCTL32.dll的导出函数，特别查找序数381
    """
    print("正在检查COMCTL32.dll的导出函数...")
    
    # 可能的COMCTL32.dll路径
    comctl32_paths = [
        r"C:\Windows\System32\comctl32.dll",
        r"C:\Windows\SysWOW64\comctl32.dll"
    ]
    
    found_valid_dll = False
    
    for dll_path in comctl32_paths:
        if os.path.exists(dll_path):
            found_valid_dll = True
            print(f"\n检查DLL: {dll_path}")
            
            # 获取文件版本信息
            try:
                import win32api
                info = win32api.GetFileVersionInfo(dll_path, '\\')
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                print(f"文件版本: {version}")
            except ImportError:
                print("无法获取文件版本信息(缺少win32api模块)")
            except Exception as e:
                print(f"获取文件版本信息失败: {e}")
            
            # 使用LLVM工具分析导出表
            llvm_objdump = r"C:\Program Files\LLVM\bin\llvm-objdump.exe"
            if not os.path.exists(llvm_objdump):
                print(f"错误: 找不到LLVM工具 {llvm_objdump}")
                return 1
            
            try:
                cmd = [llvm_objdump, "-p", dll_path]
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode != 0:
                    print(f"错误: 执行llvm-objdump失败: {result.stderr}")
                    continue
                
                lines = result.stdout.split('\n')
                found_ordinal = False
                
                print("分析导出表...")
                
                for i, line in enumerate(lines):
                    if "Export Address Table:" in line:
                        # 开始查找导出函数
                        print("\n--- 导出函数列表 (部分) ---")
                        
                        # 查找包含序数381的行
                        for j in range(i+1, min(i+200, len(lines))):
                            line_j = lines[j].strip()
                            if line_j and not line_j.startswith("Name Pointer Table:"):
                                print(f"行 {j+1}: {line_j}")
                                
                                # 检查是否包含序数381
                                if "[381]" in line_j:
                                    print(f"\n✅ 找到序数381在COMCTL32.dll中!")
                                    print(f"   行内容: {line_j}")
                                    found_ordinal = True
                                    
                                    # 检查下一行是否包含函数名
                                    if j + 1 < len(lines):
                                        next_line = lines[j+1].strip()
                                        if "Name:" in next_line:
                                            function_name = next_line.split("Name:")[-1].strip()
                                            print(f"   函数名: {function_name}")
                                    break
                        break
                
                if not found_ordinal:
                    print("\n❌ 在COMCTL32.dll中未找到序数381的函数")
                    
                    # 尝试另一种方法：使用llvm-readobj
                    print("\n尝试使用llvm-readobj分析...")
                    llvm_readobj = r"C:\Program Files\LLVM\bin\llvm-readobj.exe"
                    cmd = [llvm_readobj, "--coff-exports", dll_path]
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                    
                    if result.returncode == 0:
                        output = result.stdout
                        # 查找包含"Ordinal: 381"的行
                        if "Ordinal: 381" in output:
                            print("✅ 找到序数381在COMCTL32.dll中!")
                            
                            # 提取函数名
                            lines_objdump = output.split('\n')
                            for line in lines_objdump:
                                if "Ordinal: 381" in line:
                                    print(f"   行内容: {line.strip()}")
                                    # 查找相关的Name信息
                                    break
                
            except Exception as e:
                print(f"分析失败: {e}")
                import traceback
                traceback.print_exc()
    
    if not found_valid_dll:
        print("错误: 找不到COMCTL32.dll文件")
        return 1
    
    return 0


if __name__ == "__main__":
    check_comctl32_exports()
