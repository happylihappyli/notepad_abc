# Notepad++ SCons 构建系统使用说明

这是Notepad++项目的SCons构建系统，用于替代原来的Visual Studio项目文件。

## 环境要求

- Windows 10/11
- Visual Studio 2022 (Community/Professional/Enterprise)
- SCons (通过`pip install scons`安装)
- Python 3.8+

## 使用方法

### 快速开始

1. 打开命令提示符或PowerShell
2. 进入项目根目录
3. 运行构建脚本:
   ```
   build.bat
   ```

### 高级用法

构建Debug版本:
```
build.bat debug
```

构建32位版本:
```
build.bat x86
```

清理并重新构建:
```
build.bat clean
```

组合使用:
```
build.bat debug x86 clean
```

### 直接使用SCons

如果你更喜欢直接使用SCons命令:

构建Release x64版本:
```
scons build=Release arch=x64
```

构建Debug x86版本:
```
scons build=Debug arch=x86
```

清理构建:
```
scons -c
```

## 项目结构

- `SConstruct`: 主构建脚本，定义全局环境变量和配置
- `SConscript`: 子构建脚本，定义源文件列表和构建规则
- `build.bat`: Windows批处理脚本，简化构建过程
- `bin/`: 构建输出目录
- `obj/`: 中间文件目录

## 构建配置

### 支持的配置

- **构建类型**: Debug, Release
- **目标架构**: x86, x64, ARM64

### 编译选项

- C++标准: C++20
- C标准: C17
- 字符集: Unicode
- 运行时库: 多线程DLL (/MD 或 /MDd)

### 预处理器定义

#### 通用定义
- `_UNICODE`, `UNICODE`
- `_WIN32_WINNT=0x0601` (Windows 7)
- `WIN32`, `_WINDOWS`
- `WINVER=0x0601`
- `_CRT_SECURE_NO_WARNINGS`

#### Debug特有定义
- `_DEBUG`
- `DEBUG`

#### Release特有定义
- `NDEBUG`

## 依赖库

- Windows API库
- RichEdit控件
- Common Controls
- COM库
- WinMM (Windows多媒体)
- WinINet (Windows网络)
- SetupAPI
- Shell32
- Ole32
- OleAut32
- Imm32 (输入法)
- Psapi (进程状态)
- Version
- Shlwapi
- Gdi32
- ComCtl32
- ComDlg32
- WinSpool
- User32
- AdvAPI32
- UxTheme
- dwmapi
- msimg32
- htmlhelp

## 构建事件

### 预构建事件

- 执行`NppLibsVersionH-generator.bat`生成版本头文件

### 后构建事件

- 复制配置文件到输出目录
- 添加应用程序清单文件

## 注意事项

1. 确保VS2022安装在默认路径或修改`build.bat`中的路径
2. 首次构建可能需要较长时间，因为需要编译所有源文件
3. 如果构建失败，请检查:
   - VS2022是否正确安装
   - SCons是否正确安装
   - 所有源文件是否存在

## 故障排除

### 常见问题

1. **找不到cl.exe**: 确保VS2022环境变量正确设置
2. **链接错误**: 检查所有依赖库是否正确链接
3. **编译错误**: 检查源文件路径是否正确

### 调试技巧

1. 使用`scons --debug=explain`查看详细构建信息
2. 检查`obj`目录中的编译日志
3. 使用Visual Studio打开项目进行调试