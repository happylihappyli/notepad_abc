# 构建两个版本说明

本项目现在支持构建两个版本：

1. **Windows版本** (`notepad_abc.exe`) - 只显示图形界面，不显示控制台窗口
2. **控制台版本** (`notepad_abc_console.exe`) - 显示控制台窗口和图形界面

## 使用方法

### 方法1: 使用Python脚本（推荐）

#### 同时构建两个版本
```bash
python build.py
```
或
```bash
python build.py both
```

#### 构建单个版本
```bash
python build.py windows    # 只构建Windows版本
python build.py console    # 只构建控制台版本
```

#### 构建Debug版本
```bash
python build.py debug both
python build.py debug console
python build.py debug windows
```

#### 清理构建
```bash
python build.py clean
```

### 方法2: 直接使用SCons命令

#### 构建Windows版本（只显示图形界面）
```bash
scons build=Release arch=x64 subsystem=WINDOWS
```

#### 构建控制台版本（显示console和图形界面）
```bash
scons build=Release arch=x64 subsystem=CONSOLE
```

#### 同时构建两个版本
```bash
# 先构建Windows版本
scons build=Release arch=x64 subsystem=WINDOWS

# 再构建控制台版本
scons build=Release arch=x64 subsystem=CONSOLE
```

#### 构建Debug版本
```bash
scons build=Debug arch=x64 subsystem=WINDOWS
scons build=Debug arch=x64 subsystem=CONSOLE
```

#### 清理构建
```bash
scons -c
```

#### 并行构建（加快速度）
```bash
scons build=Release arch=x64 subsystem=WINDOWS -j8
scons build=Release arch=x64 subsystem=CONSOLE -j8
```

### 方法3: 使用批处理脚本（Windows）

#### 构建单个版本
```batch
build.bat              # 构建Windows版本（默认）
build.bat console      # 构建控制台版本
build.bat windows      # 构建Windows版本
```

#### 同时构建两个版本
```batch
build.bat both
```

#### 其他选项
```batch
build.bat debug both           # Debug模式构建两个版本
build.bat clean both           # 清理后构建两个版本
```

## 输出文件

- Windows版本: `bin\notepad_abc.exe`
- 控制台版本: `bin\notepad_abc_console.exe`

## 区别说明

- **Windows版本** (`/SUBSYSTEM:WINDOWS`): 只显示图形界面，适合普通用户使用
- **控制台版本** (`/SUBSYSTEM:CONSOLE`): 显示控制台窗口和图形界面，适合调试和开发使用，可以看到程序输出的调试信息

## SCons参数说明

- `build=Release` 或 `build=Debug`: 构建类型
- `arch=x64` 或 `arch=x86`: 目标架构
- `subsystem=WINDOWS`: Windows子系统（只显示图形界面）
- `subsystem=CONSOLE`: 控制台子系统（显示控制台和图形界面）
- `-jN`: 并行构建，N为并行任务数（如 `-j8` 表示8个并行任务）

