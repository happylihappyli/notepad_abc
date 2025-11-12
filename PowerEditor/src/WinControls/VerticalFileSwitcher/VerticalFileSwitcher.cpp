// This file is part of Notepad++ project
// Copyright (C)2021 Don HO <don.h@free.fr>

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



#include "VerticalFileSwitcher.h"
#include "menuCmdID.h"
#include "Parameters.h"
#include "resource.h"
#include "localization.h"
#include "Common.h"
// 确保包含windows.h以支持窗口创建函数
#include <windows.h>
// 包含异常处理相关头文件
#include <stdexcept>

using namespace std;

#define GET_X_LPARAM(lp) static_cast<short>(LOWORD(lp))
#define GET_Y_LPARAM(lp) static_cast<short>(HIWORD(lp))

#define CLMNEXT_ID     1
#define CLMNPATH_ID    2
#define SEP_POS        3
#define LVGROUPS_ID    4
#define FONTSIZE_ID    5

COLORREF VerticalFileSwitcher::_bgColor = 0xFFFFFF;

int CALLBACK ListViewCompareProc(LPARAM lParam1, LPARAM lParam2, LPARAM lParamSort)
{
	sortCompareData* sortData = (sortCompareData*)lParamSort;
	wchar_t str1[MAX_PATH] = { '\0' };
	wchar_t str2[MAX_PATH] = { '\0' };

	ListView_GetItemText(sortData->hListView, lParam1, sortData->columnIndex, str1, sizeof(str1));
	ListView_GetItemText(sortData->hListView, lParam2, sortData->columnIndex, str2, sizeof(str2));

	int result = lstrcmp(str1, str2);

	if (sortData->sortDirection == SORT_DIRECTION_UP)
		return result;

	return (0 - result);
}

LRESULT run_listViewProc(WNDPROC oldEditProc, HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	switch (message)
	{

		case WM_MBUTTONUP:
		{
			// Redirect the message to parent
			::SendMessage(::GetParent(hwnd), WM_PARENTNOTIFY, WM_MBUTTONUP, lParam);
			return TRUE;
		}

		default:
			break;
	}
	// 调用原始窗口过程，确保消息正常传递
	return ::CallWindowProc(oldEditProc, hwnd, message, wParam, lParam);
}

void VerticalFileSwitcher::startColumnSort()
{
	// reset sorting if exts column was just disabled
	HWND colHeader = reinterpret_cast<HWND>(SendMessage(_fileListView.getHSelf(), LVM_GETHEADER, 0, 0));
	int columnCount = static_cast<int32_t>(SendMessage(colHeader, HDM_GETITEMCOUNT, 0, 0));
	if (_lastSortingColumn >= columnCount)
	{
		_lastSortingColumn = 0;
		_lastSortingDirection = SORT_DIRECTION_NONE;
	}

	if (_lastSortingDirection != SORT_DIRECTION_NONE)
	{
		sortCompareData sortData = {_fileListView.getHSelf(), _lastSortingColumn, _lastSortingDirection};
		ListView_SortItemsEx(_fileListView.getHSelf(), ListViewCompareProc, reinterpret_cast<LPARAM>(&sortData));
	}
	
	updateHeaderArrow();
}

LRESULT VerticalFileSwitcher::listViewNotifyCustomDraw(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	auto lplvcd = reinterpret_cast<LPNMLVCUSTOMDRAW>(lParam);

	switch (lplvcd->nmcd.dwDrawStage)
	{
		case CDDS_PREPAINT:
		{
			if ((lplvcd->dwItemType == LVCDI_GROUP) && NppDarkMode::isThemeDark())
			{
				RECT rcHeader{};
				ListView_GetGroupRect(lplvcd->nmcd.hdr.hwndFrom, lplvcd->nmcd.dwItemSpec, LVGGR_HEADER, &rcHeader);

				HBRUSH hBrush = ::CreateSolidBrush(VerticalFileSwitcher::_bgColor);
				::FillRect(lplvcd->nmcd.hdc, &rcHeader, hBrush);
				::DeleteObject(hBrush);
				hBrush = nullptr;
			}
			return CDRF_NOTIFYITEMDRAW;
		}

		case CDDS_ITEMPREPAINT:
		{
			const RECT& rcRow = lplvcd->nmcd.rc;

			const bool isThemeDark = NppDarkMode::isThemeDark();

			const auto hHeader = ListView_GetHeader(lplvcd->nmcd.hdr.hwndFrom);
			const auto colCount = Header_GetItemCount(hHeader);

			const LONG paddingLeft = isThemeDark ? 1 : 0;
			const LONG paddingRight = isThemeDark ? 2 : 1;

			RECT rcSubItem{ rcRow };
			RECT rcSubItem2{};
			RECT rcSubItem3{};

			rcSubItem.right -= paddingRight;

			auto setRectForSubItem = [hHeader, paddingLeft, paddingRight](RECT& first, RECT& second, int idxSecond) -> void {
				Header_GetItemRect(hHeader, idxSecond, &second);
				first.right = second.left - paddingRight;

				second.left -= paddingLeft;
				second.right -= paddingRight;
				second.top = first.top;
				second.bottom = first.bottom;
			};

			if (colCount >= 2)
			{
				setRectForSubItem(rcSubItem, rcSubItem2, 1);
			}

			if (colCount == 3)
			{
				setRectForSubItem(rcSubItem2, rcSubItem3, 2);
			}

			const auto isSelected = ListView_GetItemState(lplvcd->nmcd.hdr.hwndFrom, lplvcd->nmcd.dwItemSpec, LVIS_SELECTED) == LVIS_SELECTED;
			const bool isHot = (lplvcd->nmcd.uItemState & CDIS_HOT) == CDIS_HOT;
			const int colorID = reinterpret_cast<TaskLstFnStatus*>(lplvcd->nmcd.lItemlParam)->_docColor;

			COLORREF bgColor{0xFFFFFF};
			bool applyColor = false;

			if (colorID != -1)
			{
				bgColor = NppParameters::getInstance().getIndividualTabColor(colorID, isThemeDark, false);
				applyColor = true;
			}
			else if (isThemeDark)
			{
				if (isSelected)
				{
					bgColor = NppDarkMode::getCtrlBackgroundColor();
					applyColor = true;
				}
				else if (isHot)
				{
					bgColor = NppDarkMode::getHotBackgroundColor();
					applyColor = true;
				}
			}

			if (applyColor)
			{
				if (isThemeDark)
				{
					lplvcd->clrText = NppDarkMode::getTextColor();
				}

				lplvcd->clrTextBk = bgColor;

				HBRUSH hBrush = ::CreateSolidBrush(bgColor);

				::FillRect(lplvcd->nmcd.hdc, &rcSubItem, hBrush);
				if (colCount >= 2)
				{
					::FillRect(lplvcd->nmcd.hdc, &rcSubItem2, hBrush);
				}

				if (colCount == 3)
				{
					::FillRect(lplvcd->nmcd.hdc, &rcSubItem3, hBrush);
				}

				::DeleteObject(hBrush);
				hBrush = nullptr;
			}

			if (isSelected)
			{
				::DrawFocusRect(lplvcd->nmcd.hdc, &rcRow);
			} 
			else if (isHot)
			{
				::FrameRect(lplvcd->nmcd.hdc, &rcRow, isThemeDark ? NppDarkMode::getHotEdgeBrush() : ::GetSysColorBrush(COLOR_WINDOWTEXT));
			}

			return CDRF_NEWFONT;
		}

		default:
			break;
	}
	return ::DefSubclassProc(hWnd, uMsg, wParam, lParam);
}

LRESULT CALLBACK VerticalFileSwitcher::FileSwitcherNotifySubclass(
	HWND hWnd,
	UINT uMsg,
	WPARAM wParam,
	LPARAM lParam,
	UINT_PTR uIdSubclass,
	DWORD_PTR /*dwRefData*/
)
{
	switch (uMsg)
	{
		case WM_NCDESTROY:
		{
			::RemoveWindowSubclass(hWnd, VerticalFileSwitcher::FileSwitcherNotifySubclass, uIdSubclass);
			break;
		}

		case WM_NOTIFY:
		{
			auto nmhdr = reinterpret_cast<LPNMHDR>(lParam);
			switch (nmhdr->code)
			{
				case NM_CUSTOMDRAW:
				{
					constexpr size_t classNameLen = 16;
					wchar_t className[classNameLen]{};
					GetClassName(nmhdr->hwndFrom, className, classNameLen);

					if (wcscmp(className, WC_LISTVIEW) == 0)
					{
						return VerticalFileSwitcher::listViewNotifyCustomDraw(hWnd, uMsg, wParam, lParam);
					}
					break;
				}
			}
			break;
		}
	}
	return DefSubclassProc(hWnd, uMsg, wParam, lParam);
}

void VerticalFileSwitcher::autoSubclassWindowNotify(HWND hParent)
{
	::SetWindowSubclass(hParent, VerticalFileSwitcher::FileSwitcherNotifySubclass, _fileSwitcherNotifySubclassID, 0);
}

// 自定义窗口类名
static const wchar_t* VERTICAL_FILE_SWITCHER_CLASS_NAME = L"VerticalFileSwitcherClass";

// 注册自定义窗口类
bool VerticalFileSwitcher::registerWindowClass(HINSTANCE hInst) {
	WNDCLASSEX wc = {
		sizeof(WNDCLASSEX),
		0,
		wndProc,  // 使用我们的窗口过程
		0,
		0,
		hInst,
		NULL,  // 不使用图标
		::LoadCursor(NULL, IDC_ARROW),
		(HBRUSH)::GetStockObject(WHITE_BRUSH),
		NULL,
		VERTICAL_FILE_SWITCHER_CLASS_NAME,
		NULL
	};

	// 尝试注册窗口类
	if (!::RegisterClassEx(&wc)) {
		// 如果失败，检查是否已经注册
		if (GetLastError() != ERROR_CLASS_ALREADY_EXISTS) {
			printf("注册窗口类失败，错误码: %d\n", GetLastError());
			return false;
		}
	}

	return true;
}

void VerticalFileSwitcher::create(tTbData* data, bool isRTL) {
	// 使用基类的create方法，它会从资源文件加载对话框
	DockingDlgInterface::create(data, isRTL);

	// 初始化_fileListView
	_fileListView.Window::init(_hInst, _hSelf);

	// 在WM_CREATE消息处理中，我们会获取并设置列表视图控件
}

void VerticalFileSwitcher::create(tTbData* data, std::array<int, 3> iconIDs, bool isRTL) {
	_iconIDs = iconIDs;
	// 调用另一个重载版本的create方法
	this->create(data, isRTL);
}

LRESULT CALLBACK VerticalFileSwitcher::run_dlgProc(UINT message, WPARAM wParam, LPARAM lParam)
{
	switch (message)
	{
		case WM_INITDIALOG :
		{
			// 对话框初始化时初始化控件
			VerticalFileSwitcher::initPopupMenus();

			// 从窗口中获取列表视图控件
			HWND hListView = ::GetDlgItem(_hSelf, IDC_LIST_DOCLIST);
			debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 获取ListView控件句柄: %p, _hSelf: %p", hListView, _hSelf);
			
			// 初始化分类管理器
		_categoryManager.initialize(L"categories.json");
		
		// 设置分类管理器指针到列表视图
		_fileListView.setCategoryManager(&_categoryManager);
		
		// 创建分类按钮栏
		createCategoryButtons();
		
		// 初始化字体大小下拉框
		_hFontSizeCombo = ::GetDlgItem(_hSelf, IDC_FONTSIZE_COMBO);
		if (_hFontSizeCombo)
		{
			debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 获取字体大小下拉框句柄: %p", _hFontSizeCombo);
			
			// 创建字体大小标签
			_hFontSizeLabel = ::CreateWindowEx(
				0, 
				L"STATIC", 
				L"字体大小:", 
				WS_CHILD | WS_VISIBLE | SS_LEFT,
				5, 5, 60, 20, 
				_hSelf, 
				(HMENU)IDC_FONTSIZE_STATIC, 
				_hInst, 
				NULL
			);
			
			if (_hFontSizeLabel)
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 字体大小标签创建成功，句柄: %p", _hFontSizeLabel);
				// 设置字体
				HFONT hFont = (HFONT)::SendMessage(_hSelf, WM_GETFONT, 0, 0);
				if (hFont)
				{
					::SendMessage(_hFontSizeLabel, WM_SETFONT, (WPARAM)hFont, TRUE);
				}
			}
			else
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 错误：无法创建字体大小标签！");
			}
				
				// 添加字体大小选项到下拉框
				::SendMessage(_hFontSizeCombo, CB_ADDSTRING, 0, (LPARAM)L"6");
				::SendMessage(_hFontSizeCombo, CB_ADDSTRING, 0, (LPARAM)L"8");
				::SendMessage(_hFontSizeCombo, CB_ADDSTRING, 0, (LPARAM)L"10");
				::SendMessage(_hFontSizeCombo, CB_ADDSTRING, 0, (LPARAM)L"12");
				::SendMessage(_hFontSizeCombo, CB_ADDSTRING, 0, (LPARAM)L"14");
				::SendMessage(_hFontSizeCombo, CB_ADDSTRING, 0, (LPARAM)L"16");
				
				// 加载当前字体大小配置并设置下拉框选中项
				NppParameters& nppParams = NppParameters::getInstance();
				int fontSize = nppParams.getNppGUI()._fileSwitcherFontSize;
				wchar_t fontSizeStr[10];
				swprintf(fontSizeStr, 10, L"%d", fontSize);
				
				// 查找并选中当前字体大小
				int index = ::SendMessage(_hFontSizeCombo, CB_FINDSTRINGEXACT, -1, (LPARAM)fontSizeStr);
				if (index != CB_ERR)
				{
					::SendMessage(_hFontSizeCombo, CB_SETCURSEL, index, 0);
				}
				else
				{
					// 如果找不到，默认选中10号字体
					::SendMessage(_hFontSizeCombo, CB_SETCURSEL, 2, 0);
				}
			}
			else
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 错误：无法获取IDC_FONTSIZE_COMBO控件句柄！");
			}
			
			if (hListView)
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - ListView控件有效，开始初始化");
				
				// 确保_fileListView正确关联到这个控件
			if (_fileListView.getHSelf() != hListView)
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 设置_fileListView的句柄和图像列表");
				// 先调用init方法设置父窗口句柄
				_fileListView.init(_hInst, _hParent, _hImaLst);
				// 然后设置列表视图控件句柄
				_fileListView.setHSelf(hListView);
			}
				
				// 保存原始窗口过程
				_defaultListViewProc = (WNDPROC)GetWindowLongPtr(hListView, GWLP_WNDPROC);
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 原始窗口过程: %p", _defaultListViewProc);
				
				// 保存VerticalFileSwitcher实例指针到列表视图控件
				SetWindowLongPtr(hListView, -21, (LONG_PTR)this); // -21 是GWL_USERDATA的替代
				// 使用正确的窗口过程
				SetWindowLongPtr(hListView, GWLP_WNDPROC, (LONG_PTR)VerticalFileSwitcher::listViewStaticProc);
				
				// 设置列表视图的扩展样式
				ListView_SetExtendedListViewStyle(hListView, LVS_EX_FULLROWSELECT | LVS_EX_DOUBLEBUFFER);
				
				// 设置图像列表
				ListView_SetImageList(hListView, _hImaLst, LVSIL_SMALL);
				
				// 加载字体大小配置
				NppParameters& nppParams = NppParameters::getInstance();
				int fontSize = nppParams.getNppGUI()._fileSwitcherFontSize;
				_fileListView.setFontSize(fontSize);
				
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 准备调用_fileListView.initList()");
				// 初始化列表和显示
				_fileListView.initList();
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - _fileListView.initList()调用完成");
			}
			else
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 错误：无法获取IDC_LIST_DOCLIST控件句柄！");
			}

			NppDarkMode::autoSubclassAndThemeChildControls(_hSelf);
			VerticalFileSwitcher::autoSubclassWindowNotify(_hSelf);

			return TRUE; // 返回TRUE表示成功处理WM_INITDIALOG
		}

		case NPPM_INTERNAL_REFRESHDARKMODE:
		{
			NppDarkMode::autoThemeChildControls(_hSelf);
			return TRUE;
		}

		// Different from WM_MBUTTONDOWN, WM_MBUTTONUP message is not sent to parent hwnd by WIN32 API
		// So we subclass listview to redirect WM_MBUTTONUP via WM_PARENTNOTIFY (as WM_MBUTTONDOWN)
		case WM_PARENTNOTIFY:
		{
			switch ( wParam )
			{
				case WM_MBUTTONUP:
				{
					// Get item ID under cursor
					LVHITTESTINFO hitInfo{};
					hitInfo.pt.x = GET_X_LPARAM(lParam);
					hitInfo.pt.y = GET_Y_LPARAM(lParam);

					::ClientToScreen(getHSelf(), &hitInfo.pt);
					::ScreenToClient(_fileListView.getHSelf(), &hitInfo.pt);
					ListView_HitTest(_fileListView.getHSelf(), &hitInfo);
			
					if (hitInfo.iItem != -1)
					{
						// Get the actual item info from the ID
						LVITEM item{};
						item.mask = LVIF_PARAM;
						item.iItem = hitInfo.iItem;	
						ListView_GetItem(_fileListView.getHSelf(), &item);
						TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;

						// Close the document
						closeDoc(tlfs);

						return TRUE;
					}
				}
			}

			break;
		}


		case WM_NOTIFY:
		{
			switch (reinterpret_cast<LPNMHDR>(lParam)->code)
			{
				case DMN_CLOSE:
				{
					::SendMessage(_hParent, WM_COMMAND, IDM_VIEW_DOCLIST, 0);
					return TRUE;
				}

				case NM_DBLCLK:
				{
					LPNMITEMACTIVATE lpnmitem = (LPNMITEMACTIVATE) lParam;
					int i = lpnmitem->iItem;
					if (i == -1)
					{
						::SendMessage(_hParent, WM_COMMAND, IDM_FILE_NEW, 0);
					}
					return TRUE;
				}

				case NM_CLICK:
				{
					if ((0x80 & GetKeyState(VK_CONTROL)) || (0x80 & GetKeyState(VK_SHIFT)))
						return TRUE;

					LPNMITEMACTIVATE lpnmitem = (LPNMITEMACTIVATE) lParam;
					int nbItem = ListView_GetItemCount(_fileListView.getHSelf());
					int i = lpnmitem->iItem;
					if (i == -1 || i >= nbItem)
						return TRUE;

					LVITEM item{};
					item.mask = LVIF_PARAM;
					item.iItem = i;
					ListView_GetItem(((LPNMHDR)lParam)->hwndFrom, &item);
					TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;

					activateDoc(tlfs);
					return TRUE;
				}

				case NM_RCLICK :
				{
					// Switch to the right document
					LPNMITEMACTIVATE lpnmitem = (LPNMITEMACTIVATE) lParam;

					if (lpnmitem->hdr.hwndFrom != _fileListView.getHSelf())
					{
						colHeaderRClick = true;
						return TRUE;
					}

					int nbItem = ListView_GetItemCount(_fileListView.getHSelf());

					if (nbSelectedFiles() == 1)
					{
						int i = lpnmitem->iItem;
						if (i == -1 || i >= nbItem)
 							return TRUE;

						LVITEM item{};
						item.mask = LVIF_PARAM;
						item.iItem = i;
						ListView_GetItem(((LPNMHDR)lParam)->hwndFrom, &item);
						TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;

						activateDoc(tlfs);
					}

					if (nbSelectedFiles() >= 1)
					{
						// Redirect NM_RCLICK message to Notepad_plus handle
						NMHDR nmhdr{};
						nmhdr.code = reinterpret_cast<LPNMHDR>(lParam)->code; //NM_RCLICK
						nmhdr.hwndFrom = _hSelf;
						nmhdr.idFrom = ::GetDlgCtrlID(nmhdr.hwndFrom);
						::SendMessage(_hParent, WM_NOTIFY, nmhdr.idFrom, reinterpret_cast<LPARAM>(&nmhdr));
					}
					return TRUE;
				}

				case LVN_GETINFOTIP:
				{
					LPNMLVGETINFOTIP pGetInfoTip = (LPNMLVGETINFOTIP)lParam;
					int i = pGetInfoTip->iItem;
					if (i == -1)
						return TRUE;
					wstring fn = getFullFilePathInternal((size_t)i);
					lstrcpyn(pGetInfoTip->pszText, fn.c_str(), pGetInfoTip->cchTextMax);
					return TRUE;
				}

				case LVN_COLUMNCLICK:
				{
					LPNMLISTVIEW pnmLV = (LPNMLISTVIEW)lParam;
					_lastSortingDirection = setHeaderOrder(pnmLV->iSubItem);
					_lastSortingColumn = pnmLV->iSubItem;
					if (_lastSortingDirection != SORT_DIRECTION_NONE)
					{
						startColumnSort();
					}
					else
					{
						_fileListView.reload();
						updateHeaderArrow();
					}
					return TRUE;
				}
				case HDN_DIVIDERDBLCLICK:
				case HDN_ENDTRACK:
				{
					NppParameters& nppParams = NppParameters::getInstance();
					NativeLangSpeaker* pNativeSpeaker = nppParams.getNativeLangSpeaker();
					
					LPNMHEADER test = (LPNMHEADER)lParam;
					HWND hwndHD = ListView_GetHeader(_fileListView.getHSelf());
					wchar_t HDtext[MAX_PATH] = { '\0' };
					HDITEM hdi = {};
					hdi.mask = HDI_TEXT | HDI_WIDTH;
					hdi.pszText = HDtext;
					hdi.cchTextMax = MAX_PATH;
					Header_GetItem(hwndHD, test->iItem, &hdi);

					// storing column width data
					if (hdi.pszText == pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT))
						nppParams.getNppGUI()._fileSwitcherExtWidth = hdi.cxy;
					else if (hdi.pszText == pNativeSpeaker->getAttrNameStr(L"Path", FS_ROOTNODE, FS_CLMNPATH))
						nppParams.getNppGUI()._fileSwitcherPathWidth = hdi.cxy;

					return TRUE;
				}
				case LVN_KEYDOWN:
				{
					switch (((LPNMLVKEYDOWN)lParam)->wVKey)
					{
						case VK_RETURN:
						{
							int i = ListView_GetSelectionMark(_fileListView.getHSelf());
							if (i == -1)
								return TRUE;

							LVITEM item{};
							item.mask = LVIF_PARAM;
							item.iItem = i;	
							ListView_GetItem(((LPNMHDR)lParam)->hwndFrom, &item);
							TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;
							activateDoc(tlfs);
							return TRUE;
						}
						default:
							break;
					}
				}
				break;

				default:
					break;
			}
		}
		return TRUE;

        case WM_SIZE:
        {
		int width = LOWORD(lParam);
            int height = HIWORD(lParam);
			
			// 计算控件位置和大小
		int labelWidth = 40;
		int comboWidth = 100;
		int spacing = 5;
		int buttonBarHeight = 35; // 分类按钮栏高度
		
		// 字体大小控件位置（在按钮栏上方）
		int fontSizeLabelX = width - labelWidth - comboWidth - spacing * 2;
		int fontSizeComboX = width - comboWidth - spacing;
		
		// 设置字体大小控件位置和大小
		if (_hFontSizeLabel && _hFontSizeCombo)
		{
			::MoveWindow(_hFontSizeLabel, fontSizeLabelX, spacing, labelWidth, 20, TRUE);
			::MoveWindow(_hFontSizeCombo, fontSizeComboX, spacing, comboWidth, 200, TRUE);
		}
		
		// 设置分类按钮位置（在按钮栏内）
		int buttonHeight = 25;
		int buttonWidth = 80;
		int buttonSpacing = 5;
		int startX = 5;
		int startY = spacing;
		
		for (size_t i = 0; i < _categoryButtons.size(); ++i)
		{
			int x = startX + i * (buttonWidth + buttonSpacing);
			::MoveWindow(_categoryButtons[i], x, startY, buttonWidth, buttonHeight, TRUE);
		}
		
		// 设置列表视图位置和大小（在按钮栏下方）
		int listViewY = buttonBarHeight;
		int listViewHeight = height - buttonBarHeight;
		
		if (_fileListView.getHSelf())
		{
			::MoveWindow(_fileListView.getHSelf(), 0, listViewY, width, listViewHeight, TRUE);
		}
		
		_fileListView.resizeColumns(width);
            break;
        }
        
		case WM_CONTEXTMENU:
		{
			// 检查是否在文件列表上右键
			POINT pt = { GET_X_LPARAM(lParam), GET_Y_LPARAM(lParam) };
			RECT listRect;
			::GetWindowRect(_fileListView.getHSelf(), &listRect);
			
			// 如果点击位置在文件列表区域内，显示文件右键菜单
			if (PtInRect(&listRect, pt))
			{
				_fileListView.showFileContextMenu(pt.x, pt.y);
			}
			else if (nbSelectedFiles() == 0 || colHeaderRClick)
			{
				::TrackPopupMenu(_hGlobalMenu, 
					NppParameters::getInstance().getNativeLangSpeaker()->isRTL() ? TPM_RIGHTALIGN | TPM_LAYOUTRTL : TPM_LEFTALIGN,
					GET_X_LPARAM(lParam), GET_Y_LPARAM(lParam), 0, _hSelf, NULL);
				colHeaderRClick = false;
			}
			return TRUE;
		}

		case WM_COMMAND:
		{
			// 处理分类按钮点击
			if (LOWORD(wParam) >= CATEGORY_MENU_START && LOWORD(wParam) <= CATEGORY_MENU_END)
			{
				// 检查是否为文件右键菜单的分类选择（通过检查是否有选中的文件）
				int selectedCount = _fileListView.nbSelectedFiles();
				if (selectedCount > 0)
				{
					// 文件右键菜单的分类选择
					int categoryIndex = LOWORD(wParam) - CATEGORY_MENU_START;
					const auto& categories = _categoryManager.getCategories();
					
					if (categoryIndex >= 0 && categoryIndex < static_cast<int>(categories.size()))
					{
						const auto& selectedCategory = categories[categoryIndex];
						_fileListView.onFileCategoryChange(selectedCategory.name);
						
						debugLog(L"VerticalFileSwitcher::WM_COMMAND - 文件分类已更改为: %s", selectedCategory.name.c_str());
					}
				}
				else
				{
					// 分类按钮点击
					int buttonIndex = LOWORD(wParam) - CATEGORY_MENU_START;
					if (buttonIndex >= 0 && buttonIndex < static_cast<int>(_categoryButtons.size()))
					{
						onCategoryButtonClick(_categoryButtons[buttonIndex]);
					}
				}
			}
			// 处理字体下拉框选择变化
			else if (HIWORD(wParam) == CBN_SELCHANGE && LOWORD(wParam) == IDC_FONTSIZE_COMBO)
			{
				// 获取选中的字体大小
				int selectedIndex = ::SendMessage(_hFontSizeCombo, CB_GETCURSEL, 0, 0);
				if (selectedIndex != CB_ERR)
				{
					wchar_t fontSizeStr[10];
					::SendMessage(_hFontSizeCombo, CB_GETLBTEXT, selectedIndex, (LPARAM)fontSizeStr);
					
					// 转换为整数
					int fontSize = _wtoi(fontSizeStr);
					if (fontSize > 0)
					{
						// 设置字体大小
						setFontSize(fontSize);
						
						// 保存配置
						NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = fontSize;
						
						debugLog(L"VerticalFileSwitcher::WM_COMMAND - 字体大小已更改为: %d", fontSize);
					}
				}
			}
			else
			{
				popupMenuCmd(LOWORD(wParam));
			}
			break;
		}

		case WM_DESTROY:
        {
			_fileListView.destroy();
			::DestroyMenu(_hGlobalMenu);
            break;
        }

        default :
            return DockingDlgInterface::run_dlgProc(message, wParam, lParam);
    }
	return DockingDlgInterface::run_dlgProc(message, wParam, lParam);
}

// 创建分类按钮栏
void VerticalFileSwitcher::createCategoryButtons()
{
	// 清空现有的按钮
	for (HWND hButton : _categoryButtons)
	{
		::DestroyWindow(hButton);
	}
	_categoryButtons.clear();
	
	const auto& categories = _categoryManager.getCategories();
	if (categories.empty())
		return;
	
	// 按钮参数
	int buttonHeight = 25;
	int buttonWidth = 80;
	int buttonSpacing = 5;
	int startX = 5;
	int startY = 5;
	
	// 创建分类按钮
	for (size_t i = 0; i < categories.size(); ++i)
	{
		int x = startX + i * (buttonWidth + buttonSpacing);
		
		HWND hButton = ::CreateWindowEx(
			0,
			L"BUTTON",
			categories[i].name.c_str(),
			WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
			x, startY, buttonWidth, buttonHeight,
			_hSelf,
			(HMENU)(CATEGORY_MENU_START + i), // 使用分类菜单ID
			_hInst,
			NULL
		);
		
		if (hButton)
		{
			_categoryButtons.push_back(hButton);
			
			// 设置字体
			HFONT hFont = (HFONT)::SendMessage(_hSelf, WM_GETFONT, 0, 0);
			if (hFont)
			{
				::SendMessage(hButton, WM_SETFONT, (WPARAM)hFont, TRUE);
			}
			
			// 默认选中第一个按钮（"全部"分类）
			if (i == 0)
			{
				_currentCategoryButton = hButton;
				updateCategoryButtonState(hButton);
			}
		}
	}
}

// 处理分类按钮点击
void VerticalFileSwitcher::onCategoryButtonClick(HWND hButton)
{
	// 查找按钮索引
	int buttonIndex = -1;
	for (size_t i = 0; i < _categoryButtons.size(); ++i)
	{
		if (_categoryButtons[i] == hButton)
		{
			buttonIndex = static_cast<int>(i);
			break;
		}
	}
	
	if (buttonIndex >= 0 && buttonIndex < static_cast<int>(_categoryManager.getCategories().size()))
	{
		const auto& categories = _categoryManager.getCategories();
		const auto& selectedCategory = categories[buttonIndex];
		
		// 根据选中的分类过滤文件列表
		if (selectedCategory.name == L"全部")
		{
			// 选择"全部"分类，清除过滤
			_fileListView.clearCategoryFilter();
		}
		else
		{
			// 设置当前分类进行过滤
			_fileListView.setCurrentCategory(selectedCategory.name);
		}
		
		// 更新按钮状态
		updateCategoryButtonState(hButton);
		
		debugLog(L"VerticalFileSwitcher::onCategoryButtonClick - 分类已更改为: %s", selectedCategory.name.c_str());
	}
}

// 更新分类按钮状态
void VerticalFileSwitcher::updateCategoryButtonState(HWND selectedButton)
{
	// 更新所有按钮状态
	for (HWND hButton : _categoryButtons)
	{
		if (hButton == selectedButton)
		{
			// 选中状态：设置按下样式
			::SendMessage(hButton, BM_SETSTYLE, BS_DEFPUSHBUTTON, TRUE);
			_currentCategoryButton = hButton;
		}
		else
		{
			// 未选中状态：恢复普通样式
			::SendMessage(hButton, BM_SETSTYLE, BS_PUSHBUTTON, TRUE);
		}
		
		// 重绘按钮
		::InvalidateRect(hButton, NULL, TRUE);
	}
}

void VerticalFileSwitcher::initPopupMenus()
{
	NativeLangSpeaker* pNativeSpeaker = NppParameters::getInstance().getNativeLangSpeaker();
	const NppGUI& nppGUI = NppParameters::getInstance().getNppGUI();

	wstring extStr = pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT);
	wstring pathStr = pNativeSpeaker->getAttrNameStr(L"Path", FS_ROOTNODE, FS_CLMNPATH);
	wstring groupStr = pNativeSpeaker->getAttrNameStr(L"Group by View", FS_ROOTNODE, FS_LVGROUPS);

	_hGlobalMenu = ::CreatePopupMenu();
	
	// 添加分类选择菜单
	HMENU hCategoryMenu = ::CreatePopupMenu();
	const auto& categories = _categoryManager.getCategories();
	
	// 添加所有分类到菜单
	for (size_t i = 0; i < categories.size(); ++i)
	{
		UINT menuId = CATEGORY_MENU_START + static_cast<UINT>(i);
		::InsertMenu(hCategoryMenu, menuId, MF_BYCOMMAND | MF_STRING, menuId, categories[i].name.c_str());
	}
	wstring categoryStr = L"选择分类";
	::InsertMenu(_hGlobalMenu, CATEGORY_MENU_ID, MF_BYCOMMAND | MF_POPUP, reinterpret_cast<UINT_PTR>(hCategoryMenu), categoryStr.c_str());
	
	::InsertMenu(_hGlobalMenu, CLMNEXT_ID, MF_BYCOMMAND | MF_STRING, CLMNEXT_ID, extStr.c_str());
	::InsertMenu(_hGlobalMenu, CLMNPATH_ID, MF_BYCOMMAND | MF_STRING, CLMNPATH_ID, pathStr.c_str());
	::InsertMenu(_hGlobalMenu, SEP_POS, MF_BYCOMMAND | MF_SEPARATOR, 0, nullptr);
	::InsertMenu(_hGlobalMenu, LVGROUPS_ID, MF_BYCOMMAND | MF_STRING, LVGROUPS_ID, groupStr.c_str());
	
	// 添加字体大小菜单
	HMENU hFontSizeMenu = ::CreatePopupMenu();
	wstring fontSizeStr = pNativeSpeaker->getAttrNameStr(L"Font Size", FS_ROOTNODE, FS_FONTSIZE);
	::InsertMenu(hFontSizeMenu, FONTSIZE_6, MF_BYCOMMAND | MF_STRING, FONTSIZE_6, L"6");
	::InsertMenu(hFontSizeMenu, FONTSIZE_8, MF_BYCOMMAND | MF_STRING, FONTSIZE_8, L"8");
	::InsertMenu(hFontSizeMenu, FONTSIZE_10, MF_BYCOMMAND | MF_STRING, FONTSIZE_10, L"10");
	::InsertMenu(hFontSizeMenu, FONTSIZE_12, MF_BYCOMMAND | MF_STRING, FONTSIZE_12, L"12");
	::InsertMenu(hFontSizeMenu, FONTSIZE_14, MF_BYCOMMAND | MF_STRING, FONTSIZE_14, L"14");
	::InsertMenu(_hGlobalMenu, FONTSIZE_ID, MF_BYCOMMAND | MF_POPUP, reinterpret_cast<UINT_PTR>(hFontSizeMenu), fontSizeStr.c_str());

	bool isExtColumn = nppGUI._fileSwitcherWithoutExtColumn;
	::CheckMenuItem(_hGlobalMenu, CLMNEXT_ID, MF_BYCOMMAND | (isExtColumn ? MF_UNCHECKED : MF_CHECKED));
	bool isPathColumn = nppGUI._fileSwitcherWithoutPathColumn;
	::CheckMenuItem(_hGlobalMenu, CLMNPATH_ID, MF_BYCOMMAND | (isPathColumn ? MF_UNCHECKED : MF_CHECKED));
	bool isListViewGroups = nppGUI._fileSwitcherDisableListViewGroups;
	::CheckMenuItem(_hGlobalMenu, LVGROUPS_ID, MF_BYCOMMAND | (isListViewGroups ? MF_UNCHECKED : MF_CHECKED));
}

void VerticalFileSwitcher::popupMenuCmd(int cmdID)
{
	switch (cmdID)
	{
		case CLMNEXT_ID:
		{
			bool& isExtColumn = NppParameters::getInstance().getNppGUI()._fileSwitcherWithoutExtColumn;
			isExtColumn = !isExtColumn;
			::CheckMenuItem(_hGlobalMenu, CLMNEXT_ID, MF_BYCOMMAND | (isExtColumn ? MF_UNCHECKED : MF_CHECKED));
			reload();
		}
		break;
		case CLMNPATH_ID:
		{
			bool& isPathColumn = NppParameters::getInstance().getNppGUI()._fileSwitcherWithoutPathColumn;
			isPathColumn = !isPathColumn;
			::CheckMenuItem(_hGlobalMenu, CLMNPATH_ID, MF_BYCOMMAND | (isPathColumn ? MF_UNCHECKED : MF_CHECKED));
			reload();
		}
		break;
		case LVGROUPS_ID:
		{
			bool& isListViewGroups = NppParameters::getInstance().getNppGUI()._fileSwitcherDisableListViewGroups;
			isListViewGroups = !isListViewGroups;
			::CheckMenuItem(_hGlobalMenu, LVGROUPS_ID, MF_BYCOMMAND | (isListViewGroups ? MF_UNCHECKED : MF_CHECKED));
			reload();
		}
		break;
		
		// 字体大小菜单处理
		case FONTSIZE_6:
			setFontSize(6);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 6;
			_fileListView.refreshDisplay(); // 只刷新显示，不重新加载数据
			break;
		case FONTSIZE_8:
			setFontSize(8);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 8;
			_fileListView.refreshDisplay(); // 只刷新显示，不重新加载数据
			break;
		case FONTSIZE_10:
			setFontSize(10);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 10;
			_fileListView.refreshDisplay(); // 只刷新显示，不重新加载数据
			break;
		case FONTSIZE_12:
			setFontSize(12);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 12;
			_fileListView.refreshDisplay(); // 只刷新显示，不重新加载数据
			break;
		case FONTSIZE_14:
			setFontSize(14);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 14;
			_fileListView.refreshDisplay(); // 只刷新显示，不重新加载数据
			break;
	}
}

void VerticalFileSwitcher::display(bool toShow) const
{
	// 添加调试信息
	debugLog(L"VerticalFileSwitcher::display() called with toShow=%d\n", toShow);
	
	DockingDlgInterface::display(toShow);
	
	// 添加调试信息
	debugLog(L"VerticalFileSwitcher::display() after DockingDlgInterface::display()\n");
	
	_fileListView.ensureVisibleCurrentItem();	// without this call the current item may stay above visible area after the program startup
	
	// 添加调试信息
	debugLog(L"VerticalFileSwitcher::display() after ensureVisibleCurrentItem()\n");
}

void VerticalFileSwitcher::activateDoc(TaskLstFnStatus *tlfs) const
{
	int view = tlfs->_iView;
	BufferID bufferID = static_cast<BufferID>(tlfs->_bufID);
	
	auto currentView = ::SendMessage(_hParent, NPPM_GETCURRENTVIEW, 0, 0);
	BufferID currentBufID = reinterpret_cast<BufferID>(::SendMessage(_hParent, NPPM_GETCURRENTBUFFERID, 0, 0));

	if (bufferID == currentBufID && view == currentView)
		return;
	
	int docPosInfo = static_cast<int32_t>(::SendMessage(_hParent, NPPM_GETPOSFROMBUFFERID, reinterpret_cast<WPARAM>(bufferID), view));
	int view2set = docPosInfo >> 30;
	int index2Switch = (docPosInfo << 2) >> 2;

	::SendMessage(_hParent, NPPM_ACTIVATEDOC, view2set, index2Switch);
}

void VerticalFileSwitcher::closeDoc(TaskLstFnStatus *tlfs) const
{
	int view = tlfs->_iView;
	BufferID bufferID = static_cast<BufferID>(tlfs->_bufID);
		
	int docPosInfo = static_cast<int32_t>(::SendMessage(_hParent, NPPM_GETPOSFROMBUFFERID, reinterpret_cast<WPARAM>(bufferID), view));
	int view2set = docPosInfo >> 30;
	int index2Switch = (docPosInfo << 2) >> 2;

	::SendMessage(_hParent, NPPM_INTERNAL_CLOSEDOC, view2set, index2Switch);
}

int VerticalFileSwitcher::setHeaderOrder(int columnIndex)
{
	HWND hListView = _fileListView.getHSelf();
	LVCOLUMN lvc{};
	lvc.mask = LVCF_FMT;
	
	//strip HDF_SORTUP and HDF_SORTDOWN from old sort column
	if (_lastSortingColumn != columnIndex && _lastSortingDirection != SORT_DIRECTION_NONE)
	{
		HWND colHeader = reinterpret_cast<HWND>(SendMessage(hListView, LVM_GETHEADER, 0, 0));
		int columnCount = static_cast<int32_t>(SendMessage(colHeader, HDM_GETITEMCOUNT, 0, 0));
		if (_lastSortingColumn < columnCount)
		{
			// Get current fmt
			SendMessage(hListView, LVM_GETCOLUMN, _lastSortingColumn, reinterpret_cast<LPARAM>(&lvc));
			
			// remove both sort-up and sort-down
			lvc.fmt = lvc.fmt & (~HDF_SORTUP) & (~HDF_SORTDOWN);
			SendMessage(hListView, LVM_SETCOLUMN, _lastSortingColumn, reinterpret_cast<LPARAM>(&lvc));
		}
		
		_lastSortingDirection = SORT_DIRECTION_NONE;
	}
	
	if (_lastSortingDirection == SORT_DIRECTION_NONE)
	{
		return SORT_DIRECTION_UP;
	}
	
	if (_lastSortingDirection == SORT_DIRECTION_UP)
	{
		return SORT_DIRECTION_DOWN;
	}

	//if (_lastSortingDirection == SORT_DIRECTION_DOWN)
	return SORT_DIRECTION_NONE;
}

void VerticalFileSwitcher::updateHeaderArrow()
{
	HWND hListView = _fileListView.getHSelf();
	LVCOLUMN lvc{};
	lvc.mask = LVCF_FMT;
	
	SendMessage(hListView, LVM_GETCOLUMN, _lastSortingColumn, reinterpret_cast<LPARAM>(&lvc));
	
	if (_lastSortingDirection == SORT_DIRECTION_UP)
	{
		lvc.fmt = (lvc.fmt | HDF_SORTUP) & ~HDF_SORTDOWN;
		SendMessage(hListView, LVM_SETCOLUMN, _lastSortingColumn, reinterpret_cast<LPARAM>(&lvc));
	}
	else if (_lastSortingDirection == SORT_DIRECTION_DOWN)
	{
		lvc.fmt = (lvc.fmt & ~HDF_SORTUP) | HDF_SORTDOWN;
		SendMessage(hListView, LVM_SETCOLUMN, _lastSortingColumn, reinterpret_cast<LPARAM>(&lvc));
	}
	else if (_lastSortingDirection == SORT_DIRECTION_NONE)
	{
		lvc.fmt = lvc.fmt & (~HDF_SORTUP) & (~HDF_SORTDOWN);
		SendMessage(hListView, LVM_SETCOLUMN, _lastSortingColumn, reinterpret_cast<LPARAM>(&lvc));
	}
}
