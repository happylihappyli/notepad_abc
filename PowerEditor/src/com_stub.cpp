// COM支持库替代实现
// 提供简单的COM错误处理函数，避免依赖comsuppw.lib

#include <windows.h>
#include <stdio.h>

// 使用C++名称修饰，确保与链接器期望的签名匹配

// 简单的_com_issue_error函数实现 - 使用C++名称修饰
void __cdecl _com_issue_error(long hr)
{
    // 简单的错误处理：输出错误信息到调试器
    char buffer[256];
    sprintf_s(buffer, sizeof(buffer), "COM Error: 0x%08X", hr);
    OutputDebugStringA(buffer);
    
    // 抛出简单的异常
    throw hr;
}

// 其他可能的COM支持库函数占位符
void __cdecl _com_raise_error(long hr)
{
    _com_issue_error(hr);
}

// 简单的COM错误类实现
class _com_error
{
public:
    _com_error(long hr) : m_hr(hr) {}
    long Error() const { return m_hr; }
    
private:
    long m_hr;
};