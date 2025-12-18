#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建完成语音提示
"""

import os
import sys
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def play_completion_voice():
    """播放构建完成语音提示"""
    try:
        import pyttsx3
        
        # 初始化TTS引擎
        engine = pyttsx3.init()
        
        # 设置语音参数
        voices = engine.getProperty('voices')
        if voices:
            # 选择中文语音（如果有的话）
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'chinese' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
        
        # 设置语速
        engine.setProperty('rate', 180)
        
        # 播放构建完成消息
        completion_message = "任务运行完毕，过来看看！"
        engine.say(completion_message)
        engine.runAndWait()
        
        print(f"语音提示播放完成: {completion_message}")
        
    except ImportError:
        print("⚠️ pyttsx3未安装，使用文本提示替代语音")
        print("=" * 50)
        print("🎉 构建完成！")
        print("=" * 50)
        print("任务运行完毕，过来看看！")
        print("=" * 50)
    except Exception as e:
        print(f"播放语音提示时出错: {e}")
        print("=" * 50)
        print("🎉 构建完成！")
        print("=" * 50)
        print("任务运行完毕，过来看看！")
        print("=" * 50)

if __name__ == "__main__":
    print("构建时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    play_completion_voice()