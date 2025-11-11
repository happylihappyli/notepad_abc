#include <windows.h>
#include <commctrl.h>

// 缺失的函数 - 创建简单的实现
extern "C" {
    // 序号381 - 可能是某个旧版本的函数
    __declspec(dllexport) void WINAPI __Ordinal381() {
        // 空实现
        return;
    }
    
    // 序号411 - 可能是某个旧版本的函数
    __declspec(dllexport) void WINAPI __Ordinal411() {
        // 空实现
        return;
    }
    
    // 导出现有函数
    __declspec(dllexport) void WINAPI InitCommonControls() {
        ::InitCommonControls();
    }
    
    __declspec(dllexport) LRESULT WINAPI RemoveWindowSubclass(HWND hWnd, SUBCLASSPROC pfnSubclass, UINT_PTR uIDSubclass) {
        return ::RemoveWindowSubclass(hWnd, pfnSubclass, uIDSubclass);
    }
    
    __declspec(dllexport) BOOL WINAPI SetWindowSubclass(HWND hWnd, SUBCLASSPROC pfnSubclass, UINT_PTR uIDSubclass, DWORD_PTR dwRefData) {
        return ::SetWindowSubclass(hWnd, pfnSubclass, uIDSubclass, dwRefData);
    }
    
    __declspec(dllexport) LRESULT WINAPI DefSubclassProc(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
        return ::DefSubclassProc(hWnd, uMsg, wParam, lParam);
    }
}

// DLL入口点
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        // 初始化通用控件
        InitCommonControls();
        break;
    case DLL_THREAD_ATTACH:
        break;
    case DLL_THREAD_DETACH:
        break;
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
