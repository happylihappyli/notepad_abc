#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终WinMain函数修复工具
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def final_winmain_fix():
    """最终WinMain函数修复"""
    
    print("🔧 开始最终WinMain修复...")
    
    # 设置UTF-8环境
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    src_dir = Path("PowerEditor/src")
    winmain_backup = Path("winmain.cpp.backup_20251120_102931")
    winmain_file = src_dir / "winmain.cpp"
    
    # 步骤1: 恢复WinMain文件
    if winmain_backup.exists():
        print("🔄 恢复WinMain文件...")
        if winmain_file.exists():
            winmain_file.unlink()
        shutil.copy2(str(winmain_backup), str(winmain_file))
        print(f"✅ 已恢复: {winmain_file}")
    else:
        print("❌ 未找到WinMain备份文件")
        return False
    
    # 步骤2: 修复API兼容性问题
    print("🔧 修复API兼容性问题...")
    success = fix_api_issues(winmain_file)
    
    # 步骤3: 更新SConscript
    print("📝 更新SConscript...")
    update_sconscript_file()
    
    # 步骤4: 清理构建并重新编译
    print("🧹 清理并重新构建...")
    return clean_and_rebuild()

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
            
            # 添加必要的头文件
            version_helpers = """
#include <VersionHelpers.h>
"""
            
            # 在已有的#include后面添加VersionHelpers.h
            include_end = content.find('\n', content.find('#include'))
            if include_end != -1 and 'VersionHelpers.h' not in content:
                content = content[:include_end] + version_helpers + content[include_end:]
            
            # 添加Windows版本检查函数
            version_check = """
// Windows版本检查函数（兼容性修复）
bool IsWindows10OrGreater() {
    OSVERSIONINFOEX osvi = {0};
    osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);
    osvi.dwMajorVersion = 10;
    osvi.dwMinorVersion = 0;
    
    DWORDLONG dwlConditionMask = 0;
    VER_SET_CONDITION(dwlConditionMask, VER_MAJORVERSION, VER_GREATER_EQUAL);
    VER_SET_CONDITION(dwlConditionMask, VER_MINORVERSION, VER_GREATER_EQUAL);
    
    return VerifyVersionInfo(&osvi, VER_MAJORVERSION | VER_MINORVERSION, dwlConditionMask) != FALSE;
}

"""
            
            # 在wWinMain函数之前添加版本检查函数
            winmain_pos = content.find('int WINAPI wWinMain(')
            if winmain_pos != -1:
                content = content[:winmain_pos] + version_check + content[winmain_pos:]
                print("  ✅ 已添加Windows版本检查函数")
            
            # 替换DPI感知调用
            dpi_fix = """// 设置DPI感知（兼容性修复）
    if (IsWindows10OrGreater()) {
        SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    } else {
        SetProcessDPIAware();
    }"""
            
            # 查找并替换SetProcessDpiAwarenessContext调用
            import re
            pattern = r'SetProcessDpiAwarenessContext\([^)]+\);'
            content = re.sub(pattern, dpi_fix, content)
            print("  ✅ 已修复DPI感知API调用")
        
        # 如果有修改，写回文件
        if content != original_content:
            print("  ✅ 写入修复后的文件...")
            with open(winmain_file, 'w', encoding='utf-8-sig') as f:
                f.write(content)
        else:
            print("  ℹ️ 无需修改")
            
        return True
            
    except Exception as e:
        print(f"  ⚠️ API修复出错: {e}")
        return False

def update_sconscript_file():
    """更新SConscript文件"""
    
    sconscript_file = Path("SConscript")
    
    if not sconscript_file.exists():
        print("  ❌ SConscript文件不存在")
        return False
    
    try:
        with open(sconscript_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 确保winmain.cpp在源文件列表中
        if '"winmain.cpp"' not in content:
            print("  📝 添加winmain.cpp到构建列表...")
            
            # 查找源文件列表的位置
            source_start = content.find('source = [')
            if source_start != -1:
                source_end = content.find(']', source_start)
                if source_end != -1:
                    # 在源文件列表中添加winmain.cpp
                    before_sources = content[source_start:source_start + len('source = [')]
                    after_sources = content[source_start + len('source = ['):source_end]
                    
                    new_sources = after_sources.strip()
                    if new_sources and not new_sources.startswith('"'):
                        new_sources = '    "winmain.cpp",\n    ' + new_sources
                    else:
                        new_sources = '"winmain.cpp",\n' + new_sources
                    
                    new_source_section = before_sources + new_sources + ']'
                    content = content[:source_start] + new_source_section + content[source_end + 1:]
                    
                    with open(sconscript_file, 'w', encoding='utf-8-sig') as f:
                        f.write(content)
                    
                    print("  ✅ 已更新SConscript文件")
                else:
                    print("  ❌ 无法找到源文件列表的结束位置")
                    return False
            else:
                print("  ❌ 无法找到源文件列表")
                return False
        else:
            print("  ℹ️ winmain.cpp已在构建列表中")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 更新SConscript失败: {e}")
        return False

def clean_and_rebuild():
    """清理并重新构建"""
    
    try:
        # 清理构建缓存
        print("  🧹 清理构建缓存...")
        for obj_dir in ['obj', 'bin']:
            if Path(obj_dir).exists():
                # 只清理obj文件，保留exe文件
                if obj_dir == 'bin':
                    for file in Path(obj_dir).glob("*.obj"):
                        file.unlink()
                    print(f"    ✅ 已清理{obj_dir}目录中的obj文件")
                else:
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
        
        print(f"    构建退出代码: {result.returncode}")
        
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
    print("🔧 Notepad++ ABC 最终WinMain修复工具")
    print("="*60)
    
    success = final_winmain_fix()
    
    if success:
        print("\n" + "="*60)
        print("🎉 修复完成！现在程序应该能正常显示GUI窗口了")
        print("📝 建议运行测试脚本验证GUI窗口显示")
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