// 备用对话框实现 - 当资源加载失败时使用
#include "VerticalFileSwitcher.h"
#include <windows.h>

// 备用对话框创建函数
HWND CreateVerticalFileSwitcherFallback(HWND hParent, HINSTANCE hInst) {
    // 使用CreateWindowEx直接创建窗口，绕过资源文件
    HWND hWnd = CreateWindowEx(
        WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
        L"STATIC",  // 使用静态控件类
        L"Document List",
        WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD | WS_VISIBLE,
        100, 100, 200, 300,  // 默认位置和大小
        hParent,
        NULL,
        hInst,
        NULL
    );
    
    if (hWnd) {
        // 创建列表视图控件
        HWND hListView = CreateWindowEx(
            WS_EX_CLIENTEDGE,
            WC_LISTVIEW,
            L"",
            WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
            10, 10, 180, 280,
            hWnd,
            (HMENU)3001,  // 使用IDC_LIST_DOCLIST的ID
            hInst,
            NULL
        );
        
        if (hListView) {
            // 设置列表视图样式
            ListView_SetExtendedListViewStyle(hListView, LVS_EX_FULLROWSELECT | LVS_EX_DOUBLEBUFFER);
        }
    }
    
    return hWnd;
}

// 修改VerticalFileSwitcher的create方法以使用备用实现
void VerticalFileSwitcher::createFallback(tTbData* data, bool isRTL) {
    // 尝试使用备用实现创建窗口
    _hSelf = CreateVerticalFileSwitcherFallback(_hParent, _hInst);
    
    if (_hSelf) {
        // 窗口创建成功，继续初始化
        _fileListView.Window::init(_hInst, _hSelf);
        
        // 获取列表视图控件
        HWND hListView = GetDlgItem(_hSelf, 3001);  // 使用备用ID
        if (hListView) {
            _fileListView.setHSelf(hListView);
            _fileListView.setHImageList(_hImaLst);
            _fileListView.initList();
        }
        
        // 设置用户数据
        data->hClient = _hSelf;
        data->pszName = L"Document List";
        data->uMask = 0;
        data->pszAddInfo = nullptr;
        
        // 发送模型对话框添加消息
        ::SendMessage(_hParent, NPPM_MODELESSDIALOG, MODELESSDIALOGADD, reinterpret_cast<WPARAM>(_hSelf));
    }
}
