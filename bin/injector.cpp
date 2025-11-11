#include <windows.h>
#include <iostream>

// 自定义LoadLibrary函数，强制使用系统DLL
HMODULE WINAPI MyLoadLibraryA(LPCSTR lpLibFileName) {
    // 如果是OLEAUT32.dll，强制使用系统版本
    if (strcmp(lpLibFileName, "OLEAUT32.dll") == 0) {
        return LoadLibraryA("C:\\Windows\\System32\\OLEAUT32.dll");
    }
    return LoadLibraryA(lpLibFileName);
}

HMODULE WINAPI MyLoadLibraryW(LPCWSTR lpLibFileName) {
    // 如果是OLEAUT32.dll，强制使用系统版本
    if (wcscmp(lpLibFileName, L"OLEAUT32.dll") == 0) {
        return LoadLibraryW(L"C:\\Windows\\System32\\OLEAUT32.dll");
    }
    return LoadLibraryW(lpLibFileName);
}

int main() {
    std::cout << "DLL注入器启动..." << std::endl;
    
    // 启动目标程序
    STARTUPINFO si = { sizeof(si) };
    PROCESS_INFORMATION pi;
    
    if (CreateProcess(L"notepad_abc.exe", NULL, NULL, NULL, FALSE, 
                      CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        std::cout << "程序已创建（挂起状态），进程ID: " << pi.dwProcessId << std::endl;
        
        // 恢复进程执行
        ResumeThread(pi.hThread);
        
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