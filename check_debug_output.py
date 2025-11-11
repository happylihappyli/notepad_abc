#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查调试输出脚本
用于捕获OutputDebugString输出的调试信息
"""

import subprocess
import time
import sys

def main():
    print("开始检查调试输出...")
    print("注意：这个脚本需要配合DebugView工具使用，或者使用其他调试输出捕获工具")
    print("您可以使用以下方法查看调试输出：")
    print("1. 下载并运行Sysinternals的DebugView工具")
    print("2. 或者使用Visual Studio的Output窗口")
    print("3. 或者使用其他调试输出捕获工具")
    print("")
    print("程序正在运行，请检查文件列表功能是否正常工作")
    print("如果文件列表仍然为空，可能需要进一步调试")
    
    # 等待用户输入
    input("按Enter键退出...")

if __name__ == "__main__":
    main()