#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
"""
查找DLL中指定序数的导出函数
"""

param(
    [Parameter(Mandatory=$true)][string]$DllPath,
    [Parameter(Mandatory=$true)][int]$Ordinal
)

Write-Host "正在分析DLL: $DllPath" -ForegroundColor Green
Write-Host "查找序数: $Ordinal" -ForegroundColor Green

# 使用Get-ItemProperty获取文件信息
try {
    $fileInfo = Get-ItemProperty -Path $DllPath -ErrorAction Stop
    Write-Host "文件版本: $($fileInfo.VersionInfo.FileVersion)" -ForegroundColor Cyan
    Write-Host "产品版本: $($fileInfo.VersionInfo.ProductVersion)" -ForegroundColor Cyan
} catch {
    Write-Host "无法获取文件信息: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 使用dumpbin命令（如果可用）
$dumpbin = "dumpbin.exe"
try {
    Get-Command $dumpbin -ErrorAction Stop | Out-Null
    Write-Host "使用dumpbin命令分析..." -ForegroundColor Yellow
    
    # 执行dumpbin命令并捕获输出
    $dumpbinOutput = & $dumpbin /exports $DllPath 2>&1
    
    # 查找指定序数的函数
    $found = $false
    foreach ($line in $dumpbinOutput) {
        if ($line -match "^\s*$Ordinal\s+[0-9A-Fa-f]+\s+([A-Za-z0-9_]+)\s*") {
            Write-Host "✅ 找到序数 $Ordinal 对应的函数: $($matches[1])" -ForegroundColor Green
            $found = $true
            break
        }
    }
    
    if (-not $found) {
        Write-Host "❌ 未找到序数 $Ordinal 对应的函数" -ForegroundColor Red
    }
} catch {
    Write-Host "dumpbin命令不可用，尝试其他方法..." -ForegroundColor Yellow
    
    # 使用LLVM工具（如果可用）
    $llvmObjdump = "C:\Program Files\LLVM\bin\llvm-objdump.exe"
    if (Test-Path $llvmObjdump) {
        Write-Host "使用LLVM工具分析..." -ForegroundColor Yellow
        
        # 执行llvm-objdump命令并捕获输出
        $objdumpOutput = & $llvmObjdump -p $DllPath 2>&1
        
        # 查找指定序数的函数
        $found = $false
        $inExportSection = $false
        foreach ($line in $objdumpOutput) {
            if ($line -match "DLL Name") {
                $inExportSection = $true
            }
            
            if ($inExportSection -and $line -match "^\s*$Ordinal\s+") {
                # 获取函数名（可能在下一行）
                Write-Host "找到序数 $Ordinal 的条目，但需要更多信息" -ForegroundColor Yellow
                $found = $true
                break
            }
        }
        
        if (-not $found) {
            Write-Host "❌ 未找到序数 $Ordinal 对应的函数" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ 没有可用的DLL分析工具" -ForegroundColor Red
        exit 1
    }
}

Write-Host "分析完成" -ForegroundColor Green
