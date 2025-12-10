// Backup Dialog Implementation - Used When Resource Loading Fails
#include "VerticalFileSwitcher.h"
#include <windows.h>

// Backup Dialog Creation Function
HWND CreateVerticalFileSwitcherFallback(HWND hParent, HINSTANCE hInst) {
    // Use CreateWindowEx to Create Window Directly, Bypassing Resource File
    HWND hWnd = CreateWindowEx(
        WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
        L"STATIC",  // Use Static Control Class
        L"Document List",
        WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD | WS_VISIBLE,
        100, 100, 200, 300,  // Default Position and Size
        hParent,
        NULL,
        hInst,
        NULL
    );
    
    if (hWnd) {
        // Create List View Control
        HWND hListView = CreateWindowEx(
            WS_EX_CLIENTEDGE,
            WC_LISTVIEW,
            L"",
            WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
            10, 10, 180, 280,
            hWnd,
            (HMENU)3001,  // Use IDC_LIST_DOCLIST ID
            hInst,
            NULL
        );
        
        if (hListView) {
            // Set List View Style
            ListView_SetExtendedListViewStyle(hListView, LVS_EX_FULLROWSELECT | LVS_EX_DOUBLEBUFFER);
        }
    }
    
    return hWnd;
}

// Modify VerticalFileSwitcher's create Method to Use Backup Implementation
void VerticalFileSwitcher::createFallback(tTbData* data, bool isRTL) {
    // Try Creating Window Using Backup Implementation
    _hSelf = CreateVerticalFileSwitcherFallback(_hParent, _hInst);
    
    if (_hSelf) {
        // Window Created Successfully, Continue Initialization
        _fileListView.Window::init(_hInst, _hSelf);
        
        // Get List View Control
        HWND hListView = GetDlgItem(_hSelf, 3001);  // Use Backup ID
        if (hListView) {
            _fileListView.setHSelf(hListView);
            _fileListView.setHImageList(_hImaLst);
            _fileListView.initList();
        }
        
        // Set User Data
        data->hClient = _hSelf;
        data->pszName = L"Document List";
        data->uMask = 0;
        data->pszAddInfo = nullptr;
        
        // Send Modal Dialog Add Message
        ::SendMessage(_hParent, NPPM_MODELESSDIALOG, MODELESSDIALOGADD, reinterpret_cast<WPARAM>(_hSelf));
    }
}
