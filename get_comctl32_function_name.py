#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取COMCTL32.dll中指定序数的函数名称
"""

import subprocess
import os


def get_comctl32_function_name(ordinal=381):
    """
    获取COMCTL32.dll中指定序数的函数名称
    
    Args:
        ordinal (int): 要查找的函数序数
    """
    print(f"正在获取COMCTL32.dll中序数 {ordinal} 的函数名称...")
    
    # COMCTL32.dll路径
    comctl32_path = r"C:\Windows\System32\comctl32.dll"
    
    if not os.path.exists(comctl32_path):
        print(f"错误: 找不到文件 {comctl32_path}")
        return None
    
    # 使用LLVM工具
    llvm_readobj = r"C:\Program Files\LLVM\bin\llvm-readobj.exe"
    if not os.path.exists(llvm_readobj):
        print(f"错误: 找不到LLVM工具 {llvm_readobj}")
        return None
    
    try:
        # 执行llvm-readobj命令查看详细的导出表
        cmd = [llvm_readobj, "--coff-exports", comctl32_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"错误: 执行llvm-readobj失败: {result.stderr}")
            return None
        
        output = result.stdout
        print("查看完整导出表...")
        
        # 输出完整的导出表（前200行）
        lines = output.split('\n')
        print("\n=== 完整导出表前200行 ===")
        for i, line in enumerate(lines[:200]):
            print(f"行 {i+1}: {line}")
        
        # 查找包含指定序数的函数
        print(f"\n=== 查找序数 {ordinal} ===")
        
        for i, line in enumerate(lines):
            # 查找包含序数的行
            if f"Ordinal: {ordinal}" in line:
                print(f"找到序数 {ordinal} 在第 {i+1} 行")
                
                # 显示周围的行以获取更多上下文
                start = max(0, i-5)
                end = min(len(lines), i+15)
                print(f"\n上下文（行 {start+1}-{end}）:")
                for j in range(start, end):
                    print(f"行 {j+1}: {lines[j]}")
                
                # 尝试提取函数名
                # 查找下一个以"Name: "开头的行
                for j in range(i+1, end):
                    if lines[j].strip().startswith("Name: "):
                        function_name = lines[j].split("Name: ")[-1].strip()
                        print(f"\n函数名: '{function_name}'")
                        
                        if function_name:
                            return function_name
                        else:
                            print("警告: 函数名为空")
                            return None
                break
        
        print(f"❌ 未找到序数 {ordinal} 对应的函数")
        return None
        
    except Exception as e:
        print(f"错误: 分析过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    function_name = get_comctl32_function_name(381)
    if function_name:
        print(f"\n结果: COMCTL32.dll中序数381对应的函数是 {function_name}")
    else:
        print("\n结果: 未能获取函数名称")
