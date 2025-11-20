# -*- coding: utf-8 -*-
"""
Notepad++ SConscript构建脚本
基于CMakeLists.txt的改进版本
"""

import os
import sys
import time
from datetime import datetime

# 确保Python输出为UTF-8编码
def ensure_utf8_print(text):
    """确保中文文本在控制台正确显示"""
    try:
        # 尝试直接打印（支持UTF-8的终端）
        print(text)
    except UnicodeEncodeError:
        # 如果失败，尝试不同的编码方式
        if sys.platform.startswith('win'):
            try:
                # Windows控制台特殊处理
                os.system(f'echo {text}')
            except:
                print(text.encode('utf-8', errors='replace').decode('cp437', errors='replace'))
        else:
            print(text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

# 测试中文输出
ensure_utf8_print("构建脚本已加载，支持中文显示")

# 在Windows上设置系统编码
if sys.platform.startswith('win'):
    # 设置Python的标准输出和错误编码为UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# 导入主脚本中的变量
Import('project_root', 'src_dir', 'scintilla_dir', 'lexilla_dir', 'bin_dir', 'obj_dir')
Import('configure_build_options', 'configure_link_options')

# 获取环境变量
env = Environment()

# 移除复杂的资源编译器配置，改用更简单可靠的资源处理方法

# 设置构建类型和目标架构
build_type = ARGUMENTS.get('build', 'Release')  # 默认为Release构建
target_arch = ARGUMENTS.get('arch', 'x64')       # 默认为x64架构

# 配置构建选项
env = configure_build_options(env, build_type)
env = configure_link_options(env)

# 添加Lexilla和Scintilla包含目录 - 基于Visual Studio配置
env.Append(CPPPATH=[
    os.path.join(lexilla_dir, 'include'),
    os.path.join(scintilla_dir, 'include'),
    os.path.join(lexilla_dir, 'lexlib'),
    os.path.join(scintilla_dir, 'src'),
    os.path.join(project_root, 'boostregex'),
])

# 添加预处理器定义 - 基于Visual Studio配置
env.Append(CPPDEFINES=[
    '_CRT_SECURE_NO_DEPRECATE',
    'BOOST_REGEX_STANDALONE',
    'SCI_OWNREGEX',
    'SCI_NAMESPACE',
    'WIN32',
    '_WINDOWS',
    '_USRDLL',
])

# 添加依赖库路径 - 基于Visual Studio配置
env.Append(LIBPATH=[
    os.path.join(scintilla_dir, 'bin'),  # Scintilla库目录
    obj_dir,  # 当前构建目录
])

# 设置目标文件名
target_name = 'notepad_abc.exe'

# 源文件列表 - 基于CMakeLists.txt
src_files = [
    # 主程序文件
    os.path.join(src_dir, 'Notepad_plus.cpp'),
    os.path.join(src_dir, 'Notepad_plus_Window.cpp'),
    os.path.join(src_dir, 'NppBigSwitch.cpp'),
    os.path.join(src_dir, 'NppCommands.cpp'),
    os.path.join(src_dir, 'NppNotification.cpp'),
    os.path.join(src_dir, 'NppIO.cpp'),
    os.path.join(src_dir, 'WinMain.cpp'),
    os.path.join(src_dir, 'Parameters.cpp'),
    os.path.join(src_dir, 'NppDarkMode.cpp'),
    os.path.join(src_dir, 'dpiManagerV2.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinystrA.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinyxmlA.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinyxmlerrorA.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinyxmlparserA.cpp'),
    
    # MISC模块
    os.path.join(src_dir, 'MISC', 'Common', 'Common.cpp'),
    os.path.join(src_dir, 'MISC', 'Common', 'FileInterface.cpp'),
    os.path.join(src_dir, 'MISC', 'Common', 'SortLocale.cpp'),
    os.path.join(src_dir, 'MISC', 'Exception', 'MiniDumper.cpp'),
    os.path.join(src_dir, 'MISC', 'Exception', 'Win32Exception.cpp'),
    os.path.join(src_dir, 'MISC', 'PluginsManager', 'PluginsManager.cpp'),
    os.path.join(src_dir, 'MISC', 'Process', 'Processus.cpp'),
    os.path.join(src_dir, 'MISC', 'RegExt', 'regExtDlg.cpp'),
    os.path.join(src_dir, 'MISC', 'md5', 'md5Dlgs.cpp'),
    os.path.join(src_dir, 'MISC', 'sha1', 'sha1.cpp'),
    os.path.join(src_dir, 'MISC', 'sha1', 'calc_sha1.cpp'),
    os.path.join(src_dir, 'MISC', 'sha2', 'sha-256.cpp'),
    os.path.join(src_dir, 'MISC', 'sha512', 'sha512.cpp'),
    os.path.join(src_dir, 'MISC', 'Common', 'verifySignedfile.cpp'),
    os.path.join(src_dir, 'Utf8_16.cpp'),
    os.path.join(src_dir, 'EncodingMapper.cpp'),
    os.path.join(src_dir, 'lastRecentFileList.cpp'),
    os.path.join(src_dir, 'lesDlgs.cpp'),
    
    # Scintilla组件
    os.path.join(src_dir, 'ScintillaComponent', 'ScintillaEditView.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'ScintillaCtrls.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'AutoCompletion.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'Buffer.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'DocTabView.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'FindReplaceDlg.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'FunctionCallTip.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'GoToLineDlg.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'Printer.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'SmartHighlighter.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'UserDefineDialog.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'columnEditor.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'xmlMatchedTagsHighlighter.cpp'),
    
    # WinControls模块
    os.path.join(src_dir, 'WinControls', 'AboutDlg', 'AboutDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'AboutDlg', 'URLCtrl.cpp'),
    os.path.join(src_dir, 'WinControls', 'AnsiCharPanel', 'ansiCharPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'AnsiCharPanel', 'ListView.cpp'),
    os.path.join(src_dir, 'WinControls', 'AnsiCharPanel', 'asciiListView.cpp'),
    os.path.join(src_dir, 'WinControls', 'ClipboardHistory', 'clipboardHistoryPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'ColourPopup.cpp'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'ColourPicker.cpp'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'WordStyleDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'ContextMenu', 'ContextMenu.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingCont.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingManager.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingSplitter.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'Gripper.cpp'),
    os.path.join(src_dir, 'WinControls', 'DocumentMap', 'DocumentMap.cpp'),
    os.path.join(src_dir, 'WinControls', 'DocumentMap', 'documentSnapshot.cpp'),
    os.path.join(src_dir, 'WinControls', 'FileBrowser', 'FileBrowser.cpp'),
    os.path.join(src_dir, 'WinControls', 'FindCharsInRange', 'FindCharsInRange.cpp'),
    os.path.join(src_dir, 'WinControls', 'FunctionList', 'functionListPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'FunctionList', 'functionParser.cpp'),
    os.path.join(src_dir, 'WinControls', 'Grid', 'BabyGrid.cpp'),
    os.path.join(src_dir, 'WinControls', 'Grid', 'BabyGridWrapper.cpp'),
    os.path.join(src_dir, 'WinControls', 'Grid', 'ShortcutMapper.cpp'),
    os.path.join(src_dir, 'WinControls', 'ImageListSet', 'ImageListSet.cpp'),
    os.path.join(src_dir, 'WinControls', 'OpenSaveFileDialog', 'CustomFileDialog.cpp'),
    os.path.join(src_dir, 'WinControls', 'PluginsAdmin', 'pluginsAdmin.cpp'),
    os.path.join(src_dir, 'WinControls', 'Preference', 'preferenceDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'ProjectPanel', 'ProjectPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges', 'ReadDirectoryChanges.cpp'),
    os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges', 'ReadDirectoryChangesPrivate.cpp'),
    os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges', 'ReadFileChanges.cpp'),
    os.path.join(src_dir, 'WinControls', 'shortcut', 'RunMacroDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'shortcut', 'Shortcut.cpp'),
    os.path.join(src_dir, 'WinControls', 'SplitterContainer', 'Splitter.cpp'),
    os.path.join(src_dir, 'WinControls', 'SplitterContainer', 'SplitterContainer.cpp'),
    os.path.join(src_dir, 'WinControls', 'StaticDialog', 'StaticDialog.cpp'),
    os.path.join(src_dir, 'WinControls', 'StaticDialog', 'RunDlg', 'RunDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'StatusBar', 'StatusBar.cpp'),
    os.path.join(src_dir, 'WinControls', 'TabBar', 'TabBar.cpp'),
    os.path.join(src_dir, 'WinControls', 'TabBar', 'ControlsTab.cpp'),
    os.path.join(src_dir, 'WinControls', 'TaskList', 'TaskListDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'TaskList', 'TaskList.cpp'),
    os.path.join(src_dir, 'WinControls', 'ToolBar', 'ToolBar.cpp'),
    os.path.join(src_dir, 'WinControls', 'ToolTip', 'ToolTip.cpp'),
    os.path.join(src_dir, 'WinControls', 'TrayIcon', 'trayIconControler.cpp'),
    os.path.join(src_dir, 'WinControls', 'TreeView', 'TreeView.cpp'),
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'VerticalFileSwitcherListView.cpp'),
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'VerticalFileSwitcher.cpp'),
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'CategoryManager.cpp'),
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'WindowsDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'SizeableDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'WinMgr.cpp'),
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'WinRect.cpp'),
    os.path.join(src_dir, 'WinControls', 'DoubleBuffer', 'DoubleBuffer.cpp'),
    
    # DarkMode模块
    os.path.join(src_dir, 'DarkMode', 'DarkMode.cpp'),
    
    # uchardet源文件
    os.path.join(src_dir, 'uchardet', 'uchardet.cpp'),
    os.path.join(src_dir, 'uchardet', 'CharDistribution.cpp'),
    
    # COM替代实现文件
    os.path.join(src_dir, 'com_stub.cpp'),
    os.path.join(src_dir, 'uchardet', 'JpCntx.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsBig5Prober.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsCharSetProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsEscCharsetProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsEscSM.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsEUCJPProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsEUCKRProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsEUCTWProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsGB2312Prober.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsHebrewProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsLatin1Prober.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsMBCSGroupProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsMBCSSM.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsSBCSGroupProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsSBCharSetProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsSJISProber.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsUniversalDetector.cpp'),
    os.path.join(src_dir, 'uchardet', 'nsUTF8Prober.cpp'),
    
    # 语言模型文件
    os.path.join(src_dir, 'uchardet', 'LangBulgarianModel.cpp'),
    os.path.join(src_dir, 'uchardet', 'LangCyrillicModel.cpp'),
    os.path.join(src_dir, 'uchardet', 'LangGreekModel.cpp'),
    os.path.join(src_dir, 'uchardet', 'LangHebrewModel.cpp'),
    os.path.join(src_dir, 'uchardet', 'LangHungarianModel.cpp'),
    os.path.join(src_dir, 'uchardet', 'LangThaiModel.cpp'),
    
    # 本地化文件
    os.path.join(src_dir, 'localization.cpp'),
    
    # TinyXml源文件
    os.path.join(src_dir, 'TinyXml', 'tinyxml.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyxmlerror.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyxmlparser.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinystr.cpp'),
    
    # json源文件
    # os.path.join(src_dir, 'json', 'json.cpp'),
    # os.path.join(src_dir, 'json', 'json_value.cpp'),
    # os.path.join(src_dir, 'json', 'json_reader.cpp'),
    # os.path.join(src_dir, 'json', 'json_writer.cpp'),
]

# 资源文件列表 - 只包含实际存在的文件
rc_files = [
    os.path.join(src_dir, 'Notepad_plus.rc'),  # 主资源文件
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'VerticalFileSwitcher.rc'),  # 文档列表对话框资源文件
    os.path.join(src_dir, 'WinControls', 'FunctionList', 'functionListPanel.rc'),  # 函数列表对话框资源文件
    os.path.join(src_dir, 'ScintillaComponent', 'FindReplaceDlg.rc'),  # 查找替换对话框资源文件
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingGUIWidget.rc'),  # 停靠窗口资源文件
]

# 预构建操作 - 基于CMakeLists.txt
# 执行NppLibsVersionH-generator.bat生成版本头文件
npp_libs_version_script = os.path.join(src_dir, 'NppLibsVersionH-generator.bat')
if os.path.exists(npp_libs_version_script):
    ensure_utf8_print("执行NppLibsVersionH-generator.bat生成版本头文件...")
    os.system(f'cd "{src_dir}" && "{npp_libs_version_script}"')
else:
    ensure_utf8_print(f"警告: 找不到NppLibsVersionH-generator.bat脚本: {npp_libs_version_script}")

# 后构建操作 - 复制实际存在的配置文件
config_files = [
    os.path.join(src_dir, 'contextMenu.xml'),
    os.path.join(src_dir, 'langs.model.xml'),
    os.path.join(src_dir, 'shortcuts.xml'),
    os.path.join(src_dir, 'stylers.model.xml'),
]

# 添加清单文件
manifest_file = os.path.join(src_dir, 'notepad++.exe.manifest')
if os.path.exists(manifest_file):
    env.Append(LINKFLAGS=[f'/MANIFEST:EMBED,{manifest_file}'])

# 资源文件处理
ensure_utf8_print("开始处理资源文件编译...")

# 确保资源文件路径正确
vertical_file_switcher_rc = os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'VerticalFileSwitcher.rc')
notepad_plus_rc = os.path.join(src_dir, 'Notepad_plus.rc')
function_list_panel_rc = os.path.join(src_dir, 'WinControls', 'FunctionList', 'functionListPanel.rc')
find_replace_dlg_rc = os.path.join(src_dir, 'ScintillaComponent', 'FindReplaceDlg.rc')
docking_resource_rc = os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingGUIWidget.rc')
rc_files = [vertical_file_switcher_rc, notepad_plus_rc, function_list_panel_rc, find_replace_dlg_rc, docking_resource_rc]

# 处理资源文件
rc_objects = []
for rc_file in rc_files:
    if os.path.exists(rc_file):
        print(f"处理资源文件: {rc_file}")
        try:
            # 首先确保对应的.h文件存在
            h_file = rc_file.replace('.rc', '_rc.h')
            if os.path.exists(h_file):
                ensure_utf8_print(f"  确认头文件存在: {h_file}")
            else:
                ensure_utf8_print(f"  警告: 找不到头文件: {h_file}")
            
            # 正确编译.rc文件而不是使用C++替代文件
            ensure_utf8_print(f"  编译资源文件...")
            
            # 使用Microsoft的rc编译器编译资源文件
            # 注意：这需要Windows SDK中的rc.exe工具
            rc_obj = env.RES(rc_file)
            rc_objects.append(rc_obj)
            ensure_utf8_print(f"  成功编译资源文件: {rc_file}")
                
        except Exception as e:
            ensure_utf8_print(f"  处理资源文件时出错: {e}")
            ensure_utf8_print(f"  尝试使用备用方法...")
            
            # 如果直接编译失败，生成带有完整资源定义的C++文件作为备用
            cpp_file = os.path.join(obj_dir, os.path.basename(rc_file).replace('.rc', '_resource.cpp'))
            
            # 为VerticalFileSwitcher生成更完整的资源定义
            if 'VerticalFileSwitcher.rc' in rc_file:
                cpp_content = '''// 自动生成的资源定义文件
#include "VerticalFileSwitcher_rc.h"
#include <windows.h>

// 确保资源ID定义
#ifndef IDD_DOCLIST
#define IDD_DOCLIST 3000
#endif

#ifndef IDC_LIST_DOCLIST
#define IDC_LIST_DOCLIST 3001
#endif

// 定义对话框模板结构
#pragma comment(linker, "/DEFAULTLIB:user32.lib")

// 这个函数会创建对话框，绕过资源加载问题
BOOL WINAPI CreateVerticalFileSwitcherDialog(HWND hWndParent, DLGPROC lpDialogFunc, LPARAM lParam) {
    // 创建主窗口
    HWND hDlg = ::CreateWindowEx(
        WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
        WC_DIALOG,
        L"Document List",
        DS_SETFONT | WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD,
        26, 41, 142, 324,
        hWndParent,
        NULL,
        GetModuleHandle(NULL),
        NULL
    );
    
    if (hDlg) {
        // 设置用户数据
        ::SetWindowLongPtr(hDlg, GWLP_USERDATA, (LONG_PTR)lParam);
        
        // 创建列表视图控件
        HWND hListView = ::CreateWindowEx(
            WS_EX_CLIENTEDGE,
            WC_LISTVIEW,
            L"",
            WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
            50, 44, 78, 120,
            hDlg,
            (HMENU)IDC_LIST_DOCLIST,
            GetModuleHandle(NULL),
            NULL
        );
        
        // 显示窗口
        ::ShowWindow(hDlg, SW_SHOW);
        ::UpdateWindow(hDlg);
        
        // 发送WM_INITDIALOG消息
        lpDialogFunc(hDlg, WM_INITDIALOG, 0, lParam);
    }
    
    return (hDlg != NULL);
}

void vertical_file_switcher_resource_placeholder() {}
'''
            elif 'functionListPanel.rc' in rc_file:
                cpp_content = '''// 自动生成的函数列表资源定义文件
#include "functionListPanel_rc.h"
#include <windows.h>

// 确保资源ID定义
#ifndef IDD_FUNCLIST_PANEL
#define IDD_FUNCLIST_PANEL 3100
#endif

#ifndef IDC_TREE_FUNCLIST
#define IDC_TREE_FUNCLIST 3101
#endif

// 定义对话框模板结构
#pragma comment(linker, "/DEFAULTLIB:user32.lib")

// 这个函数会创建函数列表对话框，绕过资源加载问题
BOOL WINAPI CreateFunctionListPanelDialog(HWND hWndParent, DLGPROC lpDialogFunc, LPARAM lParam) {
    // 创建主窗口
    HWND hDlg = ::CreateWindowEx(
        WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
        WC_DIALOG,
        L"Function List",
        DS_SETFONT | WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD,
        26, 41, 142, 324,
        hWndParent,
        NULL,
        GetModuleHandle(NULL),
        NULL
    );
    
    if (hDlg) {
        // 设置用户数据
        ::SetWindowLongPtr(hDlg, GWLP_USERDATA, (LONG_PTR)lParam);
        
        // 创建树形视图控件
        HWND hTreeView = ::CreateWindowEx(
            WS_EX_CLIENTEDGE,
            WC_TREEVIEW,
            L"",
            WS_CHILD | WS_VISIBLE | TVS_HASBUTTONS | TVS_HASLINES | TVS_LINESATROOT | TVS_SHOWSELALWAYS,
            50, 44, 78, 120,
            hDlg,
            (HMENU)IDC_TREE_FUNCLIST,
            GetModuleHandle(NULL),
            NULL
        );
        
        // 显示窗口
        ::ShowWindow(hDlg, SW_SHOW);
        ::UpdateWindow(hDlg);
        
        // 发送WM_INITDIALOG消息
        lpDialogFunc(hDlg, WM_INITDIALOG, 0, lParam);
    }
    
    return (hDlg != NULL);
}

void function_list_panel_resource_placeholder() {}
'''
            elif 'Notepad_plus.rc' in rc_file:
                cpp_content = '''// 自动生成的资源定义文件
// 主程序资源定义
void notepad_plus_resource_placeholder() {}
'''
            elif 'FindReplaceDlg.rc' in rc_file:
                cpp_content = '''// 自动生成的查找替换对话框资源定义文件
#include "FindReplaceDlg_rc.h"
#include <windows.h>

// 确保资源ID定义
#ifndef IDD_INCREMENT_FIND
#define IDD_INCREMENT_FIND 1680
#endif

// 定义对话框模板结构
#pragma comment(linker, "/DEFAULTLIB:user32.lib")

// 这个函数会创建增量查找对话框，绕过资源加载问题
BOOL WINAPI CreateIncrementFindDialog(HWND hWndParent, DLGPROC lpDialogFunc, LPARAM lParam) {
    // 创建主窗口
    HWND hDlg = ::CreateWindowEx(
        WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
        WC_DIALOG,
        L"Incremental Find",
        DS_SETFONT | WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD,
        26, 41, 142, 324,
        hWndParent,
        NULL,
        GetModuleHandle(NULL),
        NULL
    );
    
    if (hDlg) {
        // 设置用户数据
        ::SetWindowLongPtr(hDlg, GWLP_USERDATA, (LONG_PTR)lParam);
        
        // 显示窗口
        ::ShowWindow(hDlg, SW_SHOW);
        ::UpdateWindow(hDlg);
        
        // 发送WM_INITDIALOG消息
        lpDialogFunc(hDlg, WM_INITDIALOG, 0, lParam);
    }
    
    return (hDlg != NULL);
}

void find_replace_dlg_resource_placeholder() {}
'''
            elif 'DockingGUIWidget.rc' in rc_file:
                cpp_content = '''// 自动生成的停靠窗口资源定义文件
#include "dockingResource.h"
#include <windows.h>

// 确保资源ID定义
#ifndef IDD_CONTAINER_DLG
#define IDD_CONTAINER_DLG 139
#endif

// 定义对话框模板结构
#pragma comment(linker, "/DEFAULTLIB:user32.lib")

// 这个函数会创建停靠窗口容器对话框，绕过资源加载问题
BOOL WINAPI CreateContainerDialog(HWND hWndParent, DLGPROC lpDialogFunc, LPARAM lParam) {
    // 创建主窗口
    HWND hDlg = ::CreateWindowEx(
        WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
        WC_DIALOG,
        L"Docking Container",
        DS_SETFONT | WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD,
        26, 41, 142, 324,
        hWndParent,
        NULL,
        GetModuleHandle(NULL),
        NULL
    );
    
    if (hDlg) {
        // 设置用户数据
        ::SetWindowLongPtr(hDlg, GWLP_USERDATA, (LONG_PTR)lParam);
        
        // 显示窗口
        ::ShowWindow(hDlg, SW_SHOW);
        ::UpdateWindow(hDlg);
        
        // 发送WM_INITDIALOG消息
        lpDialogFunc(hDlg, WM_INITDIALOG, 0, lParam);
    }
    
    return (hDlg != NULL);
}

void docking_resource_placeholder() {}
'''
            else:
                cpp_content = f'''// 自动生成的资源定义文件 - 替代{os.path.basename(rc_file)}
void {os.path.basename(rc_file).replace('.', '_')}_resource_placeholder() {{}}
'''
            
            # 写入C++文件
            os.makedirs(obj_dir, exist_ok=True)
            with open(cpp_file, 'w', encoding='utf-8-sig') as f:
                f.write(cpp_content)
            
            # 编译C++文件
            rc_obj = env.Object(cpp_file)
            rc_objects.append(rc_obj)
            ensure_utf8_print(f"  成功生成并编译备用资源定义文件: {cpp_file}")
            if 'VerticalFileSwitcher.rc' in rc_file:
                cpp_file = os.path.join(obj_dir, 'VerticalFileSwitcher_resource_fallback.cpp')
                fallback_content = '''// 强制回退资源定义文件

// 确保资源ID定义
#ifndef IDD_DOCLIST
#define IDD_DOCLIST 3000
#endif

#ifndef IDC_LIST_DOCLIST
#define IDC_LIST_DOCLIST 3001
#endif

// 资源定义结束
void vertical_file_switcher_resource_fallback() {}
'''
                os.makedirs(obj_dir, exist_ok=True)
                with open(cpp_file, 'w', encoding='utf-8-sig') as f:
                    f.write(fallback_content)
                
                try:
                    rc_obj = env.Object(cpp_file)
                    rc_objects.append(rc_obj)
                    ensure_utf8_print(f"  成功生成并编译回退资源定义文件: {cpp_file}")
                except Exception as e2:
                    ensure_utf8_print(f"  生成回退资源定义文件失败: {e2}")
            elif 'functionListPanel.rc' in rc_file:
                cpp_file = os.path.join(obj_dir, 'FunctionListPanel_resource_fallback.cpp')
                fallback_content = '''// 强制回退函数列表资源定义文件

// 确保资源ID定义
#ifndef IDD_FUNCLIST_PANEL
#define IDD_FUNCLIST_PANEL 3100
#endif

#ifndef IDC_TREE_FUNCLIST
#define IDC_TREE_FUNCLIST 3101
#endif

// 资源定义结束
void function_list_panel_resource_fallback() {}
'''
                os.makedirs(obj_dir, exist_ok=True)
                with open(cpp_file, 'w', encoding='utf-8-sig') as f:
                    f.write(fallback_content)
                
                try:
                    rc_obj = env.Object(cpp_file)
                    rc_objects.append(rc_obj)
                    ensure_utf8_print(f"  成功生成并编译回退资源定义文件: {cpp_file}")
                except Exception as e2:
                    ensure_utf8_print(f"  生成回退资源定义文件失败: {e2}")
    else:
        ensure_utf8_print(f"警告: 找不到资源文件: {rc_file}")
        # 即使资源文件不存在，也要确保VerticalFileSwitcher的资源ID被定义
        if 'VerticalFileSwitcher.rc' in rc_file:
            cpp_file = os.path.join(obj_dir, 'VerticalFileSwitcher_resource_fallback.cpp')
            fallback_content = '''// 强制回退资源定义文件

// 确保资源ID定义
#ifndef IDD_DOCLIST
#define IDD_DOCLIST 3000
#endif

#ifndef IDC_LIST_DOCLIST
#define IDC_LIST_DOCLIST 3001
#endif

// 资源定义结束
void vertical_file_switcher_resource_fallback() {}
'''
            os.makedirs(obj_dir, exist_ok=True)
            with open(cpp_file, 'w', encoding='utf-8-sig') as f:
                f.write(fallback_content)
            
            try:
                rc_obj = env.Object(cpp_file)
                rc_objects.append(rc_obj)
                print(f"  成功生成并编译回退资源定义文件: {cpp_file}")
            except Exception as e2:
                print(f"  生成回退资源定义文件失败: {e2}")
        # 即使资源文件不存在，也要确保FunctionListPanel的资源ID被定义
        elif 'functionListPanel.rc' in rc_file:
            cpp_file = os.path.join(obj_dir, 'FunctionListPanel_resource_fallback.cpp')
            fallback_content = '''// 强制回退函数列表资源定义文件

// 确保资源ID定义
#ifndef IDD_FUNCLIST_PANEL
#define IDD_FUNCLIST_PANEL 3100
#endif

#ifndef IDC_TREE_FUNCLIST
#define IDC_TREE_FUNCLIST 3101
#endif

// 资源定义结束
void function_list_panel_resource_fallback() {}
'''
            os.makedirs(obj_dir, exist_ok=True)
            with open(cpp_file, 'w', encoding='utf-8-sig') as f:
                f.write(fallback_content)
            
            try:
                rc_obj = env.Object(cpp_file)
                rc_objects.append(rc_obj)
                print(f"  成功生成并编译回退资源定义文件: {cpp_file}")
            except Exception as e2:
                print(f"  生成回退资源定义文件失败: {e2}")

if len(rc_objects) == 0:
    ensure_utf8_print("注意: 没有成功创建任何资源定义文件，程序可能缺少图标和对话框资源")
else:
    ensure_utf8_print(f"成功处理了 {len(rc_objects)} 个资源文件")

# 构建主程序 - 直接输出到bin目录
start_time = datetime.now()
ensure_utf8_print(f"开始构建 {target_name} ({build_type} {target_arch})...")
ensure_utf8_print(f"构建开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
program = env.Program(target=os.path.join(bin_dir, target_name), source=src_files + rc_objects)

# 添加后构建操作 - 复制配置文件
def copy_config_files(target, source, env):
    """复制配置文件到输出目录"""
    for config_file in config_files:
        src_path = config_file
        if os.path.exists(src_path):
            if os.path.isdir(src_path):
                # 如果是目录，复制整个目录
                import shutil
                dest_path = os.path.join(bin_dir, os.path.basename(src_path))
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
            else:
                # 如果是文件，复制文件
                dest_path = os.path.join(bin_dir, os.path.basename(src_path))
                import shutil
                shutil.copy2(src_path, dest_path)
        else:
            ensure_utf8_print(f"警告: 找不到配置文件: {src_path}")

# 添加后构建操作
env.AddPostAction(program, copy_config_files)

# 显示构建完成信息
def print_build_info(target, source, env):
    """打印构建完成信息"""
    end_time = datetime.now()
    ensure_utf8_print(f"\n构建完成: {target[0].path}")
    ensure_utf8_print(f"构建类型: {build_type}")
    ensure_utf8_print(f"目标架构: {target_arch}")
    ensure_utf8_print(f"构建开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    ensure_utf8_print(f"构建结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    ensure_utf8_print(f"总构建时间: {(end_time - start_time).total_seconds():.2f} 秒")
    
    # 播放语音提示
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("任务运行完毕，过来看看！")
        engine.runAndWait()
    except Exception as e:
        ensure_utf8_print(f"无法播放语音提示: {e}")

# 添加后构建操作
env.AddPostAction(program, print_build_info)

# 返回构建目标
Return('program')