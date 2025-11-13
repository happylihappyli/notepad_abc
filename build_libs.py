# -*- coding: utf-8 -*-
"""
构建Scintilla和Lexilla库的独立脚本
"""

import os
import sys
import subprocess
from datetime import datetime

def run_scons_build():
    """运行SCons构建库"""
    print("开始构建Scintilla和Lexilla库...")
    
    # 设置UTF-8编码
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul')
    
    # 显示开始时间
    print("开始构建时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 运行SCons构建
    try:
        # 使用SCons构建库
        result = subprocess.run(['scons', 'libs'], 
                               capture_output=True, 
                               text=True, 
                               encoding='utf-8')
        
        if result.returncode == 0:
            print("✓ 库构建成功")
            print("构建输出:", result.stdout)
        else:
            print("✗ 库构建失败")
            print("错误输出:", result.stderr)
            print("标准输出:", result.stdout)
            return False
            
    except Exception as e:
        print(f"✗ 构建过程中出错: {e}")
        return False
    
    # 显示结束时间
    print("库构建完成时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return True

def check_libraries():
    """检查库文件是否存在"""
    bin_dir = os.path.join(os.path.abspath('.'), 'bin')
    
    scintilla_lib = os.path.join(bin_dir, 'libscintilla.lib')
    lexilla_lib = os.path.join(bin_dir, 'liblexilla.lib')
    
    if os.path.exists(scintilla_lib) and os.path.exists(lexilla_lib):
        print("✓ Scintilla和Lexilla库文件已存在")
        return True
    else:
        print("✗ 库文件不存在，需要重新构建")
        return False

def main():
    """主函数"""
    print("=== 检查并构建依赖库 ===")
    
    # 首先检查库是否已存在
    if check_libraries():
        print("库文件已存在，无需重新构建")
        return True
    
    # 如果库不存在，则构建
    print("开始构建依赖库...")
    return run_scons_build()

if __name__ == "__main__":
    success = main()
    if success:
        print("✓ 库构建/检查完成")
    else:
        print("✗ 库构建失败")
        sys.exit(1)