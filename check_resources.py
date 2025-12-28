#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查可执行文件中的资源是否正确包含
"""

import os
import sys

# 检查是否有可用的资源查看工具
def check_resource_viewer():
    """检查是否有可用的资源查看工具"""
    tools = [
        'Resource Hacker',
        'ResEdit',
        'XN Resource Editor'
    ]
    
    for tool in tools:
        try:
            # 尝试在注册表中查找工具
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                try:
                    i = 0
                    while True:
                        subkey = winreg.EnumKey(key, i)
                        if tool.lower() in subkey.lower():
                            print(f"✅ 找到资源查看工具: {tool}")
                            return True
                        i += 1
                except WindowsError:
                    pass
        except ImportError:
            print("❌ 无法导入winreg模块")
        except Exception as e:
            print(f"检查资源查看工具时出错: {e}")
    
    print("❌ 未找到资源查看工具")
    return False

# 检查可执行文件是否存在
def check_executable():
    """检查可执行文件是否存在"""
    exe_path = r"E:\GitHub3\cpp\notepad_abc\bin\notepad_abc.exe"
    if os.path.exists(exe_path):
        print(f"✅ 可执行文件存在: {exe_path}")
        print(f"   文件大小: {os.path.getsize(exe_path):,} 字节")
        return True
    else:
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False

# 检查资源文件是否存在
def check_resource_files():
    """检查资源文件是否存在"""
    resource_files = [
        r"PowerEditor\src\Notepad_plus.res",
        r"PowerEditor\src\ScintillaComponent\FindReplaceDlg.res",
        r"PowerEditor\src\WinControls\DockingWnd\DockingGUIWidget.res",
        r"PowerEditor\src\WinControls\FunctionList\functionListPanel.res",
        r"PowerEditor\src\WinControls\Preference\preference.res",
        r"PowerEditor\src\WinControls\VerticalFileSwitcher\VerticalFileSwitcher.res"
    ]
    
    print("\n检查生成的资源文件:")
    all_found = True
    for res_file in resource_files:
        full_path = os.path.join(r"E:\GitHub3\cpp\notepad_abc", res_file)
        if os.path.exists(full_path):
            print(f"✅ {res_file} - 大小: {os.path.getsize(full_path):,} 字节")
        else:
            print(f"❌ {res_file} - 未找到")
            all_found = False
    
    return all_found

# 主函数
def main():
    """主函数"""
    print("检查Notepad_abc资源文件完整性...")
    print("=" * 50)
    
    # 检查可执行文件
    if not check_executable():
        return False
    
    # 检查资源文件
    if not check_resource_files():
        return False
    
    # 检查资源查看工具
    check_resource_viewer()
    
    print("\n" + "=" * 50)
    print("🎉 资源文件检查完成！")
    print("\n提示:")
    print("1. 所有资源文件已成功生成")
    print("2. 可执行文件已创建")
    print("3. 建议使用Resource Hacker等工具检查可执行文件中的资源")
    print("4. 尝试运行程序并点击 '视图' → '文档列表' 测试功能")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
