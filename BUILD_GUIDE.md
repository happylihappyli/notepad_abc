# Notepad_abc SCons 构建指南

基于Visual Studio解决方案的SCons构建系统，参考：`E:\GitHub3\notepad_abc\PowerEditor\visual.net\notepadPlus.sln`

## 构建脚本说明

本项目提供了三个不同级别的SCons构建脚本：

### 1. SConstruct_vs_based - 基于VS解决方案的完整构建脚本
- **功能**: 完整的构建系统，基于Visual Studio解决方案结构
- **特点**: 支持多平台、完整的源文件收集、详细的构建配置
- **适用场景**: 正式发布构建、完整功能测试

### 2. SConstruct_complete - 完整构建系统（推荐）
- **功能**: 最完整的构建系统，包含依赖项目构建
- **特点**: 支持ARM64/Win32/x64多平台、自动构建Scintilla和Lexilla库
- **适用场景**: 完整的开发构建、依赖库管理

### 3. SConstruct_simple - 简化构建脚本
- **功能**: 快速构建版本，适合日常开发
- **特点**: 轻量级、快速构建、基本功能
- **适用场景**: 日常开发、快速测试

## 构建要求

### 系统要求
- Windows 10/11
- Visual Studio 2022 (v143工具集)
- Python 3.6+
- SCons 4.0+

### 依赖项目
- Scintilla: 文本编辑组件
- Lexilla: 语法高亮组件

## 构建命令

### 基本构建命令
```bash
# 使用默认配置构建（Release x64）
scons -f SConstruct_complete

# 指定构建类型和架构
scons -f SConstruct_complete build=Debug arch=Win32
scons -f SConstruct_complete build=Release arch=ARM64

# 使用简化版本构建
scons -f SConstruct_simple
```

### 支持的构建参数
- **build**: Debug / Release (默认: Release)
- **arch**: ARM64 / Win32 / x86_64 (默认: x86_64)

### 清理构建
```bash
scons -f SConstruct_complete -c
scons -f SConstruct_simple -c
```

## 项目结构

```
notepad_abc/
├── PowerEditor/
│   └── src/                 # 主程序源文件
├── scintilla/              # Scintilla文本编辑组件
├── lexilla/               # Lexilla语法高亮组件
├── bin/                   # 构建输出目录
├── obj/                   # 中间文件目录
└── *.scons*               # SCons构建脚本
```

## 构建流程

### 1. 环境配置
- 设置编译器选项（C++20标准、多处理器编译等）
- 配置预处理器定义（UNICODE、Windows版本等）
- 设置包含目录和库目录

### 2. 依赖库构建
- 自动构建Scintilla静态库
- 自动构建Lexilla静态库

### 3. 主程序构建
- 收集所有源文件（约200+个.cpp文件）
- 编译资源文件（.rc文件）
- 链接生成最终可执行文件

### 4. 后处理
- 复制配置文件到输出目录
- 生成构建报告

## 构建输出

构建完成后，在`bin/`目录下生成：
- `notepad_abc.exe` - 主程序可执行文件
- 各种配置文件（XML格式）
- 依赖库文件

## 故障排除

### 常见问题

1. **找不到源文件**
   - 检查项目目录结构是否正确
   - 确认所有依赖项目存在

2. **编译错误**
   - 检查Visual Studio 2022是否正确安装
   - 确认v143工具集可用

3. **链接错误**
   - 检查依赖库是否正确构建
   - 确认库文件路径设置正确

### 调试构建

使用Debug模式构建以获取更多调试信息：
```bash
scons -f SConstruct_complete build=Debug
```

## 性能优化

### 构建时间优化
- 使用`/MP`标志启用多处理器编译
- Release模式使用`/GL`和`/LTCG`进行全程序优化
- 增量构建避免重复编译

### 输出文件优化
- Release模式使用`/O2`最大优化
- 启用函数级链接(`/Gy`)减少代码大小
- 使用链接时代码生成(`/LTCG`)

## 版本信息

- **项目名称**: Notepad_abc
- **版本**: 8.6.6
- **构建系统**: SCons 4.0+
- **编译器**: Visual Studio 2022 (v143)
- **平台支持**: Windows (ARM64, Win32, x64)

## 相关文件

- `PowerEditor/visual.net/notepadPlus.sln` - Visual Studio解决方案文件
- `PowerEditor/visual.net/notepadPlus.vcxproj` - Visual Studio项目文件
- `ANALYSIS_REPORT.md` - 程序启动问题分析报告

## 技术支持

如有构建问题，请参考：
1. 检查构建错误信息
2. 确认环境配置正确
3. 查看详细的构建日志
4. 参考Visual Studio解决方案文件结构

---

*最后更新: {datetime.now().strftime('%Y-%m-%d')}*