# -*- coding: utf-8 -*-
# 终止正在运行的notepad_abc进程脚本

Write-Host "正在检查是否有正在运行的notepad_abc进程..." -ForegroundColor Yellow

# 查找所有notepad_abc相关的进程
$processes = Get-Process | Where-Object { $_.ProcessName -like "*notepad_abc*" }

if ($processes.Count -gt 0) {
    Write-Host "发现 $($processes.Count) 个正在运行的notepad_abc进程:" -ForegroundColor Yellow
    foreach ($process in $processes) {
        Write-Host "  PID: $($process.Id), 名称: $($process.ProcessName)" -ForegroundColor Yellow
    }
    
    # 尝试终止所有找到的进程
    foreach ($process in $processes) {
        try {
            Write-Host "正在终止进程 PID: $($process.Id)..." -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            Write-Host "成功终止进程 PID: $($process.Id)" -ForegroundColor Green
        }
        catch {
            Write-Host "无法终止进程 PID: $($process.Id)，错误: $($_.Exception.Message)" -ForegroundColor Red
            
            # 尝试使用taskkill命令
            try {
                Write-Host "尝试使用taskkill命令终止进程..." -ForegroundColor Yellow
                $result = cmd /c "taskkill /F /PID $($process.Id) 2>&1"
                Write-Host $result -ForegroundColor Yellow
            }
            catch {
                Write-Host "taskkill命令也失败了: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "没有发现正在运行的notepad_abc进程" -ForegroundColor Green
}

Write-Host "进程检查和终止操作完成" -ForegroundColor Green