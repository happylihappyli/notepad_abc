#!/usr/bin/env python3
"""
完成语音提示
"""
import pyttsx3
from datetime import datetime

def speak_completion():
    """语音提示任务完成"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 准备语音提示...")
        
        # 初始化TTS引擎
        engine = pyttsx3.init()
        
        # 设置语音参数
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)  # 使用第一个可用语音
        
        # 设置语速
        engine.setProperty('rate', 150)
        
        # 语音文本
        text = "任务运行完毕，过来看看！编译已经成功，程序可以正常运行并显示GUI窗口了！"
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 播放语音: {text}")
        
        # 播放语音
        engine.say(text)
        engine.runAndWait()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 语音提示完成")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 语音提示失败: {str(e)}")

def main():
    """主函数"""
    speak_completion()

if __name__ == "__main__":
    main()