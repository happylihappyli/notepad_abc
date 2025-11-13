#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查配置文件中的documentList设置
"""

import os
import xml.etree.ElementTree as ET

def check_documentlist_config():
    """检查配置文件中的documentList设置"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"检查配置文件: {config_path}")
    
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
        
        # 查找GUI配置
        for gui_config in root.iter():
            if gui_config.tag == "GUIConfig" and gui_config.get("name") == "":
                print("✓ 找到GUI配置")
                
                # 检查documentList设置
                document_list = gui_config.get("documentList")
                if document_list:
                    print(f"documentList设置: {document_list}")
                    if document_list.lower() == "yes":
                        print("✓ documentList设置为yes")
                        return True
                    else:
                        print("✗ documentList设置为no")
                        return False
                else:
                    print("✗ 未找到documentList设置")
                    return False
        
        print("✗ 未找到GUI配置")
        return False
        
    except Exception as e:
        print(f"✗ 检查配置文件失败: {e}")
        return False

def fix_documentlist_config():
    """修复配置文件中的documentList设置"""
    config_path = os.path.join(os.getenv("APPDATA"), "Notepad++", "config.xml")
    
    if not os.path.exists(config_path):
        print("✗ 配置文件不存在")
        return False
    
    print(f"修复配置文件: {config_path}")
    
    try:
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已存在documentList设置
        if 'documentList="' in content:
            # 替换现有的documentList设置
            if 'documentList="no"' in content:
                content = content.replace('documentList="no"', 'documentList="yes"')
                print("✓ 已将documentList从no改为yes")
            elif 'documentList="yes"' in content:
                print("✓ documentList已经是yes")
                return True
        else:
            # 在GUIConfig标签中添加documentList设置
            if '<GUIConfig name="">' in content:
                content = content.replace('<GUIConfig name="">', '<GUIConfig name="" documentList="yes">')
                print("✓ 已添加documentList='yes'设置")
            else:
                print("✗ 未找到GUIConfig标签")
                return False
        
        # 创建备份
        backup_path = config_path + '.documentlist.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 已创建备份: {backup_path}")
        
        # 保存修改后的配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ 配置文件已保存")
        
        return True
        
    except Exception as e:
        print(f"✗ 修复配置文件失败: {e}")
        return False

if __name__ == "__main__":
    print("检查配置文件中的documentList设置")
    print("=" * 60)
    
    # 检查当前设置
    if not check_documentlist_config():
        print("\n尝试修复documentList设置...")
        if fix_documentlist_config():
            print("\n✓ 修复成功")
            
            # 重新检查
            print("\n重新检查设置...")
            check_documentlist_config()
        else:
            print("\n✗ 修复失败")
    else:
        print("\n✓ documentList设置正确")
    
    print("\n=== 检查完成 ===")