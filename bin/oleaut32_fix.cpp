#include <windows.h>

// Export SysAllocStringLen function
EXTERN_C __declspec(dllexport) BSTR WINAPI SysAllocStringLen(const OLECHAR* str, UINT len)
{
    // Load real OLEAUT32.dll from system directory
    HMODULE hOleAut32 = LoadLibraryExA("oleaut32.dll", NULL, LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!hOleAut32) return NULL;
    
    // Get real function address
    FARPROC pRealFunc = GetProcAddress(hOleAut32, "SysAllocStringLen");
    if (!pRealFunc) {
        FreeLibrary(hOleAut32);
        return NULL;
    }
    
    // Call real function
    BSTR ret = ((BSTR (WINAPI*)(const OLECHAR*, UINT))pRealFunc)(str, len);
    FreeLibrary(hOleAut32);
    return ret;
}

// Export SysFreeString function
EXTERN_C __declspec(dllexport) void WINAPI SysFreeString(BSTR bstr)
{
    // Load real OLEAUT32.dll from system directory
    HMODULE hOleAut32 = LoadLibraryExA("oleaut32.dll", NULL, LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!hOleAut32) return;
    
    // Get real function address
    FARPROC pRealFunc = GetProcAddress(hOleAut32, "SysFreeString");
    if (!pRealFunc) {
        FreeLibrary(hOleAut32);
        return;
    }
    
    // Call real function
    ((void (WINAPI*)(BSTR))pRealFunc)(bstr);
    FreeLibrary(hOleAut32);
}

// Export VarUI1FromI4 function (ordinal 381)
EXTERN_C __declspec(dllexport) HRESULT WINAPI VarUI1FromI4(LONG lIn, BYTE *pbOut)
{
    // Load real OLEAUT32.dll from system directory
    HMODULE hOleAut32 = LoadLibraryExA("oleaut32.dll", NULL, LOAD_LIBRARY_SEARCH_SYSTEM32);
    if (!hOleAut32) return E_FAIL;
    
    // Get real function address
    FARPROC pRealFunc = GetProcAddress(hOleAut32, "VarUI1FromI4");
    if (!pRealFunc) {
        pRealFunc = GetProcAddress(hOleAut32, MAKEINTRESOURCEA(381));
    }
    
    if (!pRealFunc) {
        FreeLibrary(hOleAut32);
        return E_FAIL;
    }
    
    HRESULT hr = ((HRESULT (WINAPI*)(LONG, BYTE*))pRealFunc)(lIn, pbOut);
    FreeLibrary(hOleAut32);
    return hr;
}

// DLL entry point
BOOL APIENTRY DllMain(HMODULE hModule, DWORD dwReason, LPVOID lpReserved)
{
    return TRUE;
}