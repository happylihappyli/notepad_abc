#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
播放任务完成提示音
"""

import subprocess
import sys

def main():
    try:
        # 使用PowerShell的Add-Type和SpeechSynthesizer
        ps_command = """
        Add-Type -AssemblyName System.Speech
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $synth.Speak("任务运行完毕，过来看看！")
        """
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        return 0
    except Exception as e:
        print(f"无法播放语音提示: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())