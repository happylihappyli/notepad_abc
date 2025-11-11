# -*- coding: utf-8 -*-
# Notepad++ ABC 编译脚本
# 会先终止正在运行的进程，然后执行编译

Write-Host "=== Notepad++ ABC 编译脚本 ===" -ForegroundColor Cyan
Write-Host "开始执行编译前的准备工作..." -ForegroundColor Yellow

# 设置UTF-8编码
chcp 65001 > $null

# 获取脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "脚本路径: $scriptPath" -ForegroundColor Gray

# 执行终止进程脚本
Write-Host "1. 终止正在运行的notepad_abc进程..." -ForegroundColor Yellow
$killScript = Join-Path $scriptPath "kill_notepad_abc.ps1"
if (Test-Path $killScript) {
    Write-Host "执行脚本: $killScript" -ForegroundColor Gray
    & $killScript
} else {
    Write-Host "警告: 找不到终止进程脚本 $killScript" -ForegroundColor Red
}

# 等待一段时间确保进程被终止
Start-Sleep -Seconds 2

# 执行scons编译
Write-Host "2. 开始执行scons编译..." -ForegroundColor Yellow
$startTime = Get-Date
Write-Host "编译开始时间: $($startTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray

try {
    # 执行scons编译命令
    $result = scons 2>&1
    
    # 显示编译输出
    $result | ForEach-Object { Write-Host $_ }
    
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    Write-Host "编译结束时间: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
    Write-Host "总编译时间: $([math]::Round($duration, 2)) 秒" -ForegroundColor Gray
    
    # 检查编译结果
    if ($LASTEXITCODE -eq 0) {
        Write-Host "编译成功完成!" -ForegroundColor Green
        
        # 检查生成的可执行文件
        $exePath = Join-Path $scriptPath "bin\notepad_abc_new.exe"
        if (Test-Path $exePath) {
            $fileInfo = Get-Item $exePath
            Write-Host "生成的可执行文件: $($fileInfo.Name)" -ForegroundColor Green
            Write-Host "文件大小: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Green
            Write-Host "最后修改时间: $($fileInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Green
        } else {
            Write-Host "警告: 未找到生成的可执行文件 $exePath" -ForegroundColor Red
        }
    } else {
        Write-Host "编译失败，退出代码: $LASTEXITCODE" -ForegroundColor Red
    }
}
catch {
    Write-Host "编译过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    Write-Host "编译结束时间: $($endTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
    Write-Host "总编译时间: $([math]::Round($duration, 2)) 秒" -ForegroundColor Gray
}

Write-Host "=== 编译脚本执行完毕 ===" -ForegroundColor Cyan