# -*- coding: utf-8 -*-
"""
构建Scintilla和Lexilla库的SCons脚本
"""

import os
import sys
from datetime import datetime

# 导入SCons
from SCons.Environment import Environment

# 获取环境变量
env = Environment()

# 设置基本环境变量
env['TARGET_ARCH'] = 'x86_64'  # 默认为64位
env['MSVC_VERSION'] = '14.3'   # VS2022
env['MSVS_VERSION'] = '2022'

# 设置项目路径
project_root = Dir('.').abspath
scintilla_dir = os.path.join(project_root, 'scintilla')
lexilla_dir = os.path.join(project_root, 'lexilla')
scintilla_src_dir = os.path.join(scintilla_dir, 'src')
scintilla_win32_dir = os.path.join(scintilla_dir, 'win32')
lexilla_src_dir = os.path.join(lexilla_dir, 'src')
bin_dir = os.path.join(project_root, 'bin')

# 确保输出目录存在
if not os.path.exists(bin_dir):
    os.makedirs(bin_dir)

# 构建Scintilla库
def build_scintilla(env):
    """构建Scintilla库"""
    print("开始构建Scintilla库...")
    
    # 创建Scintilla构建环境
    scintilla_env = env.Clone()
    
    # 设置编译选项
    scintilla_env.Append(CCFLAGS=[
        '/std:c++17',
        '/utf-8',
        '/EHsc',
        '/GR',
        '/W3',
        '/MP',
        '/MD',                # 使用多线程DLL运行时库，与主项目一致
    ])
    
    # 预处理器定义
    scintilla_env.Append(CPPDEFINES=[
        'WIN32',
        '_WINDOWS',
        'UNICODE',
        '_UNICODE',
        '_USRDLL',
        'SCI_LEXER',
        'SCI_OEMREG',
        '_CRT_SECURE_NO_WARNINGS',
        'STATIC_BUILD',          # 静态构建
        'SCI_DISABLE_AUTOMATICWORDSELECTION',
        'SCI_DISABLE_PROVISIONAL',
    ])
    
    # 包含目录
    scintilla_env.Append(CPPPATH=[
        os.path.join(scintilla_dir, 'include'),
        os.path.join(scintilla_dir, 'src'),
    ])
    
    # Scintilla源文件
    scintilla_src_files = [
        'AutoComplete.cxx',
        'CallTip.cxx',
        'CaseConvert.cxx',
        'CaseFolder.cxx',
        'CellBuffer.cxx',
        'ChangeHistory.cxx',
        'CharacterCategoryMap.cxx',
        'CharacterType.cxx',
        'CharClassify.cxx',
        'ContractionState.cxx',
        'DBCS.cxx',
        'Decoration.cxx',
        'Document.cxx',
        'EditModel.cxx',
        'Editor.cxx',
        'EditView.cxx',
        'Geometry.cxx',
        'Indicator.cxx',
        'KeyMap.cxx',
        'LineMarker.cxx',
        'MarginView.cxx',
        'PerLine.cxx',
        'PositionCache.cxx',
        'RESearch.cxx',
        'RunStyles.cxx',
        'Selection.cxx',
        'Style.cxx',
        'UndoHistory.cxx',
        'UniConversion.cxx',
        'UniqueString.cxx',
        'ViewStyle.cxx',
        'XPM.cxx',
        'ScintillaBase.cxx',  # 添加缺失的ScintillaBase.cxx
    ]
    
    # Windows特定源文件
    scintilla_win32_files = [
        'HanjaDic.cxx',
        'PlatWin.cxx',
        'ListBox.cxx',
        'SurfaceGDI.cxx',
        'SurfaceD2D.cxx',
        'ScintillaWin.cxx',
    ]
    
    # 添加完整路径
    scintilla_src_files = [os.path.join(scintilla_src_dir, f) for f in scintilla_src_files]
    scintilla_win32_files = [os.path.join(scintilla_win32_dir, f) for f in scintilla_win32_files]
    
    # 编译对象文件
    scintilla_objs = []
    for src in scintilla_src_files + scintilla_win32_files:
        obj = scintilla_env.Object(src)
        scintilla_objs.append(obj)
    
    # 构建静态库
    scintilla_lib = scintilla_env.StaticLibrary(
        target=os.path.join(bin_dir, 'libscintilla'),
        source=scintilla_objs
    )
    
    return scintilla_lib

# 构建Lexilla库
def build_lexilla(env):
    """构建Lexilla库"""
    print("开始构建Lexilla库...")
    
    # 创建Lexilla构建环境
    lexilla_env = env.Clone()
    
    # 设置编译选项
    lexilla_env.Append(CCFLAGS=[
        '/std:c++17',
        '/utf-8',
        '/EHsc',
        '/GR',
        '/W3',
        '/MP',
        '/MD',                # 使用多线程DLL运行时库，与主项目一致
    ])
    
    # 预处理器定义
    lexilla_env.Append(CPPDEFINES=[
        'WIN32',
        '_WINDOWS',
        'UNICODE',
        '_UNICODE',
        '_USRDLL',
        'SCI_LEXER',
        '_CRT_SECURE_NO_WARNINGS',
    ])
    
    # 包含目录
    lexilla_env.Append(CPPPATH=[
        os.path.join(lexilla_dir, 'include'),
        os.path.join(lexilla_dir, 'src'),
        os.path.join(lexilla_dir, 'lexlib'),
        os.path.join(scintilla_dir, 'include'),
    ])
    
    # Lexilla核心源文件
    lexilla_core_files = [
        'Lexilla.cxx',
    ]
    
    # Lexilla库源文件
    lexilla_lib_files = [
        'Accessor.cxx',
        'CharacterCategory.cxx',
        'CharacterSet.cxx',
        'DefaultLexer.cxx',
        'InList.cxx',
        'LexAccessor.cxx',
        'LexerBase.cxx',
        'LexerModule.cxx',
        'LexerSimple.cxx',
        'PropSetSimple.cxx',
        'StyleContext.cxx',
        'WordList.cxx',
    ]
    
    # 获取所有词法分析器文件
    lexers_dir = os.path.join(lexilla_dir, 'lexers')
    lexer_files = []
    if os.path.exists(lexers_dir):
        for file in os.listdir(lexers_dir):
            if file.startswith('Lex') and file.endswith('.cxx'):
                lexer_files.append(os.path.join(lexers_dir, file))
    
    # 添加完整路径
    lexilla_core_files = [os.path.join(lexilla_src_dir, f) for f in lexilla_core_files]
    lexilla_lib_files = [os.path.join(lexilla_dir, 'lexlib', f) for f in lexilla_lib_files]
    
    # 编译对象文件
    lexilla_objs = []
    for src in lexilla_core_files + lexilla_lib_files + lexer_files:
        obj = lexilla_env.Object(src)
        lexilla_objs.append(obj)
    
    # 构建静态库
    lexilla_lib = lexilla_env.StaticLibrary(
        target=os.path.join(bin_dir, 'liblexilla'),
        source=lexilla_objs
    )
    
    return lexilla_lib

# 构建库
scintilla_lib = build_scintilla(env)
lexilla_lib = build_lexilla(env)

# 默认目标
Default(scintilla_lib, lexilla_lib)

print("库构建完成时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))