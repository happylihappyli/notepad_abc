@echo off
chcp 65001 >nul
cd /d "E:\GitHub3\notepad_abc"
"D:\Code\VS2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cl /EHsc /std:c++17 /utf-8 /I. /Fe:test_category_path.exe -
