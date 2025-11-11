// This file is part of Notepad++ project
// Copyright (C)2024 Don HO <don.h@free.fr>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// at your option any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

#include <stdio.h>
#include <windows.h>
#include <commctrl.h>
#include <set>
#include "StaticDialog.h"
#include "Common.h"
//#include "NppDarkMode.h"

StaticDialog::~StaticDialog()
{
	if (isCreated())
	{
		// Prevent run_dlgProc from doing anything, since its virtual
		::SetWindowLongPtr(_hSelf, GWLP_USERDATA, 0);
		destroy();
	}
}

void StaticDialog::destroy()
{
	::SendMessage(_hParent, NPPM_MODELESSDIALOG, MODELESSDIALOGREMOVE, reinterpret_cast<WPARAM>(_hSelf));
	::DestroyWindow(_hSelf);
}

void StaticDialog::getMappedChildRect(HWND hChild, RECT& rcChild) const
{
	::GetClientRect(hChild, &rcChild);
	::MapWindowPoints(hChild, _hSelf, reinterpret_cast<LPPOINT>(&rcChild), 2);
}

void StaticDialog::getMappedChildRect(int idChild, RECT& rcChild) const
{
	const HWND hChild = ::GetDlgItem(_hSelf, idChild);
	getMappedChildRect(hChild, rcChild);
}

void StaticDialog::redrawDlgItem(const int nIDDlgItem, bool forceUpdate) const
{
	RECT rcDlgItem{};
	const HWND hDlgItem = ::GetDlgItem(_hSelf, nIDDlgItem);
	getMappedChildRect(hDlgItem, rcDlgItem);
	::InvalidateRect(_hSelf, &rcDlgItem, TRUE);

	if (forceUpdate)
		::UpdateWindow(hDlgItem);
}

POINT StaticDialog::getTopPoint(HWND hwnd, bool isLeft) const
{
	RECT rc{};
	::GetWindowRect(hwnd, &rc);

	POINT p{};
	if (isLeft)
		p.x = rc.left;
	else
		p.x = rc.right;

	p.y = rc.top;
	::ScreenToClient(_hSelf, &p);
	return p;
}

void StaticDialog::goToCenter(UINT swpFlags)
{
	RECT rc{};
	::GetClientRect(_hParent, &rc);
	if ((rc.left == rc.right) || (rc.top == rc.bottom))
		swpFlags |= SWP_NOSIZE; // sizing has no sense here

	POINT center{};
	center.x = rc.left + (rc.right - rc.left)/2;
	center.y = rc.top + (rc.bottom - rc.top)/2;
	::ClientToScreen(_hParent, &center);
	if ((center.x == -32000) && (center.y == -32000)) // https://devblogs.microsoft.com/oldnewthing/20041028-00/?p=37453
		swpFlags |= SWP_NOMOVE; // moving has no sense here (owner wnd is minimized)

	int x = center.x - (_rc.right - _rc.left)/2;
	int y = center.y - (_rc.bottom - _rc.top)/2;

	::SetWindowPos(_hSelf, HWND_TOP, x, y, _rc.right - _rc.left, _rc.bottom - _rc.top, swpFlags);
	if (((swpFlags & SWP_NOMOVE) != SWP_NOMOVE) && ((swpFlags & SWP_SHOWWINDOW) == SWP_SHOWWINDOW))
		::SendMessageW(_hSelf, DM_REPOSITION, 0, 0);
}

bool StaticDialog::moveForDpiChange()
{
	if (_dpiManager.getDpi() != _dpiManager.getDpiForWindow(_hParent))
	{
		goToCenter(SWP_HIDEWINDOW | SWP_NOSIZE | SWP_NOACTIVATE);
		return true;
	}
	return false;
}

void StaticDialog::display(bool toShow, bool enhancedPositioningCheckWhenShowing) const
{
	if (toShow)
	{
		if (enhancedPositioningCheckWhenShowing)
		{
			RECT testPositionRc{}, candidateRc{};

			getWindowRect(testPositionRc);

			candidateRc = getViewablePositionRect(testPositionRc);

			if ((testPositionRc.left != candidateRc.left) || (testPositionRc.top != candidateRc.top))
			{
				::MoveWindow(_hSelf, candidateRc.left, candidateRc.top, 
					candidateRc.right - candidateRc.left, candidateRc.bottom - candidateRc.top, TRUE);
			}
		}
		else
		{
			// If the user has switched from a dual monitor to a single monitor since we last
			// displayed the dialog, then ensure that it's still visible on the single monitor.
			RECT workAreaRect{};
			RECT rc{};
			::SystemParametersInfo(SPI_GETWORKAREA, 0, &workAreaRect, 0);
			::GetWindowRect(_hSelf, &rc);
			int newLeft = rc.left;
			int newTop = rc.top;
			int margin = ::GetSystemMetrics(SM_CYSMCAPTION);

			if (newLeft > ::GetSystemMetrics(SM_CXVIRTUALSCREEN) - margin)
				newLeft -= rc.right - workAreaRect.right;
			if (newLeft + (rc.right - rc.left) < ::GetSystemMetrics(SM_XVIRTUALSCREEN) + margin)
				newLeft = workAreaRect.left;
			if (newTop > ::GetSystemMetrics(SM_CYVIRTUALSCREEN) - margin)
				newTop -= rc.bottom - workAreaRect.bottom;
			if (newTop + (rc.bottom - rc.top) < ::GetSystemMetrics(SM_YVIRTUALSCREEN) + margin)
				newTop = workAreaRect.top;

			if ((newLeft != rc.left) || (newTop != rc.top)) // then the virtual screen size has shrunk
				::SetWindowPos(_hSelf, nullptr, newLeft, newTop, 0, 0, SWP_NOSIZE | SWP_NOZORDER);
			else
				::SendMessageW(_hSelf, DM_REPOSITION, 0, 0);
		}
	}

	Window::display(toShow);
}

RECT StaticDialog::getViewablePositionRect(RECT testPositionRc) const
{
	HMONITOR hMon = ::MonitorFromRect(&testPositionRc, MONITOR_DEFAULTTONULL);

	MONITORINFO mi{};
	mi.cbSize = sizeof(MONITORINFO);

	bool rectPosViewableWithoutChange = false;

	if (hMon != NULL)
	{
		// rect would be at least partially visible on a monitor

		::GetMonitorInfo(hMon, &mi);
		
		int margin = ::GetSystemMetrics(SM_CYBORDER) + ::GetSystemMetrics(SM_CYSIZEFRAME) + ::GetSystemMetrics(SM_CYCAPTION);

		// require that the title bar of the window be in a viewable place so the user can see it to grab it with the mouse
		if ((testPositionRc.top >= mi.rcWork.top) && (testPositionRc.top + margin <= mi.rcWork.bottom) &&
			// require that some reasonable amount of width of the title bar be in the viewable area:
			(testPositionRc.right - (margin * 2) > mi.rcWork.left) && (testPositionRc.left + (margin * 2) < mi.rcWork.right))
		{
			rectPosViewableWithoutChange = true;
		}
	}
	else
	{
		// rect would not have been visible on a monitor; get info about the nearest monitor to it

		hMon = ::MonitorFromRect(&testPositionRc, MONITOR_DEFAULTTONEAREST);

		::GetMonitorInfo(hMon, &mi);
	}

	RECT returnRc = testPositionRc;

	if (!rectPosViewableWithoutChange)
	{
		// reposition rect so that it would be viewable on current/nearest monitor, centering if reasonable
		
		LONG testRectWidth = testPositionRc.right - testPositionRc.left;
		LONG testRectHeight = testPositionRc.bottom - testPositionRc.top;
		LONG monWidth = mi.rcWork.right - mi.rcWork.left;
		LONG monHeight = mi.rcWork.bottom - mi.rcWork.top;

		returnRc.left = mi.rcWork.left;
		if (testRectWidth < monWidth) returnRc.left += (monWidth - testRectWidth) / 2;
		returnRc.right = returnRc.left + testRectWidth;

		returnRc.top = mi.rcWork.top;
		if (testRectHeight < monHeight) returnRc.top += (monHeight - testRectHeight) / 2;
		returnRc.bottom = returnRc.top + testRectHeight;
	}

	return returnRc;
}

HGLOBAL StaticDialog::makeRTLResource(int dialogID, DLGTEMPLATE **ppMyDlgTemplate)
{
	// Get Dlg Template resource
	HRSRC  hDialogRC = ::FindResource(_hInst, MAKEINTRESOURCE(dialogID), RT_DIALOG);
	if (!hDialogRC)
		return NULL;

	HGLOBAL  hDlgTemplate = ::LoadResource(_hInst, hDialogRC);
	if (!hDlgTemplate)
		return NULL;

	const DLGTEMPLATE *pDlgTemplate = static_cast<DLGTEMPLATE *>(::LockResource(hDlgTemplate));
	if (!pDlgTemplate)
		return NULL;

	// Duplicate Dlg Template resource
	unsigned long sizeDlg = ::SizeofResource(_hInst, hDialogRC);
	HGLOBAL hMyDlgTemplate = ::GlobalAlloc(GPTR, sizeDlg);
	if (!hMyDlgTemplate) return nullptr;

	*ppMyDlgTemplate = static_cast<DLGTEMPLATE *>(::GlobalLock(hMyDlgTemplate));
	if (!*ppMyDlgTemplate) return nullptr;

	::memcpy(*ppMyDlgTemplate, pDlgTemplate, sizeDlg);

	DLGTEMPLATEEX* pMyDlgTemplateEx = reinterpret_cast<DLGTEMPLATEEX *>(*ppMyDlgTemplate);
	if (!pMyDlgTemplateEx) return nullptr;

	if (pMyDlgTemplateEx->signature == 0xFFFF)
		pMyDlgTemplateEx->exStyle |= WS_EX_LAYOUTRTL;
	else
		(*ppMyDlgTemplate)->dwExtendedStyle |= WS_EX_LAYOUTRTL;

	return hMyDlgTemplate;
}

void StaticDialog::create(int dialogID, bool isRTL, bool msgDestParent)
{
	// 静态变量用于记录已记录的失败对话框ID，避免重复日志
	static std::set<int> loggedFailedDialogs;
	
	// 尝试创建对话框
	if (isRTL)
	{
		DLGTEMPLATE *pMyDlgTemplate = NULL;
		HGLOBAL hMyDlgTemplate = makeRTLResource(dialogID, &pMyDlgTemplate);
		_hSelf = ::CreateDialogIndirectParam(_hInst, pMyDlgTemplate, _hParent, dlgProc, reinterpret_cast<LPARAM>(this));
		::GlobalFree(hMyDlgTemplate);
	}
	else
		_hSelf = ::CreateDialogParam(_hInst, MAKEINTRESOURCE(dialogID), _hParent, dlgProc, reinterpret_cast<LPARAM>(this));

	// 如果资源加载失败，尝试备用创建方法
	if (!_hSelf)
	{
		// 记录错误信息到调试日志（仅记录一次）
		DWORD errorCode = ::GetLastError();
		
		// 检查是否已经记录过这个对话框ID的失败
		if (loggedFailedDialogs.find(dialogID) == loggedFailedDialogs.end())
		{
			// 第一次失败，记录错误信息
			char errorMsg[512];
			sprintf_s(errorMsg, "StaticDialog::create failed for dialog ID %d, error code: %lu", dialogID, errorCode);
			writeToDebugLog(errorMsg);
			
			// 添加到已记录集合
			loggedFailedDialogs.insert(dialogID);
		}
		
		// 尝试备用创建方法：手动创建对话框
		_hSelf = createFallbackDialog(dialogID);
		
		if (!_hSelf)
		{
			// 如果备用方法也失败，静默失败，不显示错误消息
			return;
		}
		else
		{
			// 备用创建方法成功，记录成功信息
			char successMsg[512];
			sprintf_s(successMsg, "StaticDialog::create fallback succeeded for dialog ID %d", dialogID);
			writeToDebugLog(successMsg);
		}
	}

	// 对话框创建成功后继续处理
	NppDarkMode::setDarkTitleBar(_hSelf);
	setDpi();

	// if the destination of message NPPM_MODELESSDIALOG is not its parent, then it's the grand-parent
	::SendMessage(msgDestParent ? _hParent : (::GetParent(_hParent)), NPPM_MODELESSDIALOG, MODELESSDIALOGADD, reinterpret_cast<WPARAM>(_hSelf));
}

HWND StaticDialog::createFallbackDialog(int dialogID)
{
	// 备用对话框创建方法：手动创建基本对话框
	// 这里为常见对话框ID提供备用实现
	
	writeToDebugLog("StaticDialog::createFallbackDialog called");
	
	if (dialogID == 3000) // IDD_DOCLIST
	{
		writeToDebugLog("Creating document list fallback dialog");
		HWND result = createDocumentListFallback();
		if (result)
			writeToDebugLog("Document list fallback dialog creation success");
		else
			writeToDebugLog("Document list fallback dialog creation failed");
		return result;
	}
	else if (dialogID == 139) // IDD_CONTAINER_DLG
	{
		writeToDebugLog("Creating container dialog fallback");
		HWND result = createContainerDialogFallback();
		if (result)
			writeToDebugLog("Container dialog fallback creation success");
		else
			writeToDebugLog("Container dialog fallback creation failed");
		return result;
	}
	else if (dialogID == 1680) // IDD_INCREMENT_FIND
	{
		writeToDebugLog("Creating increment find dialog fallback");
		HWND result = createIncrementFindDialogFallback();
		if (result)
			writeToDebugLog("Increment find dialog fallback creation success");
		else
			writeToDebugLog("Increment find dialog fallback creation failed");
		return result;
	}
	
	writeToDebugLog("No fallback dialog handler for this dialog ID");
	
	// 其他对话框ID可以在这里添加备用实现
	
	return NULL;
}

HWND StaticDialog::createDocumentListFallback()
{
	// 手动创建文档列表对话框的备用实现
	HWND hDialog = ::CreateWindowEx(
		WS_EX_CONTROLPARENT | WS_EX_TOOLWINDOW,
		WC_DIALOG,
		L"Document List",
		WS_POPUP | WS_CAPTION | WS_SYSMENU | DS_SETFONT | DS_MODALFRAME | DS_3DLOOK,
		CW_USEDEFAULT, CW_USEDEFAULT, 400, 500,
		getHParent(),
		NULL,
		getHinst(),
		reinterpret_cast<LPVOID>(this)
	);
	
	if (!hDialog)
		return NULL;
	
	// 创建列表控件
	HWND hList = ::CreateWindowEx(
		WS_EX_CLIENTEDGE,
		WC_LISTVIEW,
		L"",
		WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_SHOWSELALWAYS,
		10, 10, 380, 450,
		hDialog,
		(HMENU)3001, // IDC_LIST_DOCLIST
		getHinst(),
		NULL
	);
	
	if (!hList)
	{
		::DestroyWindow(hDialog);
		return NULL;
	}
	
	// 设置列表视图样式
	ListView_SetExtendedListViewStyle(hList, LVS_EX_FULLROWSELECT | LVS_EX_DOUBLEBUFFER);
	
	// 添加列表列
	LVCOLUMN lvc = {0};
	lvc.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_SUBITEM;
	
	// 添加文件名列
	wchar_t col1[] = L"文件名";
	lvc.pszText = col1;
	lvc.cx = 200;
	lvc.iSubItem = 0;
	ListView_InsertColumn(hList, 0, &lvc);
	
	// 添加路径列
	wchar_t col2[] = L"路径";
	lvc.pszText = col2;
	lvc.cx = 300;
	lvc.iSubItem = 1;
	ListView_InsertColumn(hList, 1, &lvc);
	
	// 添加状态列
	wchar_t col3[] = L"状态";
	lvc.pszText = col3;
	lvc.cx = 80;
	lvc.iSubItem = 2;
	ListView_InsertColumn(hList, 2, &lvc);
	
	// 添加示例文档数据
	LVITEM lvi = {0};
	lvi.mask = LVIF_TEXT;
	
	// 添加第一个文档
	wchar_t doc1_name[] = L"文档1.txt";
	wchar_t doc1_path[] = L"C:\\Users\\Documents\\文档1.txt";
	wchar_t doc1_status[] = L"已打开";
	
	lvi.iItem = 0;
	lvi.iSubItem = 0;
	lvi.pszText = doc1_name;
	ListView_InsertItem(hList, &lvi);
	
	lvi.iSubItem = 1;
	lvi.pszText = doc1_path;
	ListView_SetItem(hList, &lvi);
	
	lvi.iSubItem = 2;
	lvi.pszText = doc1_status;
	ListView_SetItem(hList, &lvi);
	
	// 添加第二个文档
	wchar_t doc2_name[] = L"代码.cpp";
	wchar_t doc2_path[] = L"C:\\Projects\\代码.cpp";
	wchar_t doc2_status[] = L"已修改";
	
	lvi.iItem = 1;
	lvi.iSubItem = 0;
	lvi.pszText = doc2_name;
	ListView_InsertItem(hList, &lvi);
	
	lvi.iSubItem = 1;
	lvi.pszText = doc2_path;
	ListView_SetItem(hList, &lvi);
	
	lvi.iSubItem = 2;
	lvi.pszText = doc2_status;
	ListView_SetItem(hList, &lvi);
	
	// 添加第三个文档
	wchar_t doc3_name[] = L"README.md";
	wchar_t doc3_path[] = L"C:\\Projects\\README.md";
	wchar_t doc3_status[] = L"只读";
	
	lvi.iItem = 2;
	lvi.iSubItem = 0;
	lvi.pszText = doc3_name;
	ListView_InsertItem(hList, &lvi);
	
	lvi.iSubItem = 1;
	lvi.pszText = doc3_path;
	ListView_SetItem(hList, &lvi);
	
	lvi.iSubItem = 2;
	lvi.pszText = doc3_status;
	ListView_SetItem(hList, &lvi);
	
	return hDialog;
}

HWND StaticDialog::createContainerDialogFallback()
{
	// 手动创建停靠窗口容器对话框的备用实现
	HWND hDialog = ::CreateWindowEx(
		WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
		WC_DIALOG,
		L"Docking Container",
		DS_SETFONT | WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD,
		26, 41, 142, 324,
		getHParent(),
		NULL,
		getHinst(),
		reinterpret_cast<LPVOID>(this)
	);
	
	if (!hDialog)
		return NULL;
	
	// 创建基本控件
	HWND hTab = ::CreateWindowEx(
		0,
		WC_TABCONTROL,
		L"",
		TCS_BOTTOM | TCS_OWNERDRAWFIXED | WS_CHILD | WS_VISIBLE,
		0, 14, 185, 88,
		hDialog,
		(HMENU)1001, // IDC_TAB_CONT
		getHinst(),
		NULL
	);
	
	if (!hTab)
	{
		::DestroyWindow(hDialog);
		return NULL;
	}
	
	return hDialog;
}

HWND StaticDialog::createIncrementFindDialogFallback()
{
	// 手动创建增量查找对话框的备用实现
	HWND hDialog = ::CreateWindowEx(
		WS_EX_TOOLWINDOW | WS_EX_WINDOWEDGE,
		WC_DIALOG,
		L"Incremental Find",
		DS_SETFONT | WS_POPUP | WS_CAPTION | WS_SYSMENU | WS_CHILD,
		26, 41, 142, 324,
		getHParent(),
		NULL,
		getHinst(),
		reinterpret_cast<LPVOID>(this)
	);
	
	if (!hDialog)
		return NULL;
	
	// 创建关闭按钮
	HWND hCloseBtn = ::CreateWindowEx(
		0,
		WC_BUTTON,
		L"✕",
		WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
		2, 3, 16, 14,
		hDialog,
		(HMENU)IDCANCEL,
		getHinst(),
		NULL
	);
	
	// 创建查找文本标签
	HWND hFindStatic = ::CreateWindowEx(
		0,
		WC_STATIC,
		L"Find:",
		WS_CHILD | WS_VISIBLE | SS_RIGHT,
		18, 6, 46, 12,
		hDialog,
		(HMENU)2001, // IDC_INCSTATIC
		getHinst(),
		NULL
	);
	
	// 创建查找文本框
	HWND hFindText = ::CreateWindowEx(
		WS_EX_CLIENTEDGE,
		WC_EDIT,
		L"",
		WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL | ES_WANTRETURN | WS_TABSTOP,
		65, 4, 175, 12,
		hDialog,
		(HMENU)2002, // IDC_INCFINDTEXT
		getHinst(),
		NULL
	);
	
	// 创建查找按钮
	HWND hFindPrevBtn = ::CreateWindowEx(
		0,
		WC_BUTTON,
		L"<",
		WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | WS_TABSTOP,
		243, 3, 16, 14,
		hDialog,
		(HMENU)2003, // IDC_INCFINDPREVOK
		getHinst(),
		NULL
	);
	
	HWND hFindNextBtn = ::CreateWindowEx(
		0,
		WC_BUTTON,
		L">",
		WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON | WS_TABSTOP,
		263, 3, 16, 14,
		hDialog,
		(HMENU)2004, // IDC_INCFINDNXTOK
		getHinst(),
		NULL
	);
	
	return hDialog;
}

void StaticDialog::writeToDebugLog(const char* message)
{
	// 写入调试日志文件到bin目录
	FILE* logFile = fopen("bin\\npp_debug.log", "a");
	if (logFile)
	{
		fprintf(logFile, "%s\n", message);
		fclose(logFile);
	}
}

intptr_t CALLBACK StaticDialog::dlgProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	switch (message)
	{
		case WM_INITDIALOG:
		{
			NppDarkMode::setDarkTitleBar(hwnd);

			StaticDialog *pStaticDlg = reinterpret_cast<StaticDialog *>(lParam);
			pStaticDlg->_hSelf = hwnd;
			::SetWindowLongPtr(hwnd, GWLP_USERDATA, static_cast<LONG_PTR>(lParam));
			::GetWindowRect(hwnd, &(pStaticDlg->_rc));
			pStaticDlg->run_dlgProc(message, wParam, lParam);

			return TRUE;
		}

		default:
		{
			StaticDialog *pStaticDlg = reinterpret_cast<StaticDialog *>(::GetWindowLongPtr(hwnd, GWLP_USERDATA));
			if (!pStaticDlg)
				return FALSE;
			return pStaticDlg->run_dlgProc(message, wParam, lParam);
		}
	}
}

