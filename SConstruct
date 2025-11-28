# -*- coding: utf-8 -*-
"""
Notepad++ SCons构建脚本
基于CMakeLists.txt的改进版本
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# 强制Python使用UTF-8编码
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 设置UTF-8编码环境
if sys.platform == 'win32':
    # 设置系统代码页为UTF-8
    os.system('chcp 65001 > nul')
    # 设置Windows环境变量以支持UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# 在构建开始时终止可能正在运行的notepad_abc进程
def kill_running_processes():
    """终止正在运行的notepad_abc进程"""
    print("检查并终止正在运行的notepad_abc进程...")
    try:
        # 首先尝试使用taskkill命令终止进程
        result = subprocess.run(['taskkill', '/f', '/im', 'notepad_abc.exe'], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("成功终止正在运行的notepad_abc进程")
        else:
            # 如果没有找到进程，这不是错误
            if "notepad_abc.exe" in result.stderr:
                print("没有发现正在运行的notepad_abc进程")
            else:
                print(f"终止进程时出现警告: {result.stderr}")
    except Exception as e:
        print(f"终止进程时出错: {str(e)}")
        
    # 添加额外的检查，确保进程确实被终止
    try:
        # 等待一段时间确保进程被完全终止
        time.sleep(1)
        
        # 再次检查是否还有进程在运行
        check_result = subprocess.run(['tasklist', '/fi', 'imagename eq notepad_abc.exe'], 
                                    capture_output=True, text=True, encoding='utf-8')
        if 'notepad_abc.exe' in check_result.stdout and 'No tasks are running' not in check_result.stdout:
            print("警告: 仍有notepad_abc进程在运行，尝试强制终止...")
            # 使用更强的终止方式
            subprocess.run(['taskkill', '/f', '/t', '/im', 'notepad_abc.exe'], 
                         capture_output=True, text=True, encoding='utf-8')
            time.sleep(2)  # 等待更长时间
            
            # 最后再检查一次
            final_check = subprocess.run(['tasklist', '/fi', 'imagename eq notepad_abc.exe'], 
                                       capture_output=True, text=True, encoding='utf-8')
            if 'notepad_abc.exe' in final_check.stdout and 'No tasks are running' not in final_check.stdout:
                print("警告: 仍然无法终止notepad_abc进程")
            else:
                print("成功终止所有notepad_abc进程")
        else:
            print("确认没有notepad_abc进程在运行")
    except Exception as e:
        print(f"检查进程状态时出错: {str(e)}")

# 调用函数终止进程
kill_running_processes()

# 显示开始时间
print("开始构建时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 设置项目路径（使用标准的Python方式）
project_root = os.path.abspath('.')

# 导入SCons标准函数
import SCons.Environment

# 获取环境变量
env = SCons.Environment.Environment()

# 设置基本环境变量
env['TARGET_ARCH'] = 'x86_64'  # 默认为64位
env['MSVC_VERSION'] = '14.3'   # VS2022
env['MSVS_VERSION'] = '2022'
src_dir = os.path.join(project_root, 'PowerEditor', 'src')
scintilla_dir = os.path.join(project_root, 'scintilla')
lexilla_dir = os.path.join(project_root, 'lexilla')
bin_dir = os.path.join(project_root, 'bin')
obj_dir = os.path.join(project_root, 'obj')

# 确保输出目录存在
if not os.path.exists(bin_dir):
    os.makedirs(bin_dir)
if not os.path.exists(obj_dir):
    os.makedirs(obj_dir)

# 设置构建选项
def configure_build_options(env, build_type='Release'):
    """配置构建选项 - 基于Visual Studio配置"""
    # 基本编译器设置 - 基于Visual Studio v143工具集
    env.Append(CCFLAGS=[
        '/std:c++17',          # C++17标准，匹配Visual Studio配置
        '/Zc:__cplusplus',     # 正确的__cplusplus宏
        '/utf-8',              # 设置UTF-8编码（包含源文件字符集）
        '/Zc:strictStrings',   # 严格字符串处理
        '/w15262',             # 启用特定警告
        '/MP',                 # 多处理器编译
        '/GR',                 # 启用RTTI
        '/EHa',                # 异常处理，支持SEH
        '/W4',                 # 高警告级别，与Visual Studio一致
        '/FS',                 # 解决PDB文件冲突问题
    ])
    
    # 预处理器定义 - 基于CMakeLists.txt
    defines = [
        'WIN32',
        '_WINDOWS',
        'UNICODE',
        '_UNICODE',
        '_WIN32_WINNT=_WIN32_WINNT_WIN7',
        'NTDDI_VERSION=NTDDI_WIN7',
        'OEMRESOURCE',
        'NOMINMAX',
        '_USE_64BIT_TIME_T',
        'TIXML_USE_STL',
        'TIXMLA_USE_STL',
        '_CRT_NONSTDC_NO_DEPRECATE',
        '_CRT_SECURE_NO_WARNINGS',
        '_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING',  # 添加CMakeLists.txt中的定义
        # 尝试禁用某些COM功能以避免comsuppw.lib依赖
        '_ATL_DISABLE_NO_VTABLE',
    ]
    
    # 禁用特定警告
    env.Append(CCFLAGS=['/wd4456', '/wd4457', '/wd4459'])
    
    # 包含目录 - 基于CMakeLists.txt
    include_dirs = [
        src_dir,
        os.path.join(src_dir, 'MISC'),
        os.path.join(src_dir, 'MISC', 'Common'),
        os.path.join(src_dir, 'MISC', 'Exception'),
        os.path.join(src_dir, 'MISC', 'PluginsManager'),
        os.path.join(src_dir, 'MISC', 'Process'),
        os.path.join(src_dir, 'MISC', 'RegExt'),
        os.path.join(src_dir, 'MISC', 'md5'),
        os.path.join(src_dir, 'MISC', 'sha1'),
        os.path.join(src_dir, 'MISC', 'sha2'),
        os.path.join(src_dir, 'MISC', 'sha512'),
        os.path.join(src_dir, 'ScintillaComponent'),
        os.path.join(src_dir, 'WinControls'),
        os.path.join(src_dir, 'WinControls', 'AboutDlg'),
        os.path.join(src_dir, 'WinControls', 'AnsiCharPanel'),
        os.path.join(src_dir, 'WinControls', 'ClipboardHistory'),
        os.path.join(src_dir, 'WinControls', 'ColourPicker'),
        os.path.join(src_dir, 'WinControls', 'ContextMenu'),
        os.path.join(src_dir, 'WinControls', 'DockingWnd'),
        os.path.join(src_dir, 'WinControls', 'DocumentMap'),
        os.path.join(src_dir, 'WinControls', 'FileBrowser'),
        os.path.join(src_dir, 'WinControls', 'FindCharsInRange'),
        os.path.join(src_dir, 'WinControls', 'FunctionList'),
        os.path.join(src_dir, 'WinControls', 'Grid'),
        os.path.join(src_dir, 'WinControls', 'ImageListSet'),
        os.path.join(src_dir, 'WinControls', 'OpenSaveFileDialog'),
        os.path.join(src_dir, 'WinControls', 'PluginsAdmin'),
        os.path.join(src_dir, 'WinControls', 'Preference'),
        os.path.join(src_dir, 'WinControls', 'ProjectPanel'),
        os.path.join(src_dir, 'WinControls', 'ReadDirectoryChanges'),
        os.path.join(src_dir, 'WinControls', 'shortcut'),
        os.path.join(src_dir, 'WinControls', 'SplitterContainer'),
        os.path.join(src_dir, 'WinControls', 'StaticDialog'),
        os.path.join(src_dir, 'WinControls', 'StaticDialog', 'RunDlg'),
        os.path.join(src_dir, 'WinControls', 'StatusBar'),
        os.path.join(src_dir, 'WinControls', 'TabBar'),
        os.path.join(src_dir, 'WinControls', 'TaskList'),
        os.path.join(src_dir, 'WinControls', 'ToolBar'),
        os.path.join(src_dir, 'WinControls', 'ToolTip'),
        os.path.join(src_dir, 'WinControls', 'TrayIcon'),
        os.path.join(src_dir, 'WinControls', 'TreeView'),
        os.path.join(src_dir, 'WinControls', 'VerticalFileSwitcher'),
        os.path.join(src_dir, 'WinControls', 'WindowsDlg'),
        os.path.join(src_dir, 'TinyXml'),
        os.path.join(src_dir, 'TinyXml', 'tinyXmlA'),
        os.path.join(src_dir, 'uchardet'),
        os.path.join(src_dir, 'json'),
        os.path.join(lexilla_dir, 'include'),
        os.path.join(scintilla_dir, 'include'),
    ]
    
    # 根据构建类型设置选项 - 基于CMakeLists.txt
    if build_type == 'Debug':
        defines.append('_DEBUG')
        env.Append(CCFLAGS=['/Od', '/Zi'])  # 禁用优化，启用调试信息
        env.Append(LINKFLAGS=['/DEBUG'])    # 链接调试信息
        env.Append(CCFLAGS=['/RTC1'])       # 运行时检查
        env.Append(CPPDEFINES=['_DEBUG'])
        env.Append(CCFLAGS=['/MDd'])        # 多线程调试动态库，与Scintilla库匹配
    else:  # Release
        defines.append('NDEBUG')
        env.Append(CCFLAGS=['/O2', '/GL'])  # 最大优化，全程序优化
        env.Append(LINKFLAGS=['/LTCG', '/OPT:REF', '/OPT:ICF'])  # 链接时优化
        env.Append(CCFLAGS=['/Gw', '/GA'])  # 优化
        env.Append(CPPDEFINES=['NDEBUG'])
        env.Append(CCFLAGS=['/MD'])         # 多线程动态库，与Scintilla库匹配
    
    # 应用定义和包含目录
    env.Append(CPPDEFINES=defines)
    env.Append(CPPPATH=include_dirs)
    
    return env

# 配置链接选项 - 基于CMakeLists.txt
def configure_link_options(env, subsystem='WINDOWS'):
    """配置链接选项
    Args:
        env: SCons环境对象
        subsystem: 子系统类型，'WINDOWS' 或 'CONSOLE'
    """
    # 链接库 - 基于Visual Studio项目文件的完整依赖链
    # 注意：oleaut32.lib必须在comsuppw.lib之前链接，以正确解析依赖关系
    libs = [
        'comctl32.lib',           # 通用控件库
        'shlwapi.lib',            # Shell轻量级API
        'shell32.lib',            # Shell API
        'dbghelp.lib',            # 调试帮助库
        'version.lib',            # 版本信息库
        'crypt32.lib',            # 加密库
        'wintrust.lib',           # Windows信任库
        'sensapi.lib',            # 传感器API
        'wininet.lib',            # Windows Internet API
        'imm32.lib',              # 输入法管理器
        'msimg32.lib',            # Microsoft图像库
        'uxtheme.lib',            # Windows主题库
        'dwmapi.lib',             # 桌面窗口管理器API
        'comdlg32.lib',           # 通用对话框库
        'gdi32.lib',              # 图形设备接口
        'user32.lib',             # 用户界面库
        'kernel32.lib',           # 内核库
        'ole32.lib',              # OLE基础库
        'oleaut32.lib',           # OLE自动化库（关键：解决序数381错误）
        'advapi32.lib',           # 高级API库
        'uuid.lib',               # UUID库（添加缺失的依赖）
        'odbc32.lib',             # ODBC库（添加缺失的依赖）
        'odbccp32.lib',           # ODBC安装程序库（添加缺失的依赖）
        'comsuppw.lib',           # COM支持库（关键：解决GetErrorInfo等符号）
        # 标准C/ C++运行时库（保持 /MD 风格）
        'ucrt.lib',
        'vcruntime.lib',
        'msvcrt.lib',
        'msvcprt.lib',
        'libscintilla.lib',       # Scintilla库
        'liblexilla.lib',         # Lexilla库
    ]
    
    # 库目录 - 添加系统库目录，确保链接器能找到所有依赖库
    lib_dirs = [
        bin_dir,                    # 添加bin目录，包含libscintilla.lib和liblexilla.lib
        os.path.join(scintilla_dir, 'bin'),
        obj_dir,
        # 添加Windows SDK库目录，确保能找到系统库
        os.path.join(os.environ.get('WindowsSdkDir', 'C:\\Program Files\\Windows Kits\\10\\Lib\\10.0.22621.0\\um\\x64')),
        os.path.join(os.environ.get('VCToolsInstallDir', 'C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.39.33519\\lib\\x64')),
    ]
    
    # 根据子系统类型设置SUBSYSTEM链接标志
    if subsystem.upper() == 'CONSOLE':
        subsystem_flag = '/SUBSYSTEM:CONSOLE,6.00'  # 控制台子系统，显示控制台窗口
        # 控制台版本需要使用wWinMain作为入口点，否则链接器会寻找main函数
        # 注意：/ENTRY必须放在/SUBSYSTEM之前才能生效
        entry_point_flag = '/ENTRY:wWinMain'
    else:
        subsystem_flag = '/SUBSYSTEM:WINDOWS,6.00'  # Windows子系统，只显示图形界面
        entry_point_flag = None  # Windows版本默认使用wWinMain，不需要显式指定
    
    # 链接标志 - 基于Visual Studio项目文件的完整链接器选项
    linkflags = []
    
    # 如果是控制台版本，先添加入口点选项（必须在SUBSYSTEM之前）
    if entry_point_flag:
        linkflags.append(entry_point_flag)
    
    # 添加子系统标志
    linkflags.append(subsystem_flag)
    
    # 继续添加其他链接标志
    linkflags.extend([
        '/VERSION:1.0',
        '/DYNAMICBASE',              # 启用ASLR
        '/NXCOMPAT',                 # 启用数据执行保护
        '/LARGEADDRESSAWARE',        # 启用大地址感知
        '/MANIFEST',                 # 启用清单文件
        '/manifest:embed',           # 嵌入清单
        '/manifestinput:' + os.path.join(src_dir, 'notepad_abc.exe.manifest'),  # 清单输入文件（已包含DPI和UAC设置）
        '/DEBUG',                    # 调试信息
        '/PDB:notepadPlus.pdb',      # PDB文件
        '/TLBOUT:/TLBID',            # 类型库输出
        '/TLBID:5',                  # 类型库ID
        '/FIXED:NO',                 # 不固定基址
        '/IMPLIB:notepad_abc.lib',   # 导入库
        '/MACHINE:X64',              # 目标机器架构
        '/CETCOMPAT:NO',             # CET兼容性
    ])
    
    # 应用链接设置
    env.Append(LIBS=libs)
    env.Append(LIBPATH=lib_dirs)
    env.Append(LINKFLAGS=linkflags)
    
    return env

# 构建依赖库函数
def build_dependencies(env, build_type):
    """构建Lexilla和Scintilla依赖库 - 基于Visual Studio配置"""
    
    print(f"开始构建依赖库 ({build_type})...")
    
    # 创建依赖库构建环境
    deps_env = env.Clone()
    
    # 配置依赖库构建选项
    deps_env = configure_build_options(deps_env, build_type)
    
    # Lexilla库构建
    lexilla_src_files = [
        os.path.join(lexilla_dir, 'src', 'Lexilla.cxx'),
        os.path.join(lexilla_dir, 'lexers', '*.cxx'),
        os.path.join(lexilla_dir, 'lexlib', '*.cxx'),
    ]
    
    # 展开通配符
    lexilla_sources = []
    for pattern in lexilla_src_files:
        import glob
        lexilla_sources.extend(glob.glob(pattern))
    
    # Lexilla包含目录
    lexilla_includes = [
        os.path.join(lexilla_dir, 'include'),
        os.path.join(scintilla_dir, 'include'),
        os.path.join(lexilla_dir, 'lexlib'),
    ]
    
    # Lexilla预处理器定义
    lexilla_defines = [
        '_CRT_SECURE_NO_DEPRECATE',
        '_USRDLL',
        'WIN32',
        '_WINDOWS',
    ]
    
    deps_env.Append(CPPPATH=lexilla_includes)
    deps_env.Append(CPPDEFINES=lexilla_defines)
    
    # 构建Lexilla静态库
    lexilla_lib = deps_env.StaticLibrary(
        target='liblexilla',
        source=lexilla_sources
    )
    
    # Scintilla库构建
    scintilla_src_files = [
        os.path.join(scintilla_dir, 'src', '*.cxx'),
        os.path.join(scintilla_dir, 'win32', '*.cxx'),
        os.path.join(project_root, 'boostregex', '*.cxx'),
    ]
    
    # 展开通配符
    scintilla_sources = []
    for pattern in scintilla_src_files:
        import glob
        scintilla_sources.extend(glob.glob(pattern))
    
    # Scintilla包含目录
    scintilla_includes = [
        os.path.join(scintilla_dir, 'include'),
        os.path.join(scintilla_dir, 'src'),
        os.path.join(project_root, 'boostregex'),
    ]
    
    # Scintilla预处理器定义
    scintilla_defines = [
        '_CRT_SECURE_NO_DEPRECATE',
        '_USRDLL',
        'BOOST_REGEX_STANDALONE',
        'SCI_OWNREGEX',
        'SCI_NAMESPACE',
        'WIN32',
        '_WINDOWS',
    ]
    
    deps_env.Append(CPPPATH=scintilla_includes)
    deps_env.Append(CPPDEFINES=scintilla_defines)
    
    # 构建Scintilla静态库
    scintilla_lib = deps_env.StaticLibrary(
        target='libscintilla',
        source=scintilla_sources
    )
    
    print("依赖库构建完成")
    return lexilla_lib, scintilla_lib

# 获取构建类型（从命令行参数或环境变量）
build_type = 'Release'  # 默认为Release构建
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg.startswith('--build='):
            build_type = arg.split('=', 1)[1]
        elif arg == '--debug':
            build_type = 'Debug'

# 构建依赖库
lexilla_lib, scintilla_lib = build_dependencies(env, build_type)

# 导出函数供子脚本使用
Export('project_root', 'src_dir', 'scintilla_dir', 'lexilla_dir', 'bin_dir', 'obj_dir')
Export('configure_build_options', 'configure_link_options')

# 构建主程序
SConscript('SConscript', variant_dir=obj_dir, duplicate=0)

# 显示结束时间
print("构建脚本准备完毕:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 确保终端输出使用UTF-8
def ensure_utf8_print(text):
    """确保文本以UTF-8格式输出到终端"""
    print(text.encode('utf-8').decode('utf-8'))

# 测试中文输出
ensure_utf8_print("\n=== 编码测试: 中文显示正常 ===")