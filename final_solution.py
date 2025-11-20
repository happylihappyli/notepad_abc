#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终解决方案：修复notepad_abc只创建控制台窗口的问题
"""

import os
import sys
import time
import subprocess
import psutil
from ctypes import windll, byref, c_void_p, c_int
from ctypes.wintypes import DWORD, HWND, LPARAM, BOOL
import json
import win32api
import win32con
import win32gui
import win32process

def fix_utf8_environment():
    """设置UTF-8编码环境"""
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul')
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def get_dependency_status(executable_path):
    """检查依赖文件状态"""
    print("=== 依赖文件检查 ===")
    
    deps_to_check = [
        "comctl32.dll", "shlwapi.dll", "shell32.dll", "version.dll",
        "crypt32.dll", "wintrust.dll", "wininet.dll", "imm32.dll",
        "uxtheme.dll", "dwmapi.dll", "comdlg32.dll", "gdi32.dll",
        "user32.dll", "kernel32.dll", "ole32.dll", "oleaut32.dll",
        "advapi32.dll", "msvcrt.dll", "vcruntime140.dll",
        "ucrtbase.dll", "api-ms-win-crt-runtime-l1-1-0.dll"
    ]
    
    deps_status = {}
    system32_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
    
    for dep in deps_to_check:
        dep_path = os.path.join(system32_path, dep)
        exists = os.path.exists(dep_path)
        deps_status[dep] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {dep}")
    
    return deps_status

def check_missing_dependencies():
    """检查缺失的系统依赖"""
    print("\n=== 系统依赖检查 ===")
    
    # 检查Visual C++运行库
    vcredist_keys = [
        r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
    ]
    
    vcredist_found = False
    for key_path in vcredist_keys:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            vcredist_found = True
            winreg.CloseKey(key)
            print("✅ Visual C++ Redistributable 已安装")
            break
        except FileNotFoundError:
            continue
    
    if not vcredist_found:
        print("❌ Visual C++ Redistributable 可能缺失")
    
    return vcredist_found

def create_corrected_config():
    """创建修正的配置文件"""
    print("\n=== 创建修正的配置 ===")
    
    config_files = {
        "config.xml": """<?xml version="1.0" encoding="Windows-1252"?>
<NotepadPlus>
    <GUIConfig name="stylerTheme">default_black.xml</GUIConfig>
    <GUIConfig name="appPos" x="100" y="100" width="1200" height="800" isMaximized="false"/>
    <GUIConfig name="styleConfig">stylers.xml</GUIConfig>
    <GUIConfig name="langsConfig">langs.xml</GUIConfig>
    <GUIConfig name="list" line="200" width="600"/>
    <GUIConfig name="findWindowPos" width="540" height="370"/>
    <GUIConfig name="replaceWindowPos" width="540" height="420"/>
    <GUIConfig name="columnEdit" />
    <GUIConfig name="autoIndent" />
    <GUIConfig name="SmartHighLight" />
    <GUIConfig name="SmartHighLightConfig" />
    <GUIConfig name="TagsMatchHps" />
    <GUIConfig name="TagsMatchHpsConfig" />
    <GUIConfig name="WordCharList" />
    <GUIConfig name="Print" lineNumber="false" color="#000000" bkColor="#FFFFFF"/>
    <GUIConfig name="ScintillaPrimaryView" linenumber="true" viewWS="false" viewEOL="false" viewIndentGuide="true" viewBookmark="true" viewSyntax="true" viewTooltip="true" wrap="false" wrapSymbol="true" focus="true" currentLineHiliting="true" styleSelect="true" indentGuideLine="true" braceHiliting="true" braceStyle="straight"/>
    <GUIConfig name="TaskPos" x="10" y="10" width="400" height="300"/>
    <GUIConfig name="Plugin" id="0"/>
    <GUIConfig name="FileBrowser" path=""/>
    <GUIConfig name="Session" file=""/>
    <GUIConfig name="LaunchHistory" size="8"/>
    <GUIConfig name="docSwitcher" />
    <GUIConfig name="Workspace" />
    <GUIConfig name="ProjectPanel" />
    <GUIConfig name="FunctionList" />
    <GUIConfig name="DocumentMap" />
    <GUIConfig name="ClipboardHistory" />
    <GUIConfig name="Backup" isSnapshot="false" backupDir="" />
    <GUIConfig name="WebServer1" path="" port="8000" />
    <GUIConfig name="WebServer2" path="" port="8080" />
    <GUIConfig name="WebServer3" path="" port="8181" />
    <GUIConfig name="Cloud" link="" />
    <GUIConfig name="SearchEngine" name="" />
    <GUIConfig name="TxWChLogCtrlPos" />
    <GUIConfig name="UserDefineLang" />
    <GUIConfig name="udlGlobalXmlFilesPath" />
    <GUIConfig name="printAndSave" print="false" save="false"/>
    <GUIConfig name="saveAllOpen" />
    <GUIConfig name="saveLog" />
    <GUIConfig name="sessionExt" />
    <GUIConfig name="fileSaveReDirectory" />
    <GUIConfig name="fileSaveReExt" />
    <GUIConfig name="fileSaveReFilter" />
    <GUIConfig name="AppImage" />
    <GUIConfig name="ToolBar" />
    <GUIConfig name="TabSetting" space="false" size="4"/>
    <GUIConfig name="Caret" width="1" blinkRate="500"/>
    <GUIConfig name="MISC" autoHCPos="false" autoCP="false" newDocDefaultSetting="false" />
    <GUIConfig name="MISC" openSaveDir="false" />
    <GUIConfig name="MISC" detectEncoding="true" />
    <GUIConfig name="MISC" autoSave="false" />
    <GUIConfig name="MISC" styleMRU="true" />
    <GUIConfig name="MISC" rememberLastSession="false" />
    <GUIConfig name="MISC" mainGUIStatus="false" />
    <GUIConfig name="MISC" check4Update="false" />
    <GUIConfig name="MISC" enableNotepad2Function="false" />
    <GUIConfig name="MISC" enablePluginFunction="false" />
    <GUIConfig name="MISC" enableCloseAllFunction="false" />
    <GUIConfig name="MISC" enableMultiInstance="false" />
    <GUIConfig name="MISC" enableTabsPosition="false" />
    <GUIConfig name="MISC" enableTabSwitcher="false" />
    <GUIConfig name="MISC" tabPosition="0" />
    <GUIConfig name="MISC" enableTabAtRight="false" />
    <GUIConfig name="MISC" themeSwitcher="false" />
    <GUIConfig name="MISC" hideMenuBar="false" />
    <GUIConfig name="MISC" hideToolBar="false" />
    <GUIConfig name="statusBar="false" />
    <GUIConfig name="MRU" />
    <GUIConfig name="FileOpenDialog" />
    <GUIConfig name="FileSaveDialog" />
    <GUIConfig name="FindHistory" />
    <GUIConfig name="ReplaceHistory" />
    <GUIConfig name="FindHistory" />
    <GUIConfig name="History" />
    <GUIConfig name="ShortcutMapper" />
    <GUIConfig name="UserKeywords" />
    <GUIConfig name="UserDefinedLangExt" />
    <GUIConfig name="macros" />
    <GUIConfig name="ScintillaGlobalSettings" />
    <GUIConfig name="File association" />
</NotepadPlus>""",
        
        "contextMenu.xml": """<?xml version="1.0" encoding="Windows-1252" ?>
<NotepadPlus>
    <ScintillaContextMenu>
        <Item id="1"/>
        <Item id="2"/>
        <Item id="3"/>
        <Item sep="yes"/>
        <Item id="40001"/>
        <Item id="40002"/>
        <Item id="40003"/>
        <Item sep="yes"/>
        <Item id="40004"/>
        <Item id="40005"/>
        <Item sep="yes"/>
        <Item id="40006"/>
        <Item id="40007"/>
        <Item sep="yes"/>
        <Item id="40008"/>
        <Item id="40009"/>
        <Item sep="yes"/>
        <Item id="41001"/>
        <Item id="41002"/>
        <Item id="41003"/>
        <Item sep="yes"/>
        <Item id="42001"/>
        <Item id="42002"/>
        <Item id="42003"/>
        <Item sep="yes"/>
        <Item id="43001"/>
        <Item id="43002"/>
        <Item id="43003"/>
        <Item id="43004"/>
        <Item id="43005"/>
    </ScintillaContextMenu>
</NotepadPlus>""",
        
        "doLocalConf.xml": """<?xml version="1.0" encoding="Windows-1252"?>
<NotepadPlus>
    <GUIConfig name="localization">None</GUIConfig>
</NotepadPlus>"""
    }
    
    for filename, content in config_files.items():
        file_path = os.path.join(os.getcwd(), filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 创建/更新: {filename}")

def test_gui_startup():
    """测试GUI启动"""
    print("\n=== GUI启动测试 ===")
    
    exe_path = os.path.join(os.getcwd(), "bin", "notepad_abc_new.exe")
    
    if not os.path.exists(exe_path):
        print(f"❌ 可执行文件不存在: {exe_path}")
        return False
    
    # 测试不同的启动方式
    startup_modes = [
        ("默认启动", [exe_path]),
        ("带参数", [exe_path, "-multiInst"]),
        ("静默启动", [exe_path, "-noPlugin"]),
    ]
    
    for mode_name, cmd in startup_modes:
        print(f"\n--- {mode_name} ---")
        try:
            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            print(f"✅ 进程启动成功，PID: {process.pid}")
            
            # 等待窗口创建
            time.sleep(3)
            
            # 查找窗口
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if "notepad" in window_title.lower() or "abc" in window_title.lower():
                        class_name = win32gui.GetClassName(hwnd)
                        windows.append((hwnd, window_title, class_name))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            gui_windows = [w for w in windows if not any(term in w[2] for term in ['Console', 'IME', 'MSCTF'])]
            
            if gui_windows:
                print(f"✅ 找到GUI窗口:")
                for hwnd, title, class_name in gui_windows:
                    print(f"   窗口: {title}")
                    print(f"   类名: {class_name}")
                    print(f"   句柄: {hwnd}")
                result = True
            else:
                print("❌ 未找到GUI窗口，只找到控制台窗口")
                result = False
            
            # 终止进程
            try:
                os.system(f"taskkill /PID {process.pid} /F > nul")
            except:
                pass
                
            return result
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    return False

def create_minimal_gui_test():
    """创建最小GUI测试程序"""
    print("\n=== 创建最小GUI测试程序 ===")
    
    test_cpp = '''#include <windows.h>
#include <iostream>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    MessageBox(NULL, "GUI测试程序", "Notepad++ ABC", MB_OK);
    
    // 创建主窗口
    HWND hwnd = CreateWindowEx(
        0,
        "STATIC",
        "Notepad++ ABC 主窗口",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT,
        800, 600,
        NULL, NULL, hInstance, NULL
    );
    
    if (hwnd == NULL) {
        MessageBox(NULL, "窗口创建失败", "错误", MB_OK);
        return -1;
    }
    
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);
    
    // 消息循环
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    return (int)msg.wParam;
}
'''
    
    test_cpp_path = "gui_test.cpp"
    with open(test_cpp_path, 'w', encoding='utf-8') as f:
        f.write(test_cpp)
    
    print(f"✅ 创建测试程序: {test_cpp_path}")
    
    # 尝试编译测试程序
    compile_cmd = f'cl /Fe:gui_test.exe /SUBSYSTEM:WINDOWS "{test_cpp_path}" user32.lib kernel32.lib gdi32.lib'
    print(f"编译命令: {compile_cmd}")
    
    return test_cpp_path

def main():
    """主函数"""
    print("============================================================")
    print("Notepad++ ABC 最终解决方案")
    print("============================================================")
    
    fix_utf8_environment()
    
    # 检查依赖
    executable_path = os.path.join(os.getcwd(), "bin", "notepad_abc_new.exe")
    deps_status = get_dependency_status(executable_path)
    vcredist_status = check_missing_dependencies()
    
    # 创建修正配置
    create_corrected_config()
    
    # 测试GUI启动
    gui_success = test_gui_startup()
    
    if gui_success:
        print("\n✅ 问题已解决！GUI窗口正常显示")
    else:
        print("\n❌ GUI窗口仍无法创建，创建最小测试程序...")
        create_minimal_gui_test()
    
    print("\n============================================================")
    print("诊断结论:")
    print("============================================================")
    print("基于测试结果，可能的原因包括:")
    print("1. GUI初始化代码中的未处理异常")
    print("2. 缺少必需的Windows API依赖")
    print("3. 窗口类注册失败")
    print("4. 主题或样式加载问题")
    print("5. 插件加载时的冲突")
    print("\n建议解决方案:")
    print("1. 检查Windows事件日志")
    print("2. 使用调试器分析GUI初始化过程")
    print("3. 临时禁用所有插件")
    print("4. 检查主题文件完整性")
    print("5. 验证所有DLL依赖文件")

if __name__ == "__main__":
    main()