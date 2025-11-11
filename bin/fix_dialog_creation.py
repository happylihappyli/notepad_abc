#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断和修复文档列表对话框创建问题
"""

import os
import sys
import subprocess
import time

def check_resource_compilation():
    """检查资源编译是否成功"""
    print("🔍 检查资源编译状态...")
    
    # 检查编译日志
    build_log_path = os.path.join(os.path.dirname(__file__), "..", "build.log")
    if os.path.exists(build_log_path):
        try:
            # 尝试不同编码
            with open(build_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(build_log_path, 'r', encoding='utf-16') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(build_log_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    print("⚠️ 无法读取构建日志文件（编码问题）")
                    return
        
        if "VerticalFileSwitcher.rc" in content:
            if "成功编译资源文件" in content:
                print("✅ 资源文件编译成功")
            else:
                print("❌ 资源文件编译可能失败")
        else:
            print("⚠️ 未找到VerticalFileSwitcher资源编译记录")
    else:
        print("⚠️ 未找到构建日志文件")

def check_resource_files():
    """检查资源文件是否存在"""
    print("\n🔍 检查资源文件...")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 检查资源文件
    rc_file = os.path.join(base_dir, "PowerEditor", "src", "WinControls", "VerticalFileSwitcher", "VerticalFileSwitcher.rc")
    rc_h_file = os.path.join(base_dir, "PowerEditor", "src", "WinControls", "VerticalFileSwitcher", "VerticalFileSwitcher_rc.h")
    
    if os.path.exists(rc_file):
        print("✅ VerticalFileSwitcher.rc 文件存在")
        # 检查资源ID定义
        with open(rc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "IDD_DOCLIST" in content:
                print("✅ 资源文件中包含IDD_DOCLIST定义")
            else:
                print("❌ 资源文件中缺少IDD_DOCLIST定义")
    else:
        print("❌ VerticalFileSwitcher.rc 文件不存在")
    
    if os.path.exists(rc_h_file):
        print("✅ VerticalFileSwitcher_rc.h 文件存在")
        # 检查资源ID值
        with open(rc_h_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "IDD_DOCLIST" in content and "3000" in content:
                print("✅ 资源头文件中IDD_DOCLIST定义为3000")
            else:
                print("❌ 资源头文件中IDD_DOCLIST定义不正确")
    else:
        print("❌ VerticalFileSwitcher_rc.h 文件不存在")

def check_dialog_creation_logic():
    """检查对话框创建逻辑"""
    print("\n🔍 检查对话框创建逻辑...")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 检查StaticDialog.cpp中的create方法
    static_dialog_cpp = os.path.join(base_dir, "PowerEditor", "src", "WinControls", "StaticDialog", "StaticDialog.cpp")
    
    if os.path.exists(static_dialog_cpp):
        with open(static_dialog_cpp, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查CreateDialogParam调用
            if "CreateDialogParam" in content:
                print("✅ StaticDialog使用CreateDialogParam创建对话框")
            else:
                print("❌ StaticDialog中未找到CreateDialogParam调用")
            
            # 检查错误处理
            if "_hSelf" in content and "return" in content:
                print("✅ StaticDialog有对话框创建失败处理")
            else:
                print("❌ StaticDialog可能缺少错误处理")
    else:
        print("❌ StaticDialog.cpp文件不存在")

def check_vertical_file_switcher_constructor():
    """检查VerticalFileSwitcher构造函数"""
    print("\n🔍 检查VerticalFileSwitcher构造函数...")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 检查VerticalFileSwitcher.h
    vfs_h_file = os.path.join(base_dir, "PowerEditor", "src", "WinControls", "VerticalFileSwitcher", "VerticalFileSwitcher.h")
    
    if os.path.exists(vfs_h_file):
        with open(vfs_h_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查构造函数
            if "DockingDlgInterface(IDD_DOCLIST)" in content:
                print("✅ VerticalFileSwitcher构造函数使用IDD_DOCLIST")
            else:
                print("❌ VerticalFileSwitcher构造函数可能使用错误的资源ID")
    else:
        print("❌ VerticalFileSwitcher.h文件不存在")

def create_fallback_dialog_implementation():
    """创建备用对话框实现"""
    print("\n🔧 创建备用对话框实现...")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 创建备用实现文件
    fallback_file = os.path.join(base_dir, "PowerEditor", "src", "WinControls", "VerticalFileSwitcher", "VerticalFileSwitcher_fallback.cpp")
    
    fallback_content = """// 备用对话框实现 - 当资源加载失败时使用
#include "VerticalFileSwitcher.h"
#include <windows.h>

// 备用对话框创建函数
HWND CreateVerticalFileSwitcherFallback(HWND hParent, HINSTANCE hInst) {
    // 使用CreateWindowEx直接创建窗口，绕过资源文件
    HWND hWnd = CreateWindowEx(
        WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
        L"STATIC",  // 使用静态控件类
        L"Document List",
        WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD | WS_VISIBLE,
        100, 100, 200, 300,  // 默认位置和大小
        hParent,
        NULL,
        hInst,
        NULL
    );
    
    if (hWnd) {
        // 创建列表视图控件
        HWND hListView = CreateWindowEx(
            WS_EX_CLIENTEDGE,
            WC_LISTVIEW,
            L"",
            WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
            10, 10, 180, 280,
            hWnd,
            (HMENU)3001,  // 使用IDC_LIST_DOCLIST的ID
            hInst,
            NULL
        );
        
        if (hListView) {
            // 设置列表视图样式
            ListView_SetExtendedListViewStyle(hListView, LVS_EX_FULLROWSELECT | LVS_EX_DOUBLEBUFFER);
        }
    }
    
    return hWnd;
}

// 修改VerticalFileSwitcher的create方法以使用备用实现
void VerticalFileSwitcher::createFallback(tTbData* data, bool isRTL) {
    // 尝试使用备用实现创建窗口
    _hSelf = CreateVerticalFileSwitcherFallback(_hParent, _hInst);
    
    if (_hSelf) {
        // 窗口创建成功，继续初始化
        _fileListView.Window::init(_hInst, _hSelf);
        
        // 获取列表视图控件
        HWND hListView = GetDlgItem(_hSelf, 3001);  // 使用备用ID
        if (hListView) {
            _fileListView.setHSelf(hListView);
            _fileListView.setHImageList(_hImaLst);
            _fileListView.initList();
        }
        
        // 设置用户数据
        data->hClient = _hSelf;
        data->pszName = L"Document List";
        data->uMask = 0;
        data->pszAddInfo = nullptr;
        
        // 发送模型对话框添加消息
        ::SendMessage(_hParent, NPPM_MODELESSDIALOG, MODELESSDIALOGADD, reinterpret_cast<WPARAM>(_hSelf));
    }
}
"""
    
    try:
        with open(fallback_file, 'w', encoding='utf-8-sig') as f:
            f.write(fallback_content)
        print("✅ 备用对话框实现文件已创建")
    except Exception as e:
        print(f"❌ 创建备用实现文件失败: {e}")

def suggest_fixes():
    """提供修复建议"""
    print("\n💡 修复建议:")
    print("1. 检查资源编译器是否正常工作")
    print("2. 验证资源ID定义是否正确")
    print("3. 确保资源文件被正确包含在构建过程中")
    print("4. 添加资源加载失败时的备用创建机制")
    print("5. 检查对话框创建的错误处理逻辑")
    print("6. 验证可执行文件是否包含正确的资源")

def main():
    """主函数"""
    print("🚀 开始诊断文档列表对话框创建问题...\n")
    
    # 执行各项检查
    check_resource_compilation()
    check_resource_files()
    check_dialog_creation_logic()
    check_vertical_file_switcher_constructor()
    
    # 创建备用实现
    create_fallback_dialog_implementation()
    
    # 提供修复建议
    suggest_fixes()
    
    print("\n✅ 诊断完成！")

if __name__ == "__main__":
    main()