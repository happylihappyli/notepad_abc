#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单WinMain函数修复工具
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def simple_winmain_fix():
    """简单修复WinMain函数并重新构建"""
    
    print("🔧 开始简单WinMain修复...")
    
    # 设置UTF-8环境
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    src_dir = Path("PowerEditor/src")
    winmain_file = src_dir / "winmain.cpp"
    backup_file = src_dir / "winmain.cpp.backup_1763605589"
    
    # 步骤1: 找到实际的WinMain文件
    actual_winmain_file = find_actual_winmain_file(src_dir)
    if not actual_winmain_file:
        print("❌ 未找到WinMain文件，尝试使用备份...")
        if backup_file.exists():
            actual_winmain_file = backup_file
            print(f"✅ 使用备份文件: {actual_winmain_file}")
        else:
            print("❌ 无可用的WinMain文件")
            return False
    
    print(f"✅ 找到WinMain文件: {actual_winmain_file}")
    
    # 步骤2: 修复API兼容性问题
    print("🔧 修复API兼容性问题...")
    fix_api_issues(actual_winmain_file)
    
    # 步骤3: 清理构建并重新编译
    print("🧹 清理并重新构建...")
    return clean_and_rebuild()

def find_actual_winmain_file(src_dir):
    """查找实际的WinMain文件"""
    
    # 查找所有可能的主入口文件
    possible_files = [
        src_dir / "winmain.cpp",
        src_dir / "WinMain.cpp",
        src_dir / "main.cpp",
        src_dir / "Main.cpp"
    ]
    
    for file in possible_files:
        if file.exists():
            # 检查文件内容是否包含WinMain函数
            try:
                with open(file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    content = f.read()
                    if 'wWinMain' in content or 'WinMain' in content:
                        print(f"✅ 找到包含WinMain函数的文件: {file}")
                        return file
            except:
                continue
    
    return None

def fix_api_issues(winmain_file):
    """修复API兼容性问题"""
    
    try:
        # 读取文件内容
        with open(winmain_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 修复SetProcessDpiAwarenessContext问题
        if 'SetProcessDpiAwarenessContext' in content:
            print("  🔧 修复DPI感知API调用...")
            
            # 添加Windows版本检查函数
            version_check = """
// Windows版本检查函数（兼容性修复）
bool IsWindows10OrGreater() {
#ifdef _WIN32_WINNT_WIN10
    OSVERSIONINFOEX osvi = {0};
    osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);
    osvi.dwMajorVersion = 10;
    osvi.dwMinorVersion = 0;
    
    DWORDLONG dwlConditionMask = 0;
    VER_SET_CONDITION(dwlConditionMask, VER_MAJORVERSION, VER_GREATER_EQUAL);
    VER_SET_CONDITION(dwlConditionMask, VER_MINORVERSION, VER_GREATER_EQUAL);
    
    return VerifyVersionInfo(&osvi, VER_MAJORVERSION | VER_MINORVERSION, dwlConditionMask) != FALSE;
#else
    return false; // 不支持版本检查，使用旧方法
#endif
}

"""
            
            # 查找wWinMain函数定义位置
            winmain_pos = content.find('int WINAPI wWinMain(')
            if winmain_pos != -1:
                # 在wWinMain函数之前添加版本检查函数
                content = content[:winmain_pos] + version_check + content[winmain_pos:]
            
            # 替换DPI感知调用
            dpi_fix = """// 设置DPI感知（兼容性修复）
#ifdef _WIN32_WINNT_WIN10
    if (IsWindows10OrGreater()) {
        SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    } else {
        SetProcessDPIAware();
    }
#else
    SetProcessDPIAware();
#endif"""
            
            # 查找并替换所有DPI感知调用
            import re
            pattern = r'SetProcessDpiAwarenessContext\([^)]+\);'
            content = re.sub(pattern, dpi_fix, content)
        
        # 2. 添加必要的头文件
        headers_to_add = """
#ifdef _WIN32_WINNT_WIN10
#include <VersionHelpers.h>
#endif
"""
        
        if 'VersionHelpers.h' not in content and '#include' in content:
            # 在第一个#include后添加
            include_pos = content.find('#include')
            if include_pos != -1:
                # 找到include块的结束位置
                next_include = content.find('#include', include_pos + 1)
                if next_include == -1:
                    # 只有一行include
                    include_end = content.find('\n', include_pos)
                    if include_end != -1:
                        content = content[:include_end] + headers_to_add + content[include_end:]
        
        # 如果有修改，写回文件
        if content != original_content:
            print("  ✅ API修复完成，写入文件...")
            with open(winmain_file, 'w', encoding='utf-8-sig') as f:
                f.write(content)
        else:
            print("  ℹ️ 无需修改")
            
    except Exception as e:
        print(f"  ⚠️ API修复出错: {e}")
        # 即使修复失败，也继续尝试构建

def clean_and_rebuild():
    """清理并重新构建"""
    
    try:
        # 清理构建缓存
        print("  🧹 清理构建缓存...")
        for obj_dir in ['obj', 'bin']:
            if Path(obj_dir).exists():
                shutil.rmtree(obj_dir)
                print(f"    ✅ 已清理{obj_dir}目录")
        
        # 重新构建
        print("  🏗️ 开始重新构建...")
        result = subprocess.run(
            "chcp 65001 && scons",
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("  ✅ 构建成功！")
            
            # 检查exe文件
            exe_files = list(Path("bin").glob("*.exe"))
            if exe_files:
                print(f"  ✅ 生成的可执行文件:")
                for exe in exe_files:
                    print(f"    - {exe}")
                return True
            else:
                print("  ⚠️ 构建成功但未找到exe文件")
                return False
        else:
            print("  ❌ 构建失败:")
            print(f"    stdout: {result.stdout}")
            print(f"    stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ 构建过程出错: {e}")
        return False

def main():
    """主函数"""
    
    print("="*60)
    print("🔧 Notepad++ ABC 简单WinMain修复工具")
    print("="*60)
    
    success = simple_winmain_fix()
    
    if success:
        print("\n" + "="*60)
        print("🎉 修复完成！现在程序应该能正常显示GUI窗口了")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("❌ 修复失败，请检查错误信息")
        print("="*60)
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        sys.exit(1)