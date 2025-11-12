#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理源码中的obj文件，将所有编译产生的obj文件统一放到obj目录
"""

import os
import shutil
import glob

def clean_obj_files():
    """清理所有分散的obj文件，统一移动到obj目录"""
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    obj_dir = os.path.join(project_root, 'obj')
    
    # 确保obj目录存在
    if not os.path.exists(obj_dir):
        os.makedirs(obj_dir)
    
    print("开始清理obj文件...")
    
    # 查找所有.obj文件
    obj_files = []
    
    # 搜索整个项目目录中的.obj文件
    for root, dirs, files in os.walk(project_root):
        # 跳过obj目录本身，避免重复移动
        if 'obj' in dirs and os.path.abspath(os.path.join(root, 'obj')) == obj_dir:
            dirs.remove('obj')
        
        for file in files:
            if file.lower().endswith('.obj'):
                obj_path = os.path.join(root, file)
                obj_files.append(obj_path)
    
    print(f"找到 {len(obj_files)} 个obj文件")
    
    # 移动obj文件到统一目录
    moved_count = 0
    for obj_path in obj_files:
        try:
            # 获取相对路径，用于在obj目录中保持目录结构
            relative_path = os.path.relpath(obj_path, project_root)
            # 在obj目录中创建相同的目录结构
            target_dir = os.path.join(obj_dir, os.path.dirname(relative_path))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            # 目标文件路径
            target_path = os.path.join(obj_dir, relative_path)
            
            # 移动文件
            shutil.move(obj_path, target_path)
            print(f"移动: {relative_path} -> obj/{relative_path}")
            moved_count += 1
            
        except Exception as e:
            print(f"移动失败 {obj_path}: {e}")
    
    print(f"\n成功移动 {moved_count} 个obj文件到obj目录")
    
    # 清理空目录
    print("\n清理空目录...")
    empty_dirs_cleaned = 0
    for root, dirs, files in os.walk(project_root, topdown=False):
        # 跳过obj目录和.git目录
        if 'obj' in root or '.git' in root:
            continue
            
        if not files and not dirs:
            try:
                os.rmdir(root)
                print(f"删除空目录: {os.path.relpath(root, project_root)}")
                empty_dirs_cleaned += 1
            except Exception as e:
                print(f"删除目录失败 {root}: {e}")
    
    print(f"清理了 {empty_dirs_cleaned} 个空目录")
    
    # 检查scintilla和lexilla目录中的obj文件
    print("\n检查scintilla和lexilla目录中的obj文件...")
    scintilla_obj_dirs = []
    lexilla_obj_dirs = []
    
    # 查找scintilla目录中的obj相关目录
    scintilla_root = os.path.join(project_root, 'scintilla')
    if os.path.exists(scintilla_root):
        for root, dirs, files in os.walk(scintilla_root):
            if 'Intermediates' in root or any(f.endswith('.obj') for f in files):
                scintilla_obj_dirs.append(root)
    
    # 查找lexilla目录中的obj相关目录
    lexilla_root = os.path.join(project_root, 'lexilla')
    if os.path.exists(lexilla_root):
        for root, dirs, files in os.walk(lexilla_root):
            if any(f.endswith('.obj') for f in files):
                lexilla_obj_dirs.append(root)
    
    print(f"scintilla中发现 {len(scintilla_obj_dirs)} 个包含obj文件的目录")
    print(f"lexilla中发现 {len(lexilla_obj_dirs)} 个包含obj文件的目录")
    
    return moved_count, empty_dirs_cleaned

def main():
    """主函数"""
    print("=" * 60)
    print("清理obj文件工具")
    print("=" * 60)
    
    try:
        moved_count, empty_dirs_cleaned = clean_obj_files()
        
        print("\n" + "=" * 60)
        print("清理完成!")
        print(f"- 移动了 {moved_count} 个obj文件到obj目录")
        print(f"- 清理了 {empty_dirs_cleaned} 个空目录")
        print("=" * 60)
        
    except Exception as e:
        print(f"清理过程中出现错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())