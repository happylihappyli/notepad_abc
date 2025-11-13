#include <iostream>
#include <windows.h>
#include <filesystem>
#include <fstream>
#include <string>

// 简化版本的分类管理器测试
void testCategoryManager() {
    std::wstring configPath = L"bin/categories.json";
    
    // 将相对路径转换为绝对路径
    std::filesystem::path fsPath(configPath);
    if (fsPath.is_relative()) {
        fsPath = std::filesystem::absolute(fsPath);
    }
    
    std::wcout << L"配置文件路径: " << fsPath.wstring() << std::endl;
    
    // 确保配置目录存在
    std::filesystem::path configDir = fsPath.parent_path();
    std::wcout << L"配置目录: " << configDir.wstring() << std::endl;
    
    if (!configDir.empty() && configDir != std::filesystem::current_path()) {
        if (!std::filesystem::exists(configDir)) {
            std::wcout << L"配置目录不存在，正在创建..." << std::endl;
            if (std::filesystem::create_directories(configDir)) {
                std::wcout << L"配置目录创建成功" << std::endl;
            } else {
                std::wcout << L"配置目录创建失败" << std::endl;
                return;
            }
        } else {
            std::wcout << L"配置目录已存在" << std::endl;
        }
    } else {
        std::wcout << L"配置文件在当前目录，不需要创建目录" << std::endl;
    }
    
    // 创建测试配置文件
    std::ofstream file(fsPath);
    if (file.is_open()) {
        file << "{\"categories\":[],\"fileMappings\":[]}";
        file.close();
        std::wcout << L"测试配置文件创建成功" << std::endl;
        
        // 检查文件大小
        std::filesystem::path checkPath(fsPath);
        if (std::filesystem::exists(checkPath)) {
            auto fileSize = std::filesystem::file_size(checkPath);
            std::wcout << L"文件大小: " << fileSize << L" 字节" << std::endl;
        }
    } else {
        std::wcout << L"无法创建测试配置文件" << std::endl;
    }
}

int main() {
    // 设置控制台编码为UTF-8
    SetConsoleOutputCP(65001);
    
    std::wcout << L"开始测试分类管理器..." << std::endl;
    
    // 测试当前工作目录
    std::wcout << L"当前工作目录: " << std::filesystem::current_path().wstring() << std::endl;
    
    // 测试bin目录是否存在
    std::filesystem::path binPath("bin");
    if (std::filesystem::exists(binPath)) {
        std::wcout << L"bin目录存在" << std::endl;
    } else {
        std::wcout << L"bin目录不存在" << std::endl;
    }
    
    // 测试分类管理器功能
    testCategoryManager();
    
    std::wcout << L"测试完成" << std::endl;
    return 0;
}