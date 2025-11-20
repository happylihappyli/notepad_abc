#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完成字体大小标签问题修复并播放语音提示
"""

import pyttsx3
import time

def play_completion_voice():
    """播放完成语音提示"""
    try:
        engine = pyttsx3.init()
        
        # 设置语音属性
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)  # 使用默认语音
        
        engine.setProperty('rate', 200)  # 语速
        engine.setProperty('volume', 0.8)  # 音量
        
        # 构建语音内容
        message = """字体大小标签问题修复完成！
        
问题的根源是：垂直文件切换器中同时存在两种定义字体大小标签的方式：
1. 资源文件VerticalFileSwitcher.rc中已定义LTEXT控件"字体大小:"
2. VerticalFileSwitcher.cpp中动态创建相同的标签

修复方案：
1. 移除了动态创建标签的代码
2. 改为获取资源文件中已存在的标签句柄
3. 避免了标签重复创建导致显示异常的问题
        
现在'字体大小:'标签后面不会再有额外的文字信息了！
修复已经验证通过，程序可以正常编译和运行！"""
        
        engine.say(message)
        engine.runAndWait()
        
        print(f"语音提示完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"语音提示播放失败: {e}")

if __name__ == "__main__":
    play_completion_voice()