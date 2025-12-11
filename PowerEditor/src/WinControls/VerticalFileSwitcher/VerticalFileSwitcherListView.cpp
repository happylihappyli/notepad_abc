#include <shlwapi.h>
#include <stdexcept>
#include <iostream>
#include <algorithm>
#include <cctype>
#include "VerticalFileSwitcherListView.h"
#include "VerticalFileSwitcher_rc.h"
#include "Buffer.h"
#include "localization.h"
#include "Common.h"
#include "Notepad_plus.h"
#include "menuCmdID.h"

using namespace std;

void VerticalFileSwitcherListView::init(HINSTANCE hInst, HWND parent, HIMAGELIST hImaLst)
{
	Window::init(hInst, parent);
	_hImaLst = hImaLst;
	INITCOMMONCONTROLSEX icex{};

	// Ensure that the common control DLL is loaded. 
	icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
	icex.dwICC  = ICC_LISTVIEW_CLASSES;
	InitCommonControlsEx(&icex);

	// Note: No longer create new ListView control here, use the existing control in the dialog template
	// Actual ListView control creation and association is completed in VerticalFileSwitcher's WM_CREATE message handling

	// Initialize Group Information
	LVGROUP group{};
	constexpr size_t headerLen = 1;
	wchar_t header[headerLen] = L"";
	group.cbSize = sizeof(LVGROUP);
	group.mask = LVGF_HEADER | LVGF_GROUPID | LVGF_STATE;
	group.pszHeader = header;
	group.cchHeader = headerLen;
	group.iGroupId = _groupID;
	group.state = LVGS_COLLAPSIBLE;

	LVGROUP group2 = group;
	group2.iGroupId = _group2ID;

	// Note: Do not insert groups here because _hSelf may not be set yet
	// Group insertion will be completed in the initList method
}

void VerticalFileSwitcherListView::destroy()
{
	LVITEM item{};
	item.mask = LVIF_PARAM;
	int nbItem = ListView_GetItemCount(_hSelf);
	for (int i = 0 ; i < nbItem ; ++i)
	{
		item.iItem = i;
		ListView_GetItem(_hSelf, &item);
		TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;
		delete tlfs;
	}
	::DestroyWindow(_hSelf);
	_hSelf = NULL;
} 

void VerticalFileSwitcherListView::initList()
{
	// Check if _hSelf is valid
	if (!_hSelf || !::IsWindow(_hSelf)) {
		debugLog(L"VerticalFileSwitcherListView::initList() - 错误：ListView控件句柄无效！");
		return;
	}

	NppParameters& nppParams = NppParameters::getInstance();
	NativeLangSpeaker *pNativeSpeaker = nppParams.getNativeLangSpeaker();
	
	const bool isListViewGroups = !nppParams.getNppGUI()._fileSwitcherDisableListViewGroups;
	ListView_EnableGroupView(_hSelf, isListViewGroups ? TRUE : FALSE);
	
	// Set extended styles for list view
	ListView_SetExtendedListViewStyle(_hSelf, LVS_EX_FULLROWSELECT | LVS_EX_BORDERSELECT | LVS_EX_INFOTIP | LVS_EX_DOUBLEBUFFER);
	ListView_SetItemCountEx(_hSelf, 50, LVSICF_NOSCROLL);
	
	// Insert group information
	LVGROUP group{};
	constexpr size_t headerLen = 1;
	wchar_t header[headerLen] = L"";
	group.cbSize = sizeof(LVGROUP);
	group.mask = LVGF_HEADER | LVGF_GROUPID | LVGF_STATE;
	group.pszHeader = header;
	group.cchHeader = headerLen;
	group.iGroupId = _groupID;
	group.state = LVGS_COLLAPSIBLE;

	LVGROUP group2 = group;
	group2.iGroupId = _group2ID;

	ListView_InsertGroup(_hSelf, -1, &group);
	ListView_InsertGroup(_hSelf, -1, &group2);

	// Force display only filename and category columns, hide extension column
	bool isExtColumn = false;  // 隐藏扩展名列
	bool isCategoryColumn = true; // Always display category column

	RECT rc{};
	::GetClientRect(_hParent, &rc);
	int nameWidth = rc.right - rc.left;
	int colIndex = 0;
	if (isExtColumn)
		nameWidth -= nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherExtWidth);
	if (isCategoryColumn)
		nameWidth -= nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherCategoryWidth); // 使用保存的分类列宽度

	// Limit the maximum width of the first column (filename) to 200 pixels (considering DPI scaling), adjust to smaller width
	const int maxNameWidth = nppParams._dpiManager.scaleX(200);
	if (nameWidth > maxNameWidth)
		nameWidth = maxNameWidth;

	//add columns
	wstring nameStr = pNativeSpeaker->getAttrNameStr(L"Name", FS_ROOTNODE, FS_CLMNNAME);
	insertColumn(nameStr.c_str(), nameWidth, ++colIndex);
	if (isExtColumn)
	{
		wstring extStr = pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT);
		insertColumn(extStr.c_str(), nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherExtWidth), ++colIndex); //2nd column
	}
	// 新增：Add Category列
	if (isCategoryColumn)
	{
		wstring categoryStr = pNativeSpeaker->getAttrNameStr(L"Category", FS_ROOTNODE, FS_CLMNCATEGORY);
		int categoryWidth = nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherCategoryWidth); // 使用保存的分类列宽度
		insertColumn(categoryStr.c_str(), categoryWidth, ++colIndex); //3rd column
		debugLog(L"VerticalFileSwitcherListView::initList() - Add Category列，宽度: %d", categoryWidth);
	}
	// 注释掉路径列的添加，确保只显示三列

	TaskListInfo taskListInfo;
	// 使用我们设置的Notepad++ Main Window Handle，而不是通过GetParent获取
	HWND nppHwnd = _nppMainWnd;
	
	// Add detailed debug logs: Check window handles and hierarchy
	debugLog(L"VerticalFileSwitcherListView::initList() - 开始获取Document List信息");
	debugLog(L"当前窗口句柄: %p", _hSelf);
	debugLog(L"父窗口句柄: %p", _hParent);
	debugLog(L"Notepad_abc Main Window Handle: %p", nppHwnd);
	debugLog(L"WM_GETTASKLISTINFO消息值: %d", WM_GETTASKLISTINFO);
	
	// 检查窗口是否有效
	if (!::IsWindow(nppHwnd)) {
		debugLog(L"VerticalFileSwitcherListView::initList() - 错误：Notepad++ Main Window Handle无效！");
		// 尝试直接获取顶级窗口
		nppHwnd = ::GetAncestor(_hParent, GA_ROOT);
		debugLog(L"VerticalFileSwitcherListView::initList() - 尝试使用顶级窗口句柄: %p", nppHwnd);
	}
	
	::SendMessage(nppHwnd, WM_GETTASKLISTINFO, reinterpret_cast<WPARAM>(&taskListInfo), 0);
	
	// Add detailed debug logs: Check the number of documents retrieved
	debugLog(L"获取的文档数量: %zu", taskListInfo._tlfsLst.size());
	debugLog(L"当前索引: %d", taskListInfo._currentIndex);
	debugLog(L"TaskListInfo地址: %p", &taskListInfo);
	
	// 如果获取的Document List为空，直接返回，不添加示例数据
	if (taskListInfo._tlfsLst.empty()) {
		debugLog(L"VerticalFileSwitcherListView::initList() - Document List为空，跳过加载");
		removeAll(); // 清空列表
		return;
	}

	int itemIndex = 0;
	for (size_t i = 0, len = taskListInfo._tlfsLst.size(); i < len ; ++i)
	{
		TaskLstFnStatus & fileNameStatus = taskListInfo._tlfsLst[i];
		
		// Category filtering: If current category is set, check if files belong to that category
		if (!_currentCategory.empty() && _categoryManager)
		{
			std::wstring filePath = fileNameStatus._fn;
			
			// 如果当前分类是"All"或"Default Category"，显示所有文件
			if (_currentCategory == L"All" || _currentCategory == L"Default Category")
			{
				// 不跳过任何文件，显示All
				debugLog(L"VerticalFileSwitcherListView::initList - 显示All文件: %s, 当前分类: %s", 
					filePath.c_str(), _currentCategory.c_str());
			}
			else
			{
				std::wstring fileCategoryId = _categoryManager->getFileCategory(filePath);
				
				// Get category name by category ID
				FileCategory* fileCategory = _categoryManager->getCategoryById(fileCategoryId);
				std::wstring fileCategoryName = fileCategory ? fileCategory->name : _categoryManager->getDefaultCategoryName();
				
				// Get the ID of the currently selected category
				FileCategory* currentCategory = _categoryManager->getCategoryByName(_currentCategory);
				std::wstring currentCategoryId = currentCategory ? currentCategory->id : _categoryManager->getDefaultCategoryId();
				
				// If the file category ID does not match the currently selected category ID, skip the file
				if (fileCategoryId != currentCategoryId)
				{
					// Debug info: Show filtered files
					debugLog(L"VerticalFileSwitcherListView::initList - 过滤文件: %s, 文件Category ID: %s, 当前Category ID: %s, Category Name: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
					continue;
				}
				else
				{
					// Debug info: Show retained files
					debugLog(L"VerticalFileSwitcherListView::initList - 保留文件: %s, 文件Category ID: %s, 当前Category ID: %s, Category Name: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
				}
			}
		}
		else
		{
			// Debug info: Category filtering not enabled, show all files
			debugLog(L"VerticalFileSwitcherListView::initList - 分类过滤未启用，显示所有文件: _currentCategory=%s, _categoryManager=%p", 
				_currentCategory.c_str(), _categoryManager);
		}

		TaskLstFnStatus *tl = new TaskLstFnStatus(fileNameStatus);

		wchar_t fn[MAX_PATH] = { '\0' };
		wcscpy_s(fn, MAX_PATH, ::PathFindFileName(fileNameStatus._fn.c_str()));

		// Fix: Keep filename as is, do not remove extension
		// Extension will be displayed separately in the extension column
		LVITEM item{};
		item.mask = LVIF_TEXT | LVIF_IMAGE | LVIF_PARAM | LVIF_GROUPID;
		
		item.pszText = fn;
		item.iItem = itemIndex;
		item.iSubItem = 0;
		item.iImage = fileNameStatus._status;
		item.lParam = reinterpret_cast<LPARAM>(tl);
		item.iGroupId = (fileNameStatus._iView == MAIN_VIEW) ? _groupID : _group2ID;
		ListView_InsertItem(_hSelf, &item);
		int colIndex2 = 0;
		if (isExtColumn)
		{
			ListView_SetItemText(_hSelf, itemIndex, ++colIndex2, ::PathFindExtension(fileNameStatus._fn.c_str()));
		}
		// New: Set category column data
		if (isCategoryColumn)
		{
			// Get file category information (with auto-categorization logic)
			std::wstring filePath = fileNameStatus._fn;
			std::wstring fileCategoryName = getFileCategoryName(filePath);
			
			ListView_SetItemText(_hSelf, itemIndex, ++colIndex2, (LPWSTR)fileCategoryName.c_str());
			debugLog(L"VerticalFileSwitcherListView::initList - 为文件 %s Set category列数据: %s", filePath.c_str(), fileCategoryName.c_str());
		}
		// Comment out path column data setting to ensure only three columns are displayed
		itemIndex++;
	}
	_currentIndex = taskListInfo._currentIndex;
	selectCurrentItem();
	ensureVisibleCurrentItem();	// without this call the current item may become invisible after adding/removing columns
}

void VerticalFileSwitcherListView::reload()
{
	// Suppress redraws for performance. We target _hParent to prevent scroll bar flickering.
	::SendMessage(_hParent, WM_SETREDRAW, false, 0);
	
	// Check if _hSelf is valid
	if (!_hSelf || !::IsWindow(_hSelf)) {
		debugLog(L"VerticalFileSwitcherListView::reload() - 错误：ListView控件句柄无效！");
		::SendMessage(_hParent, WM_SETREDRAW, true, 0);
		return;
	}

	// Clear existing list items and columns
	removeAll();
	
	// Force refresh interface to ensure clearing operation takes effect
	::InvalidateRect(_hSelf, NULL, TRUE);
	::UpdateWindow(_hSelf);

	NppParameters& nppParams = NppParameters::getInstance();
	NativeLangSpeaker *pNativeSpeaker = nppParams.getNativeLangSpeaker();
	
	const bool isListViewGroups = !nppParams.getNppGUI()._fileSwitcherDisableListViewGroups;
	ListView_EnableGroupView(_hSelf, isListViewGroups ? TRUE : FALSE);
	
	// Set extended styles for list view
	ListView_SetExtendedListViewStyle(_hSelf, LVS_EX_FULLROWSELECT | LVS_EX_BORDERSELECT | LVS_EX_INFOTIP | LVS_EX_DOUBLEBUFFER);
	ListView_SetItemCountEx(_hSelf, 50, LVSICF_NOSCROLL);
	
	// Insert group information
	LVGROUP group{};
	constexpr size_t headerLen = 1;
	wchar_t header[headerLen] = L"";
	group.cbSize = sizeof(LVGROUP);
	group.mask = LVGF_HEADER | LVGF_GROUPID | LVGF_STATE;
	group.pszHeader = header;
	group.cchHeader = headerLen;
	group.iGroupId = _groupID;
	group.state = LVGS_COLLAPSIBLE;

	LVGROUP group2 = group;
	group2.iGroupId = _group2ID;

	ListView_InsertGroup(_hSelf, -1, &group);
	ListView_InsertGroup(_hSelf, -1, &group2);

	// Force display only filename and category columns, hide extension column
	bool isExtColumn = false;  // 隐藏扩展名列
	bool isCategoryColumn = true; // Always display category column

	RECT rc{};
	::GetClientRect(_hParent, &rc);
	int nameWidth = rc.right - rc.left;
	int colIndex = 0;
	if (isExtColumn)
		nameWidth -= nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherExtWidth);
	if (isCategoryColumn)
		nameWidth -= nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherCategoryWidth); // 使用保存的分类列宽度

	// Limit the maximum width of the first column (filename) to 200 pixels (considering DPI scaling), adjust to smaller width
	const int maxNameWidth = nppParams._dpiManager.scaleX(200);
	if (nameWidth > maxNameWidth)
		nameWidth = maxNameWidth;

	//add columns
	wstring nameStr = pNativeSpeaker->getAttrNameStr(L"Name", FS_ROOTNODE, FS_CLMNNAME);
	insertColumn(nameStr.c_str(), nameWidth, ++colIndex);
	if (isExtColumn)
	{
		wstring extStr = pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT);
		insertColumn(extStr.c_str(), nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherExtWidth), ++colIndex); //2nd column
	}
	// 新增：Add Category列
	if (isCategoryColumn)
	{
		wstring categoryStr = pNativeSpeaker->getAttrNameStr(L"Category", FS_ROOTNODE, FS_CLMNCATEGORY);
		int categoryWidth = nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherCategoryWidth); // 使用保存的分类列宽度
		insertColumn(categoryStr.c_str(), categoryWidth, ++colIndex); //3rd column
		debugLog(L"VerticalFileSwitcherListView::reload() - Add Category列，宽度: %d", categoryWidth);
	}
	// 注释掉路径列的添加，确保只显示三列

	TaskListInfo taskListInfo;
	// 使用我们设置的Notepad++ Main Window Handle，而不是通过GetParent获取
	HWND nppHwnd = _nppMainWnd;
	
	// 检查窗口是否有效
	if (!::IsWindow(nppHwnd)) {
		debugLog(L"VerticalFileSwitcherListView::reload() - 错误：Notepad++ Main Window Handle无效！");
		nppHwnd = ::GetAncestor(_hParent, GA_ROOT);
	}
	
	::SendMessage(nppHwnd, WM_GETTASKLISTINFO, reinterpret_cast<WPARAM>(&taskListInfo), 0);
	
	// 如果获取的Document List为空，Clear file list
	if (taskListInfo._tlfsLst.empty()) {
		debugLog(L"VerticalFileSwitcherListView::reload() - Document List为空，Clear file list");
		removeAll(); // Clear file list
		::SendMessage(_hParent, WM_SETREDRAW, true, 0);
		::InvalidateRect(_hSelf, NULL, TRUE);
		::UpdateWindow(_hSelf);
		return;
	}

	int itemIndex = 0;
	for (size_t i = 0, len = taskListInfo._tlfsLst.size(); i < len ; ++i)
	{
		TaskLstFnStatus & fileNameStatus = taskListInfo._tlfsLst[i];
		
		// Category filtering: If current category is set, check if files belong to that category
		if (!_currentCategory.empty() && _categoryManager)
		{
			std::wstring filePath = fileNameStatus._fn;
			
			// 如果当前分类是"All"或"Default Category"，显示所有文件
			if (_currentCategory == L"All" || _currentCategory == L"Default Category")
			{
				// 不跳过任何文件，显示All
				debugLog(L"VerticalFileSwitcherListView::reload - 显示All文件: %s, 当前分类: %s", 
					filePath.c_str(), _currentCategory.c_str());
			}
			else
			{
				std::wstring fileCategoryId = _categoryManager->getFileCategory(filePath);
				
				// Get category name by category ID
				FileCategory* fileCategory = _categoryManager->getCategoryById(fileCategoryId);
				std::wstring fileCategoryName = fileCategory ? fileCategory->name : _categoryManager->getDefaultCategoryName();
				
				// Get the ID of the currently selected category
				FileCategory* currentCategory = _categoryManager->getCategoryByName(_currentCategory);
				std::wstring currentCategoryId = currentCategory ? currentCategory->id : _categoryManager->getDefaultCategoryId();
				
				// If the file category ID does not match the currently selected category ID, skip the file
				if (fileCategoryId != currentCategoryId)
				{
					// Debug info: Show filtered files
					debugLog(L"VerticalFileSwitcherListView::reload - 过滤文件: %s, 文件Category ID: %s, 当前Category ID: %s, Category Name: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
					continue;
				}
				else
				{
					// Debug info: Show retained files
					debugLog(L"VerticalFileSwitcherListView::reload - 保留文件: %s, 文件Category ID: %s, 当前Category ID: %s, Category Name: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
				}
			}
		}
		else
		{
			// Debug info: Category filtering not enabled, show all files
			debugLog(L"VerticalFileSwitcherListView::reload - 分类过滤未启用，显示所有文件: _currentCategory=%s, _categoryManager=%p", 
				_currentCategory.c_str(), _categoryManager);
		}

		TaskLstFnStatus *tl = new TaskLstFnStatus(fileNameStatus);

		wchar_t fn[MAX_PATH] = { '\0' };
		wcscpy_s(fn, MAX_PATH, ::PathFindFileName(fileNameStatus._fn.c_str()));

		// Fix: Keep filename as is, do not remove extension
		// Extension will be displayed separately in the extension column
		LVITEM item{};
		item.mask = LVIF_TEXT | LVIF_IMAGE | LVIF_PARAM | LVIF_GROUPID;
		
		item.pszText = fn;
		item.iItem = itemIndex;
		item.iSubItem = 0;
		item.iImage = fileNameStatus._status;
		item.lParam = reinterpret_cast<LPARAM>(tl);
		item.iGroupId = (fileNameStatus._iView == MAIN_VIEW) ? _groupID : _group2ID;
		ListView_InsertItem(_hSelf, &item);
		// if (isExtColumn)
		// {
		// 	ListView_SetItemText(_hSelf, itemIndex, 1, (LPTSTR)::PathFindExtension(fileNameStatus._fn.c_str()));
		// }
		// New: Set category column data
		if (isCategoryColumn)
		{
			// Get file category information (with auto-categorization logic)
			std::wstring filePath = fileNameStatus._fn;
			std::wstring fileCategoryName = getFileCategoryName(filePath);
			
			// Correctly calculate category column index: if extension column is hidden, category column is the second column
			int categoryColIndex = isExtColumn ? 2 : 1;
			ListView_SetItemText(_hSelf, itemIndex, categoryColIndex, (LPWSTR)fileCategoryName.c_str());
			debugLog(L"VerticalFileSwitcherListView::reload - 为文件 %s Set category列数据: %s", filePath.c_str(), fileCategoryName.c_str());
		}
		// Comment out path column data setting to ensure only three columns are displayed
		
		itemIndex++;
	}

	resizeColumns(rc.right - rc.left);
	::SendMessage(_hParent, WM_SETREDRAW, true, 0);
	redrawItems();
	
	// 强制刷新界面，确保新数据正确显示
	::InvalidateRect(_hSelf, NULL, TRUE);
	::UpdateWindow(_hSelf);
}

void VerticalFileSwitcherListView::redrawItems()
{
	int nbItem = ListView_GetItemCount(_hSelf);
	::SendMessage(_hSelf, WM_PAINT, 0, 0);
	ListView_RedrawItems(_hSelf, 0, nbItem - 1);
}

BufferID VerticalFileSwitcherListView::getBufferInfoFromIndex(int index, int & view) const
{
	int nbItem = ListView_GetItemCount(_hSelf);
	if (index < 0 || index >= nbItem)
		return BUFFER_INVALID;

	LVITEM item{};
	item.mask = LVIF_PARAM;
	item.iItem = index;
	ListView_GetItem(_hSelf, &item);
	TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;

	view = tlfs->_iView;
	return static_cast<BufferID>(tlfs->_bufID);
}

int VerticalFileSwitcherListView::newItem(BufferID bufferID, int iView)
{
	int i = find(bufferID, iView);
	if (i == -1)
	{
		i = add(bufferID, iView);
	}
	return i;
}

void VerticalFileSwitcherListView::setItemIconStatus(BufferID bufferID)
{
	Buffer *buf = bufferID;
	
	// 生成Sample Document名称
	wchar_t exampleName[MAX_PATH] = { '\0' };
	int fileIndex = find(bufferID, MAIN_VIEW); // 查找文件在列表中的位置
	if (fileIndex == -1) fileIndex = find(bufferID, SUB_VIEW);
	if (fileIndex == -1) fileIndex = 0;
	
	swprintf_s(exampleName, MAX_PATH, L"Sample Document%d", fileIndex + 1);
	
	bool isExtColumn = !(NppParameters::getInstance()).getNppGUI()._fileSwitcherWithoutExtColumn;
	if (isExtColumn)
	{
		// 对于Sample Document，不需要移除扩展名
	}
	LVITEM item{};
	item.pszText = exampleName;
	item.iSubItem = 0;
	item.iImage = buf->isMonitoringOn()?3:(buf->isReadOnly()?2:(buf->isDirty()?1:0));

	int nbItem = ListView_GetItemCount(_hSelf);

	for (int i = 0 ; i < nbItem ; ++i)
	{
		item.mask = LVIF_PARAM;
		item.iItem = i;
		ListView_GetItem(_hSelf, &item);
		TaskLstFnStatus *tlfs = (TaskLstFnStatus *)(item.lParam);
		if (tlfs->_bufID == bufferID)
		{
			tlfs->_fn = buf->getFullPathName();
			item.mask = LVIF_TEXT | LVIF_IMAGE;
			
			// Do not update display text when clicking filename, keep original filename unchanged
			// Use original filename, do not display full path
			wchar_t fileNameOnly[MAX_PATH] = { '\0' };
			wcscpy_s(fileNameOnly, MAX_PATH, PathFindFileName(tlfs->_fn.c_str()));
			item.pszText = fileNameOnly;
			
			ListView_SetItem(_hSelf, &item);
			bool isCategoryColumn = true; // Always display category column
			
			// Set category列的数据
			if (isCategoryColumn)
			{
				// Get file category information (with auto-categorization logic)
				std::wstring filePath = tlfs->_fn;
				std::wstring fileCategoryName = getFileCategoryName(filePath);
				
				// Correctly calculate category column index: if extension column is hidden, category column is the second column
				int categoryColIndex = isExtColumn ? 2 : 1;
				
				// Debug log: Check category column data setting
				debugLog(L"VerticalFileSwitcherListView::setItemIconStatus - 文件: %s, Category Name: %s, Category Column Index: %d, 扩展名列状态: %d", 
					filePath.c_str(), fileCategoryName.c_str(), categoryColIndex, isExtColumn);
				
				// 检查是否错误地设置了扩展名
				std::wstring ext = ::PathFindExtension(filePath.c_str());
				if (fileCategoryName == ext)
				{
					debugLog(L"VerticalFileSwitcherListView::setItemIconStatus - Warning: Category column displays extension instead of category name！");
				}
				
				ListView_SetItemText(_hSelf, i, categoryColIndex, (LPWSTR)fileCategoryName.c_str());
			}
		}
	}
}

void VerticalFileSwitcherListView::setItemColor(BufferID bufferID, int colorIndex)
{
	LVITEM item{};
	item.mask = LVIF_PARAM;

	int nbItem = ListView_GetItemCount(_hSelf);

	for (int i = 0; i < nbItem; ++i)
	{
		item.iItem = i;
		ListView_GetItem(_hSelf, &item);
		TaskLstFnStatus* tlfs = reinterpret_cast<TaskLstFnStatus*>(item.lParam);
		if (tlfs->_bufID == bufferID)
		{
			tlfs->_docColor = colorIndex;
			ListView_SetItem(_hSelf, &item);
		}
	}

	redraw();
}

wstring VerticalFileSwitcherListView::getFullFilePath(size_t i) const
{
	size_t nbItem = ListView_GetItemCount(_hSelf);
	if (i > nbItem)
		return L"";

	LVITEM item{};
	item.mask = LVIF_PARAM;
	item.iItem = static_cast<int32_t>(i);
	ListView_GetItem(_hSelf, &item);
	const TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;

	return tlfs->_fn;
}

int VerticalFileSwitcherListView::closeItem(BufferID bufferID, int iView)
{
	int i = find(bufferID, iView);
	if (i != -1)
		remove(i);
	return i;
}

void VerticalFileSwitcherListView::activateItem(BufferID bufferID, int iView)
{
	// Suppress redraws while we're resetting states
	::SendMessage(_hSelf, WM_SETREDRAW, false, 0);

	// Clean all selection
	int nbItem = ListView_GetItemCount(_hSelf);
	for (int i = 0; i < nbItem; ++i)
		ListView_SetItemState(_hSelf, i, 0, LVIS_FOCUSED|LVIS_SELECTED);

	_currentIndex = newItem(bufferID, iView);
	selectCurrentItem();
	// Have to enable redraw to be able to move selection to the current item
	::SendMessage(_hSelf, WM_SETREDRAW, true, 0);
	ensureVisibleCurrentItem();
	redrawItems();
}

int VerticalFileSwitcherListView::add(BufferID bufferID, int iView)
{
	_currentIndex = ListView_GetItemCount(_hSelf);
	Buffer *buf = bufferID;
	const wchar_t *fileName = buf->getFileName();
	const NppGUI& nppGUI = NppParameters::getInstance().getNppGUI();
	TaskLstFnStatus *tl = new TaskLstFnStatus(iView, 0, buf->getFullPathName(), 0, (void *)bufferID, -1);

	bool isExtColumn = !nppGUI._fileSwitcherWithoutExtColumn;
	
	// Keep filename unchanged, do not process
	// Use original filename directly
	
	LVITEM item{};
	item.mask = LVIF_TEXT | LVIF_IMAGE | LVIF_PARAM | LVIF_GROUPID;
	
	item.pszText = const_cast<wchar_t*>(fileName);
	item.iItem = _currentIndex;
	item.iSubItem = 0;
	item.iImage = buf->isMonitoringOn()?3:(buf->isReadOnly()?2:(buf->isDirty()?1:0));
	item.lParam = reinterpret_cast<LPARAM>(tl);
	item.iGroupId = (iView == MAIN_VIEW) ? _groupID : _group2ID;
	ListView_InsertItem(_hSelf, &item);
	bool isCategoryColumn = true; // Always display category column
	
	if (isExtColumn)
	{
		// Display extension
		ListView_SetItemText(_hSelf, _currentIndex, 1, ::PathFindExtension(buf->getFullPathName()));
	}
	
	// Set category列的数据
	if (isCategoryColumn)
	{
		// Get file category information (with auto-categorization logic)
		std::wstring filePath = buf->getFullPathName();
		std::wstring fileCategoryName = getFileCategoryName(filePath);
		
		// Correctly calculate category column index: if extension column is hidden, category column is the second column
		int categoryColIndex = isExtColumn ? 2 : 1;
		ListView_SetItemText(_hSelf, _currentIndex, categoryColIndex, (LPWSTR)fileCategoryName.c_str());
	}
	
	selectCurrentItem();
	
	return _currentIndex;
}


void VerticalFileSwitcherListView::remove(int index, bool removeFromListview)
{
	LVITEM item{};
	item.mask = LVIF_PARAM;
	item.iItem = index;
	ListView_GetItem(_hSelf, &item);
	TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;
	delete tlfs;
	
	if (removeFromListview)
		ListView_DeleteItem(_hSelf, index);
}

void VerticalFileSwitcherListView::removeAll()
{
	int nbItem = ListView_GetItemCount(_hSelf);
	
	for (int i = nbItem - 1; i >= 0 ; --i)
	{
		remove(i, false);
	}
	ListView_DeleteAllItems(_hSelf);

	HWND colHeader = reinterpret_cast<HWND>(SendMessage(_hSelf, LVM_GETHEADER, 0, 0));
	int columnCount = static_cast<int32_t>(SendMessage(colHeader, HDM_GETITEMCOUNT, 0, 0));

	for (int i = 0; i < columnCount; ++i)
	{
		ListView_DeleteColumn(_hSelf, 0);
	}
}

int VerticalFileSwitcherListView::find(BufferID bufferID, int iView) const
{
	LVITEM item{};
	bool found = false;
	int nbItem = ListView_GetItemCount(_hSelf);
	int i = 0;
	for (; i < nbItem ; ++i)
	{
		item.mask = LVIF_PARAM;
		item.iItem = i;
		ListView_GetItem(_hSelf, &item);
		const TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;
		if (tlfs->_bufID == bufferID && tlfs->_iView == iView)
		{
			found =  true;
			break;
		}
	}
	return (found?i:-1);	
}

void VerticalFileSwitcherListView::insertColumn(const wchar_t *name, int width, int index)
{
	LVCOLUMN lvColumn{};
 
	lvColumn.mask = LVCF_TEXT | LVCF_WIDTH;
	lvColumn.cx = width;
	lvColumn.pszText = (wchar_t *)name;
	ListView_InsertColumn(_hSelf, index, &lvColumn); // index is not 0 based but 1 based
}

void VerticalFileSwitcherListView::resizeColumns(int totalWidth)
{
	NppParameters& nppParams = NppParameters::getInstance();
	// Force display only filename and extension columns, ignore path column configuration
	bool isExtColumn = true;  // 总是Display extension列
	bool isCategoryColumn = true; // Always display category column

	const int extWidthDyn = nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherExtWidth);
	const int categoryWidthDyn = nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherCategoryWidth);
	int totalColWidthDynExceptName = 0;
	int colIndex = 0;

	if (isExtColumn)
	{
		totalColWidthDynExceptName += extWidthDyn;
		ListView_SetColumnWidth(_hSelf, ++colIndex, extWidthDyn);
	}
	if (isCategoryColumn)
	{
		totalColWidthDynExceptName += categoryWidthDyn;
		ListView_SetColumnWidth(_hSelf, ++colIndex, categoryWidthDyn);
	}

	const auto style = ::GetWindowLongPtr(_hSelf, GWL_STYLE);
	if ((style & WS_VSCROLL) == WS_VSCROLL)
	{
		totalColWidthDynExceptName += ::GetSystemMetrics(SM_CXVSCROLL);
	}

	// Calculate first column width, but limit maximum value to 300 pixels (considering DPI scaling)
	int nameWidth = totalWidth - totalColWidthDynExceptName;
	const int maxNameWidth = nppParams._dpiManager.scaleX(300);
	if (nameWidth > maxNameWidth)
		nameWidth = maxNameWidth;

	ListView_SetColumnWidth(_hSelf, 0, nameWidth);
}

std::vector<BufferViewInfo> VerticalFileSwitcherListView::getSelectedFiles(bool reverse) const
{
	std::vector<BufferViewInfo> files;
	LVITEM item{};
	int nbItem = ListView_GetItemCount(_hSelf);
	int i = 0;
	for (; i < nbItem ; ++i)
	{
		int isSelected = ListView_GetItemState(_hSelf, i, LVIS_SELECTED);
		bool isChosen = reverse?isSelected != LVIS_SELECTED:isSelected == LVIS_SELECTED;
		if (isChosen)
		{
			item.mask = LVIF_PARAM;
			item.iItem = i;
			ListView_GetItem(_hSelf, &item);

			TaskLstFnStatus *tlfs = (TaskLstFnStatus *)item.lParam;
			files.push_back(BufferViewInfo(static_cast<BufferID>(tlfs->_bufID), tlfs->_iView));
		}
	}

	return files;
}

// Update font
void VerticalFileSwitcherListView::updateFont()
{
	// Delete old font
	if (_hFont != nullptr) {
		DeleteObject(_hFont);
		_hFont = nullptr;
	}

	// Create new font
	LOGFONT lf = {};
	lf.lfHeight = -MulDiv(_fontSize, GetDeviceCaps(GetDC(_hSelf), LOGPIXELSY), 72);
	lf.lfWeight = FW_NORMAL;
	lf.lfCharSet = DEFAULT_CHARSET;
	lf.lfOutPrecision = OUT_DEFAULT_PRECIS;
	lf.lfClipPrecision = CLIP_DEFAULT_PRECIS;
	lf.lfQuality = DEFAULT_QUALITY;
	lf.lfPitchAndFamily = DEFAULT_PITCH | FF_DONTCARE;
	wcscpy_s(lf.lfFaceName, LF_FACESIZE, L"MS Sans Serif");

	_hFont = CreateFontIndirect(&lf);
	
	// Set new font
	if (_hFont != nullptr) {
		SendMessage(_hSelf, WM_SETFONT, reinterpret_cast<WPARAM>(_hFont), TRUE);
		redraw(true);
	}
}

// Initialize unified right-click menu
void VerticalFileSwitcherListView::initContextMenu(HMENU hGlobalMenu)
{
    debugLog(L"========== VerticalFileSwitcherListView::initContextMenu - 开始");
            
    // Destroy existing menu (if exists)
    if (_hContextMenu)
    {
        ::DestroyMenu(_hContextMenu);
        _hContextMenu = nullptr;
    }
    
    // Use global menu as base
    _hContextMenu = hGlobalMenu;
    
    // Add file-specific menu items (if menu is valid)
    if (_hContextMenu)
    {
        // 添加分隔符
        ::AppendMenu(_hContextMenu, MF_SEPARATOR, 0, NULL);
        
        // 添加Tab Color子菜单
        HMENU hTabColorMenu = ::CreatePopupMenu();
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 0, L"Red Tab");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 1, L"Green Tab");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 2, L"Blue Tab");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 3, L"Yellow Tab");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 4, L"Purple Tab");
        
        // 添加Tab Color菜单项
        ::AppendMenu(_hContextMenu, MF_STRING | MF_POPUP, (UINT_PTR)hTabColorMenu, L"Tab Color");
        
        // Add Category选择子菜单（仅在File List Right-Click Menu中显示）
        HMENU hCategoryMenu = ::CreatePopupMenu();
        if (_categoryManager)
        {
            const auto& categories = _categoryManager->getCategories();
            
            debugLog(L"VerticalFileSwitcherListView::initContextMenu - 开始Add Category，Category Count: %d", categories.size());
            
            // 添加所有分类到菜单
            for (size_t i = 0; i < categories.size(); ++i)
            {
                UINT menuId = CATEGORY_MENU_START + static_cast<UINT>(i);
                BOOL result = ::AppendMenu(hCategoryMenu, MF_STRING, menuId, categories[i].name.c_str());
                if (result)
                {
                    debugLog(L"VerticalFileSwitcherListView::initContextMenu - 成功Add Category菜单项: %s (ID: %d)", 
                        categories[i].name.c_str(), menuId);
                }
                else
                {
                    DWORD error = ::GetLastError();
                    debugLog(L"VerticalFileSwitcherListView::initContextMenu - Add Category菜单项失败: %s (ID: %d)，错误码: %d", 
                        categories[i].name.c_str(), menuId, error);
                }
            }
        }
        else
        {
            debugLog(L"VerticalFileSwitcherListView::initContextMenu - _categoryManager为nullptr");
        }
        
        // 添加Document Category菜单项（仅在File List Right-Click Menu中显示）
        BOOL menuResult = ::AppendMenu(_hContextMenu, MF_STRING | MF_POPUP, (UINT_PTR)hCategoryMenu, L"Document Category");
        if (menuResult)
        {
            debugLog(L"VerticalFileSwitcherListView::initContextMenu - 成功添加Document Category子菜单");
        }
        else
        {
            DWORD error = ::GetLastError();
            debugLog(L"VerticalFileSwitcherListView::initContextMenu - 添加Document Category子菜单失败，错误码: %d", error);
        }
        
        ::AppendMenu(_hContextMenu, MF_SEPARATOR, 0, NULL);
        ::AppendMenu(_hContextMenu, MF_STRING, 1001, L"Open File Location");
        ::AppendMenu(_hContextMenu, MF_STRING, 1002, L"Copy File Path");
        ::AppendMenu(_hContextMenu, MF_SEPARATOR, 0, NULL);
        ::AppendMenu(_hContextMenu, MF_STRING, IDM_EDIT_CATEGORY_JSON, L"Edit File Category JSON File");
    }
}

// Show unified right-click menu
void VerticalFileSwitcherListView::showContextMenu(int x, int y)
{
    // Show right-click menu
    if (_hContextMenu)
    {
        ::TrackPopupMenu(_hContextMenu, 
            NppParameters::getInstance().getNativeLangSpeaker()->isRTL() ? TPM_RIGHTALIGN | TPM_LAYOUTRTL : TPM_LEFTALIGN,
            x, y, 0, _hParent, NULL);
        
        debugLog(L"VerticalFileSwitcherListView::showContextMenu - Unified right-click menu displayed");
    }
}

// 获取文件Category Name（带自动分类逻辑）
std::wstring VerticalFileSwitcherListView::getFileCategoryName(const std::wstring& filePath)
{
	std::wstring fileCategoryName;
	
	if (_categoryManager)
	{
		// Get file category ID
		std::wstring categoryId = _categoryManager->getFileCategory(filePath);
		
		// Check if auto-categorization is needed (.js or .py files without category)
		if (categoryId == _categoryManager->getDefaultCategoryId())
		{
			// Get file extension
			std::wstring ext = ::PathFindExtension(filePath.c_str());
			// Convert to lowercase for comparison
			std::wstring extLower = ext;
			std::transform(extLower.begin(), extLower.end(), extLower.begin(), ::towlower);
			
			// 如果是.js或.py文件，自动分类到"Programming"
			if (extLower == L".js" || extLower == L".py")
			{
				// 查找"Programming"分类
				FileCategory* programmingCategory = _categoryManager->getCategoryByName(L"Programming");
				if (programmingCategory)
				{
					// Auto-set category
					_categoryManager->addFileToCategory(filePath, L"Programming");
					fileCategoryName = L"Programming";
					debugLog(L"VerticalFileSwitcherListView::getFileCategoryName - Auto-categorize file %s 到Programming分类", filePath.c_str());
					return fileCategoryName;
				}
			}
		}
		
		// Get category name by category ID
		FileCategory* category = _categoryManager->getCategoryById(categoryId);
		if (category)
		{
			fileCategoryName = category->name;
		}
		else
		{
			fileCategoryName = _categoryManager->getDefaultCategoryName();
		}
	}
	else
	{
		fileCategoryName = L"Uncategorized";
	}
	
	return fileCategoryName;
}

// Handle file category change
void VerticalFileSwitcherListView::onFileCategoryChange(const std::wstring& categoryName)
{
    // Get selected files
    std::vector<BufferViewInfo> selectedFiles = getSelectedFiles();
    if (selectedFiles.empty() || !_categoryManager)
        return;
    
    // OKCategory Column Index
    bool isExtColumn = true;  // 总是Display extension列
    int categoryColIndex = 1; // 默认第二列
    if (isExtColumn)
        categoryColIndex = 2; // 如果有扩展名列，分类列是第三列
    
    // Set category and update display for each selected file
    for (const auto& fileInfo : selectedFiles)
    {
        // Get file path
        Buffer* buffer = MainFileManager.getBufferByID(fileInfo._bufID);
        if (buffer)
        {
            std::wstring filePath = buffer->getFullPathName();
            
            // Set file category
            if (categoryName == L"All")
            {
                // Clear category
                _categoryManager->removeFileFromCategory(filePath);
            }
            else
            {
                // Set category
                _categoryManager->addFileToCategory(filePath, categoryName);
            }
            
            // Update category column display for that file in the list
            int nbItem = ListView_GetItemCount(_hSelf);
            for (int i = 0; i < nbItem; ++i)
            {
                LVITEM item{};
                item.mask = LVIF_PARAM;
                item.iItem = i;
                ListView_GetItem(_hSelf, &item);
                TaskLstFnStatus* tlfs = reinterpret_cast<TaskLstFnStatus*>(item.lParam);
                if (tlfs && tlfs->_bufID == fileInfo._bufID)
                {
                    // Update category column display
                    std::wstring displayCategoryName = categoryName;
                    if (categoryName == L"All")
                    {
                        // 如果Clear category，显示Default Category名称
                        displayCategoryName = _categoryManager->getDefaultCategoryName();
                    }
                    ListView_SetItemText(_hSelf, i, categoryColIndex, const_cast<LPWSTR>(displayCategoryName.c_str()));
                    debugLog(L"VerticalFileSwitcherListView::onFileCategoryChange - 更新文件 %s 的分类列为: %s", 
                        filePath.c_str(), displayCategoryName.c_str());
                    break;
                }
            }
        }
    }
    
    // Refresh display
    redrawItems();
    
    debugLog(L"VerticalFileSwitcherListView::onFileCategoryChange - 已为%d个文件Set category: %s", 
        selectedFiles.size(), categoryName.c_str());
}

// 处理Tab Color变更
void VerticalFileSwitcherListView::onTabColorChange(int colorIndex)
{
    // Get selected files
    std::vector<BufferViewInfo> selectedFiles = getSelectedFiles();
    if (selectedFiles.empty())
        return;
    
    // 为每个选中的文件设置Tab Color
    for (const auto& fileInfo : selectedFiles)
    {
        // Get file path
        Buffer* buffer = MainFileManager.getBufferByID(fileInfo._bufID);
        if (buffer)
        {
            // 设置Tab Color
            setItemColor(fileInfo._bufID, colorIndex);
        }
    }
    
    // Refresh display
    redrawItems();
    
    debugLog(L"VerticalFileSwitcherListView::onTabColorChange - 已为%d个文件设置Tab Color: %d", 
        selectedFiles.size(), colorIndex);
}
