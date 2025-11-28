@echo off
chcp 65001 >nul
echo 测试构建脚本...

:: 测试参数解析
set BUILD_MODE=single
if /i "%~1"=="both" set BUILD_MODE=both
echo 构建模式: %BUILD_MODE%

:: 测试变量设置
set BUILD_TYPE=Release
set TARGET_ARCH=x64
if "%NUMBER_OF_PROCESSORS%"=="" set NUMBER_OF_PROCESSORS=4

echo 构建类型: %BUILD_TYPE%
echo 目标架构: %TARGET_ARCH%
echo 并行任务数: %NUMBER_OF_PROCESSORS%

:: 测试SCons命令格式
echo.
echo 测试SCons命令格式:
echo scons build=%BUILD_TYPE% arch=%TARGET_ARCH% subsystem=WINDOWS -j%NUMBER_OF_PROCESSORS%
echo scons build=%BUILD_TYPE% arch=%TARGET_ARCH% subsystem=CONSOLE -j%NUMBER_OF_PROCESSORS%

pause

