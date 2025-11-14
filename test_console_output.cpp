#include <iostream>
#include <windows.h>
#include <string>

int main() {
    // 测试方法1: 使用cout输出窄字符
    std::cout << "测试中文输出 - 窄字符 (cout)" << std::endl;
    
    // 测试方法2: 使用wcout输出宽字符
    std::wcout << L"测试中文输出 - 宽字符 (wcout)" << std::endl;
    
    // 测试方法3: 使用WriteConsoleW直接输出
    HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
    if (hConsole != INVALID_HANDLE_VALUE) {
        DWORD charsWritten;
        WriteConsoleW(hConsole, L"测试中文输出 - WriteConsoleW\n", 10, &charsWritten, NULL);
    }
    
    // 测试方法4: 使用printf输出窄字符
    printf("测试中文输出 - 窄字符 (printf)\n");
    
    // 测试方法5: 使用wprintf输出宽字符
    wprintf(L"测试中文输出 - 宽字符 (wprintf)\n");
    
    // 设置控制台编码为UTF-8
    SetConsoleOutputCP(CP_UTF8);
    std::cout << "设置UTF-8编码后 - 窄字符 (cout)" << std::endl;
    std::wcout << L"设置UTF-8编码后 - 宽字符 (wcout)" << std::endl;
    
    return 0;
}