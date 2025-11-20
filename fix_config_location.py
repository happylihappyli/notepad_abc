#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件位置修复脚本 - 将配置文件复制到正确位置
"""

import os
import shutil
from pathlib import Path

def fix_config_location():
    """修复配置文件位置"""
    print("=== 配置文件位置修复 ===")
    
    # 源目录和目标目录
    source_dir = Path("bin")
    target_dir = Path(".")
    target_config_dir = target_dir / "config"
    
    # 确保目标config目录存在
    target_config_dir.mkdir(exist_ok=True)
    
    # 需要复制的配置文件
    config_files = [
        "config.xml",
        "nativeLang.xml", 
        "shortcuts.xml",
        "stylers.xml",
        "contextMenu.xml",
        "doLocalConf.xml",
        "langs.xml",
        "langs.model.xml",
        "stylers.model.xml"
    ]
    
    print("配置文件复制:")
    copied_files = []
    missing_files = []
    
    for config_file in config_files:
        source_path = source_dir / config_file
        target_path = target_config_dir / config_file
        
        if source_path.exists():
            try:
                # 复制文件
                shutil.copy2(source_path, target_path)
                print(f"   ✓ {config_file}")
                copied_files.append(config_file)
            except Exception as e:
                print(f"   ✗ {config_file} - 复制失败: {e}")
        else:
            print(f"   ! {config_file} - 源文件不存在")
            missing_files.append(config_file)
    
    # 复制themes目录
    source_themes_dir = source_dir / "themes"
    target_themes_dir = target_dir / "themes"
    
    if source_themes_dir.exists():
        try:
            if target_themes_dir.exists():
                shutil.rmtree(target_themes_dir)
            shutil.copytree(source_themes_dir, target_themes_dir)
            print("   ✓ themes/ 目录")
        except Exception as e:
            print(f"   ✗ themes/ 目录 - 复制失败: {e}")
    else:
        print("   ! themes/ 目录不存在")
    
    # 复制plugins目录
    source_plugins_dir = source_dir / "plugins"
    target_plugins_dir = target_dir / "plugins"
    
    if source_plugins_dir.exists():
        try:
            if target_plugins_dir.exists():
                shutil.rmtree(target_plugins_dir)
            shutil.copytree(source_plugins_dir, target_plugins_dir)
            print("   ✓ plugins/ 目录")
        except Exception as e:
            print(f"   ✗ plugins/ 目录 - 复制失败: {e}")
    else:
        print("   ! plugins/ 目录不存在")
    
    # 也将config文件复制到根目录（兼容一些程序）
    for config_file in ["config.xml", "nativeLang.xml", "shortcuts.xml", "stylers.xml"]:
        source_path = source_dir / config_file
        target_path = target_dir / config_file
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, target_path)
                print(f"   ✓ 根目录 {config_file}")
            except Exception as e:
                print(f"   ! 根目录 {config_file} - 复制失败: {e}")
    
    print(f"\n修复结果:")
    print(f"   成功复制: {len(copied_files)} 个文件")
    print(f"   缺失文件: {len(missing_files)} 个文件")
    
    if missing_files:
        print(f"   缺失文件列表: {', '.join(missing_files)}")
    
    return len(copied_files), len(missing_files)

def verify_config_files():
    """验证配置文件"""
    print("\n=== 配置文件验证 ===")
    
    # 检查根目录和config目录中的重要文件
    important_files = [
        "config.xml",
        "nativeLang.xml", 
        "shortcuts.xml",
        "stylers.xml",
        "contextMenu.xml"
    ]
    
    config_dir = Path("config")
    
    for config_file in important_files:
        root_file = Path(config_file)
        config_file_path = config_dir / config_file
        
        root_exists = root_file.exists()
        config_exists = config_file_path.exists()
        
        if root_exists or config_exists:
            print(f"   ✓ {config_file} - 找到")
        else:
            print(f"   ✗ {config_file} - 缺失")

def test_startup_after_fix():
    """修复后测试启动"""
    print("\n=== 修复后启动测试 ===")
    
    executable = Path("bin/notepad_abc_new.exe")
    if not executable.exists():
        executable = Path("notepad_abc_new.exe")
    
    if not executable.exists():
        print("   ✗ 可执行文件不存在")
        return
    
    print(f"   准备测试: {executable}")
    
    # 检查工作目录结构
    print("   工作目录结构:")
    for item in Path(".").iterdir():
        if item.is_dir():
            print(f"     📁 {item.name}/")
        else:
            print(f"     📄 {item.name}")
    
    print("\n   配置文件检查:")
    for config_file in ["config.xml", "nativeLang.xml", "shortcuts.xml", "stylers.xml"]:
        if Path(config_file).exists():
            print(f"     ✓ {config_file}")
        elif Path("config/" + config_file).exists():
            print(f"     ✓ config/{config_file}")
        else:
            print(f"     ✗ {config_file} (缺失)")

def main():
    print("修复配置文件位置问题")
    print("工作目录:", os.getcwd())
    print()
    
    # 1. 修复配置文件位置
    copied, missing = fix_config_location()
    
    # 2. 验证配置文件
    verify_config_files()
    
    # 3. 测试启动
    test_startup_after_fix()
    
    print("\n=== 修复完成 ===")
    if missing == 0:
        print("✓ 所有重要配置文件已就位")
        print("现在可以尝试运行程序了!")
    else:
        print(f"⚠ 仍有 {missing} 个文件缺失，可能影响程序运行")

if __name__ == "__main__":
    main()