#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试IDM_SETTINGS_VFS未运行问题
"""

def analyze_vertical_file_switcher_issue():
    """分析IDM_SETTINGS_VFS没有运行的原因"""
    
    print("=" * 80)
    print("🔍 调试IDM_SETTINGS_VFS (1451行) 未运行问题")
    print("=" * 80)
    
    print("\n📋 问题分析:")
    print("1. 您点击的是设置按钮，还是右键菜单的设置项？")
    print("   • 设置按钮: 触发第710行的WM_COMMAND处理")
    print("   • 右键菜单设置: 触发第1451行的popupMenuCmd处理")
    
    print("\n🎯 两种不同的设置机制:")
    print("\n1️⃣  设置按钮 (WM_COMMAND处理):")
    print("   ├── 文件: VerticalFileSwitcher.cpp")
    print("   ├── 行号: 710行")
    print("   ├── 事件: IDC_SETTINGS_BUTTON_VFS (ID: 3099)")
    print("   ├── 函数: showSettingsDialog()")
    print("   └── 作用: 显示自定义设置对话框")
    
    print("\n2️⃣  右键菜单设置 (popupMenuCmd处理):")
    print("   ├── 文件: VerticalFileSwitcher.cpp")
    print("   ├── 行号: 1451行")
    print("   ├── 事件: IDM_SETTINGS_VFS")
    print("   ├── 函数: SendMessage(_hParent, NPPM_MENUCOMMAND, 0, IDM_SETTING_PREFERENCE)")
    print("   └── 作用: 打开标准Notepad++设置对话框")
    
    print("\n🔧 调试步骤:")
    print("1. 检查您点击的是哪种设置:")
    print("   • 界面顶部的'设置'按钮 → 会执行showSettingsDialog()")
    print("   • 右键菜单的'设置'项 → 会执行1451行代码")
    
    print("\n2. 确认断点设置:")
    print("   • 设置按钮: 在第710行设置断点")
    print("   • 右键菜单: 在第1451行设置断点")
    
    print("\n3. 检查消息循环:")
    print("   • 设置按钮: WM_COMMAND → LOWORD(wParam) == IDC_SETTINGS_BUTTON_VFS")
    print("   • 右键菜单: NM_RCLICK → TrackPopupMenu → WM_COMMAND → popupMenuCmd()")
    
    print("\n⚡ 快速验证方法:")
    print("1. 在第710行设置断点，点击设置按钮")
    print("2. 在第1451行设置断点，右键点击文件列表 → 选择'设置'")
    print("3. 运行程序观察哪个断点会被触发")
    
    print("\n💡 常见问题排查:")
    print("• 断点未触发: 可能是代码没有重新编译")
    print("• 断点触发但跳过1451行: 说明执行了其他代码路径")
    print("• 设置对话框没有打开: 检查showSettingsDialog()函数")
    
    print("\n📍 相关代码位置:")
    print("• 设置按钮处理: VerticalFileSwitcher.cpp:710")
    print("• 右键菜单处理: VerticalFileSwitcher.cpp:1451")  
    print("• showSettingsDialog函数: VerticalFileSwitcher.cpp:1178")
    print("• 菜单绑定代码: VerticalFileSwitcher.cpp:1346, 1378")
    
    print("\n" + "=" * 80)
    print("✅ 请根据上述分析，确认您点击的是哪种设置，然后相应地设置断点")
    print("=" * 80)

if __name__ == "__main__":
    analyze_vertical_file_switcher_issue()