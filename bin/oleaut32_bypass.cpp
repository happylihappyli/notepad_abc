// OLEAUT32.dll绕过解决方案
// 只提供程序需要的两个函数，避免完整的OLEAUT32.dll依赖

#include <windows.h>

// 序号4对应的函数（通常是VarUI1FromI4）
HRESULT WINAPI VarUI1FromI4(LONG lIn, BYTE *pbOut)
{
    // 简单的实现，返回成功
    if (pbOut)
    {
        *pbOut = (BYTE)(lIn & 0xFF);
        return S_OK;
    }
    return E_INVALIDARG;
}

// 序号6对应的函数（通常是VarI4FromUI1）
HRESULT WINAPI VarI4FromUI1(BYTE bIn, LONG *plOut)
{
    // 简单的实现，返回成功
    if (plOut)
    {
        *plOut = (LONG)bIn;
        return S_OK;
    }
    return E_INVALIDARG;
}

// DLL入口点
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    return TRUE;
}

// 导出函数表
extern "C" {
    #pragma comment(linker, "/EXPORT:VarUI1FromI4=VarUI1FromI4,@4")
    #pragma comment(linker, "/EXPORT:VarI4FromUI1=VarI4FromUI1,@6")
}