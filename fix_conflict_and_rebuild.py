#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复WinMain函数冲突并重新构建
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def fix_winmain_conflict():
    """修复WinMain函数冲突并重新构建"""
    
    print("🔧 开始修复WinMain函数冲突...")
    
    # 设置UTF-8环境
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # 路径定义
    src_dir = Path("PowerEditor/src")
    winmain_file = src_dir / "winmain.cpp"
    backup_file = src_dir / "winmain.cpp.backup_1763605589"
    
    print("📁 路径信息:")
    print(f"  - 源文件目录: {src_dir}")
    print(f"  - WinMain文件: {winmain_file}")
    print(f"  - 备份文件: {backup_file}")
    
    # 步骤1: 删除冲突的WinMain.cpp文件
    if winmain_file.exists():
        print("🗑️  删除冲突的WinMain.cpp文件...")
        winmain_file.unlink()
    
    # 步骤2: 重命名backup文件为winmain.cpp
    if backup_file.exists():
        print("🔄 重命名备份文件为winmain.cpp...")
        if winmain_file.exists():
            winmain_file.unlink()
        shutil.move(str(backup_file), str(winmain_file))
    
    # 步骤3: 修复API兼容性问题
    print("🔧 修复API兼容性问题...")
    fix_api_compatibility(winmain_file)
    
    # 步骤4: 更新SConscript文件
    print("📝 更新SConscript构建配置...")
    update_sconscript()
    
    # 步骤5: 清理并重新构建
    print("🧹 清理构建缓存...")
    clean_build()
    
    print("🏗️  开始重新构建...")
    return rebuild_project()

def fix_api_compatibility(winmain_file):
    """修复API兼容性问题"""
    
    with open(winmain_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 修复SetProcessDpiAwarenessContext调用（Windows 10 1607+才支持）
    old_api = "SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);"
    new_api = """// 设置DPI感知（兼容性修复）
#ifdef _WIN32_WINNT_WIN10
    if (IsWindows10OrGreater()) {
        SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    } else {
        SetProcessDPIAware();
    }
#else
    SetProcessDPIAware();
#endif"""
    
    if old_api in content:
        print("  ✅ 修复DPI感知API调用...")
        content = content.replace(old_api, new_api)
    
    # 添加Windows版本检查函数
    add_version_check = """
// Windows版本检查函数
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
    if "IsWindows10OrGreater" not in content:
        # 找到wWinMain函数定义位置
        winmain_pos = content.find("int WINAPI wWinMain(")
        if winmain_pos != -1:
            print("  ✅ 添加Windows版本检查函数...")
            content = content[:winmain_pos] + add_version_check + content[winmain_pos:]
    
    with open(winmain_file, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    print("  ✅ API兼容性修复完成")

def update_sconscript():
    """更新SConscript构建配置"""
    
    sconscript_file = Path("SConscript")
    
    if not sconscript_file.exists():
        print("  ❌ SConscript文件不存在")
        return False
    
    with open(sconscript_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 确保winmain.cpp在源文件列表中
    if '"WinMain.cpp"' not in content:
        print("  ✅ 添加WinMain.cpp到构建列表...")
        
        # 查找源文件列表的位置
        source_start = content.find('source = [')
        if source_start != -1:
            # 在源文件列表中添加WinMain.cpp
            source_section = content[source_start:content.find(']', source_start) + 1]
            
            # 在源文件列表的开头添加WinMain.cpp
            old_source = 'source = ['
            new_source = 'source = [\n    "WinMain.cpp",'
            
            content = content.replace(source_section, new_source + source_section[len(old_source):])
    
    with open(sconscript_file, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    print("  ✅ SConscript更新完成")
    return True

def clean_build():
    """清理构建缓存"""
    
    # 清理obj目录
    if Path("obj").exists():
        shutil.rmtree("obj")
        print("  🧹 已清理obj目录")
    
    # 清理bin目录（保留exe）
    bin_dir = Path("bin")
    if bin_dir.exists():
        for file in bin_dir.glob("*.obj"):
            file.unlink()
        print("  🧹 已清理bin目录中的obj文件")

def rebuild_project():
    """重新构建项目"""
    
    try:
        # 使用UTF-8编码构建
        result = subprocess.run(
            ["chcp", "65001", "&&", "scons"],
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ 构建成功！")
            
            # 检查exe文件是否存在
            exe_files = list(Path("bin").glob("*.exe"))
            if exe_files:
                print(f"✅ 生成的可执行文件:")
                for exe in exe_files:
                    print(f"  - {exe}")
                return True
            else:
                print("⚠️ 构建成功但未找到exe文件")
                return False
        else:
            print("❌ 构建失败:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def main():
    """主函数"""
    
    print("="*60)
    print("🔧 Notepad++ ABC WinMain冲突修复工具")
    print("="*60)
    
    success = fix_winmain_conflict()
    
    if success:
        print("\n" + "="*60)
        print("🎉 修复完成！程序现在应该能正常显示GUI窗口了")
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