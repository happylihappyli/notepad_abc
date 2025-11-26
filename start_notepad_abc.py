#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

workspace = Path(__file__).parent
exe_path = workspace / "bin" / "notepad_abc.exe"

if exe_path.exists():
    print(f"启动应用程序: {exe_path}")
    subprocess.run([str(exe_path)])
else:
    print(f"找不到可执行文件: {exe_path}")
    print("请先编译项目")
