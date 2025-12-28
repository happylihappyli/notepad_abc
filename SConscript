# -*- coding: utf-8 -*-
"""
Notepad++ SConscript构建脚本
基于CMakeLists.txt的改进版本
"""

import os
import sys
import time
import subprocess
import glob
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

# 在构建开始时终止可能正在运行的notepad_abc进程
def kill_running_processes():
    """终止正在运行的notepad_abc进程"""
    ensure_utf8_print("检查并终止正在运行的notepad_abc进程...")
    try:
        # 首先尝试使用taskkill命令终止进程
        result = subprocess.run(['taskkill', '/f', '/im', 'notepad_abc.exe'], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            ensure_utf8_print("成功终止正在运行的notepad_abc进程")
        else:
            # 如果没有找到进程，这不是错误
            if "notepad_abc.exe" in result.stderr:
                ensure_utf8_print("没有发现正在运行的notepad_abc进程")
            else:
                ensure_utf8_print(f"终止进程时出现警告: {result.stderr}")
    except Exception as e:
        ensure_utf8_print(f"终止进程时出错: {str(e)}")
        
    # 添加额外的检查，确保进程确实被终止
    try:
        # 等待一段时间确保进程被完全终止
        time.sleep(1)
        
        # 再次检查是否还有进程在运行
        check_result = subprocess.run(['tasklist', '/fi', 'imagename eq notepad_abc.exe'], 
                                    capture_output=True, text=True, encoding='utf-8')
        if 'notepad_abc.exe' in check_result.stdout and 'No tasks are running' not in check_result.stdout:
            ensure_utf8_print("警告: 仍有notepad_abc进程在运行，尝试强制终止...")
            # 使用更强的终止方式
            subprocess.run(['taskkill', '/f', '/t', '/im', 'notepad_abc.exe'], 
                         capture_output=True, text=True, encoding='utf-8')
            time.sleep(2)  # 等待更长时间
            
            # 最后再检查一次
            final_check = subprocess.run(['tasklist', '/fi', 'imagename eq notepad_abc.exe'], 
                                       capture_output=True, text=True, encoding='utf-8')
            if 'notepad_abc.exe' in final_check.stdout and 'No tasks are running' not in final_check.stdout:
                ensure_utf8_print("警告: 仍然无法终止notepad_abc进程")
            else:
                ensure_utf8_print("成功终止所有notepad_abc进程")
        else:
            ensure_utf8_print("确认没有notepad_abc进程在运行")
    except Exception as e:
        ensure_utf8_print(f"检查进程状态时出错: {str(e)}")

# 调用函数终止进程
kill_running_processes()

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

# 导入主脚本中的变量和环境
Import('project_root', 'src_dir', 'scintilla_dir', 'lexilla_dir', 'bin_dir', 'obj_dir')
Import('configure_build_options', 'configure_link_options', 'get_compiler_type')
Import('env', 'lexilla_lib', 'scintilla_lib', 'libs')  # 导入配置好的环境变量和预编译库

# 使用从SConstruct导入的环境，不再创建新环境

# 移除复杂的资源编译器配置，改用更简单可靠的资源处理方法

# 设置构建类型和目标架构
build_type = ARGUMENTS.get('build', 'Release')  # 默认为Release构建
target_arch = ARGUMENTS.get('arch', 'x64')       # 默认为x64架构
subsystem = ARGUMENTS.get('subsystem', 'WINDOWS')  # 默认为WINDOWS子系统

# 配置构建选项
env = configure_build_options(env, build_type)

# 获取编译器类型
compiler_type = get_compiler_type(env)
print(f"SConscript配置 - 编译器类型: {compiler_type}")

# 强制使用Clang编译器
if compiler_type != 'clang':
    print("❌ 错误: SConscript中检测到非Clang编译器，构建终止")
    sys.exit(1)

# Clang编译器选项 - 使用GCC/Clang风格参数，避免MSVC参数
env.Append(CCFLAGS=['-fexceptions'])  # Clang需要显式启用异常处理
env.Append(CCFLAGS=['-fms-extensions'])  # 启用Microsoft扩展支持
env.Append(CCFLAGS=['-std=c++20'])  # 使用C++20标准
env.Append(CCFLAGS=['-Wall'])  # 启用所有警告
env.Append(CCFLAGS=['-Wextra'])  # 启用额外警告
env.Append(CCFLAGS=['-Wno-unused-parameter'])  # 禁用未使用参数警告
env.Append(CCFLAGS=['-Wno-unused-variable'])  # 禁用未使用变量警告
env.Append(CCFLAGS=['-Wno-microsoft-cast'])  # 禁用Microsoft类型转换警告
env.Append(CCFLAGS=['-Wno-microsoft-enum-value'])  # 禁用Microsoft枚举值警告

# 设置链接器选项 - 已在configure_link_options中设置，避免重复

# 链接器配置已在configure_link_options中完成，避免重复设置
print("🔧 链接器配置已从SConstruct导入，无需重复设置")
print(f"✅ 当前链接器: {env.get('LINK', '未设置')}")
print(f"✅ 当前链接器标志: {env.get('LINKFLAGS', [])}")

# 添加Lexilla和Scintilla包含目录 - 已通过CCFLAGS中的-I选项添加，避免重复

# 添加预处理器定义 - 使用Clang格式
env.Append(CCFLAGS=[
    '-D_CRT_SECURE_NO_DEPRECATE',
    '-DBOOST_REGEX_STANDALONE',
    '-DSCI_NAMESPACE',
    '-DWIN32',
    '-D_WINDOWS',
    #'-D_USRDLL', # Notepad++ is an EXE, not a DLL
])

# 添加额外的包含路径 - 根据编译器类型动态适配
if compiler_type == 'clang':
    # Clang编译器格式 - 直接添加到CCFLAGS使用-I选项
    # 统一使用Clang编译器格式
    clang_include_dirs = [
        src_dir,  # 主源码目录
        os.path.join(src_dir, 'MISC'),  # MISC模块顶层目录
        os.path.join(src_dir, 'MISC', 'Common'),  # MISC/Common子目录
        os.path.join(src_dir, 'MISC', 'PluginsManager'),  # MISC/PluginsManager子目录（包含Notepad_plus_msgs.h）
        os.path.join(src_dir, 'MISC', 'Exception'),  # MISC/Exception子目录（包含Win32Exception.h）
        os.path.join(src_dir, 'ScintillaComponent'),  # Scintilla组件目录
        os.path.join(src_dir, 'WinControls'),  # WinControls顶层目录
        os.path.join(src_dir, 'WinControls', 'DockingWnd'),  # DockingWnd子目录
        os.path.join(src_dir, 'WinControls', 'FunctionList'),  # FunctionList子目录
        os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher'),  # VerticalFileSwitcher子目录
        os.path.join(src_dir, 'WinControls', 'ToolBar'),  # ToolBar子目录（包含ToolBar.h）
        os.path.join(src_dir, 'WinControls', 'ImageListSet'),  # ImageListSet子目录（包含ImageListSet.h）
        os.path.join(src_dir, 'WinControls', 'shortcut'),  # shortcut子目录（包含shortcut.h）
        os.path.join(src_dir, 'WinControls', 'StaticDialog'),  # StaticDialog子目录（包含StaticDialog.h）
        os.path.join(src_dir, 'WinControls', 'TomatoTimer'),  # TomatoTimer子目录（包含TomatoTimer.h）
        os.path.join(src_dir, 'WinControls', 'ContextMenu'),  # ContextMenu子目录（包含ContextMenu.h）
        os.path.join(src_dir, 'WinControls', 'TabBar'),  # TabBar子目录（包含ControlsTab.h）
        os.path.join(src_dir, 'WinControls', 'ColourPicker'),  # ColourPicker子目录（包含ColourPicker.h）
        os.path.join(src_dir, 'WinControls', 'AboutDlg'),  # AboutDlg子目录（包含URLCtrl.h）
        os.path.join(src_dir, 'WinControls', 'SplitterContainer'),  # SplitterContainer子目录（包含SplitterContainer.h）
        os.path.join(src_dir, 'WinControls', 'StatusBar'),  # StatusBar子目录（包含StatusBar.h）
        os.path.join(src_dir, 'WinControls', 'StaticDialog', 'RunDlg'),  # RunDlg子目录（包含RunDlg.h）
        os.path.join(src_dir, 'WinControls', 'FindCharsInRange'),  # FindCharsInRange子目录（包含FindCharsInRange.h）
        os.path.join(src_dir, 'WinControls', 'TrayIcon'),  # TrayIcon子目录（包含trayIconControler.h）
        os.path.join(src_dir, 'WinControls', 'Preference'),  # Preference子目录（包含preferenceDlg.h）
        os.path.join(src_dir, 'MISC', 'RegExt'),  # RegExt子目录（包含regExtDlg.h）
        os.path.join(src_dir, 'WinControls', 'WindowsDlg'),  # WindowsDlg子目录（包含WindowsDlg.h）
        os.path.join(src_dir, 'MISC', 'Process'),  # Process子目录（包含Processus.h）
        os.path.join(src_dir, 'WinControls', 'PluginsAdmin'),  # PluginsAdmin子目录（包含pluginsAdmin.h）
        os.path.join(src_dir, 'WinControls', 'AnsiCharPanel'),  # AnsiCharPanel子目录（包含ListView.h）
        os.path.join(src_dir, 'WinControls', 'DocumentMap'),  # DocumentMap子目录（包含documentSnapshot.h）
        os.path.join(src_dir, 'MISC', 'md5'),  # md5子目录（包含md5Dlgs.h）
        os.path.join(src_dir, 'WinControls', 'OpenSaveFileDialog'),  # OpenSaveFileDialog子目录（包含CustomFileDialog.h）
        os.path.join(src_dir, 'WinControls', 'Grid'),  # Grid子目录（包含ShortcutMapper.h）
        os.path.join(src_dir, 'WinControls', 'TaskList'),  # TaskList子目录（包含TaskListDlg.h）
        os.path.join(src_dir, 'WinControls', 'ClipboardHistory'),  # ClipboardHistory子目录（包含clipboardHistoryPanel.h）
        os.path.join(src_dir, 'WinControls', 'ProjectPanel'),  # ProjectPanel子目录（包含ProjectPanel.h）
        os.path.join(src_dir, 'WinControls', 'TreeView'),  # TreeView子目录（包含TreeView.h）
        os.path.join(src_dir, 'WinControls', 'FileBrowser'),  # FileBrowser子目录（包含fileBrowser.h）
        os.path.join(src_dir, 'MISC', 'sha2'),  # sha2子目录（包含sha-256.h）
        os.path.join(src_dir, 'MISC', 'sha1'),  # sha1子目录（包含calc_sha1.h）
        os.path.join(src_dir, 'MISC', 'sha512'),  # sha512子目录（包含sha512.h）
        os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges'),  # ReadDirectoryChanges子目录（包含ReadDirectoryChanges.h）
        os.path.join(src_dir, 'WinControls', 'ToolTip'),  # ToolTip子目录（包含ToolTip.h）
        os.path.join(src_dir, 'TinyXml'),  # TinyXml目录
        os.path.join(src_dir, 'TinyXml', 'tinyXmlA'),  # TinyXmlA子目录
        os.path.join(src_dir, 'uchardet'),  # uchardet目录
        os.path.join(src_dir, 'json'),  # json目录
        os.path.join(lexilla_dir, 'include'),  # Lexilla包含目录
        os.path.join(scintilla_dir, 'include'),  # Scintilla包含目录
        os.path.join(lexilla_dir, 'lexlib'),  # Lexilla库目录
        os.path.join(scintilla_dir, 'src'),  # Scintilla源码目录
        os.path.join(project_root, 'boostregex'),  # boostregex目录
    ]
    
    # 使用Clang格式的-I选项直接添加到CCFLAGS
    for include_dir in clang_include_dirs:
        env.Append(CCFLAGS=['-I' + include_dir])
    
    print(f"✅ 已添加Clang格式包含路径: 共{len(clang_include_dirs)}个目录")

# 依赖库路径 - 使用项目根目录下的预编译库
# 注意：不再使用env.Append(LIBPATH)来避免触发默认链接器命令生成器
# 库路径将在自定义链接器命令模板中处理
lib_paths = [
    project_root,  # 项目根目录（包含预编译的liblexilla.lib和libscintilla.lib）
    obj_dir,  # 当前构建目录
]

print(f"✅ 库路径已设置（将在自定义链接器命令中处理）: {lib_paths}")

# 链接器配置已在SConstruct中通过configure_link_options完成，无需重复设置
print("🔧 链接器配置已在SConstruct中完成，无需重复设置")
print(f"✅ 当前链接器: {env.get('LINK', '未设置')}")
print(f"✅ 当前链接器标志: {env.get('LINKFLAGS', [])}")
print(f"✅ 当前LIBS: {env.get('LIBS', [])}")

# 设置目标文件名 - 根据子系统类型设置不同的文件名
if subsystem.upper() == 'CONSOLE':
    target_name = 'notepad_abc_console.exe'  # 控制台版本
else:
    target_name = 'notepad_abc.exe'  # Windows版本（默认）

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
# TinyXML源文件 - 包含ANSI和非ANSI版本
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinystrA.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinyxmlA.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinyxmlerrorA.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyXmlA', 'tinyxmlparserA.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinystr.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyxml.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyxmlerror.cpp'),
    os.path.join(src_dir, 'TinyXml', 'tinyxmlparser.cpp'),
    
    # MISC模块
    os.path.join(src_dir, 'MISC', 'Common', 'Common.cpp'),
    os.path.join(src_dir, 'localization.cpp'),  # 添加localization.cpp
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
    os.path.join(src_dir, 'ScintillaComponent', 'SmartHighlighter.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'Buffer.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'DocTabView.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'FindReplaceDlg.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'FunctionCallTip.cpp'),
    # os.path.join(src_dir, 'ScintillaComponent', 'FunctionParser.cpp'), # Moved to WinControls/FunctionList
    os.path.join(src_dir, 'ScintillaComponent', 'GoToLineDlg.cpp'),
    # os.path.join(src_dir, 'ScintillaComponent', 'IncrementalSearch.cpp'), # Removed (file missing)
    os.path.join(src_dir, 'ScintillaComponent', 'ParametersDlg.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'Printer.cpp'),  # 添加Printer.cpp
    os.path.join(src_dir, 'ScintillaComponent', 'UserDefineDialog.cpp'),
    os.path.join(src_dir, 'ScintillaComponent', 'columnEditor.cpp'),  # 添加columnEditor.cpp
    os.path.join(src_dir, 'ScintillaComponent', 'xmlMatchedTagsHighlighter.cpp'),
    
    # WinControls模块
    os.path.join(src_dir, 'WinControls', 'AboutDlg', 'AboutDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'AboutDlg', 'URLCtrl.cpp'),
    os.path.join(src_dir, 'WinControls', 'AnsiCharPanel', 'AnsiCharPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'AnsiCharPanel', 'ListView.cpp'),
    os.path.join(src_dir, 'WinControls', 'ClipboardHistory', 'clipboardHistoryPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'ColourPicker.cpp'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'WordStyleDlg.cpp'),  # 添加WordStyleDlg.cpp
    os.path.join(src_dir, 'WinControls', 'ContextMenu', 'ContextMenu.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingGUIWidget.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingManager.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingCont.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingSplitter.cpp'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'Gripper.cpp'),
    os.path.join(src_dir, 'WinControls', 'DocumentMap', 'documentMap.cpp'),
    os.path.join(src_dir, 'WinControls', 'DocumentMap', 'documentSnapshot.cpp'),
    os.path.join(src_dir, 'WinControls', 'FileBrowser', 'fileBrowser.cpp'),
    os.path.join(src_dir, 'WinControls', 'FindCharsInRange', 'FindCharsInRange.cpp'),
    os.path.join(src_dir, 'WinControls', 'DoubleBuffer', 'DoubleBuffer.cpp'),
    os.path.join(src_dir, 'WinControls', 'FunctionList', 'functionListPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'Grid', 'Grid.cpp'),
    os.path.join(src_dir, 'WinControls', 'Grid', 'BabyGrid.cpp'),  # 添加BabyGrid.cpp
    os.path.join(src_dir, 'WinControls', 'Grid', 'ShortcutMapper.cpp'),
    os.path.join(src_dir, 'WinControls', 'ImageListSet', 'ImageListSet.cpp'),
    os.path.join(src_dir, 'WinControls', 'OpenSaveFileDialog', 'CustomFileDialog.cpp'),
    os.path.join(src_dir, 'WinControls', 'PluginsAdmin', 'pluginsAdmin.cpp'),
    os.path.join(src_dir, 'WinControls', 'Preference', 'preferenceDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'ProjectPanel', 'ProjectPanel.cpp'),
    os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges', 'ReadDirectoryChanges.cpp'),
    os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges', 'ReadFileChanges.cpp'),
    os.path.join(src_dir, 'WinControls', 'SplitterContainer', 'SplitterContainer.cpp'),
    os.path.join(src_dir, 'WinControls', 'SplitterContainer', 'Splitter.cpp'),  # 添加Splitter.cpp
    os.path.join(src_dir, 'WinControls', 'StaticDialog', 'StaticDialog.cpp'),
    os.path.join(src_dir, 'WinControls', 'StaticDialog', 'RunDlg', 'RunDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'StatusBar', 'StatusBar.cpp'),
    os.path.join(src_dir, 'WinControls', 'TabBar', 'ControlsTab.cpp'),
    os.path.join(src_dir, 'WinControls', 'TabBar', 'TabBar.cpp'),
    os.path.join(src_dir, 'WinControls', 'TaskList', 'TaskList.cpp'),
    os.path.join(src_dir, 'WinControls', 'TaskList', 'TaskListDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'ToolBar', 'ToolBar.cpp'),
    os.path.join(src_dir, 'WinControls', 'ToolTip', 'ToolTip.cpp'),
    os.path.join(src_dir, 'WinControls', 'TreeView', 'TreeView.cpp'),
    os.path.join(src_dir, 'WinControls', 'TrayIcon', 'trayIconControler.cpp'),
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'VerticalFileSwitcher.cpp'),
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'CategoryManager.cpp'),  # 添加CategoryManager.cpp
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'VerticalFileSwitcherListView.cpp'),
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'WindowsDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'SizeableDlg.cpp'),  # 添加SizeableDlg.cpp
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'WinMgr.cpp'),  # 添加WinMgr.cpp
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'WinRect.cpp'),  # 添加WinRect.cpp
    os.path.join(src_dir, 'WinControls', 'shortcut', 'shortcut.cpp'),
    os.path.join(src_dir, 'WinControls', 'shortcut', 'RunMacroDlg.cpp'),
    
    # TomatoTimer模块
    os.path.join(src_dir, 'WinControls', 'TomatoTimer', 'TomatoTimer.cpp'),
    os.path.join(src_dir, 'WinControls', 'TomatoTimer', 'TomatoTimerDlg.cpp'),
    os.path.join(src_dir, 'WinControls', 'TomatoTimer', 'CycleAlarm.cpp'),
    
    # DarkMode模块
    os.path.join(src_dir, 'DarkMode', 'DarkMode.cpp'),
    
    # uchardet源文件 - 将在列表定义后使用glob添加
    
    # boostregex源文件
    os.path.join(project_root, 'boostregex', 'BoostRegExSearch.cxx'),
    os.path.join(project_root, 'boostregex', 'UTF8DocumentIterator.cxx'),
    
    # Lexilla lexers
    os.path.join(lexilla_dir, 'lexers', 'LexJulia.cxx'),

    # 其他缺失的源文件
    os.path.join(src_dir, 'WinControls', 'FunctionList', 'functionParser.cpp'),
    os.path.join(src_dir, 'WinControls', 'AnsiCharPanel', 'asciiListView.cpp'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'ColourPopup.cpp'),
    os.path.join(src_dir, 'WinControls', 'Grid', 'BabyGridWrapper.cpp'),
    os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges', 'ReadDirectoryChangesPrivate.cpp'),
]

# 添加所有uchardet源文件
src_files.extend(glob.glob(os.path.join(src_dir, 'uchardet', '*.cpp')))

# 检查源文件是否存在，过滤掉不存在的文件
filtered_src_files = []
for src_file in src_files:
    if os.path.exists(src_file):
        filtered_src_files.append(src_file)
    else:
        print(f"警告: 源文件不存在，已跳过: {src_file}")

# 编译所有源文件 - 使用SCons的标准方式，一次性编译所有源文件
print(f"开始编译 {len(filtered_src_files)} 个源文件...")
try:
    objects = env.Object(filtered_src_files)
    print(f"✅ 编译成功: 所有 {len(filtered_src_files)} 个源文件")
except Exception as e:
    print(f"❌ 编译失败: {str(e)}")
    # 如果批量编译失败，尝试逐个编译
    print("尝试逐个编译源文件...")
    objects = []
    for src_file in filtered_src_files:
        try:
            obj = env.Object(src_file)
            objects.append(obj)
            print(f"  编译成功: {os.path.basename(src_file)}")
        except Exception as e2:
            print(f"❌ 编译失败: {os.path.basename(src_file)} - {str(e2)}")

# 处理资源文件 - 使用资源编译器编译.rc文件
rc_objects = []
rc_files = [
    os.path.join(src_dir, 'Notepad_plus.rc'),
    os.path.join(src_dir, 'ScintillaComponent', 'FindReplaceDlg.rc'),
    os.path.join(src_dir, 'ScintillaComponent', 'UserDefineDialog.rc'),
    os.path.join(src_dir, 'ScintillaComponent', 'columnEditor.rc'),
    os.path.join(src_dir, 'WinControls', 'DockingWnd', 'DockingGUIWidget.rc'),
    os.path.join(src_dir, 'WinControls', 'FunctionList', 'functionListPanel.rc'),
    os.path.join(src_dir, 'WinControls', 'Preference', 'preference.rc'),
    os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher', 'VerticalFileSwitcher.rc'),
    os.path.join(src_dir, 'WinControls', 'WindowsDlg', 'WindowsDlg.rc'),
    os.path.join(src_dir, 'WinControls', 'shortcut', 'RunMacroDlg.rc'),
    os.path.join(src_dir, 'WinControls', 'shortcut', 'shortcut.rc'),
    os.path.join(src_dir, 'WinControls', 'StaticDialog', 'RunDlg', 'RunDlg.rc'),
    os.path.join(src_dir, 'WinControls', 'PluginsAdmin', 'pluginsAdmin.rc'),
    os.path.join(src_dir, 'WinControls', 'TaskList', 'TaskListDlg.rc'),
    os.path.join(src_dir, 'WinControls', 'ProjectPanel', 'ProjectPanel.rc'),
    os.path.join(src_dir, 'WinControls', 'FindCharsInRange', 'findCharsInRange.rc'),
    os.path.join(src_dir, 'WinControls', 'FileBrowser', 'fileBrowser.rc'),
    os.path.join(src_dir, 'WinControls', 'Grid', 'ShortcutMapper.rc'),
    os.path.join(src_dir, 'WinControls', 'DocumentMap', 'documentMap.rc'),
    os.path.join(src_dir, 'WinControls', 'DocumentMap', 'documentSnapshot.rc'),
    os.path.join(src_dir, 'WinControls', 'AnsiCharPanel', 'ansiCharPanel.rc'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'ColourPopup.rc'),
    os.path.join(src_dir, 'WinControls', 'ColourPicker', 'WordStyleDlg.rc'),
    os.path.join(src_dir, 'WinControls', 'ClipboardHistory', 'clipboardHistoryPanel.rc'),
    os.path.join(src_dir, 'WinControls', 'TomatoTimer', 'TomatoTimer.rc'),
    os.path.join(src_dir, 'MISC', 'RegExt', 'regExtDlg.rc'),
    os.path.join(src_dir, 'MISC', 'md5', 'md5Dlgs.rc'),
]

print("处理资源文件...")
print(f"资源编译器: {env.get('RC', '未设置')}")
print(f"资源编译器标志: {env.get('RCFLAGS', [])}")
print(f"资源编译命令: {env.get('RCCOM', '未设置')}")

for rc_file in rc_files:
    if os.path.exists(rc_file):
        print(f"  编译资源文件: {os.path.basename(rc_file)}")
        # 使用资源编译器处理
        rc_obj = env.RES(rc_file)
        rc_objects.append(rc_obj)
        print(f"  ✅ 资源文件处理成功: {os.path.basename(rc_file)}")
    else:
        print(f"❌ 错误: 资源文件不存在: {rc_file}")
        sys.exit(1)

# 调试：检查预编译库变量的类型和值
print(f"调试 - lexilla_lib 类型: {type(lexilla_lib)}")
print(f"调试 - scintilla_lib 类型: {type(scintilla_lib)}")

# 添加预编译库到链接器 - 确保使用正确的预编译库文件
if isinstance(lexilla_lib, str) and isinstance(scintilla_lib, str):
    # 如果预编译库是文件路径，直接添加到链接器
    print(f"✅ 使用预编译库: {os.path.basename(lexilla_lib)}")
    print(f"✅ 使用预编译库: {os.path.basename(scintilla_lib)}")
    
    # 注意：不再使用env.Append(LIBPATH)来避免触发默认链接器命令生成器
    # 库目录路径将在自定义链接器命令生成器中处理
    print("✅ 跳过标准LIBPATH添加方式，避免触发默认链接器行为")
    
    # 对于Clang编译器，直接使用库文件路径，而不是通过LIBS变量
    # 这可以避免SCons自动添加-l前缀
    print("✅ 使用直接库文件路径进行链接")
    
    # 检查是否已经存在/OPT:REF和/OPT:ICF选项，避免重复添加
    current_linkflags = env.get('LINKFLAGS', [])
    existing_opt_ref = [flag for flag in current_linkflags if '/OPT:REF' in flag]
    existing_opt_icf = [flag for flag in current_linkflags if '/OPT:ICF' in flag]
    
    # 只有在不存在时才添加这些选项
    if not existing_opt_ref:
        env.Append(LINKFLAGS=['/OPT:REF'])  # 删除未引用的函数和数据
    if not existing_opt_icf:
        env.Append(LINKFLAGS=['/OPT:ICF'])   # 执行相同COMDAT折叠
    
    # 注意：由于已经移除了SCI_OWNREGEX宏定义，CreateRegexSearch符号只在libscintilla.a中定义
    # 不再需要符号排除选项，避免重复添加
    print("✅ 符号重复定义问题已通过移除SCI_OWNREGEX宏解决")
else:
    # 如果预编译库是SCons对象，使用标准方式链接
    print("⚠️ 使用SCons静态库对象进行链接")
    # 注意：这里只添加一次，避免重复添加
    # 重要：这里不再使用env.Append(LIBS=...)来避免添加Visual Studio运行时库
    print("✅ 跳过标准库添加方式，避免Visual Studio运行时库问题")

# 构建主程序 - 直接输出到bin目录
start_time = datetime.now()
print(f"开始构建 {target_name} ({build_type} {target_arch})...")
print(f"构建开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 合并所有对象文件
all_objects = objects + rc_objects
print(f"总对象文件数: {len(all_objects)}")

# 对于预编译库，使用自定义链接器命令生成器
# 确保正确处理.a文件而不是.lib文件
if isinstance(lexilla_lib, str) and isinstance(scintilla_lib, str):
    # 注意：库文件已经在前面添加过了，这里不再重复添加
    print(f"✅ 使用自定义链接器命令生成器")
    print(f"✅ 预编译库: {os.path.basename(lexilla_lib)}, {os.path.basename(scintilla_lib)}")
    
    # 强制使用自定义链接器命令生成器
    # 确保链接器命令正确生成，避免自动添加-l前缀
    print("✅ 强制使用自定义链接器命令生成器")
    
    # 创建链接器响应文件
    rsp_file_path = os.path.join(bin_dir, 'linker.rsp')
    print(f"🔧 创建链接器响应文件: {rsp_file_path}")
    
    # 使用导入的系统库列表
    print(f"🔧 调试: 系统库列表包含 {len(libs)} 个库")
    
    with open(rsp_file_path, 'w', encoding='utf-8') as f:
        # 添加所有对象文件
        for obj in all_objects:
            obj_path = str(obj)
            # 添加对象文件（.o或.obj）和资源文件（.res）
            if obj_path.endswith('.o') or obj_path.endswith('.obj') or obj_path.endswith('.res'):
                f.write(f'"{obj_path}"\n')
                print(f"  添加文件: {os.path.basename(obj_path)}")
        
        # 显式添加所有.res文件（确保资源文件被包含）
        print("🔧 显式添加所有.res文件到响应文件...")
        for rc_file in rc_files:
            if os.path.exists(rc_file):
                # 计算对应的.res文件路径
                res_file = os.path.splitext(rc_file)[0] + '.res'
                if os.path.exists(res_file):
                    f.write(f'"{res_file}"\n')
                    print(f"  添加资源文件: {os.path.basename(res_file)}")
                else:
                    print(f"  ⚠️ 资源文件不存在: {res_file}")
        
        # 添加预编译库文件
        f.write(f'"{lexilla_lib}"\n')
        f.write(f'"{scintilla_lib}"\n')
        
        # 添加系统库
        for lib in libs:
            if isinstance(lib, str):
                f.write(f'{lib}\n')
                print(f"  添加系统库: {lib}")
    
    print(f"✅ 响应文件已创建，包含 {len(all_objects)} 个对象文件和 {len(libs)} 个系统库")

# 构建程序
program = env.Program(target=os.path.join(bin_dir, target_name), source=all_objects)

# 添加后构建操作 - 复制配置文件
config_files = [
    os.path.join(src_dir, 'contextMenu.xml'),
    os.path.join(src_dir, 'langs.model.xml'),
    os.path.join(src_dir, 'shortcuts.xml'),
    os.path.join(src_dir, 'stylers.model.xml'),
]

def copy_config_files(target, source, env):
    """复制配置与本地化文件到输出目录"""
    print("复制配置文件到bin目录...")
    for config_file in config_files:
        if os.path.exists(config_file):
            dest_file = os.path.join(bin_dir, os.path.basename(config_file))
            import shutil
            shutil.copy2(config_file, dest_file)
            print(f"  复制成功: {os.path.basename(config_file)}")
        else:
            print(f"  警告: 配置文件不存在: {config_file}")
    # 复制本地化语言XML到 bin\\localization
    localization_src_dir = os.path.join(project_root, 'PowerEditor', 'installer', 'nativeLang')
    localization_dest_dir = os.path.join(bin_dir, 'localization')
    try:
        if os.path.isdir(localization_src_dir):
            os.makedirs(localization_dest_dir, exist_ok=True)
            import glob
            import shutil
            xml_list = glob.glob(os.path.join(localization_src_dir, '*.xml'))
            if xml_list:
                for xml_path in xml_list:
                    dest_xml = os.path.join(localization_dest_dir, os.path.basename(xml_path))
                    shutil.copy2(xml_path, dest_xml)
                print(f"  本地化语言文件已复制: {len(xml_list)} 个 -> {localization_dest_dir}")
            else:
                print("  警告: 未在installer\\nativeLang中找到任何XML语言文件")
        else:
            print(f"  警告: 本地化源目录不存在: {localization_src_dir}")
    except Exception as e:
        print(f"  错误: 复制本地化文件失败: {e}")

# 添加后构建操作
env.AddPostAction(program, copy_config_files)

# 显示构建完成信息
def print_build_info(target, source, env):
    """打印构建完成信息"""
    end_time = datetime.now()
    print(f"\n构建完成: {target[0].path}")
    print(f"构建类型: {build_type}")
    print(f"目标架构: {target_arch}")
    print(f"构建开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"构建结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总构建时间: {(end_time - start_time).total_seconds():.2f} 秒")
    
    # 播放语音提示
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say("任务运行完毕，过来看看！")
        engine.runAndWait()
    except Exception as e:
        print(f"无法播放语音提示: {e}")

# 添加后构建操作
env.AddPostAction(program, print_build_info)

# 返回构建目标
Return('program')
