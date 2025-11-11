#include <windows.h>

// OLEAUT32.dll序号381对应的函数（假设是VarUI1FromI4）
EXTERN_C __declspec(dllexport) HRESULT WINAPI VarUI1FromI4(LONG lIn, BYTE *pbOut)
{
    // 加载真正的OLEAUT32.dll
    HMODULE hOleAut32 = LoadLibraryA("oleaut32.dll");
    if (!hOleAut32) return E_FAIL;
    
    // 获取真正的函数地址
    FARPROC pRealFunc = GetProcAddress(hOleAut32, "VarUI1FromI4");
    if (!pRealFunc) {
        FreeLibrary(hOleAut32);
        return E_FAIL;
    }
    
    // 调用真正的函数
    HRESULT result = ((HRESULT (WINAPI*)(LONG, BYTE*))pRealFunc)(lIn, pbOut);
    FreeLibrary(hOleAut32);
    return result;
}

// DLL入口点
BOOL APIENTRY DllMain(HMODULE hModule, DWORD dwReason, LPVOID lpReserved)
{
    return TRUE;
}
