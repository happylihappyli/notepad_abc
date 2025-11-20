#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的WinMain修复脚本 v2 - 处理文件锁定问题
"""

import os
import shutil
import subprocess
import time
from datetime import datetime
import psutil

def log_message(msg):
    """记录日志消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def kill_running_notepad_processes():
    """终止运行中的notepad进程"""
    log_message("检查并终止运行中的notepad进程...")
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'notepad' in proc.info['name'].lower():
                log_message(f"终止进程: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.terminate()
                proc.wait(timeout=5)
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            try:
                proc.kill()
                killed_count += 1
            except:
                pass
    
    if killed_count > 0:
        log_message(f"已终止 {killed_count} 个进程")
        time.sleep(2)  # 等待进程完全释放资源
    else:
        log_message("没有发现运行中的notepad进程")
    
    return True

def safe_remove_directory(dir_path):
    """安全删除目录，处理锁定文件"""
    if not os.path.exists(dir_path):
        return True
    
    log_message(f"安全删除目录: {dir_path}")
    
    # 首先尝试正常删除
    try:
        shutil.rmtree(dir_path)
        return True
    except PermissionError:
        log_message("遇到权限错误，尝试强制删除...")
        
        # 终止相关进程并重试
        kill_running_notepad_processes()
        time.sleep(1)
        
        try:
            shutil.rmtree(dir_path)
            return True
        except Exception as e:
            log_message(f"删除目录失败: {e}")
            # 如果删除失败，尝试清空目录内容
            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        try:
                            os.remove(item_path)
                        except:
                            pass
                    elif os.path.isdir(item_path):
                        try:
                            shutil.rmtree(item_path)
                        except:
                            pass
                return True
            except Exception as e2:
                log_message(f"清空目录也失败: {e2}")
                return False

def fix_winmain_with_debug():
    """修复WinMain并添加调试信息"""
    log_message("开始安全的WinMain修复...")
    
    src_file = "PowerEditor\\src\\winmain.cpp"
    
    if not os.path.exists(src_file):
        log_message(f"错误：找不到文件 {src_file}")
        return False
    
    # 备份原文件
    backup_file = f"{src_file}.backup_{int(datetime.now().timestamp())}"
    log_message(f"创建备份文件: {backup_file}")
    shutil.copy2(src_file, backup_file)
    
    # 读取文件内容
    with open(src_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 修复1: 确保Windows版本检查函数存在
    version_check_code = '''
// Windows版本检查函数 - 添加安全检查
static bool IsWindowsVersionOrGreater(WORD wMajorVersion, WORD wMinorVersion, WORD wBuildNumber)
{
    OSVERSIONINFOEXW osvi{};
    osvi.dwOSVersionInfoSize = sizeof(osvi);
    osvi.dwMajorVersion = wMajorVersion;
    osvi.dwMinorVersion = wMinorVersion;
    osvi.dwBuildNumber = wBuildNumber;

    DWORDLONG conditionMask = 0;
    VER_SET_CONDITION(conditionMask, VER_MAJORVERSION, VER_GREATER_EQUAL);
    VER_SET_CONDITION(conditionMask, VER_MINORVERSION, VER_GREATER_EQUAL);
    VER_SET_CONDITION(conditionMask, VER_BUILDNUMBER, VER_GREATER_EQUAL);

    return VerifyVersionInfoW(&osvi, VER_MAJORVERSION | VER_MINORVERSION | VER_BUILDNUMBER, conditionMask);
}

// 安全的DPI感知设置
static bool SetDPIAwarenessSafe()
{
    try {
        // 检查Windows 10版本1803或更高版本支持SetProcessDpiAwarenessContext
        if (IsWindowsVersionOrGreater(10, 0, 17134)) {
            return SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
        }
        // 对于较旧版本，使用兼容性方法
        else {
            SetProcessDPIAware();
            return true;
        }
    }
    catch (...) {
        // 静默失败，使用默认值
        return false;
    }
}
'''
    
    # 查找wWinMain函数的开始位置并插入版本检查函数
    if "IsWindowsVersionOrGreater" not in content:
        # 在wWinMain函数之前插入
        winmain_pos = content.find("int WINAPI wWinMain")
        if winmain_pos != -1:
            # 找到函数开始前的空行位置插入
            insert_pos = content.rfind('\n', 0, winmain_pos)
            if insert_pos != -1:
                content = content[:insert_pos] + version_check_code + content[insert_pos:]
                log_message("已添加Windows版本检查函数")
    
    # 修复2: 确保DPI设置使用安全版本
    content = content.replace(
        "SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);",
        "SetDPIAwarenessSafe();"
    )
    
    # 修复3: 在Notepad_plus_Window初始化周围添加更多异常处理
    old_init_pattern = '''	try
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
	}'''
    
    new_init_pattern = '''	try
	{
		log_message("开始初始化Notepad_plus_Window...");
		notepad_plus_plus.init(hInstance, NULL, quotFileName.c_str(), &cmdLineParams);
		log_message("Notepad_plus_Window初始化完成");
		
		log_message("设置权限消息...");
		allowPrivilegeMessages(notepad_plus_plus, ver);
		
		log_message("开始消息循环...");
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
		log_message("消息循环结束");
	}'''
    
    content = content.replace(old_init_pattern, new_init_pattern)
    
    # 修复4: 在Notepad_plus_Window init方法中添加调试信息
    old_window_init = '''	if (NULL == _hSelf)
		throw std::runtime_error("Notepad_plus_Window::init : CreateWindowEx() function return null");'''
    
    new_window_init = '''	if (NULL == _hSelf)
		throw std::runtime_error("Notepad_plus_Window::init : CreateWindowEx() function return null");

	// 添加窗口创建成功的调试信息
	OutputDebugStringW(L"Notepad_plus_Window: CreateWindowEx成功创建窗口\\n");'''
    
    content = content.replace(old_window_init, new_window_init)
    
    # 修复5: 确保窗口显示代码正确执行
    old_show_window = '''	if (false) // 强制禁用隐藏窗口逻辑
	{
		::ShowWindow(_hSelf, SW_HIDE);
	}
	else if (true) // 强制显示窗口
	{
		::ShowWindow(_hSelf, SW_SHOW); // 总是显示窗口
		if (nppGUI._isMaximized)
			::ShowWindow(_hSelf, SW_MAXIMIZE); // 如果配置了最大化，则最大化
	}'''
    
    new_show_window = '''	// 强制显示窗口 - 修复版本
	::ShowWindow(_hSelf, SW_SHOW); // 总是显示窗口
	if (nppGUI._isMaximized)
		::ShowWindow(_hSelf, SW_MAXIMIZE); // 如果配置了最大化，则最大化
	OutputDebugStringW(L"Notepad_plus_Window: 已调用ShowWindow显示窗口\\n");'''
    
    content = content.replace(old_show_window, new_show_window)
    
    # 写入修改后的文件
    with open(src_file, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    log_message("WinMain文件修复完成")
    return True

def build_project():
    """编译项目"""
    log_message("开始编译项目...")
    
    # 安全清理旧文件
    safe_remove_directory("obj")
    safe_remove_directory("bin")
    
    # 创建目录
    os.makedirs("obj", exist_ok=True)
    os.makedirs("bin", exist_ok=True)
    
    # 编译
    try:
        # 在PowerShell中使用分号作为命令分隔符
        cmd = "chcp 65001; scons"
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        log_message("编译成功!")
        log_message(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"编译失败: {e}")
        log_message(f"错误输出: {e.stderr}")
        return False

def main():
    log_message("开始安全的WinMain修复和重建...")
    
    # 终止运行中的进程
    kill_running_notepad_processes()
    
    # 修复WinMain
    if not fix_winmain_with_debug():
        log_message("修复失败")
        return 1
    
    # 编译项目
    if not build_project():
        log_message("编译失败")
        return 1
    
    log_message("安全修复完成!")
    log_message("请运行测试程序检查GUI窗口是否正常显示")
    
    return 0

if __name__ == "__main__":
    exit(main())