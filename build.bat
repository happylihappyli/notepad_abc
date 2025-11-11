@echo off
chcp 65001 >nul
echo 开始构建 Notepad++ (使用SCons)
echo ================================

:: 设置VS2022环境变量
set VS2022_PATH=D:\Code\VS2022\Community
if exist "%VS2022_PATH%\VC\Auxiliary\Build\vcvars64.bat" (
    call "%VS2022_PATH%\VC\Auxiliary\Build\vcvars64.bat"
    echo 已设置VS2022环境变量
) else (
    echo 警告: VS2022路径不正确，请检查VS2022_PATH变量
    echo 尝试使用默认VS环境...
)

:: 检查SCons是否安装
where scons >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: SCons未安装或不在PATH中
    echo 请安装SCons: pip install scons
    pause
    exit /b 1
)

:: 解析命令行参数
set BUILD_TYPE=Release
set TARGET_ARCH=x64
set CLEAN_BUILD=false

:parse_args
if "%~1"=="" goto :start_build
if /i "%~1"=="debug" set BUILD_TYPE=Debug
if /i "%~1"=="release" set BUILD_TYPE=Release
if /i "%~1"=="x86" set TARGET_ARCH=x86
if /i "%~1"=="x64" set TARGET_ARCH=x64
if /i "%~1"=="clean" set CLEAN_BUILD=true
shift
goto :parse_args

:start_build
echo 构建类型: %BUILD_TYPE%
echo 目标架构: %TARGET_ARCH%

:: 如果是清理构建，先清理
if "%CLEAN_BUILD%"=="true" (
    echo 清理构建目录...
    if exist "obj" rmdir /s /q "obj"
    if exist "bin\notepad_abc.exe" del "bin\notepad_abc.exe"
)

:: 执行SCons构建
echo 开始SCons构建...
scons build=%BUILD_TYPE% arch=%TARGET_ARCH% -j%NUMBER_OF_PROCESSORS%

:: 检查构建结果
if %errorlevel% equ 0 (
    echo ================================
    echo 构建成功!
    echo 可执行文件位于: bin\notepad_abc.exe
    echo ================================
    
    :: 询问是否运行程序
    set /p RUN_PROGRAM=是否运行程序? (y/n): 
    if /i "%RUN_PROGRAM%"=="y" (
        start bin\notepad_abc.exe
    )
) else (
    echo ================================
    echo 构建失败!
    echo ================================
)

pause