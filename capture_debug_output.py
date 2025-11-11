#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
捕获调试输出脚本
用于捕获OutputDebugString输出的调试信息
"""

import ctypes
from ctypes import wintypes
import sys
import time

# 定义Windows API函数
dbghelp = ctypes.windll.dbghelp
kernel32 = ctypes.windll.kernel32

# 定义常量
DBWIN_BUFFER_READY = 0
DBWIN_DATA_READY = 1

class DBWIN_BUFFER(ctypes.Structure):
    _fields_ = [
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
        ("data", wintypes.CHAR * 4096)
    ]

def capture_debug_output():
    """捕获调试输出"""
    print("开始捕获调试输出...")
    
    # 创建共享内存
    hMapObject = kernel32.CreateFileMappingW(
        wintypes.HANDLE(-1),  # INVALID_HANDLE_VALUE
        None,
        wintypes.DWORD(0x4),  # PAGE_READWRITE
        0,
        ctypes.sizeof(DBWIN_BUFFER),
        "DBWIN_BUFFER"
    )
    
    if not hMapObject:
        print("创建共享内存失败")
        return
    
    # 映射共享内存
    pBuf = kernel32.MapViewOfFile(
        hMapObject,
        wintypes.DWORD(0x2),  # FILE_MAP_WRITE
        0,
        0,
        0
    )
    
    if not pBuf:
        print("映射共享内存失败")
        kernel32.CloseHandle(hMapObject)
        return
    
    # 创建事件对象
    hEventBufferReady = kernel32.CreateEventW(None, False, False, "DBWIN_BUFFER_READY")
    hEventDataReady = kernel32.CreateEventW(None, False, False, "DBWIN_DATA_READY")
    
    if not hEventBufferReady or not hEventDataReady:
        print("创建事件对象失败")
        kernel32.UnmapViewOfFile(pBuf)
        kernel32.CloseHandle(hMapObject)
        return
    
    # 设置缓冲区就绪
    kernel32.SetEvent(hEventBufferReady)
    
    print("等待调试输出... (按Ctrl+C停止)")
    
    try:
        while True:
            # 等待数据就绪
            wait_result = kernel32.WaitForSingleObject(hEventDataReady, 1000)  # 1秒超时
            
            if wait_result == 0:  # WAIT_OBJECT_0
                # 读取调试数据
                dbwin_buffer = DBWIN_BUFFER.from_address(pBuf)
                debug_data = dbwin_buffer.data.decode('utf-8', errors='ignore').rstrip('\x00')
                
                if debug_data:
                    print(f"[PID:{dbwin_buffer.dwProcessId}] {debug_data}")
                
                # 重置事件
                kernel32.SetEvent(hEventBufferReady)
            elif wait_result == 0x102:  # WAIT_TIMEOUT
                # 超时，继续等待
                pass
            else:
                print(f"等待事件失败: {wait_result}")
                break
                
    except KeyboardInterrupt:
        print("\n停止捕获调试输出")
    
    # 清理资源
    kernel32.CloseHandle(hEventDataReady)
    kernel32.CloseHandle(hEventBufferReady)
    kernel32.UnmapViewOfFile(pBuf)
    kernel32.CloseHandle(hMapObject)

if __name__ == "__main__":
    capture_debug_output()