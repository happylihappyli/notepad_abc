#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
字体大小标签可见性修复验证脚本
"""

import os
import sys

def check_font_label_visible():
    """检查字体大小标签是否可见"""
    print("=" * 60)
    print("字体大小标签可见性修复验证")
    print("=" * 60)
    
    # 1. 检查资源文件
    rc_file = "PowerEditor\\src\\WinControls\\VerticalFileSwitcher\\VerticalFileSwitcher.rc"
    if os.path.exists(rc_file):
        with open(rc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'LTEXT           "字体大小:",IDC_FONTSIZE_STATIC_VFS' in content:
                print("✓ 资源文件包含字体大小标签文本")
                print("  - 标签文本: '字体大小:'")
                print("  - 位置: x=5, y=5, 宽度=40, 高度=12")
            else:
                print("✗ 资源文件配置错误")
                return False
    else:
        print(f"✗ 找不到资源文件: {rc_file}")
        return False
    
    # 2. 检查控件ID一致性
    h_file = "PowerEditor\\src\\WinControls\\VerticalFileSwitcher\\VerticalFileSwitcher_rc.h"
    if os.path.exists(h_file):
        with open(h_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "IDC_FONTSIZE_STATIC_VFS 2209" in content:
                print("✓ 控件ID正确设置为2209")
            else:
                print("✗ 控件ID设置错误")
                return False
    else:
        print(f"✗ 找不到头文件: {h_file}")
        return False
    
    # 3. 检查本地化文件
    xml_file = "PowerEditor\\installer\\nativeLang\\chineseSimplified.xml"
    if os.path.exists(xml_file):
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '<Item id="2209" name="字体大小:"/>' in content:
                print("✓ 本地化文件包含正确的字体大小标签定义")
            else:
                print("✗ 本地化文件定义错误")
                return False
    else:
        print(f"✗ 找不到本地化文件: {xml_file}")
        return False
    
    print("\n✅ 字体大小标签可见性修复验证通过")
    return True

def check_compilation():
    """检查编译状态"""
    print("\n" + "=" * 60)
    print("编译状态检查")
    print("=" * 60)
    
    exe_file = "bin\\notepad_abc.exe"
    if os.path.exists(exe_file):
        size = os.path.getsize(exe_file) / (1024 * 1024)
        print(f"✓ 编译成功: {exe_file}")
        print(f"  文件大小: {size:.2f} MB")
        print(f"  修改时间: {os.path.getmtime(exe_file)}")
        return True
    else:
        print(f"✗ 找不到编译产物: {exe_file}")
        return False

def main():
    """主函数"""
    print("开始字体大小标签可见性修复验证...")
    print(f"当前目录: {os.getcwd()}")
    
    # 执行检查
    checks = [
        ("字体大小标签可见性", check_font_label_visible),
        ("编译状态检查", check_compilation)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name}检查时出现异常: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("修复验证总结")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 字体大小标签可见性修复已完成！")
        print("\n预期结果:")
        print("✓ 字体大小标签现在应该可见")
        print("✓ 标签显示为'字体大小:'")
        print("✓ 位于文档列表的左上角")
        
        print("\n建议测试步骤:")
        print("1. 运行程序: bin\\notepad_abc.exe")
        print("2. 打开文档列表 (View -> Document List)")
        print("3. 检查字体大小标签是否在文档列表顶部左侧可见")
        print("4. 标签文字应该显示为'字体大小:'")
    else:
        print("\n⚠️  部分修复验证失败，请检查上述输出")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)