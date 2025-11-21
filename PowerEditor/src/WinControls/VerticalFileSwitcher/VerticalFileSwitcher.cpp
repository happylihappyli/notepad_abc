



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
			debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 开始初始化分类管理器，配置文件路径: ..\\bin\\categories.json");
			_categoryManager.initialize(L"..\\bin\\categories.json");
			debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 分类管理器初始化完成");
		
		// 设置分类管理器指针到列表视图
		_fileListView.setCategoryManager(&_categoryManager);
		debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 分类管理器指针已设置到列表视图: %p", &_categoryManager);
		
		// 创建分类按钮栏
		createCategoryButtons();
		
		if (hListView)
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - ListView控件有效，开始初始化");
				
				// 确保_fileListView正确关联到这个控件
			if (_fileListView.getHSelf() != hListView)
			{
				debugLog(L"VerticalFileSwitcher::WM_INITDIALOG - 设置_fileListView的句柄和图像列表");
				// 先调用init方法设置父窗口句柄
				_fileListView.init(_hInst, _hParent, _hImaLst);
				// 设置Notepad++主窗口句柄
				_fileListView.setNppMainWnd(_hParent);
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
						// 在列表视图头部右键，显示不包含文档分类的菜单
						POINT pt = { GET_X_LPARAM(lpnmitem->ptAction.x), GET_Y_LPARAM(lpnmitem->ptAction.y) };
						::ClientToScreen(lpnmitem->hdr.hwndFrom, &pt);
						::TrackPopupMenu(_hGlobalMenu, 
							NppParameters::getInstance().getNativeLangSpeaker()->isRTL() ? TPM_RIGHTALIGN | TPM_LAYOUTRTL : TPM_LEFTALIGN,
							pt.x, pt.y, 0, _hSelf, NULL);
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
						// 在文件列表上右键，显示包含文档分类的菜单
						POINT pt = { GET_X_LPARAM(lpnmitem->ptAction.x), GET_Y_LPARAM(lpnmitem->ptAction.y) };
						::ClientToScreen(lpnmitem->hdr.hwndFrom, &pt);
						::TrackPopupMenu(_hFileListMenu, 
							NppParameters::getInstance().getNativeLangSpeaker()->isRTL() ? TPM_RIGHTALIGN | TPM_LAYOUTRTL : TPM_LEFTALIGN,
							pt.x, pt.y, 0, _hSelf, NULL);
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
			
			// 调整文件列表视图大小
		int listViewHeight = height - 100; // 减去顶部控件的高度（分类按钮栏和下拉框）
		if (listViewHeight > 0)
		{
			::SetWindowPos(_fileListView.getHSelf(), NULL, 0, 100, width, listViewHeight, SWP_NOZORDER);
		}
            break;
        }
        
		case WM_CONTEXTMENU:
        {
            // 检查是否在文件列表上右键
            POINT pt = { GET_X_LPARAM(lParam), GET_Y_LPARAM(lParam) };
            RECT listRect;
            ::GetWindowRect(_fileListView.getHSelf(), &listRect);
            
            // 检查右键点击位置是否在列表视图内
            bool isInListView = ::PtInRect(&listRect, pt);
            
            if (isInListView) {
                // 在文件列表上右键，显示包含文档分类的菜单
                ::TrackPopupMenu(_hFileListMenu, 
                    NppParameters::getInstance().getNativeLangSpeaker()->isRTL() ? TPM_RIGHTALIGN | TPM_LAYOUTRTL : TPM_LEFTALIGN,
                    pt.x, pt.y, 0, _hSelf, NULL);
            } else {
                // 在列表视图外（如头部）右键，显示不包含文档分类的菜单
                ::TrackPopupMenu(_hGlobalMenu, 
                    NppParameters::getInstance().getNativeLangSpeaker()->isRTL() ? TPM_RIGHTALIGN | TPM_LAYOUTRTL : TPM_LEFTALIGN,
                    pt.x, pt.y, 0, _hSelf, NULL);
            }
            return TRUE;
        }

		case WM_COMMAND:
		{
			// 处理设置按钮点击事件
			if (LOWORD(wParam) == IDM_SETTINGS_VFS)// IDC_SETTINGS_BUTTON_VFS)
			{
				// 显示设置对话框
				showSettingsDialog();
				debugLog(L"VerticalFileSwitcher::WM_COMMAND - 设置按钮被点击，已显示设置对话框");
				break;
			}
			
			// 处理分类按钮点击事件（用于过滤查看文件）
			if (LOWORD(wParam) >= CATEGORY_BUTTON_START && LOWORD(wParam) <= CATEGORY_BUTTON_END)
			{
				// 分类按钮点击 - 过滤整个文件列表
				int buttonIndex = LOWORD(wParam) - CATEGORY_BUTTON_START;
				if (buttonIndex >= 0 && buttonIndex < static_cast<int>(_categoryButtons.size()))
				{
					onCategoryButtonClick(_categoryButtons[buttonIndex]);
				}
			}
			// 处理文件右键菜单的分类选择
			else if (LOWORD(wParam) >= CATEGORY_MENU_START && LOWORD(wParam) <= CATEGORY_MENU_END)
			{
				// 文件右键菜单的分类选择 - 设置单个文件的分类
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

// 创建分类按钮栏和分类下拉框
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
	
	// 创建分类按钮栏（用于过滤查看文件）
	int buttonX = 5;
	int buttonY = 5;  // 调整为从顶部开始，因为删除了字体控件
	int buttonWidth = 80;  // 增大按钮宽度从60到80
	int buttonHeight = 28; // 增大按钮高度从20到28
	int buttonSpacing = 8; // 增大按钮间距从5到8
	
	for (size_t i = 0; i < categories.size(); ++i)
	{
		HWND hButton = ::CreateWindowEx(
			0,
			L"BUTTON",
			categories[i].name.c_str(),
			WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
			buttonX, buttonY, buttonWidth, buttonHeight,
			_hSelf,
			(HMENU)(CATEGORY_BUTTON_START + i),
			_hInst,
			NULL
		);
		
		if (hButton)
		{
			_categoryButtons.push_back(hButton);
			
			// 设置分类按钮的字体（使用更大的字号）
			HFONT hFont = (HFONT)::SendMessage(_hSelf, WM_GETFONT, 0, 0);
			if (hFont)
			{
				// 获取当前字体信息并创建一个更大字号的字体
				LOGFONT lf;
				if (GetObject(hFont, sizeof(LOGFONT), &lf))
				{
					lf.lfHeight = 16;  // 设置为16号字体，比原来的更大
					lf.lfWeight = FW_NORMAL; // 正常粗细
					wcscpy_s(lf.lfFaceName, L"宋体"); // 使用宋体字体
					
					HFONT hNewFont = ::CreateFontIndirect(&lf);
					if (hNewFont)
					{
						::SendMessage(hButton, WM_SETFONT, (WPARAM)hNewFont, TRUE);
						// 注意：这里不删除字体，因为按钮可能还会使用
					}
					else
					{
						// 如果创建新字体失败，使用原来的字体
						::SendMessage(hButton, WM_SETFONT, (WPARAM)hFont, TRUE);
					}
				}
				else
				{
					// 如果获取字体信息失败，使用原来的字体
					::SendMessage(hButton, WM_SETFONT, (WPARAM)hFont, TRUE);
				}
			}
			
			// 更新按钮位置
			buttonX += buttonWidth + buttonSpacing;
		}
	}
	
	// 默认选中第一个按钮（"全部"分类）
	if (!_categoryButtons.empty())
	{
		_currentCategoryButton = _categoryButtons[0];
		updateCategoryButtonState(_currentCategoryButton);
	}
}

// 处理分类按钮点击事件（用于过滤查看文件）
void VerticalFileSwitcher::onCategoryButtonClick(HWND hButton)
{
	// 查找按钮对应的分类索引
	int categoryIndex = -1;
	for (size_t i = 0; i < _categoryButtons.size(); ++i)
	{
		if (_categoryButtons[i] == hButton)
		{
			categoryIndex = static_cast<int>(i);
			break;
		}
	}
	
	if (categoryIndex < 0 || categoryIndex >= static_cast<int>(_categoryManager.getCategories().size()))
		return;
	
	const auto& categories = _categoryManager.getCategories();
	const std::wstring& selectedCategory = categories[categoryIndex].name;
	
	debugLog(L"VerticalFileSwitcher::onCategoryButtonClick - 选择分类按钮: %s", selectedCategory.c_str());
	
	// 更新按钮状态
	_currentCategoryButton = hButton;
	updateCategoryButtonState(_currentCategoryButton);
	
	// 过滤文件列表
	if (selectedCategory == L"全部")
	{
		// 选择"全部"分类，清除过滤
		debugLog(L"VerticalFileSwitcher::onCategoryButtonClick - 清除分类过滤，显示全部文件");
		_fileListView.clearCategoryFilter();
	}
	else
	{
		// 设置当前分类进行过滤
		debugLog(L"VerticalFileSwitcher::onCategoryButtonClick - 设置当前分类进行过滤: %s", selectedCategory.c_str());
		_fileListView.setCurrentCategory(selectedCategory);
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

// 设置对话框窗口过程
static INT_PTR CALLBACK SettingsDlgProc(HWND hwndDlg, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
	switch (uMsg)
	{
		case WM_INITDIALOG:
		{
			// 获取VerticalFileSwitcher实例指针
			VerticalFileSwitcher* pThis = reinterpret_cast<VerticalFileSwitcher*>(lParam);
			::SetWindowLongPtr(hwndDlg, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(pThis));
			
			// 初始化字体大小滑块（6-16号字体）
			HWND hFontSlider = ::GetDlgItem(hwndDlg, IDC_FONTSIZE_SLIDER);
			if (hFontSlider)
			{
				::SendMessage(hFontSlider, TBM_SETRANGE, TRUE, MAKELPARAM(6, 16));
				::SendMessage(hFontSlider, TBM_SETTICFREQ, 1, 0);
				
				// 获取当前字体大小并设置滑块位置
				NppParameters& nppParams = NppParameters::getInstance();
				int currentFontSize = nppParams.getNppGUI()._fileSwitcherFontSize;
				if (currentFontSize < 6) currentFontSize = 6;
				if (currentFontSize > 16) currentFontSize = 16;
				
				::SendMessage(hFontSlider, TBM_SETPOS, TRUE, currentFontSize);
				
				// 更新字体大小显示
				wchar_t fontSizeStr[10];
				swprintf(fontSizeStr, 10, L"%d", currentFontSize);
				::SetDlgItemText(hwndDlg, IDC_FONTSIZE_DISPLAY, fontSizeStr);
				
				debugLog(L"设置对话框初始化：当前字体大小 = %d", currentFontSize);
			}
			
			// 初始化分类列表
			if (pThis)
			{
				HWND hCategoryList = ::GetDlgItem(hwndDlg, IDC_CATEGORY_LIST);
				if (hCategoryList)
				{
					// 清空列表
					::SendMessage(hCategoryList, LB_RESETCONTENT, 0, 0);
					
					// 更新分类列表显示
					const auto& categories = pThis->getCategoryManager()->getCategories();
					for (const auto& category : categories)
					{
						int index = ::SendMessage(hCategoryList, LB_ADDSTRING, 0, reinterpret_cast<LPARAM>(category.name.c_str()));
						::SendMessage(hCategoryList, LB_SETITEMDATA, index, reinterpret_cast<LPARAM>(&category));
					}
					
					debugLog(L"设置对话框初始化：加载了 %d 个分类", categories.size());
				}
			}
			return TRUE;
		}
		
		case WM_HSCROLL:
		case WM_VSCROLL:
		{
			// 处理滑块消息
			if (LOWORD(wParam) != SB_THUMBPOSITION && LOWORD(wParam) != SB_ENDSCROLL)
			{
				break;
			}
			
			HWND hFontSlider = ::GetDlgItem(hwndDlg, IDC_FONTSIZE_SLIDER);
			if (hFontSlider == (HWND)lParam)
			{
				int fontSize = ::SendMessage(hFontSlider, TBM_GETPOS, 0, 0);
				
				// 更新字体大小显示
				wchar_t fontSizeStr[10];
				swprintf(fontSizeStr, 10, L"%d", fontSize);
				::SetDlgItemText(hwndDlg, IDC_FONTSIZE_DISPLAY, fontSizeStr);
				
				debugLog(L"设置对话框：字体大小滑块位置变化 = %d", fontSize);
			}
			break;
		}
		
		case WM_COMMAND:
		{
			VerticalFileSwitcher* pThis = reinterpret_cast<VerticalFileSwitcher*>(::GetWindowLongPtr(hwndDlg, GWLP_USERDATA));
			
			switch (LOWORD(wParam))
			{
				case IDOK:
				{
					// 处理确定按钮：保存设置
					HWND hFontSlider = ::GetDlgItem(hwndDlg, IDC_FONTSIZE_SLIDER);
					if (hFontSlider && pThis)
					{
						int fontSize = ::SendMessage(hFontSlider, TBM_GETPOS, 0, 0);
						
						// 更新配置
						NppParameters& nppParams = NppParameters::getInstance();
						nppParams.getNppGUI()._fileSwitcherFontSize = fontSize;
						nppParams.saveConfig_xml();
						
						// 更新文件列表的字体大小
						pThis->setFontSize(fontSize);
						
						debugLog(L"设置对话框：保存字体大小设置 = %d", fontSize);
					}
					
					::EndDialog(hwndDlg, IDOK);
					return TRUE;
				}
				
				case IDCANCEL:
				{
					// 处理取消按钮：不保存设置
					debugLog(L"设置对话框：取消设置");
					::EndDialog(hwndDlg, IDCANCEL);
					return TRUE;
				}
				
				case IDC_ADD_CATEGORY:
				{
					if (pThis)
					{
						// 添加分类功能 - 简化版本，使用固定名称
						wstring newCategoryName = L"新分类";
						
						// 使用MessageBox确认添加
						wchar_t buffer[200];
						wsprintf(buffer, L"确定要添加名为'%s'的分类吗？", newCategoryName.c_str());
						if (::MessageBox(hwndDlg, buffer, L"添加分类", MB_YESNO | MB_ICONQUESTION) == IDYES)
						{
							// 添加新分类
						FileCategory newCategory;
						newCategory.id = L"cat_" + std::to_wstring(pThis->getCategoryManager()->getCategories().size());
						newCategory.name = newCategoryName;
						newCategory.description = L"";
						newCategory.order = static_cast<int>(pThis->getCategoryManager()->getCategories().size());
							
							pThis->getCategoryManager()->addCategory(newCategory);
							
							// 重新加载分类列表
							HWND hCategoryList = ::GetDlgItem(hwndDlg, IDC_CATEGORY_LIST);
							if (hCategoryList)
							{
								::SendMessage(hCategoryList, LB_RESETCONTENT, 0, 0);
								const auto& categories = pThis->getCategoryManager()->getCategories();
								for (const auto& category : categories)
								{
									int index = ::SendMessage(hCategoryList, LB_ADDSTRING, 0, reinterpret_cast<LPARAM>(category.name.c_str()));
									::SendMessage(hCategoryList, LB_SETITEMDATA, index, reinterpret_cast<LPARAM>(&category));
								}
							}
							
							debugLog(L"设置对话框：成功添加分类 '%s'", newCategoryName.c_str());
						}
					}
					return TRUE;
				}
				
				case IDC_DELETE_CATEGORY:
				{
					if (pThis)
					{
						// 删除分类功能
						HWND hCategoryList = ::GetDlgItem(hwndDlg, IDC_CATEGORY_LIST);
						if (hCategoryList)
						{
							int selectedIndex = ::SendMessage(hCategoryList, LB_GETCURSEL, 0, 0);
							if (selectedIndex != LB_ERR)
							{
								// 获取选中的分类
								FileCategory* pCategory = reinterpret_cast<FileCategory*>(
									::SendMessage(hCategoryList, LB_GETITEMDATA, selectedIndex, 0));
								
								if (pCategory && wcscmp(pCategory->name.c_str(), L"全部") != 0)
								{
									if (::MessageBox(hwndDlg, L"确定要删除这个分类吗？", L"确认删除", MB_YESNO | MB_ICONQUESTION) == IDYES)
									{
										// 删除分类
										pThis->getCategoryManager()->removeCategory(pCategory->id);
										
										// 重新加载分类列表
										::SendMessage(hCategoryList, LB_RESETCONTENT, 0, 0);
										const auto& categories = pThis->getCategoryManager()->getCategories();
										for (const auto& category : categories)
										{
											int index = ::SendMessage(hCategoryList, LB_ADDSTRING, 0, reinterpret_cast<LPARAM>(category.name.c_str()));
											::SendMessage(hCategoryList, LB_SETITEMDATA, index, reinterpret_cast<LPARAM>(&category));
										}
										
										debugLog(L"设置对话框：成功删除分类 '%s'", pCategory->name.c_str());
									}
								}
								else
								{
									MessageBox(hwndDlg, L"不能删除默认的'全部'分类！", L"提示", MB_OK | MB_ICONWARNING);
								}
							}
							else
							{
								MessageBox(hwndDlg, L"请先选择一个要删除的分类！", L"提示", MB_OK | MB_ICONINFORMATION);
							}
						}
					}
					return TRUE;
				}
				
				case IDC_RENAME_CATEGORY:
				{
					if (pThis)
					{
						// 重命名分类功能
						HWND hCategoryList = ::GetDlgItem(hwndDlg, IDC_CATEGORY_LIST);
						if (hCategoryList)
						{
							int selectedIndex = ::SendMessage(hCategoryList, LB_GETCURSEL, 0, 0);
							if (selectedIndex != LB_ERR)
							{
								// 获取选中的分类
								FileCategory* pCategory = reinterpret_cast<FileCategory*>(
									::SendMessage(hCategoryList, LB_GETITEMDATA, selectedIndex, 0));
								
								if (pCategory && wcscmp(pCategory->name.c_str(), L"全部") != 0)
								{
									if (::MessageBox(hwndDlg, L"重命名功能暂未实现", L"提示", MB_OK | MB_ICONINFORMATION) == IDOK)
									{
										debugLog(L"设置对话框：重命名分类功能被调用");
									}
								}
								else
								{
									MessageBox(hwndDlg, L"不能重命名默认的'全部'分类！", L"提示", MB_OK | MB_ICONWARNING);
								}
							}
							else
							{
								MessageBox(hwndDlg, L"请先选择一个要重命名的分类！", L"提示", MB_OK | MB_ICONINFORMATION);
							}
						}
					}
					return TRUE;
				}
			}
			break;
		}
	}
	return FALSE;
}

// 实现设置对话框显示功能
void VerticalFileSwitcher::showSettingsDialog()
{
	debugLog(L"VerticalFileSwitcher::showSettingsDialog - 准备显示设置对话框");

	// 创建设置对话框的模态对话框，传递this指针
	INT_PTR result = ::DialogBoxParam(_hInst, MAKEINTRESOURCE(IDD_DOCLIST_SETTINGS), _hSelf, SettingsDlgProc, reinterpret_cast<LPARAM>(this));

	if (result == IDOK)
	{
		debugLog(L"VerticalFileSwitcher::showSettingsDialog - 设置对话框已确认，配置已保存");
	}
	else if (result == IDCANCEL)
	{
		debugLog(L"VerticalFileSwitcher::showSettingsDialog - 设置对话框已取消");
	}
	else
	{
		debugLog(L"VerticalFileSwitcher::showSettingsDialog - 设置对话框创建失败，错误码: %d", result);
	}
}

void VerticalFileSwitcher::initPopupMenus()
{
    // 初始化全局菜单
    
    // 销毁现有的全局菜单（如果存在）
    if (_hGlobalMenu)
    {
        ::DestroyMenu(_hGlobalMenu);
        _hGlobalMenu = NULL;
    }
    
    // 创建新的全局菜单（头部右键菜单，不包含文档分类功能）
    _hGlobalMenu = ::CreatePopupMenu();
    
    // 获取本地化语言支持
    NativeLangSpeaker* pNativeSpeaker = NppParameters::getInstance().getNativeLangSpeaker();
    const NppGUI& nppGUI = NppParameters::getInstance().getNppGUI();
    
    // 获取菜单项文本
    wstring extStr = pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT);
    wstring pathStr = pNativeSpeaker->getAttrNameStr(L"Path", FS_ROOTNODE, FS_CLMNPATH);
    wstring groupStr = pNativeSpeaker->getAttrNameStr(L"Group by View", FS_ROOTNODE, FS_LVGROUPS);

    // 注意：头部右键菜单不包含文档分类菜单
    
    ::InsertMenu(_hGlobalMenu, CLMNEXT_ID, MF_BYCOMMAND | MF_STRING, CLMNEXT_ID, extStr.c_str());
    ::InsertMenu(_hGlobalMenu, CLMNPATH_ID, MF_BYCOMMAND | MF_STRING, CLMNPATH_ID, pathStr.c_str());
    ::InsertMenu(_hGlobalMenu, SEP_POS, MF_BYCOMMAND | MF_SEPARATOR, 0, nullptr);
    ::InsertMenu(_hGlobalMenu, LVGROUPS_ID, MF_BYCOMMAND | MF_STRING, LVGROUPS_ID, groupStr.c_str());
    
    // 添加分隔符
    ::InsertMenu(_hGlobalMenu, 0, MF_BYCOMMAND | MF_SEPARATOR, 0, nullptr);
    
    // 添加设置菜单项
    wstring settingsStr = pNativeSpeaker->getAttrNameStr(L"Settings", FS_ROOTNODE, FS_SETTINGS);
    ::InsertMenu(_hGlobalMenu, IDM_SETTINGS_VFS, MF_BYCOMMAND | MF_STRING, IDM_SETTINGS_VFS, settingsStr.c_str());
    
    // 添加字体大小菜单
    HMENU hFontSizeMenu = ::CreatePopupMenu();
    wstring fontSizeStr = pNativeSpeaker->getAttrNameStr(L"Font Size", FS_ROOTNODE, FS_FONTSIZE);
    ::InsertMenu(hFontSizeMenu, FONTSIZE_6, MF_BYCOMMAND | MF_STRING, FONTSIZE_6, L"6");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_8, MF_BYCOMMAND | MF_STRING, FONTSIZE_8, L"8");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_10, MF_BYCOMMAND | MF_STRING, FONTSIZE_10, L"10");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_12, MF_BYCOMMAND | MF_STRING, FONTSIZE_12, L"12");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_14, MF_BYCOMMAND | MF_STRING, FONTSIZE_14, L"14");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_16, MF_BYCOMMAND | MF_STRING, FONTSIZE_16, L"16");
    ::InsertMenu(_hGlobalMenu, FONTSIZE_ID, MF_BYCOMMAND | MF_POPUP, reinterpret_cast<UINT_PTR>(hFontSizeMenu), fontSizeStr.c_str());

    bool isExtColumn = nppGUI._fileSwitcherWithoutExtColumn;
    ::CheckMenuItem(_hGlobalMenu, CLMNEXT_ID, MF_BYCOMMAND | (isExtColumn ? MF_UNCHECKED : MF_CHECKED));
    bool isPathColumn = nppGUI._fileSwitcherWithoutPathColumn;
    ::CheckMenuItem(_hGlobalMenu, CLMNPATH_ID, MF_BYCOMMAND | (isPathColumn ? MF_UNCHECKED : MF_CHECKED));
    bool isListViewGroups = nppGUI._fileSwitcherDisableListViewGroups;
    ::CheckMenuItem(_hGlobalMenu, LVGROUPS_ID, MF_BYCOMMAND | (isListViewGroups ? MF_UNCHECKED : MF_CHECKED));
    
    // 初始化文件列表右键菜单（包含文档分类功能）
    initFileListContextMenu();
}

// 初始化文件列表右键菜单（包含文档分类功能）
void VerticalFileSwitcher::initFileListContextMenu()
{
    // 销毁现有的文件列表菜单（如果存在）
    if (_hFileListMenu)
    {
        ::DestroyMenu(_hFileListMenu);
        _hFileListMenu = NULL;
    }
    
    // 创建新的文件列表菜单（包含文档分类功能）
    _hFileListMenu = ::CreatePopupMenu();
    
    // 获取本地化语言支持
    NativeLangSpeaker* pNativeSpeaker = NppParameters::getInstance().getNativeLangSpeaker();
    const NppGUI& nppGUI = NppParameters::getInstance().getNppGUI();
    
    // 获取菜单项文本
    wstring extStr = pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT);
    wstring pathStr = pNativeSpeaker->getAttrNameStr(L"Path", FS_ROOTNODE, FS_CLMNPATH);
    wstring groupStr = pNativeSpeaker->getAttrNameStr(L"Group by View", FS_ROOTNODE, FS_LVGROUPS);

    // 添加文档分类菜单
    HMENU hDocumentCategoryMenu = ::CreatePopupMenu();
    const auto& categories = _categoryManager.getCategories();
    
    // 添加所有分类到菜单
    for (size_t i = 0; i < categories.size(); ++i)
    {
        UINT menuId = CATEGORY_MENU_START + static_cast<UINT>(i);
        ::InsertMenu(hDocumentCategoryMenu, menuId, MF_BYCOMMAND | MF_STRING, menuId, categories[i].name.c_str());
    }
    wstring documentCategoryStr = L"文档分类";
    ::InsertMenu(_hFileListMenu, CATEGORY_MENU_ID, MF_BYCOMMAND | MF_POPUP, reinterpret_cast<UINT_PTR>(hDocumentCategoryMenu), documentCategoryStr.c_str());
    
    ::InsertMenu(_hFileListMenu, CLMNEXT_ID, MF_BYCOMMAND | MF_STRING, CLMNEXT_ID, extStr.c_str());
    ::InsertMenu(_hFileListMenu, CLMNPATH_ID, MF_BYCOMMAND | MF_STRING, CLMNPATH_ID, pathStr.c_str());
    ::InsertMenu(_hFileListMenu, SEP_POS, MF_BYCOMMAND | MF_SEPARATOR, 0, nullptr);
    ::InsertMenu(_hFileListMenu, LVGROUPS_ID, MF_BYCOMMAND | MF_STRING, LVGROUPS_ID, groupStr.c_str());
    
    // 添加字体大小菜单
    HMENU hFontSizeMenu = ::CreatePopupMenu();
    wstring fontSizeStr = L"设置字体"; //pNativeSpeaker->getAttrNameStr(L"Font Size", FS_ROOTNODE, FS_FONTSIZE);
    ::InsertMenu(hFontSizeMenu, FONTSIZE_6, MF_BYCOMMAND | MF_STRING, FONTSIZE_6, L"6");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_8, MF_BYCOMMAND | MF_STRING, FONTSIZE_8, L"8");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_10, MF_BYCOMMAND | MF_STRING, FONTSIZE_10, L"10");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_12, MF_BYCOMMAND | MF_STRING, FONTSIZE_12, L"12");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_14, MF_BYCOMMAND | MF_STRING, FONTSIZE_14, L"14");
    ::InsertMenu(hFontSizeMenu, FONTSIZE_16, MF_BYCOMMAND | MF_STRING, FONTSIZE_16, L"16");
    ::InsertMenu(_hFileListMenu, FONTSIZE_ID, MF_BYCOMMAND | MF_POPUP, reinterpret_cast<UINT_PTR>(hFontSizeMenu), fontSizeStr.c_str());

    bool isExtColumn = nppGUI._fileSwitcherWithoutExtColumn;
    ::CheckMenuItem(_hFileListMenu, CLMNEXT_ID, MF_BYCOMMAND | (isExtColumn ? MF_UNCHECKED : MF_CHECKED));
    bool isPathColumn = nppGUI._fileSwitcherWithoutPathColumn;
    ::CheckMenuItem(_hFileListMenu, CLMNPATH_ID, MF_BYCOMMAND | (isPathColumn ? MF_UNCHECKED : MF_CHECKED));
    bool isListViewGroups = nppGUI._fileSwitcherDisableListViewGroups;
    ::CheckMenuItem(_hFileListMenu, LVGROUPS_ID, MF_BYCOMMAND | (isListViewGroups ? MF_UNCHECKED : MF_CHECKED));
    
    // 添加文件特定的菜单项
    // 添加分隔符
    ::AppendMenu(_hFileListMenu, MF_SEPARATOR, 0, NULL);

    // 添加设置菜单项
    wstring settingsStr = L"设置"; //pNativeSpeaker->getAttrNameStr(L"Settings", FS_ROOTNODE, FS_SETTINGS);
    ::AppendMenu(_hFileListMenu, MF_STRING, IDM_SETTINGS_VFS, settingsStr.c_str());

    // 添加分隔符
    ::AppendMenu(_hFileListMenu, MF_SEPARATOR, 0, NULL);

    // 添加标签颜色子菜单
    HMENU hTabColorMenu = ::CreatePopupMenu();
    ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 0, L"红色标签");
    ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 1, L"绿色标签");
    ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 2, L"蓝色标签");
    ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 3, L"黄色标签");
    ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 4, L"紫色标签");
    
    // 添加标签颜色菜单项
    ::AppendMenu(_hFileListMenu, MF_STRING | MF_POPUP, (UINT_PTR)hTabColorMenu, L"标签颜色");
    
    ::AppendMenu(_hFileListMenu, MF_SEPARATOR, 0, NULL);
    ::AppendMenu(_hFileListMenu, MF_STRING, 1001, L"打开文件所在目录");
    ::AppendMenu(_hFileListMenu, MF_STRING, 1002, L"复制文件路径");
}

void VerticalFileSwitcher::popupMenuCmd(int cmdID)
{
	// 处理标签颜色菜单点击
	if (cmdID >= TAB_COLOR_MENU_START && cmdID < TAB_COLOR_MENU_START + 10)
	{
		// 获取颜色索引
		int colorIndex = cmdID - TAB_COLOR_MENU_START;
		
		// 设置标签颜色
		_fileListView.onTabColorChange(colorIndex);
		
		debugLog(L"VerticalFileSwitcher::popupMenuCmd - 标签颜色已更改为: %d", colorIndex);
		return;
	}
	
	// 处理分类菜单点击
	if (cmdID >= CATEGORY_MENU_START && cmdID < CATEGORY_MENU_START + 100)
	{
		// 获取分类索引
		size_t categoryIndex = cmdID - CATEGORY_MENU_START;
		const auto& categories = _categoryManager.getCategories();
		
		if (categoryIndex < categories.size())
		{
			const auto& selectedCategory = categories[categoryIndex];
			
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
			
			debugLog(L"VerticalFileSwitcher::popupMenuCmd - 分类已更改为: %s", selectedCategory.name.c_str());
		}
		return;
	}
	
	switch (cmdID)
	{
		case CLMNEXT_ID:
		{
			bool& isExtColumn = NppParameters::getInstance().getNppGUI()._fileSwitcherWithoutExtColumn;
			isExtColumn = !isExtColumn;
			// 同时更新全局菜单和文件列表菜单的检查状态
			::CheckMenuItem(_hGlobalMenu, CLMNEXT_ID, MF_BYCOMMAND | (isExtColumn ? MF_UNCHECKED : MF_CHECKED));
			::CheckMenuItem(_hFileListMenu, CLMNEXT_ID, MF_BYCOMMAND | (isExtColumn ? MF_UNCHECKED : MF_CHECKED));
			reload();
		}
		break;
		case CLMNPATH_ID:
		{
			bool& isPathColumn = NppParameters::getInstance().getNppGUI()._fileSwitcherWithoutPathColumn;
			isPathColumn = !isPathColumn;
			// 同时更新全局菜单和文件列表菜单的检查状态
			::CheckMenuItem(_hGlobalMenu, CLMNPATH_ID, MF_BYCOMMAND | (isPathColumn ? MF_UNCHECKED : MF_CHECKED));
			::CheckMenuItem(_hFileListMenu, CLMNPATH_ID, MF_BYCOMMAND | (isPathColumn ? MF_UNCHECKED : MF_CHECKED));
			reload();
		}
		break;
		case LVGROUPS_ID:
		{
			bool& isListViewGroups = NppParameters::getInstance().getNppGUI()._fileSwitcherDisableListViewGroups;
			isListViewGroups = !isListViewGroups;
			// 同时更新全局菜单和文件列表菜单的检查状态
			::CheckMenuItem(_hGlobalMenu, LVGROUPS_ID, MF_BYCOMMAND | (isListViewGroups ? MF_UNCHECKED : MF_CHECKED));
			::CheckMenuItem(_hFileListMenu, LVGROUPS_ID, MF_BYCOMMAND | (isListViewGroups ? MF_UNCHECKED : MF_CHECKED));
			reload();
		}
		break;
		
		// 字体大小菜单处理
		case FONTSIZE_6:
			setFontSize(6);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 6;
			_fileListView.reload(); // 重新加载文件列表以确保字体大小改变后列表内容正确显示
			break;
		case FONTSIZE_8:
			setFontSize(8);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 8;
			_fileListView.reload(); // 重新加载文件列表以确保字体大小改变后列表内容正确显示
			break;
		case FONTSIZE_10:
			setFontSize(10);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 10;
			_fileListView.reload(); // 重新加载文件列表以确保字体大小改变后列表内容正确显示
			break;
		case FONTSIZE_12:
			setFontSize(12);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 12;
			_fileListView.reload(); // 重新加载文件列表以确保字体大小改变后列表内容正确显示
			break;
		case FONTSIZE_14:
			setFontSize(14);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 14;
			_fileListView.reload(); // 重新加载文件列表以确保字体大小改变后列表内容正确显示
			break;
		case FONTSIZE_16:
			setFontSize(16);
			NppParameters::getInstance().getNppGUI()._fileSwitcherFontSize = 16;
			_fileListView.reload(); // 重新加载文件列表以确保字体大小改变后列表内容正确显示
			break;
		
		// 设置菜单处理
		case IDM_SETTINGS_VFS:
		{
			// 处理设置命令
			debugLog(L"VerticalFileSwitcher::popupMenuCmd - 设置命令被触发");
			
			// 发送消息打开设置对话框 - 使用标准的IDM_SETTING_PREFERENCE
			::SendMessage(_hParent, NPPM_MENUCOMMAND, 0, IDM_SETTING_PREFERENCE);
			debugLog(L"VerticalFileSwitcher::popupMenuCmd - 已发送标准设置对话框打开消息");
		}
		break;

	}
}

void VerticalFileSwitcher::display(bool toShow) const // 添加const修饰符
{
	// 添加调试信息
	debugLog(L"VerticalFileSwitcher::display() called with toShow=%d\n", toShow);
	
	DockingDlgInterface::display(toShow);
	
	// 添加调试信息
	debugLog(L"VerticalFileSwitcher::display() after DockingDlgInterface::display()\n");
	
	// 我们需要一个非const引用来调用ensureVisibleCurrentItem
	// 使用const_cast来解决这个问题
	VerticalFileSwitcher* nonConstThis = const_cast<VerticalFileSwitcher*>(this);
	nonConstThis->_fileListView.ensureVisibleCurrentItem();	// without this call the current item may stay above visible area after the program startup
	
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
	int index2Switch = (docPosInfo << 2) > 2;

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
