@echo off
chcp 65001
cd /d e:\GitHub3\notepad_abc
set CL="/utf-8 /I\"D:\Code\VS2022\Community\VC\Tools\MSVC\14.44.35207\include\""
"D:\Code\VS2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe" /EHsc test_parameters_fix.cpp /link /SUBSYSTEM:CONSOLE