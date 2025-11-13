#include <iostream>
#include <filesystem>
#include <fstream>

namespace fs = std::filesystem;

// 模拟分类管理器的路径处理逻辑
void testCategoryPath() {
    std::wcout << L"=== 测试分类管理器路径处理 ===" << std::endl;
    
    // 测试相对路径转绝对路径
    std::wstring configPath = L"bin/categories.json";
    std::wcout << L"原始配置路径: " << configPath << std::endl;
    
    try {
        // 获取当前工作目录
        fs::path currentPath = fs::current_path();
        std::wcout << L"当前工作目录: " << currentPath.wstring() << std::endl;
        
        // 将相对路径转换为绝对路径
        fs::path absolutePath = fs::absolute(configPath);
        std::wcout << L"绝对配置路径: " << absolutePath.wstring() << std::endl;
        
        // 检查目录是否存在
        fs::path configDir = absolutePath.parent_path();
        std::wcout << L"配置目录: " << configDir.wstring() << std::endl;
        
        if (!fs::exists(configDir)) {
            std::wcout << L"配置目录不存在，尝试创建..." << std::endl;
            bool created = fs::create_directories(configDir);
            std::wcout << L"目录创建结果: " << (created ? L"成功" : L"失败") << std::endl;
        } else {
            std::wcout << L"配置目录已存在" << std::endl;
        }
        
        // 尝试创建配置文件
        std::wcout << L"尝试创建配置文件..." << std::endl;
        std::ofstream configFile(absolutePath);
        if (configFile.is_open()) {
            configFile << "{\"categories\":[]}";
            configFile.close();
            std::wcout << L"配置文件创建成功" << std::endl;
        } else {
            std::wcout << L"配置文件创建失败" << std::endl;
        }
        
        // 检查文件是否真的创建了
        if (fs::exists(absolutePath)) {
            std::wcout << L"配置文件确实存在，大小: " << fs::file_size(absolutePath) << L" 字节" << std::endl;
        } else {
            std::wcout << L"配置文件不存在" << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::wcout << L"异常: " << e.what() << std::endl;
    }
}

int main() {
    // 设置控制台编码为UTF-8
    system("chcp 65001 > nul");
    
    testCategoryPath();
    
    std::wcout << L"\n=== 测试完成 ===" << std::endl;
    return 0;
}