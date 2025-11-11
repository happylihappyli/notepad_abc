@echo off
chcp 65001 > nul
echo 开始构建时间: %date% %time%

REM 设置Visual Studio环境
call "D:\Code\VS2022\Community\VC\Auxiliary\Build\vcvars64.bat"

REM 清理旧的构建文件
if exist "bin\notepad_abc.exe" del "bin\notepad_abc.exe"
if exist "obj" rmdir /s /q "obj"
mkdir "obj"

REM 编译主程序
cl.exe ^
  /std:c++17 ^
  /utf-8 ^
  /O2 ^
  /GL ^
  /MD ^
  /W4 ^
  /EHsc ^
  /MP ^
  /DWIN32 ^
  /D_WINDOWS ^
  /DUNICODE ^
  /D_UNICODE ^
  /D_WIN32_WINNT=_WIN32_WINNT_WIN7 ^
  /DNTDDI_VERSION=NTDDI_WIN7 ^
  /DOEMRESOURCE ^
  /DNOMINMAX ^
  /D_USE_64BIT_TIME_T ^
  /DTIXML_USE_STL ^
  /DTIXMLA_USE_STL ^
  /D_CRT_NONSTDC_NO_DEPRECATE ^
  /D_CRT_SECURE_NO_WARNINGS ^
  /D_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING ^
  /I"PowerEditor\src" ^
  /I"PowerEditor\src\MISC" ^
  /I"PowerEditor\src\MISC\Common" ^
  /I"PowerEditor\src\MISC\Exception" ^
  /I"PowerEditor\src\MISC\PluginsManager" ^
  /I"PowerEditor\src\MISC\Process" ^
  /I"PowerEditor\src\MISC\RegExt" ^
  /I"PowerEditor\src\MISC\md5" ^
  /I"PowerEditor\src\MISC\sha1" ^
  /I"PowerEditor\src\MISC\sha2" ^
  /I"PowerEditor\src\MISC\sha512" ^
  /I"PowerEditor\src\ScintillaComponent" ^
  /I"PowerEditor\src\WinControls" ^
  /I"PowerEditor\src\WinControls\AboutDlg" ^
  /I"PowerEditor\src\WinControls\AnsiCharPanel" ^
  /I"PowerEditor\src\WinControls\ClipboardHistory" ^
  /I"PowerEditor\src\WinControls\ColourPicker" ^
  /I"PowerEditor\src\WinControls\ContextMenu" ^
  /I"PowerEditor\src\WinControls\DockingWnd" ^
  /I"PowerEditor\src\WinControls\DocumentMap" ^
  /I"PowerEditor\src\WinControls\FileBrowser" ^
  /I"PowerEditor\src\WinControls\FindCharsInRange" ^
  /I"PowerEditor\src\WinControls\FunctionList" ^
  /I"PowerEditor\src\WinControls\Grid" ^
  /I"PowerEditor\src\WinControls\ImageListSet" ^
  /I"PowerEditor\src\WinControls\OpenSaveFileDialog" ^
  /I"PowerEditor\src\WinControls\PluginsAdmin" ^
  /I"PowerEditor\src\WinControls\Preference" ^
  /I"PowerEditor\src\WinControls\ProjectPanel" ^
  /I"PowerEditor\src\WinControls\ReadDirectoryChanges" ^
  /I"PowerEditor\src\WinControls\shortcut" ^
  /I"PowerEditor\src\WinControls\SplitterContainer" ^
  /I"PowerEditor\src\WinControls\StaticDialog" ^
  /I"PowerEditor\src\WinControls\StaticDialog\RunDlg" ^
  /I"PowerEditor\src\WinControls\StatusBar" ^
  /I"PowerEditor\src\WinControls\TabBar" ^
  /I"PowerEditor\src\WinControls\TaskList" ^
  /I"PowerEditor\src\WinControls\ToolBar" ^
  /I"PowerEditor\src\WinControls\ToolTip" ^
  /I"PowerEditor\src\WinControls\TrayIcon" ^
  /I"PowerEditor\src\WinControls\TreeView" ^
  /I"PowerEditor\src\WinControls\VerticalFileSwitcher" ^
  /I"PowerEditor\src\WinControls\WindowsDlg" ^
  /I"PowerEditor\src\TinyXml" ^
  /I"PowerEditor\src\TinyXml\tinyXmlA" ^
  /I"PowerEditor\src\uchardet" ^
  /I"PowerEditor\src\json" ^
  /I"lexilla\include" ^
  /I"scintilla\include" ^
  /Fo"obj\\" ^
  /c "PowerEditor\src\*.cpp"

if errorlevel 1 (
    echo 编译失败
    exit /b 1
)

REM 链接程序
link.exe ^
  /OUT:"bin\notepad_abc.exe" ^
  /SUBSYSTEM:WINDOWS ^
  /VERSION:1.0 ^
  /LTCG ^
  /OPT:REF ^
  /OPT:ICF ^
  "obj\*.obj" ^
  "bin\libscintilla.lib" ^
  "bin\liblexilla.lib" ^
  comctl32.lib ^
  shlwapi.lib ^
  shell32.lib ^
  dbghelp.lib ^
  version.lib ^
  crypt32.lib ^
  wintrust.lib ^
  sensapi.lib ^
  wininet.lib ^
  imm32.lib ^
  msimg32.lib ^
  uxtheme.lib ^
  dwmapi.lib ^
  comdlg32.lib ^
  gdi32.lib ^
  user32.lib ^
  kernel32.lib ^
  ole32.lib ^
  oleaut32.lib ^
  advapi32.lib

if errorlevel 1 (
    echo 链接失败
    exit /b 1
)

echo 构建完成时间: %date% %time%
echo 程序已生成: bin\notepad_abc.exe

REM 播放语音提示
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('程序构建完成'); engine.runAndWait()" 2>nul