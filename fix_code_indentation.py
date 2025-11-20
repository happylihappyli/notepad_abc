#!/usr/bin/env python3
"""
修复WinMain.cpp中的代码缩进问题
"""
import re
from datetime import datetime

def fix_code_indentation():
    """修复代码缩进和语法问题"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始修复WinMain.cpp中的代码缩进...")
    
    winmain_path = "PowerEditor\\src\\winmain.cpp"
    backup_path = f"{winmain_path}.backup_indent_fix"
    
    try:
        # 创建备份
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 创建备份文件: {backup_path}")
        with open(winmain_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 查找并修复try块附近的代码
        # 问题在于第760行左右的代码缩进错误
        pattern = r'(\s*try\s*\{\s*\n)\s*notepad_plus_plus\.init\([^)]+\);\s*\n\s*allowPrivilegeMessages\([^)]+\);\s*\n\s*bool going = true;\s*\n\s*while \(going\)\s*\n\s*\{[^}]*while[^}]*\})\s*(\n\s*\}\s*\n\s*catch)'
        
        # 替换为正确格式的代码
        replacement = r'\1\n\t\tnotepad_plus_plus.init(hInstance, NULL, quotFileName.c_str(), &cmdLineParams);\n\n\t\tallowPrivilegeMessages(notepad_plus_plus, ver);\n\t\tbool going = true;\n\t\twhile (going)\n\t\t{\n\t\t\tgoing = ::GetMessageW(&msg, NULL, 0, 0) != 0;\n\t\t\tif (going)\n\t\t\t{\n\t\t\t\t// if the message doesn\'t belong to the notepad_plus_plus\'s dialog\n\t\t\t\tif (!notepad_plus_plus.isDlgsMsg(&msg))\n\t\t\t\t{\n\t\t\t\t\tif (::TranslateAccelerator(notepad_plus_plus.getHSelf(), notepad_plus_plus.getAccTable(), &msg) == 0)\n\t\t\t\t\t{\n\t\t\t\t\t\t::TranslateMessage(&msg);\n\t\t\t\t\t\t::DispatchMessageW(&msg);\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}\2'
        
        # 使用更精确的模式来定位问题代码
        fixed_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 如果替换没有生效，手动修复
        if fixed_content == content:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 使用手动修复方法...")
            
            # 查找try块开始位置
            try_pattern = r'(\s*try\s*\{)'
            try_match = re.search(try_pattern, content)
            
            if try_match:
                # 找到try块的位置
                try_start = try_match.start(1)
                before_try = content[:try_start]
                after_try = content[try_start:]
                
                # 手动构建正确的代码块
                correct_code = '''	try
	{
		notepad_plus_plus.init(hInstance, NULL, quotFileName.c_str(), &cmdLineParams);

		allowPrivilegeMessages(notepad_plus_plus, ver);
		bool going = true;
		while (going)
		{
			going = ::GetMessageW(&msg, NULL, 0, 0) != 0;
			if (going)
			{
				// if the message doesn't belong to the notepad_plus_plus's dialog
				if (!notepad_plus_plus.isDlgsMsg(&msg))
				{
					if (::TranslateAccelerator(notepad_plus_plus.getHSelf(), notepad_plus_plus.getAccTable(), &msg) == 0)
					{
						::TranslateMessage(&msg);
						::DispatchMessageW(&msg);
					}
				}
			}
		}
	}
'''
                
                # 查找catch块的位置
                catch_pattern = r'(\s*\}\s*\n\s*catch)'
                catch_match = re.search(catch_pattern, after_try)
                
                if catch_match:
                    catch_pos = catch_match.start(1)
                    before_catch = after_try[:catch_pos]
                    after_catch = after_try[catch_pos:]
                    
                    # 组合修复后的内容
                    fixed_content = before_try + correct_code + after_catch
                else:
                    fixed_content = content
            else:
                fixed_content = content
        
        # 写入修复后的内容
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 写入修复后的代码...")
        with open(winmain_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 代码缩进修复完成")
        return True
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 修复失败: {str(e)}")
        return False

def main():
    """主函数"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始代码缩进修复...")
    
    if fix_code_indentation():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 修复完成！")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 修复失败")

if __name__ == "__main__":
    main()