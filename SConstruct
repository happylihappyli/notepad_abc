# -*- coding: utf-8 -*-
"""
Notepad++ SCons构建脚本
基于CMakeLists.txt的改进版本
"""

import os
import sys
import time
import subprocess
import glob
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

# 注意：不再设置Visual Studio环境变量，使用纯Clang构建环境
print("使用纯Clang构建环境，不依赖Visual Studio...")

# 导入SCons标准函数
import SCons.Environment
from SCons.Script import ARGUMENTS, Export, SConscript, Environment

# 强制使用Clang编译器
print("配置使用Clang编译器...")

# 配置资源文件构建器（RES构建器）
def configure_resource_builder(env):
    """配置资源文件构建器，用于处理.rc文件"""
    print("配置资源文件构建器...")
    
    # 检查windres工具是否存在
    windres_paths = [
        r"C:\Program Files\LLVM\bin\llvm-rc.exe",  # LLVM的资源编译器
        r"C:\Program Files\LLVM\bin\windres.exe",  # MinGW的资源编译器
        r"C:\msys64\mingw64\bin\windres.exe",     # MSYS2的MinGW资源编译器
    ]
    
    rc_compiler = None
    
    for rc_exe in windres_paths:
        if os.path.exists(rc_exe):
            rc_compiler = rc_exe
            print(f"✅ 找到资源编译器: {rc_exe}")
            break
    
    # 如果找不到专门的资源编译器，尝试使用clang作为资源编译器
    if rc_compiler is None:
        clang_path = r"C:\Program Files\LLVM\bin\clang.exe"
        if os.path.exists(clang_path):
            rc_compiler = clang_path
            print(f"✅ 使用Clang作为资源编译器: {clang_path}")
        else:
            print("⚠️ 警告: 未找到资源编译器，将尝试使用默认设置")
    
    # 创建RES构建器
    if rc_compiler:
        # 使用找到的资源编译器
        env['RC'] = rc_compiler
        # 简化参数格式，避免复杂的命令行参数
        
        # 检查是否是LLVM资源编译器
        if 'llvm-rc' in rc_compiler:
            # LLVM的llvm-rc.exe实际上接受Windows风格的参数格式
            env['RCFLAGS'] = ['/C', '65001']
            env['RCCOM'] = '"$RC" $RCFLAGS /fo "$TARGET" "$SOURCES"'
        elif 'windres' in rc_compiler:
            # GNU风格的windres使用不同的参数格式
            env['RCFLAGS'] = ['--codepage=65001']
            env['RCCOM'] = '"$RC" "$SOURCES" -o "$TARGET" $RCFLAGS'
        else:
            # 使用Windows风格的参数格式（/FO而不是-o）
            env['RCFLAGS'] = ['/C', '65001']
            env['RCCOM'] = '"$RC" $RCFLAGS /FO "$TARGET" "$SOURCES"'
    else:
        # 使用默认的资源编译器设置
        env['RC'] = 'rc'
        env['RCFLAGS'] = []
        env['RCCOM'] = '"$RC" $RCFLAGS /fo "$TARGET" "$SOURCES"'
    
    # 创建RES构建器
    res_builder = SCons.Builder.Builder(
        action='$RCCOM',
        suffix='.res',
        src_suffix='.rc'
    )
    
    # 将RES构建器添加到环境中
    env.Append(BUILDERS={'RES': res_builder})
    print("✅ 资源文件构建器配置完成")
    return env

# 检查Clang编译器可用性
def check_clang_compiler():
    """检查Clang编译器是否可用"""
    # 已知的Clang编译器路径
    known_clang_paths = [
        r"C:\Program Files\LLVM\bin",  # 用户提供的路径
        r"C:\LLVM\bin",
        r"C:\msys64\clang64\bin",
    ]
    
    # 首先检查已知路径
    for clang_dir in known_clang_paths:
        clang_exe = os.path.join(clang_dir, 'clang.exe')
        if os.path.exists(clang_exe):
            print(f"✅ 在已知路径找到Clang编译器: {clang_exe}")
            
            # 尝试运行clang --version
            try:
                result = subprocess.run([clang_exe, '--version'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"Clang版本信息: {result.stdout.splitlines()[0]}")
                    
                    # 将Clang路径添加到PATH环境变量
                    os.environ['PATH'] = clang_dir + ';' + os.environ.get('PATH', '')
                    print(f"✅ 已将Clang路径添加到PATH: {clang_dir}")
                    return True
                else:
                    print(f"❌ Clang版本检查失败: {result.stderr}")
            except Exception as e:
                print(f"❌ 检查Clang版本时出错: {e}")
    
    # 如果已知路径未找到，尝试使用where命令查找clang
    try:
        where_result = subprocess.run(['where', 'clang'], capture_output=True, text=True, timeout=5)
        
        if where_result.returncode == 0 and where_result.stdout.strip():
            clang_path = where_result.stdout.strip().split('\n')[0]
            print(f"✅ 在PATH中找到Clang编译器: {clang_path}")
            
            # 尝试运行clang --version
            result = subprocess.run([clang_path, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"Clang版本信息: {result.stdout.splitlines()[0]}")
                return True
            else:
                print(f"❌ Clang版本检查失败: {result.stderr}")
                return False
        else:
            print("❌ 系统中未找到Clang编译器")
            print("请确保Clang编译器已安装，或检查PATH环境变量设置")
            return False
    except Exception as e:
        print(f"❌ 检查Clang编译器时出错: {e}")
        return False

# 直接检查Clang编译器路径
def direct_check_clang():
    """直接检查Clang编译器是否可用"""
    clang_path = r"C:\Program Files\LLVM\bin"
    clang_exe = os.path.join(clang_path, 'clang.exe')
    
    if os.path.exists(clang_exe):
        print(f"✅ 直接找到Clang编译器: {clang_exe}")
        
        # 尝试运行clang --version
        try:
            result = subprocess.run([clang_exe, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"Clang版本信息: {result.stdout.splitlines()[0]}")
                
                # 将Clang路径添加到PATH环境变量
                os.environ['PATH'] = clang_path + ';' + os.environ.get('PATH', '')
                print(f"✅ 已将Clang路径添加到PATH: {clang_path}")
                return True
            else:
                print(f"❌ Clang版本检查失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 检查Clang版本时出错: {e}")
    
    return False

# 检查当前使用的编译器类型
def get_compiler_type(env):
    """获取当前使用的编译器类型"""
    cxx = env.get('CXX', '')
    if 'clang' in cxx.lower() or 'clang++' in cxx.lower():
        return 'clang'
    else:
        return 'unknown'  # 只支持Clang编译器

# 强制使用Clang编译器
using_clang = True

# 检查Clang编译器可用性
if not direct_check_clang():
    print("❌ Clang编译器检查失败，但强制使用Clang，继续构建...")
else:
    print("✅ Clang编译器检查通过")

# 创建构建环境（使用默认工具链，稍后会覆盖编译器设置）
env = Environment(ENV=os.environ.copy())

# 添加Clang路径到PATH环境变量
clang_path = r"C:\Program Files\LLVM\bin"
env.PrependENVPath('PATH', clang_path)

# 强制设置编译器类型为clang，使用完整路径
# 使用更安全的方式设置编译器路径，避免空格问题
clang_cxx = os.path.join(clang_path, 'clang++.exe')
clang_cc = os.path.join(clang_path, 'clang.exe')
clang_link = os.path.join(clang_path, 'lld-link.exe')
clang_ar = os.path.join(clang_path, 'llvm-ar.exe')

env['CXX'] = clang_cxx
env['CC'] = clang_cc
env['LINK'] = clang_link
env['AR'] = clang_ar

# 手动配置工具链，避免SCons生成MSVC风格参数
# 设置编译器和链接器命令生成器
def generate_clang_command(source, target, env, for_signature):
    """生成Clang编译器命令"""
    cmd = [clang_cxx]
    
    # 添加编译选项
    for flag in env.get('CCFLAGS', []):
        cmd.append(flag)
    
    # 添加包含路径
    for include in env.get('CPPPATH', []):
        cmd.extend(['-I', include])
    
    # 添加预处理器定义
    for define in env.get('CPPDEFINES', []):
        if isinstance(define, tuple):
            cmd.append(f"-D{define[0]}={define[1]}")
        else:
            cmd.append(f"-D{define}")
    
    # 添加源文件和目标文件
    cmd.extend(['-c', str(source[0]), '-o', str(target[0])])
    
    return cmd

def generate_link_command(target, source, env, for_signature=False):
    """生成Clang链接器命令 - 直接使用lld-link.exe"""
    
    import sys
    import os
    
    print("🔧 [DEBUG] generate_link_command函数开始执行！", file=sys.stderr)
    
    # 如果是签名模式，返回简化命令用于依赖检查
    if for_signature:
        # 使用双引号包围路径以正确处理空格
        cmd = ['"' + clang_link + '"']  # 使用lld-link作为链接器
        cmd.extend([str(s) for s in source])
        cmd.extend(['-out:' + str(target[0])])
        return ' '.join(cmd)
    
    # 正常执行模式
    print(" [DEBUG] generate_link_command被调用！", file=sys.stderr)
    print(f"🚀 [DEBUG] 目标: {str(target[0])}", file=sys.stderr)
    print(f" [DEBUG] 源文件数量: {len(source)}", file=sys.stderr)
    print(f" [DEBUG] LIBS: {env.get('LIBS', [])}", file=sys.stderr)
    print(f"🚀 [DEBUG] LINKFLAGS: {env.get('LINKFLAGS', [])}", file=sys.stderr)
    print(f" [DEBUG] LIBPATH: {env.get('LIBPATH', [])}", file=sys.stderr)
    
    # 直接使用lld-link.exe作为链接器，使用双引号包围路径以正确处理空格
    cmd = ['"' + clang_link + '"']
    
    # 添加链接器选项 - 使用LLD风格的链接器选项
    for flag in env.get('LINKFLAGS', []):
        # 直接添加所有选项，LLD使用MSVC风格选项
        # 但跳过重复的库文件路径（已经在LIBS中处理）
        # 注意：不要跳过符号排除选项，它们以--exclude-libs开头
        if isinstance(flag, str) and (flag.endswith('.a') or flag.endswith('.lib')) and not flag.startswith('--exclude-libs'):
            print(f"🔧 [DEBUG] 跳过重复库文件（已在LIBS中）: {flag}", file=sys.stderr)
            continue
        cmd.append(flag)
        print(f"🔧 [DEBUG] 添加链接器选项: {flag}", file=sys.stderr)
    
    # 处理符号排除选项 - 将--exclude-libs转换为lld-link支持的/exclude-symbols选项
    # 获取所有以--exclude-libs或/exclude-symbols开头的选项
    exclude_libs_flags = [flag for flag in env.get('LINKFLAGS', []) if isinstance(flag, str) and (flag.startswith('--exclude-libs') or flag.startswith('/exclude-symbols'))]
    for exclude_flag in exclude_libs_flags:
        # 解析--exclude-libs:libname.a:objectname.o格式或/exclude-symbols:symbolname格式
        # 转换为lld-link支持的符号排除选项
        print(f"🔧 [DEBUG] 处理符号排除选项: {exclude_flag}", file=sys.stderr)
        # 示例：--exclude-libs:libscintilla.a:Document.o 或 /exclude-symbols:CreateRegexSearch
        # 我们需要提取符号名称并转换为/exclude-symbols选项
        # 由于lld-link不直接支持基于对象文件的排除，我们需要手动指定要排除的符号
        # 根据之前的分析，Document.o中的CreateRegexSearch符号与boostregex冲突
        # 所以我们直接添加符号排除选项
        if exclude_flag.startswith('--exclude-libs'):
            # 转换--exclude-libs为/exclude-symbols
            converted_flag = exclude_flag.replace('--exclude-libs:', '/exclude-symbols:')
            cmd.append(converted_flag)
            print(f"🔧 [DEBUG] 转换并添加符号排除选项: {converted_flag}", file=sys.stderr)
        elif exclude_flag.startswith('/exclude-symbols'):
            # 直接添加/exclude-symbols选项
            cmd.append(exclude_flag)
            print(f"🔧 [DEBUG] 添加符号排除选项: {exclude_flag}", file=sys.stderr)
    
    # 注意：由于已经移除了SCI_OWNREGEX宏定义，CreateRegexSearch符号只在libscintilla.a中定义
    # 不再需要符号排除选项，避免重复添加
    print(f"🔧 [DEBUG] 符号排除选项已通过移除SCI_OWNREGEX宏解决，跳过添加", file=sys.stderr)
    
    # 添加库路径 - 使用LLD风格的/LIBPATH选项，去重
    unique_libpaths = set()
    for libpath in env.get('LIBPATH', []):
        if libpath not in unique_libpaths:
            unique_libpaths.add(libpath)
            cmd.append(f"/LIBPATH:{libpath}")
            print(f"🔧 [DEBUG] 添加库路径: /LIBPATH:{libpath}", file=sys.stderr)
    
    # 添加源文件和目标文件（应该在库文件之前）
    cmd.extend(['-out:' + str(target[0])])
    cmd.extend([str(s) for s in source])
    
    # 添加链接器选项 - 检查是否已经存在，避免重复添加
    cmd_str_for_check = ' '.join(cmd)
    if "/OPT:REF" not in cmd_str_for_check:
        cmd.append("/OPT:REF")  # 删除未引用的函数和数据
        print(f"🔧 [DEBUG] 添加链接器选项: /OPT:REF", file=sys.stderr)
    else:
        print(f"🔧 [DEBUG] 链接器选项已存在，跳过添加: /OPT:REF", file=sys.stderr)
    
    if "/OPT:ICF" not in cmd_str_for_check:
        cmd.append("/OPT:ICF")  # 执行相同COMDAT折叠
        print(f"🔧 [DEBUG] 添加链接器选项: /OPT:ICF", file=sys.stderr)
    else:
        print(f"🔧 [DEBUG] 链接器选项已存在，跳过添加: /OPT:ICF", file=sys.stderr)
    
    # 添加库文件 - 使用LLD风格的库名
    for lib in env.get('LIBS', []):
        # 如果库文件已经是完整路径，直接使用
        if isinstance(lib, str) and (lib.endswith('.a') or lib.endswith('.lib')):
            cmd.append(lib)
            print(f"🔧 [DEBUG] 添加库文件: {lib}", file=sys.stderr)
        else:
            # 对于系统库，转换为.lib格式，但不要添加/DEFAULTLIB:前缀
            if lib.startswith('-l'):
                lib_name = lib[2:] + '.lib'
                cmd.append(lib_name)
                print(f"🔧 [DEBUG] 添加系统库: {lib_name}", file=sys.stderr)
            else:
                cmd.append(lib)
                print(f"🔧 [DEBUG] 添加库: {lib}", file=sys.stderr)
    
    # 将命令写入文件以便调试
    cmd_str = ' '.join(cmd)
    with open('link_command.txt', 'w', encoding='utf-8') as f:
        f.write(cmd_str)
    print(f"� [DEBUG] 链接命令已写入文件: link_command.txt", file=sys.stderr)
    print(f"� [DEBUG] 最终链接器命令: {cmd_str}", file=sys.stderr)
    
    # 打印当前工作目录和库文件信息（不检查存在性，因为系统库文件位于系统目录中）
    print(f"📂 [DEBUG] 当前工作目录: {os.getcwd()}", file=sys.stderr)
    print(f"📚 [DEBUG] 库文件列表: {[lib for lib in env.get('LIBS', []) if isinstance(lib, str) and (lib.endswith('.a') or lib.endswith('.lib'))]}", file=sys.stderr)
    
    return cmd

# 设置文件扩展名
env['OBJSUFFIX'] = '.o'
env['LIBSUFFIX'] = '.lib'
env['PROGSUFFIX'] = '.exe'

# 使用SCons的标准工具配置，但强制使用Clang编译器
# 首先清除所有现有的工具配置
env.Tool('default')

# 清除所有MSVC相关的环境变量，避免自动添加MSVC选项
env['CC'] = None
env['CXX'] = None
env['LINK'] = None
env['AR'] = None
# 不清除env['RC']，保留资源编译器配置

# 清除所有MSVC特有的编译选项
env['CCFLAGS'] = []
env['CXXFLAGS'] = []
env['CPPFLAGS'] = []
env['LINKFLAGS'] = []

# 强制设置Clang编译器 - 使用引号包装路径以处理空格
env['CXX'] = '"' + clang_cxx + '"'
env['CC'] = '"' + clang_cc + '"'
env['LINK'] = '"' + clang_link + '"'
env['AR'] = '"' + clang_ar + '"'

# 设置Clang编译器特有的选项前缀，避免MSVC选项
env['CPPDEFPREFIX'] = '-D'
env['CPPDEFSUFFIX'] = ''
env['INCPREFIX'] = '-I'
env['INCSUFFIX'] = ''
env['CCFLAGPREFIX'] = ''
env['CCFLAGSUFFIX'] = ''
env['CXXFLAGPREFIX'] = ''
env['CXXFLAGSUFFIX'] = ''

# 设置编译命令模板 - 使用Clang兼容的模板，避免MSVC选项
# 移除SCons自动添加的MSVC选项（如/TP、/nologo等）
# 确保包含 _CPPINCFLAGS 变量，以便正确展开 CPPPATH 中的包含路径
env['CCCOM'] = '$CXX $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS -c $SOURCES -o $TARGET'
env['CXXCOM'] = '$CXX $CXXFLAGS $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS -c $SOURCES -o $TARGET'

# 禁用SCons自动添加的MSVC选项
env['CPPDEFPREFIX'] = '-D'
env['CPPDEFSUFFIX'] = ''
env['INCPREFIX'] = '-I'
env['INCSUFFIX'] = ''

# 设置链接器命令模板 - 使用Visual Studio的link.exe
# 构建基本的链接器命令模板
# 注意：这个模板将在configure_link_options函数中被覆盖
# 使用一个简单的模板，避免包含Visual Studio运行时库
linkcom_template = '$LINK $LINKFLAGS /OUT:$TARGET $SOURCES'

# 设置链接器命令
env['LINKCOM'] = linkcom_template

# 设置归档器命令
env['ARCOM'] = '$AR rc $TARGET $SOURCES'
env['RANLIBCOM'] = '$RANLIB $TARGET'

# 配置资源文件构建器
env = configure_resource_builder(env)

# 设置目标架构
env['TARGET_ARCH'] = 'x86_64'

print(f"✅ 当前编译器类型: {get_compiler_type(env)}")
print(f"✅ CXX编译器: {env['CXX']}")
print(f"✅ LINK链接器: {env['LINK']}")
print(f"✅ AR归档器: {env['AR']}")
print(f"✅ RC资源编译器: {env.get('RC', '未设置')}")
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
    """配置构建选项 - 强制使用Clang编译器"""
    
    compiler_type = get_compiler_type(env)
    print(f"配置构建选项 - 编译器类型: {compiler_type}")
    
    # 初始化库目录列表
    lib_dirs = []
    
    # 强制使用Clang编译器设置
    if compiler_type != 'clang':
        print("❌ 错误: 当前编译器不是Clang，构建终止")
        sys.exit(1)
    
    # Clang编译器设置
    env.Append(CCFLAGS=[
        '-std=c++20',           # C++20标准
        '-fms-extensions',      # 启用MS扩展支持
        '-fms-compatibility',   # 提高MSVC兼容性
        '-municode',            # Unicode支持
        '-Wall',                # 启用所有警告
        '-Wextra',              # 启用额外警告
        '-Wpedantic',           # 严格标准警告
        '-O2',                  # 优化级别2
        '-flto',                # 链接时优化
        '-fexceptions',         # 启用异常处理
        '-frtti',               # 启用RTTI
        '-fuse-ld=lld',         # 使用LLD链接器
        '-fdiagnostics-absolute-paths', # 诊断信息使用绝对路径
        '-g',                   # 生成调试信息
        # 禁用特定警告（减少编译错误）
        '-Wno-microsoft-cast',  # 禁用MS风格转换警告
        '-Wno-microsoft-enum-value', # 禁用MS枚举值警告
        '-Wno-deprecated-declarations', # 禁用弃用声明警告
        '-Wno-unknown-pragmas', # 禁用未知pragma警告
        '-Wno-unused-function', # 禁用未使用函数警告
        '-Wno-unused-variable', # 禁用未使用变量警告
        '-Wno-format',          # 禁用格式警告
        '-Wno-sign-compare',    # 禁用符号比较警告
        '-Wno-switch',          # 禁用switch警告
        '-Wno-reorder',         # 禁用成员初始化顺序警告
        '-Wno-overloaded-virtual', # 禁用重载虚函数警告
        '-Wno-invalid-offsetof', # 禁用无效offsetof警告
        '-Wno-unreachable-code', # 禁用不可达代码警告
        '-Wno-uninitialized',   # 禁用未初始化警告
        '-Wno-non-virtual-dtor', # 禁用非虚析构函数警告
        '-Wno-old-style-cast',  # 禁用旧式转换警告
        '-Wno-return-type',     # 禁用返回类型警告
    ])
    
    # 预处理器定义 - 基于CMakeLists.txt，使用Clang格式
    defines = [
        'WIN32',
        '_WINDOWS',
        'UNICODE',
        '_UNICODE',
        # '_DLL',  # 移除_DLL定义，使用静态运行时库 (MT) 以匹配预编译库
        '_WIN32_WINNT=_WIN32_WINNT_WIN7',
        'NTDDI_VERSION=NTDDI_WIN7',
        '_WIN32_IE=0x0800',  # 启用Windows公共控件功能（IE 8.0版本，支持更新的COMCTL32功能）
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
        # 添加Windows特定定义，避免Visual Studio依赖
        # '_CRT_STDIO_ISO_WIDE_SPECIFIERS',
        '_CRT_SECURE_CPP_OVERLOAD_STANDARD_NAMES=0',
         '_CRT_SECURE_CPP_OVERLOAD_STANDARD_NAMES_COUNT=0',
         '_CRT_SECURE_CPP_OVERLOAD_SECURE_NAMES=0',
        '_ALLOW_RTCc_IN_STL',
        '_HAS_STD_BYTE=0',
        '_SILENCE_ALL_CXX17_DEPRECATION_WARNINGS',
        '_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING',
        '_SILENCE_CXX20_CISO646_REMOVED_WARNING',
        '_SILENCE_CXX23_ALIGNED_UNION_DEPRECATION_WARNING',
        '__MSVCRT_VERSION__=0x1400',  # 使用较新的MSVCRT版本
    ]
    
    # 禁用特定警告 - 使用Clang风格的-Wno-格式，移除MSVC风格的警告选项
    # 已移除MSVC特有的警告禁用选项，使用Clang的-Wno-格式
    
    # 包含目录 - 基于CMakeLists.txt
    # 注意：包含路径已通过CCFLAGS中的-I选项在SConscript中添加，避免重复添加
    
    # 设置Windows SDK包含路径 - 使用Windows SDK而不是Visual Studio的库
    # 对于Clang编译器，我们需要使用Windows SDK的路径，而不是Visual Studio的路径
    windows_sdk_paths = []
    
    # 检查Windows SDK路径
    windows_sdk_versions = ['10', '8.1', '8.0']
# 检查Windows SDK包含路径
    windows_sdk_base_paths = [
        r"D:\Windows Kits\10\Include",
        r"C:\Program Files (x86)\Windows Kits\10\Include",
        r"C:\Program Files\Windows Kits\10\Include"
    ]
    
    for base_path in windows_sdk_base_paths:
        if os.path.exists(base_path):
            # 查找最新的Windows SDK版本
            for version in os.listdir(base_path):
                version_path = os.path.join(base_path, version)
                if os.path.isdir(version_path) and version.replace('.', '').isdigit():
                    # 添加主要的包含路径
                    um_path = os.path.join(version_path, 'um')
                    shared_path = os.path.join(version_path, 'shared')
                    ucrt_path = os.path.join(version_path, 'ucrt')
                    
                    if os.path.exists(um_path):
                        windows_sdk_paths.append('-I' + um_path)
                    if os.path.exists(shared_path):
                        windows_sdk_paths.append('-I' + shared_path)
                    if os.path.exists(ucrt_path):
                        windows_sdk_paths.append('-I' + ucrt_path)
                    
                    print(f"找到Windows SDK {version} 包含路径")
                    break
            
            if windows_sdk_paths:
                break
    
    # 如果没有找到Windows SDK路径，尝试使用环境变量
    if not windows_sdk_paths and 'INCLUDE' in os.environ:
        include_paths = os.environ['INCLUDE'].split(';')
        # 严格过滤：只保留Windows SDK路径，完全排除Visual Studio路径
        valid_env_paths = [p for p in include_paths if os.path.exists(p) and 'Windows Kits' in p and 'Visual Studio' not in p and 'VC' not in p and 'MSVC' not in p]
        if valid_env_paths:
            windows_sdk_paths.extend(['-I' + p for p in valid_env_paths])
            print(f"从环境变量添加Windows SDK包含路径: {valid_env_paths}")
        else:
            print("⚠️ 警告: 环境变量INCLUDE中未找到有效的Windows SDK包含路径，或路径被排除")
            print("将依赖编译器自动查找系统头文件")
    
    # 添加包含路径到CCFLAGS
    if windows_sdk_paths:
        env.Append(CCFLAGS=windows_sdk_paths)
        print(f"添加Windows SDK包含路径: {windows_sdk_paths}")
    else:
        print("⚠️ 警告: 未找到Windows SDK包含路径")
        print("尝试使用系统默认包含路径...")
        # 尝试使用系统默认路径或继续构建，让编译器自行查找系统头文件
        # 对于Clang编译器，它可能能够找到系统头文件
        print("继续构建，依赖编译器自动查找系统头文件")
    
    # 设置Windows SDK库路径 - 使用Windows SDK而不是Visual Studio的库
    # 对于Clang编译器，我们需要使用Windows SDK的库路径
    windows_lib_paths = []
    
    # 检查Windows SDK库路径
    windows_sdk_base_paths = [
        r"D:\Windows Kits\10\Lib",
        r"C:\Program Files (x86)\Windows Kits\10\Lib",
        r"C:\Program Files\Windows Kits\10\Lib"
    ]
    
    for base_path in windows_sdk_base_paths:
        if os.path.exists(base_path):
            # 查找所有可用的Windows SDK版本
            available_versions = []
            for version in os.listdir(base_path):
                version_path = os.path.join(base_path, version)
                if os.path.isdir(version_path) and version.replace('.', '').isdigit():
                    # 检查是否包含必要的目录结构
                    x64_path = os.path.join(version_path, 'um', 'x64')
                    ucrt_x64_path = os.path.join(version_path, 'ucrt', 'x64')
                    
                    if os.path.exists(x64_path) or os.path.exists(ucrt_x64_path):
                        available_versions.append(version)
            
            # 按版本号排序，选择最新版本
            if available_versions:
                available_versions.sort(key=lambda v: [int(part) for part in v.split('.')], reverse=True)
                latest_version = available_versions[0]
                version_path = os.path.join(base_path, latest_version)
                
                # 添加x64架构的库路径
                x64_path = os.path.join(version_path, 'um', 'x64')
                ucrt_x64_path = os.path.join(version_path, 'ucrt', 'x64')
                
                if os.path.exists(x64_path):
                    windows_lib_paths.append(x64_path)
                if os.path.exists(ucrt_x64_path):
                    windows_lib_paths.append(ucrt_x64_path)
                
                print(f"✅ 找到Windows SDK {latest_version} 库路径")
                print(f"   - um\\x64: {x64_path}")
                print(f"   - ucrt\\x64: {ucrt_x64_path}")
                
                # 检查是否包含必要的系统库
                if os.path.exists(x64_path):
                    lib_files = os.listdir(x64_path)
                    required_libs = ['kernel32.lib', 'user32.lib', 'gdi32.lib', 'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'advapi32.lib', 'uuid.lib']
                    missing_libs = [lib for lib in required_libs if lib not in lib_files]
                    
                    if missing_libs:
                        print(f"⚠️  警告: 缺少必要的系统库: {missing_libs}")
                    else:
                        print("✅  所有必要的系统库都存在")
                
                break
    
    # 如果没有找到Windows SDK库路径，尝试使用环境变量
    if not windows_lib_paths and 'LIB' in os.environ:
        lib_paths = os.environ['LIB'].split(';')
        # 严格过滤：只保留Windows SDK路径，完全排除Visual Studio路径
        valid_env_lib_paths = [p for p in lib_paths if os.path.exists(p) and 'Windows Kits' in p and 'Visual Studio' not in p and 'VC' not in p and 'MSVC' not in p]
        if valid_env_lib_paths:
            windows_lib_paths.extend(valid_env_lib_paths)
            print(f"从环境变量添加Windows SDK库路径: {valid_env_lib_paths}")
        else:
            print("⚠️ 警告: 环境变量LIB中未找到有效的Windows SDK库路径，或路径被排除")
            print("将依赖链接器自动查找系统库")
    
    # 添加库路径到LIBPATH环境变量
    if windows_lib_paths:
        env.Append(LIBPATH=windows_lib_paths)
        lib_dirs.extend(windows_lib_paths)
        print(f"添加Windows SDK库路径到LIBPATH: {windows_lib_paths}")
    else:
        print("⚠️ 警告: 未找到Windows SDK库路径")
        print("尝试使用系统默认库路径...")
        print("继续构建，依赖链接器自动查找系统库")
    
    # 强制使用Clang编译器，检查编译器类型
    compiler_type = get_compiler_type(env)
    print(f"配置构建选项 - 编译器类型: {compiler_type}, 构建类型: {build_type}")
    
    if compiler_type != 'clang':
        print("❌ 错误: 当前编译器不是Clang，构建终止")
        sys.exit(1)
    
    # Clang编译器：使用动态运行时库以匹配预编译库的运行时库类型
    # Clang在Windows上默认使用动态运行时库，无需额外配置
    print("使用Clang动态运行时库以匹配预编译库")
    
    if build_type == 'Debug':
        defines.append('_DEBUG')
        env.Append(CCFLAGS=['-D_DEBUG'])
        
        # Clang调试模式选项
        env.Append(CCFLAGS=['-O0', '-g'])   # 禁用优化，启用调试信息
        env.Append(LINKFLAGS=['-debug'])     # 链接调试信息
        env.Append(CCFLAGS=['-fsanitize=undefined'])  # 运行时检查
        print("Clang调试模式配置完成")
    else:  # Release
        defines.append('NDEBUG')
        env.Append(CCFLAGS=['-DNDEBUG'])
        
        # Clang发布模式选项
        env.Append(CCFLAGS=['-O2', '-flto'])  # 最大优化，链接时优化
        env.Append(LINKFLAGS=['-flto', '-opt:ref', '-opt:icf'])  # 链接时优化
        print("Clang发布模式配置完成")
    
    # 应用定义 - 使用Clang格式
    for define in defines:
        env.Append(CCFLAGS=['-D' + define])
    
    # 强制Clang编译器只使用Windows SDK路径，排除Visual Studio路径
    # 这是解决Visual Studio库依赖问题的关键
    
    # 方法1：使用-isystem明确指定系统头文件路径，覆盖默认的Visual Studio路径
    if windows_sdk_paths:
        # 将-I路径转换为-isystem路径
        for path_with_flag in windows_sdk_paths:
            if path_with_flag.startswith('-I'):
                path = path_with_flag[2:]  # 去掉-I前缀
                env.Append(CCFLAGS=['-isystem', path])
                print(f"强制添加Windows SDK系统包含路径: {path}")
    
    # 方法2：明确排除Visual Studio路径
    env.Append(CCFLAGS=['-nostdinc++'])  # 不使用C++标准库包含路径
    
    # 方法3：设置环境变量，强制Clang不使用Visual Studio路径
    # 设置INCLUDE环境变量为空，避免Clang自动检测Visual Studio路径
    env['ENV']['INCLUDE'] = ''
    env['ENV']['LIB'] = ''
    print("清空INCLUDE和LIB环境变量，避免Clang自动检测Visual Studio路径")
    
    return env

# 配置链接选项 - 基于CMakeLists.txt
def configure_link_options(env, subsystem='WINDOWS', extra_lib_paths=None, lexilla_lib=None, scintilla_lib=None):
    """配置链接选项 - 强制使用Clang编译器
    Args:
        env: SCons环境对象
        subsystem: 子系统类型，'WINDOWS' 或 'CONSOLE'
        extra_lib_paths: 额外的库路径列表，从SConscript传递过来
        lexilla_lib: Lexilla库文件路径
        scintilla_lib: Scintilla库文件路径
    """
    
    compiler_type = get_compiler_type(env)
    print(f"配置链接选项 - 编译器类型: {compiler_type}")
    
    # 强制使用Clang编译器
    if compiler_type != 'clang':
        print("❌ 错误: 当前编译器不是Clang，构建终止")
        sys.exit(1)
    
    # 清空现有链接器选项
    env['LINKFLAGS'] = []
    
    # 添加系统库 - 使用LLD原生格式（直接使用库名，不加-l前缀）
    # 简化库列表，只保留必要的核心库，让链接器自动处理其他依赖
    libs = [
        'kernel32.lib',           # 内核库
        'user32.lib',             # 用户界面库
        'gdi32.lib',              # 图形设备接口
        'shell32.lib',            # Shell API
        'ole32.lib',              # OLE基础库
        'oleaut32.lib',           # OLE自动化库（关键：解决序数381错误）
        'advapi32.lib',           # 高级API库
        'uuid.lib',               # UUID库
        # 注意：libScintilla和libLexilla现在在SConscript中手动添加，避免SCons尝试构建它们
    ]
    
    # 库目录 - 添加系统库目录，确保链接器能找到所有依赖库
    lib_dirs = [
        project_root,               # 添加项目根目录，包含预编译的Scintilla.lib和Lexilla.lib
        bin_dir,                    # 添加bin目录
        os.path.join(scintilla_dir, 'bin'),
        obj_dir,
    ]
    
    # 添加额外的库路径（如果提供）
    if extra_lib_paths:
        lib_dirs.extend(extra_lib_paths)
        print(f"✅ 已添加额外库路径: {extra_lib_paths}")
    
    # 设置Windows SDK库路径 - 使用Windows SDK而不是Visual Studio的库
    # 对于Clang编译器，我们需要使用Windows SDK的库路径
    windows_lib_paths = []
    
    # 检查Windows SDK库路径
    windows_sdk_base_paths = [
        r"D:\Windows Kits\10\Lib",
        r"C:\Program Files (x86)\Windows Kits\10\Lib",
        r"C:\Program Files\Windows Kits\10\Lib"
    ]
    
    for base_path in windows_sdk_base_paths:
        if os.path.exists(base_path):
            # 查找所有可用的Windows SDK版本
            available_versions = []
            for version in os.listdir(base_path):
                version_path = os.path.join(base_path, version)
                if os.path.isdir(version_path) and version.replace('.', '').isdigit():
                    # 检查是否包含必要的目录结构
                    x64_path = os.path.join(version_path, 'um', 'x64')
                    ucrt_x64_path = os.path.join(version_path, 'ucrt', 'x64')
                    
                    if os.path.exists(x64_path) or os.path.exists(ucrt_x64_path):
                        available_versions.append(version)
            
            # 按版本号排序，选择最新版本
            if available_versions:
                available_versions.sort(key=lambda v: [int(part) for part in v.split('.')], reverse=True)
                latest_version = available_versions[0]
                version_path = os.path.join(base_path, latest_version)
                
                # 添加x64架构的库路径
                x64_path = os.path.join(version_path, 'um', 'x64')
                ucrt_x64_path = os.path.join(version_path, 'ucrt', 'x64')
                
                if os.path.exists(x64_path):
                    windows_lib_paths.append(x64_path)
                if os.path.exists(ucrt_x64_path):
                    windows_lib_paths.append(ucrt_x64_path)
                
                print(f"✅ 找到Windows SDK {latest_version} 库路径")
                print(f"   - um\\x64: {x64_path}")
                print(f"   - ucrt\\x64: {ucrt_x64_path}")
                
                # 检查是否包含必要的系统库
                if os.path.exists(x64_path):
                    lib_files = os.listdir(x64_path)
                    required_libs = ['kernel32.lib', 'user32.lib', 'gdi32.lib', 'shell32.lib', 'ole32.lib', 'oleaut32.lib', 'advapi32.lib', 'uuid.lib']
                    missing_libs = [lib for lib in required_libs if lib not in lib_files]
                    
                    if missing_libs:
                        print(f"⚠️  警告: 缺少必要的系统库: {missing_libs}")
                    else:
                        print("✅  所有必要的系统库都存在")
                
                break
    
    # 如果没有找到Windows SDK库路径，尝试使用环境变量
    if not windows_lib_paths and 'LIB' in os.environ:
        lib_paths = os.environ['LIB'].split(';')
        # 严格过滤：只保留Windows SDK路径，完全排除Visual Studio路径
        valid_env_lib_paths = [p for p in lib_paths if os.path.exists(p) and 'Windows Kits' in p and 'Visual Studio' not in p and 'VC' not in p and 'MSVC' not in p]
        if valid_env_lib_paths:
            windows_lib_paths.extend(valid_env_lib_paths)
            print(f"从环境变量添加Windows SDK库路径: {valid_env_lib_paths}")
        else:
            print("⚠️ 警告: 环境变量LIB中未找到有效的Windows SDK库路径，或路径被排除")
            print("将依赖链接器自动查找系统库")
    
    # 添加Windows SDK库路径到LIBPATH环境变量
    if windows_lib_paths:
        env.Append(LIBPATH=windows_lib_paths)
        lib_dirs.extend(windows_lib_paths)
        print(f"添加Windows SDK库路径到LIBPATH: {windows_lib_paths}")
    else:
        print("⚠️ 警告: 未找到Windows SDK库路径")
        print("尝试使用系统默认库路径...")
        print("继续构建，依赖链接器自动查找系统库")
    
    # 查找Visual Studio库路径（仅用于链接必要的运行时库）
    # 即使不使用MSVC编译器，Clang在Windows上也需要链接MSVC运行时库（vcruntime.lib, msvcrt.lib）
    # 以支持C++异常处理(__std_exception_destroy)和其他CRT功能
    msvc_lib_paths = []
    
    # 检查Visual Studio库路径
    vs_base_paths = [
        r"D:\Code\VS2022\Community\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
        r"D:\Code\VS2019\Community\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC"
    ]
    
    for base_path in vs_base_paths:
        if os.path.exists(base_path):
            # 查找最新的MSVC版本
            versions = []
            for v in os.listdir(base_path):
                v_path = os.path.join(base_path, v)
                if os.path.isdir(v_path) and v.replace('.', '').isdigit():
                    versions.append(v)
            
            if versions:
                # 按版本号排序
                versions.sort(key=lambda v: [int(part) for part in v.split('.')], reverse=True)
                latest_version = versions[0]
                
                # 构建库路径
                lib_path_x64 = os.path.join(base_path, latest_version, 'lib', 'x64')
                
                if os.path.exists(lib_path_x64):
                    msvc_lib_paths.append(lib_path_x64)
                    print(f"✅ 找到Visual Studio MSVC库路径: {lib_path_x64}")
                    break
    
    # 添加MSVC库路径到LIBPATH
    if msvc_lib_paths:
        env.Append(LIBPATH=msvc_lib_paths)
        lib_dirs.extend(msvc_lib_paths)
        print(f"添加MSVC库路径到LIBPATH: {msvc_lib_paths}")
    else:
        print("⚠️ 警告: 未找到Visual Studio MSVC库路径")
        print("可能导致缺少vcruntime.lib和msvcrt.lib相关的链接错误")

    # 添加Clang运行时库路径（为包含空格的路径添加引号）
    clang_lib_paths = [
        r'"C:\Program Files\LLVM\lib\clang\21\lib\windows"'
    ]
    
    # 检查路径是否存在（去掉引号检查）
    actual_path = r"C:\Program Files\LLVM\lib\clang\21\lib\windows"
    if os.path.exists(actual_path):
        lib_dirs.extend(clang_lib_paths)
        print(f"添加Clang运行时库路径: {clang_lib_paths}")
    else:
        print("⚠️ 警告: 未找到Clang运行时库路径")
        
    # 检查路径是否存在，如果不存在则跳过
    for i, path in enumerate(lib_dirs):
        if not os.path.exists(path):
            print(f"⚠️ 警告: 库路径不存在，将被跳过: {path}")
            lib_dirs[i] = None  # 标记为None，稍后过滤掉
    
    # 过滤掉不存在的路径
    lib_dirs = [path for path in lib_dirs if path is not None]
    
    # 简化系统库列表，只保留必要的库
    minimal_libs = [
        'kernel32.lib',           # 内核库
        'user32.lib',             # 用户界面库
        'gdi32.lib',              # 图形设备接口
        'shell32.lib',            # Shell API
        'ole32.lib',              # OLE基础库
        'oleaut32.lib',           # OLE自动化库
        'advapi32.lib',           # 高级API库
        'uuid.lib',               # UUID库
        'Imm32.lib',              # 输入法库
    'comctl32.lib',           # 通用控件库
    'shlwapi.lib',            # Shell轻量级实用程序库
    'wininet.lib',            # 网络库
    'uxtheme.lib',            # 主题库
    'version.lib',            # 版本信息库
    'comdlg32.lib',           # 通用对话框库
    'dwmapi.lib',             # 桌面窗口管理器API
    'crypt32.lib',            # 加密API
    'oldnames.lib',           # 兼容性库(strnicmp等)
    'Dbghelp.lib',            # 调试帮助库(ImageNtHeader)
    'Sensapi.lib',            # 系统事件通知服务(IsNetworkAlive)
    'Wintrust.lib',           # Windows信任验证(WinVerifyTrust)
    'comsuppw.lib',           # COM支持库(_com_issue_error)
]
    
    # 对于Clang编译器，需要明确指定使用Windows SDK的运行时库
    # 而不是Visual Studio的运行时库
    system_libs = minimal_libs
    
    # 添加Windows SDK的C运行时库
    # 使用静态运行时库以匹配预编译库 (MT)
    system_libs.extend([
        'libucrt.lib',        # 通用C运行时库（静态版本）
        'libvcruntime.lib',   # Visual C++运行时库（静态版本）
        'libcmt.lib',         # C运行时启动库（静态版本）
        'libcpmt.lib',        # C++标准库（静态版本）
    ])
    
    # 替换原有的复杂库列表
    libs = system_libs
    print(f"使用Clang兼容库列表（包含Windows SDK和MSVC运行时库）: {libs}")
    print("注意：明确使用Windows SDK的运行时库以避免Visual Studio依赖")
    
    # 检查编译器类型
    print(f"链接器配置 - 编译器类型: {compiler_type}, 子系统: {subsystem}")
    
    # 链接器标志
    linkflags = []
    
    # 子系统设置
    if subsystem.upper() == 'CONSOLE':
        linkflags.append('/SUBSYSTEM:CONSOLE')
    else:
        linkflags.append('/SUBSYSTEM:WINDOWS')
    
    # 调试信息
    if build_type == 'debug':
        linkflags.append('/DEBUG')
    
    # 其他链接器选项
    linkflags.extend([
        '/MACHINE:X64',      # 指定目标架构为x64
        '/DYNAMICBASE',      # 启用ASLR
        '/NXCOMPAT',         # 启用数据执行保护
        '/OPT:REF',          # 删除未引用的函数和数据
        '/OPT:ICF',          # 执行相同COMDAT折叠
        # '/exclude-symbols:BoostRegExSearch',  # 排除BoostRegExSearch符号以避免冲突（在SConscript中处理）
        '/ENTRY:wWinMainCRTStartup' # 显式指定Unicode入口点
    ])
    
    # 显式设置LINKFLAGS，以便在command template中正确展开
    env['LINKFLAGS'] = linkflags
    
    # 对于Clang编译器，优先使用Clang的链接器（lld-link.exe）
    if compiler_type == 'clang':
        print("🔧 Clang编译器：优先使用Clang链接器（lld-link.exe）")
        
        # 设置Clang链接器
        clang_link_path = r"C:\Program Files\LLVM\bin\lld-link.exe"
        if os.path.exists(clang_link_path):
            # 使用带引号的路径
            env['LINK'] = '"' + clang_link_path + '"'
            print(f"✅ 链接器已设置为Clang的lld-link.exe: {env.get('LINK', '未设置')}")
            
            # 构建Clang链接器命令模板 - 使用响应文件解决命令行长度限制
            linkcom_template = '"' + clang_link_path + '" $LINKFLAGS'
            
            # 添加链接器选项 - 不禁用默认库，因为我们需要C运行时库
            # 只禁用不需要的动态运行时库
            linkcom_template += ' /NODEFAULTLIB:msvcrt.lib'   # 禁用msvcrt.lib (动态)
            linkcom_template += ' /NODEFAULTLIB:msvcprt.lib'  # 禁用msvcprt.lib (动态)
            linkcom_template += ' /NODEFAULTLIB:comsuppw.lib'  # 禁用comsuppw.lib
            
            # 添加manifest依赖，强制使用COMCTL32.dll版本6
            # 这将确保应用程序使用COMCTL32.dll版本6而不是版本5
            linkcom_template += ' /MANIFESTDEPENDENCY:"type=\'win32\' name=\'Microsoft.Windows.Common-Controls\' version=\'6.0.0.0\' processorArchitecture=\'*\' publicKeyToken=\'6595b64144ccf1df\' language=\'*\'"'
            print("✅ 已添加manifest依赖，强制使用COMCTL32.dll版本6")
            
            # 注意：manifest已经在Notepad_plus.rc资源文件中定义（IDR_RT_MANIFEST）
            # 不需要在这里通过/MANIFEST选项添加，否则会导致重复资源错误
            # 资源文件中的manifest会被正确嵌入到可执行文件中
            print("ℹ️ manifest已包含在资源文件中，无需通过链接器选项添加")
            
            # 添加库路径 - 包括预编译库目录
            libpaths = env.get('LIBPATH', [])
            
            # 添加预编译库目录路径
            prebuilt_lib_dirs = [
                os.path.join(lexilla_dir, 'bin'),
                os.path.join(scintilla_dir, 'bin'),
                bin_dir
            ]
            
            # 合并所有库路径
            all_libpaths = list(set(libpaths + prebuilt_lib_dirs))
            
            for libpath in all_libpaths:
                linkcom_template += f' /LIBPATH:"{libpath}"'
            
            # 添加输出文件
            linkcom_template += ' /OUT:$TARGET'
            
            # 使用固定的响应文件路径解决命令行长度限制问题
            rsp_file_path = os.path.join(bin_dir, 'linker.rsp')
            linkcom_template += f' @"{rsp_file_path}"'
            
            # 创建响应文件生成函数
            def create_response_file(target, source, env):
                """创建链接器响应文件"""
                with open(rsp_file_path, 'w', encoding='utf-8') as f:
                    # 添加所有源文件（.obj文件）
                    for src in source:
                        f.write(f'"{src.path}"\n')
                    
                    # 添加我们明确指定的系统库
                    for lib in libs:
                        if isinstance(lib, str):
                            f.write(f'{lib}\n')
                    
                    # 添加预编译库文件
                    if isinstance(lexilla_lib, str) and isinstance(scintilla_lib, str):
                        f.write(f'"{lexilla_lib}"\n')
                        f.write(f'"{scintilla_lib}"\n')
                
                print(f"✅ 已创建响应文件: {rsp_file_path}")
            
            # 添加链接前的操作来创建响应文件
            env.AddPreAction('$PROGPREFIX$PROGSUFFIX', create_response_file)
            
            # 设置链接器命令模板
            env['LINKCOM'] = linkcom_template
            print(f"✅ 已设置Clang链接器命令模板（使用响应文件: {rsp_file_path}）")
        else:
            # 如果找不到lld-link.exe，使用Visual Studio的link.exe作为备选
            print("⚠️ 警告: 未找到lld-link.exe，使用Visual Studio链接器（link.exe）")
            env['LINK'] = 'link.exe'
            # 添加Visual Studio的库路径到链接器路径
            vs_link_paths = [
                r"D:\Code\VS2022\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64"
            ]
            env.PrependENVPath('PATH', vs_link_paths)
            
            # 构建基本的链接器命令模板
            linkcom_template = 'link.exe $LINKFLAGS'
            
            # 添加库路径
            for libpath in env.get('LIBPATH', []):
                linkcom_template += f' /LIBPATH:"{libpath}"'
            
            # 添加输出文件和输入文件
            linkcom_template += ' /OUT:$TARGET'
            linkcom_template += ' $SOURCES'
            
            # 添加库文件 - 只添加我们明确指定的系统库，过滤掉Visual Studio运行时库
            for lib in libs:
                if isinstance(lib, str):
                    linkcom_template += f' {lib}'
                else:
                    linkcom_template += f' ${{lib[0].path}}'
            
            # 设置链接器命令
            env['LINKCOM'] = linkcom_template
            print(f"✅ 已设置链接器命令: {linkcom_template}")
        
        # 添加调试信息，检查链接器命令是否正确生成
        def debug_link_command(target, source, env):
            """调试链接器命令生成"""
            print(f"🔧 调试 - 目标文件: {target[0].path if target else 'None'}")
            print(f"🔧 调试 - 源文件数量: {len(source) if source else 0}")
            if source:
                for i, src in enumerate(source[:5]):  # 只显示前5个源文件
                    print(f"🔧 调试 - 源文件[{i}]: {src.path if hasattr(src, 'path') else src}")
            print(f"🔧 调试 - LINKFLAGS: {env.get('LINKFLAGS', [])}")
            print(f"🔧 调试 - LIBPATH: {env.get('LIBPATH', [])}")
            print(f"🔧 调试 - LIBS: {env.get('LIBS', [])}")
        
        # 添加链接前的调试操作
        env.AddPreAction('$PROGPREFIX$PROGSUFFIX', debug_link_command)
        
        # 调试：检查链接器命令模板的各个部分
        print(f"🔧 调试 - LINKFLAGS: {env.get('LINKFLAGS', [])}")
        print(f"🔧 调试 - LIBPATH: {env.get('LIBPATH', [])}")
        print(f"🔧 调试 - LIBS: {env.get('LIBS', [])}")
    
    # 应用链接设置
    # 注意：不再使用env.Append(LIBS=libs)来避免Visual Studio运行时库问题
    # 但是需要将系统库列表设置到环境变量中，供自定义链接器命令生成器使用
    # 使用env['LIBS'] = libs而不是env.Append(LIBS=libs)来避免触发默认链接器行为
    env['LIBS'] = libs
    print(f"🔧 调试: 已设置系统库到环境变量LIBS: {libs}")
    
    # 注意：LIBPATH和LINKFLAGS已经在自定义链接器命令模板中处理
    # 避免使用env.Append，防止链接器使用默认命令生成器
    print("🔧 调试: 跳过env.Append调用，使用自定义链接器命令模板")
    
    # 注意：不要清空LIBS和LIBPATH变量，因为自定义链接器命令模板需要它们
    # 只禁用SCons的默认链接器命令生成器
    
    # 强制使用我们自定义的链接器命令模板
    # 确保SCons不会使用任何默认的链接器逻辑
    env['LINKCOMSTR'] = env['LINKCOM']  # 将命令模板设置为命令字符串
    
    # 禁用SCons的默认链接器命令生成器，但保留LIBS和LIBPATH变量
    env['_LINK'] = ''
    env['_SHLINK'] = ''
    env['_LIB'] = ''
    env['_SHLIB'] = ''
    
    # 禁用所有默认的链接器命令生成器
    env['LINK'] = env['LINKCOM']
    env['SHLINK'] = env['LINKCOM']
    env['LIB'] = ''
    env['SHLIB'] = ''
    
    # 清空环境变量中的LIB和INCLUDE，避免链接器自动查找Visual Studio路径
    # 但保留env['LIBS']和env['LIBPATH']，因为自定义链接器命令模板需要它们
    env['ENV']['LIB'] = ''  # 清空LIB环境变量
    env['ENV']['INCLUDE'] = ''  # 清空INCLUDE环境变量
    
    # 禁用SCons的自动库检测和添加功能
    env['_LIBFLAGS'] = ''
    env['_LIBDIRFLAGS'] = ''
    env['_CPPDEFFLAGS'] = ''
    env['_CPPINCFLAGS'] = ''
    
    print("🔧 调试: 已禁用SCons默认链接器行为，但保留LIBS和LIBPATH变量")
    
    print(f"🔧 链接器配置完成: {build_type}, {subsystem}")
    print(f"🔧 链接器标志: {linkflags}")
    print(f"🔧 系统库: {libs}")
    print(f"🔧 库目录: {lib_dirs}")
    
    return env, libs

# 使用预编译的依赖库函数
def use_prebuilt_dependencies(env, build_type):
    """使用预编译的Lexilla和Scintilla库（仅限Clang兼容格式）"""
    
    print(f"使用预编译依赖库 ({build_type})...")
    
    # 对于Clang编译器，只使用我们构建的.a格式库文件
    # 避免使用Visual Studio的.lib格式库，防止链接器冲突
    lexilla_built_path = os.path.join(lexilla_dir, 'bin', 'liblexilla.a')
    scintilla_built_path = os.path.join(scintilla_dir, 'bin', 'libscintilla.a')
    
    if os.path.exists(lexilla_built_path) and os.path.exists(scintilla_built_path):
        print("✅ 找到我们构建的Clang兼容依赖库文件（.a格式）:")
        print(f"   - {lexilla_built_path}")
        print(f"   - {scintilla_built_path}")
        
        # 使用我们构建的库文件路径（Clang兼容格式）
        lexilla_lib = lexilla_built_path
        scintilla_lib = scintilla_built_path
        return lexilla_lib, scintilla_lib
    else:
        print("❌ 未找到Clang兼容的依赖库文件")
        print("请确保以下文件存在:")
        print(f"   - {lexilla_built_path}")
        print(f"   - {scintilla_built_path}")
        
        # 如果找不到Clang兼容库，尝试构建它们
        print("⚠️ 警告: 未找到预编译库，尝试从源码构建...")
        
        # 创建库构建专用环境
        lib_env = env.Clone()
        
        # 添加编译选项 (C++20, MSVC兼容性)
        lib_env.Append(CXXFLAGS=[
            '-std=c++20', 
            '-fms-extensions', 
            '-fms-compatibility',
            '-Wno-deprecated-declarations',
            '-Wno-unknown-pragmas'
        ])
        
        # 根据构建类型添加优化选项
        if build_type == 'Release':
            lib_env.Append(CXXFLAGS=['-O2', '-flto', '-DNDEBUG'])
        else:
            lib_env.Append(CXXFLAGS=['-g', '-O0', '-DDEBUG'])
            
        lib_env.Append(CPPDEFINES=['SCI_NAMESPACE', 'STATIC_BUILD', '_CRT_SECURE_NO_WARNINGS'])
        lib_env.Append(CPPPATH=[
            os.path.join(lexilla_dir, 'include'),
            os.path.join(lexilla_dir, 'lexlib'),
            os.path.join(scintilla_dir, 'include'),
            os.path.join(scintilla_dir, 'src'),
            os.path.join(scintilla_dir, 'win32'),
            os.path.join(scintilla_dir, 'call')
        ])
        
        # 构建Lexilla
        lexilla_src = glob.glob(os.path.join(lexilla_dir, 'src', '*.cxx')) + \
                      glob.glob(os.path.join(lexilla_dir, 'lexlib', '*.cxx')) + \
                      glob.glob(os.path.join(lexilla_dir, 'lexers', '*.cxx'))
        
        print(f"🔧 构建Lexilla库 ({len(lexilla_src)} 源文件)...")
        lexilla_lib = lib_env.StaticLibrary(target=os.path.join(lexilla_dir, 'bin', 'liblexilla'), source=lexilla_src)
        
        # 构建Scintilla
        scintilla_src = glob.glob(os.path.join(scintilla_dir, 'src', '*.cxx')) + \
                        glob.glob(os.path.join(scintilla_dir, 'win32', '*.cxx')) + \
                        glob.glob(os.path.join(scintilla_dir, 'call', '*.cxx'))
        
        # 过滤掉ScintillaDLL.cxx（因为它包含DllMain）
        scintilla_src = [f for f in scintilla_src if 'ScintillaDLL.cxx' not in f]
        
        print(f"🔧 构建Scintilla库 ({len(scintilla_src)} 源文件)...")
        scintilla_lib = lib_env.StaticLibrary(target=os.path.join(scintilla_dir, 'bin', 'libscintilla'), source=scintilla_src)
        
        return lexilla_lib, scintilla_lib

# 获取构建类型（从环境变量或命令行参数）
build_type = 'Release'  # 默认为Release构建

# 检查环境变量
if 'BUILD_TYPE' in os.environ:
    build_type = os.environ['BUILD_TYPE']

# 检查命令行参数（使用ARGUMENTS字典）
if 'debug' in ARGUMENTS:
    build_type = 'Debug'
elif 'release' in ARGUMENTS:
    build_type = 'Release'

# 使用预编译的依赖库
lexilla_lib, scintilla_lib = use_prebuilt_dependencies(env, build_type)

# 配置链接器选项（设置LIBS等环境变量）
lib_paths = [
    project_root,  # 项目根目录
    obj_dir,  # 当前构建目录
]
env, libs = configure_link_options(env, 'WINDOWS', extra_lib_paths=lib_paths, lexilla_lib=lexilla_lib, scintilla_lib=scintilla_lib)

# 导出变量到SConscript
Export('project_root', 'src_dir', 'scintilla_dir', 'lexilla_dir', 'bin_dir', 'obj_dir')
Export('configure_build_options', 'configure_link_options', 'get_compiler_type')
Export('env', 'lexilla_lib', 'scintilla_lib', 'libs')

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