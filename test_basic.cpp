#include <iostream>
#include <windows.h>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    // 创建控制台窗口用于调试输出
    if (AllocConsole()) {
        // 设置控制台编码为UTF-8，解决中文显示问号问题
        SetConsoleOutputCP(CP_UTF8);
        SetConsoleCP(CP_UTF8);
        // 重定向标准输出到控制台
        freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);
        freopen_s((FILE**)stderr, "CONOUT$", "w", stderr);
        // 设置控制台标题
        SetConsoleTitle(L"Notepad++ Basic Test");
        // 输出启动信息
        wprintf(L"=== Basic Test 启动 ===\n");
        wprintf(L"程序开始运行\n");
    }
    
    std::cout << "程序基础测试成功!" << std::endl;
    std::cout << "Press any key to continue..." << std::endl;
    
    // 等待用户按键
    _getwch();
    
    return 0;
}