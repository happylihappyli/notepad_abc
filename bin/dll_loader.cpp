#include <windows.h>
#include <iostream>

int main() {
    // 设置DLL搜索路径为系统目录
    SetDllDirectory(L"C:\\Windows\\System32");
    
    // 启动目标程序
    STARTUPINFO si = { sizeof(si) };
    PROCESS_INFORMATION pi;
    
    if (CreateProcess(L"notepad_abc.exe", NULL, NULL, NULL, FALSE, 
                     0, NULL, NULL, &si, &pi)) {
        std::cout << "程序启动成功，进程ID: " << pi.dwProcessId << std::endl;
        
        // 等待程序结束
        WaitForSingleObject(pi.hProcess, INFINITE);
        
        DWORD exitCode;
        GetExitCodeProcess(pi.hProcess, &exitCode);
        std::cout << "程序退出，返回代码: " << exitCode << std::endl;
        
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        
        return exitCode == 0 ? 0 : 1;
    } else {
        std::cout << "启动程序失败，错误代码: " << GetLastError() << std::endl;
        return 1;
    }
}