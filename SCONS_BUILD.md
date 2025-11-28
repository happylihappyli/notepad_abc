# SCons 构建快速参考

## 快速开始

### 同时构建两个版本（推荐）
```bash
python build.py
```

### 直接使用SCons构建单个版本

#### Windows版本（只显示图形界面）
```bash
scons build=Release arch=x64 subsystem=WINDOWS
```

#### 控制台版本（显示console和图形界面）
```bash
scons build=Release arch=x64 subsystem=CONSOLE
```

## 常用命令

### 构建Release版本
```bash
# Windows版本
scons build=Release arch=x64 subsystem=WINDOWS

# 控制台版本
scons build=Release arch=x64 subsystem=CONSOLE
```

### 构建Debug版本
```bash
# Windows版本
scons build=Debug arch=x64 subsystem=WINDOWS

# 控制台版本
scons build=Debug arch=x64 subsystem=CONSOLE
```

### 并行构建（加快速度）
```bash
scons build=Release arch=x64 subsystem=WINDOWS -j8
scons build=Release arch=x64 subsystem=CONSOLE -j8
```

### 清理构建
```bash
scons -c
```

### 清理并重新构建
```bash
scons -c && scons build=Release arch=x64 subsystem=WINDOWS
```

## 参数说明

| 参数 | 可选值 | 说明 |
|------|--------|------|
| `build` | `Release`, `Debug` | 构建类型，默认为Release |
| `arch` | `x64`, `x86` | 目标架构，默认为x64 |
| `subsystem` | `WINDOWS`, `CONSOLE` | 子系统类型 |
| `-jN` | 数字 | 并行构建任务数，如 `-j8` |

## 输出文件

- Windows版本: `bin\notepad_abc.exe`
- 控制台版本: `bin\notepad_abc_console.exe`

## 示例：完整构建流程

```bash
# 1. 清理之前的构建
scons -c

# 2. 构建Windows版本
scons build=Release arch=x64 subsystem=WINDOWS -j8

# 3. 构建控制台版本
scons build=Release arch=x64 subsystem=CONSOLE -j8
```

## 使用Python脚本（更简单）

```bash
# 同时构建两个版本
python build.py

# 只构建Windows版本
python build.py windows

# 只构建控制台版本
python build.py console

# Debug模式构建两个版本
python build.py debug both
```

更多详细信息请参考 `BUILD_VERSIONS.md`
