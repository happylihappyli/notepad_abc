#include <shlwapi.h>
#include <stdexcept>
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

	// 注意：这里不再创建新的ListView控件，而是使用对话框模板中已经存在的控件
	// 实际的ListView控件创建和关联在VerticalFileSwitcher的WM_CREATE消息处理中完成

	// 初始化分组信息
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

	// 注意：这里不插入分组，因为_hSelf可能还没有设置
	// 分组插入将在initList方法中完成
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
	// 检查_hSelf是否有效
	if (!_hSelf || !::IsWindow(_hSelf)) {
		debugLog(L"VerticalFileSwitcherListView::initList() - 错误：ListView控件句柄无效！");
		return;
	}

	NppParameters& nppParams = NppParameters::getInstance();
	NativeLangSpeaker *pNativeSpeaker = nppParams.getNativeLangSpeaker();
	
	const bool isListViewGroups = !nppParams.getNppGUI()._fileSwitcherDisableListViewGroups;
	ListView_EnableGroupView(_hSelf, isListViewGroups ? TRUE : FALSE);
	
	// 设置列表视图的扩展样式
	ListView_SetExtendedListViewStyle(_hSelf, LVS_EX_FULLROWSELECT | LVS_EX_BORDERSELECT | LVS_EX_INFOTIP | LVS_EX_DOUBLEBUFFER);
	ListView_SetItemCountEx(_hSelf, 50, LVSICF_NOSCROLL);
	
	// 插入分组信息
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

	// 强制只显示文件名、分类和扩展名三列，忽略路径列配置
	bool isExtColumn = true;  // 总是显示扩展名列
	bool isPathColumn = false; // 从不显示路径列

	RECT rc{};
	::GetClientRect(_hParent, &rc);
	int totalWidth = rc.right - rc.left;
	int nameWidth = totalWidth / 2; // 文件名列宽度
	int categoryWidth = totalWidth / 4; // 分类列宽度
	int extWidth = totalWidth / 4; // 扩展名列宽度

	//add columns
	wstring nameStr = pNativeSpeaker->getAttrNameStr(L"Name", FS_ROOTNODE, FS_CLMNNAME);
	insertColumn(nameStr.c_str(), nameWidth, 1); // 第1列：文件名
	
	wstring categoryStr = pNativeSpeaker->getAttrNameStr(L"Category", FS_ROOTNODE, FS_CLMNNAME);
	insertColumn(categoryStr.c_str(), categoryWidth, 2); // 第2列：分类
	
	if (isExtColumn)
	{
		wstring extStr = pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT);
		insertColumn(extStr.c_str(), extWidth, 3); // 第3列：扩展名
	}

	TaskListInfo taskListInfo;
	// 使用我们设置的Notepad++主窗口句柄，而不是通过GetParent获取
	HWND nppHwnd = _nppMainWnd;
	
	// 添加详细的调试日志：检查窗口句柄和层级关系
	debugLog(L"VerticalFileSwitcherListView::initList() - 开始获取文档列表信息");
	debugLog(L"当前窗口句柄: %p", _hSelf);
	debugLog(L"父窗口句柄: %p", _hParent);
	debugLog(L"Notepad++主窗口句柄: %p", nppHwnd);
	debugLog(L"WM_GETTASKLISTINFO消息值: %d", WM_GETTASKLISTINFO);
	
	// 检查窗口是否有效
	if (!::IsWindow(nppHwnd)) {
		debugLog(L"VerticalFileSwitcherListView::initList() - 错误：Notepad++主窗口句柄无效！");
		// 尝试直接获取顶级窗口
		nppHwnd = ::GetAncestor(_hParent, GA_ROOT);
		debugLog(L"VerticalFileSwitcherListView::initList() - 尝试使用顶级窗口句柄: %p", nppHwnd);
	}
	
	LRESULT result = ::SendMessage(nppHwnd, WM_GETTASKLISTINFO, reinterpret_cast<WPARAM>(&taskListInfo), 0);
	
	// 添加详细的调试日志：检查消息发送结果和获取的文档数量
	debugLog(L"VerticalFileSwitcherListView::initList() - WM_GETTASKLISTINFO消息发送结果: %d", result);
	debugLog(L"获取的文档数量: %zu", taskListInfo._tlfsLst.size());
	debugLog(L"当前索引: %d", taskListInfo._currentIndex);
	debugLog(L"TaskListInfo地址: %p", &taskListInfo);
	
	// 如果获取的文档列表为空，直接返回，不添加示例数据
	if (taskListInfo._tlfsLst.empty()) {
		debugLog(L"VerticalFileSwitcherListView::initList() - 文档列表为空，跳过加载");
		removeAll(); // 清空列表
		return;
	}

	int itemIndex = 0;
	for (size_t i = 0, len = taskListInfo._tlfsLst.size(); i < len ; ++i)
	{
		TaskLstFnStatus & fileNameStatus = taskListInfo._tlfsLst[i];
		
		// 分类过滤：如果设置了当前分类，检查文件是否属于该分类
		if (!_currentCategory.empty() && _categoryManager)
		{
			std::wstring filePath = fileNameStatus._fn;
			
			// 如果当前分类是"全部"或"默认分类"，显示所有文件
			if (_currentCategory == L"全部" || _currentCategory == L"默认分类")
			{
				// 不跳过任何文件，显示全部
				debugLog(L"VerticalFileSwitcherListView::initList - 显示全部文件: %s, 当前分类: %s", 
					filePath.c_str(), _currentCategory.c_str());
			}
			else
			{
				std::wstring fileCategoryId = _categoryManager->getFileCategory(filePath);
				
				// 根据分类ID获取分类名称
				FileCategory* fileCategory = _categoryManager->getCategoryById(fileCategoryId);
				std::wstring fileCategoryName = fileCategory ? fileCategory->name : _categoryManager->getDefaultCategoryName();
				
				// 获取当前选中分类的ID
				FileCategory* currentCategory = _categoryManager->getCategoryByName(_currentCategory);
				std::wstring currentCategoryId = currentCategory ? currentCategory->id : _categoryManager->getDefaultCategoryId();
				
				// 如果文件分类ID与当前选中的分类ID不匹配，跳过该文件
				if (fileCategoryId != currentCategoryId)
				{
					// 调试信息：显示过滤的文件
					debugLog(L"VerticalFileSwitcherListView::initList - 过滤文件: %s, 文件分类ID: %s, 当前分类ID: %s, 分类名称: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
					continue;
				}
				else
				{
					// 调试信息：显示保留的文件
					debugLog(L"VerticalFileSwitcherListView::initList - 保留文件: %s, 文件分类ID: %s, 当前分类ID: %s, 分类名称: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
				}
			}
		}
		else
		{
			// 调试信息：分类过滤未启用，显示所有文件
			debugLog(L"VerticalFileSwitcherListView::initList - 分类过滤未启用，显示所有文件: _currentCategory=%s, _categoryManager=%p", 
				_currentCategory.c_str(), _categoryManager);
		}

		TaskLstFnStatus *tl = new TaskLstFnStatus(fileNameStatus);

		wchar_t fn[MAX_PATH] = { '\0' };
		wcscpy_s(fn, ::PathFindFileName(fileNameStatus._fn.c_str()));

		if (isExtColumn)
		{
			::PathRemoveExtension(fn);
		}
		LVITEM item{};
		item.mask = LVIF_TEXT | LVIF_IMAGE | LVIF_PARAM | LVIF_GROUPID;
		
		item.pszText = fn;
		item.iItem = itemIndex;
		item.iSubItem = 0;
		item.iImage = fileNameStatus._status;
		item.lParam = reinterpret_cast<LPARAM>(tl);
		item.iGroupId = (fileNameStatus._iView == MAIN_VIEW) ? _groupID : _group2ID;
		ListView_InsertItem(_hSelf, &item);
		
		// 设置分类列数据
		int colIndex = 0;
		// 第1列：文件名（已设置）
		
		// 第2列：分类
		std::wstring filePath = fileNameStatus._fn;
		std::wstring fileCategoryId = _categoryManager ? _categoryManager->getFileCategory(filePath) : L"default";
		FileCategory* fileCategory = _categoryManager ? _categoryManager->getCategoryById(fileCategoryId) : nullptr;
		std::wstring fileCategoryName = fileCategory ? fileCategory->name : (_categoryManager ? _categoryManager->getDefaultCategoryName() : L"默认分类");
		wchar_t categoryText[MAX_PATH] = { '\0' };
		wcscpy_s(categoryText, fileCategoryName.c_str());
		ListView_SetItemText(_hSelf, itemIndex, ++colIndex, categoryText);
		
		// 第3列：扩展名
		if (isExtColumn)
		{
			wchar_t extText[MAX_PATH] = { '\0' };
			wcscpy_s(extText, ::PathFindExtension(fileNameStatus._fn.c_str()));
			ListView_SetItemText(_hSelf, itemIndex, ++colIndex, extText);
		}
		
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
	
	// 检查_hSelf是否有效
	if (!_hSelf || !::IsWindow(_hSelf)) {
		debugLog(L"VerticalFileSwitcherListView::reload() - 错误：ListView控件句柄无效！");
		::SendMessage(_hParent, WM_SETREDRAW, true, 0);
		return;
	}

	// 清除现有的列表项和列
	removeAll();
	
	// 强制刷新界面，确保清除操作生效
	::InvalidateRect(_hSelf, NULL, TRUE);
	::UpdateWindow(_hSelf);

	NppParameters& nppParams = NppParameters::getInstance();
	NativeLangSpeaker *pNativeSpeaker = nppParams.getNativeLangSpeaker();
	
	const bool isListViewGroups = !nppParams.getNppGUI()._fileSwitcherDisableListViewGroups;
	ListView_EnableGroupView(_hSelf, isListViewGroups ? TRUE : FALSE);
	
	// 设置列表视图的扩展样式
	ListView_SetExtendedListViewStyle(_hSelf, LVS_EX_FULLROWSELECT | LVS_EX_BORDERSELECT | LVS_EX_INFOTIP | LVS_EX_DOUBLEBUFFER);
	ListView_SetItemCountEx(_hSelf, 50, LVSICF_NOSCROLL);
	
	// 插入分组信息
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

	// 强制只显示文件名、分类和扩展名三列，忽略路径列配置
	bool isExtColumn = true;  // 总是显示扩展名列
	bool isPathColumn = false; // 从不显示路径列

	RECT rc{};
	::GetClientRect(_hParent, &rc);
	int totalWidth = rc.right - rc.left;
	int nameWidth = totalWidth / 2; // 文件名列宽度
	int categoryWidth = totalWidth / 4; // 分类列宽度
	int extWidth = totalWidth / 4; // 扩展名列宽度

	//add columns
	wstring nameStr = pNativeSpeaker->getAttrNameStr(L"Name", FS_ROOTNODE, FS_CLMNNAME);
	insertColumn(nameStr.c_str(), nameWidth, 1); // 第1列：文件名
	
	wstring categoryStr = pNativeSpeaker->getAttrNameStr(L"Category", FS_ROOTNODE, FS_CLMNNAME);
	insertColumn(categoryStr.c_str(), categoryWidth, 2); // 第2列：分类
	
	if (isExtColumn)
	{
		wstring extStr = pNativeSpeaker->getAttrNameStr(L"Ext.", FS_ROOTNODE, FS_CLMNEXT);
		insertColumn(extStr.c_str(), extWidth, 3); // 第3列：扩展名
	}

	TaskListInfo taskListInfo;
	// 使用我们设置的Notepad++主窗口句柄，而不是通过GetParent获取
	HWND nppHwnd = _nppMainWnd;
	
	// 检查窗口是否有效
	if (!::IsWindow(nppHwnd)) {
		debugLog(L"VerticalFileSwitcherListView::reload() - 错误：Notepad++主窗口句柄无效！");
		nppHwnd = ::GetAncestor(_hParent, GA_ROOT);
	}
	
	LRESULT result = ::SendMessage(nppHwnd, WM_GETTASKLISTINFO, reinterpret_cast<WPARAM>(&taskListInfo), 0);
	
	// 如果获取的文档列表为空，清空文件列表
	if (taskListInfo._tlfsLst.empty()) {
		debugLog(L"VerticalFileSwitcherListView::reload() - 文档列表为空，清空文件列表");
		removeAll(); // 清空文件列表
		::SendMessage(_hParent, WM_SETREDRAW, true, 0);
		::InvalidateRect(_hSelf, NULL, TRUE);
		::UpdateWindow(_hSelf);
		return;
	}

	int itemIndex = 0;
	for (size_t i = 0, len = taskListInfo._tlfsLst.size(); i < len ; ++i)
	{
		TaskLstFnStatus & fileNameStatus = taskListInfo._tlfsLst[i];
		
		// 分类过滤：如果设置了当前分类，检查文件是否属于该分类
		if (!_currentCategory.empty() && _categoryManager)
		{
			std::wstring filePath = fileNameStatus._fn;
			
			// 如果当前分类是"全部"或"默认分类"，显示所有文件
			if (_currentCategory == L"全部" || _currentCategory == L"默认分类")
			{
				// 不跳过任何文件，显示全部
				debugLog(L"VerticalFileSwitcherListView::reload - 显示全部文件: %s, 当前分类: %s", 
					filePath.c_str(), _currentCategory.c_str());
			}
			else
			{
				std::wstring fileCategoryId = _categoryManager->getFileCategory(filePath);
				
				// 根据分类ID获取分类名称
				FileCategory* fileCategory = _categoryManager->getCategoryById(fileCategoryId);
				std::wstring fileCategoryName = fileCategory ? fileCategory->name : _categoryManager->getDefaultCategoryName();
				
				// 获取当前选中分类的ID
				FileCategory* currentCategory = _categoryManager->getCategoryByName(_currentCategory);
				std::wstring currentCategoryId = currentCategory ? currentCategory->id : _categoryManager->getDefaultCategoryId();
				
				// 如果文件分类ID与当前选中的分类ID不匹配，跳过该文件
				if (fileCategoryId != currentCategoryId)
				{
					// 调试信息：显示过滤的文件
					debugLog(L"VerticalFileSwitcherListView::reload - 过滤文件: %s, 文件分类ID: %s, 当前分类ID: %s, 分类名称: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
					continue;
				}
				else
				{
					// 调试信息：显示保留的文件
					debugLog(L"VerticalFileSwitcherListView::reload - 保留文件: %s, 文件分类ID: %s, 当前分类ID: %s, 分类名称: %s", 
						filePath.c_str(), fileCategoryId.c_str(), currentCategoryId.c_str(), fileCategoryName.c_str());
				}
			}
		}
		else
		{
			// 调试信息：分类过滤未启用，显示所有文件
			debugLog(L"VerticalFileSwitcherListView::reload - 分类过滤未启用，显示所有文件: _currentCategory=%s, _categoryManager=%p", 
				_currentCategory.c_str(), _categoryManager);
		}

		TaskLstFnStatus *tl = new TaskLstFnStatus(fileNameStatus);

		wchar_t fn[MAX_PATH] = { '\0' };
		wcscpy_s(fn, ::PathFindFileName(fileNameStatus._fn.c_str()));

		if (isExtColumn)
		{
			::PathRemoveExtension(fn);
		}
		LVITEM item{};
		item.mask = LVIF_TEXT | LVIF_IMAGE | LVIF_PARAM | LVIF_GROUPID;
		
		item.pszText = fn;
		item.iItem = itemIndex;
		item.iSubItem = 0;
		item.iImage = fileNameStatus._status;
		item.lParam = reinterpret_cast<LPARAM>(tl);
		item.iGroupId = (fileNameStatus._iView == MAIN_VIEW) ? _groupID : _group2ID;
		ListView_InsertItem(_hSelf, &item);
		
		// 设置分类列数据
		int colIndex = 0;
		// 第1列：文件名（已设置）
		
		// 第2列：分类
		std::wstring filePath = fileNameStatus._fn;
		std::wstring fileCategoryId = _categoryManager ? _categoryManager->getFileCategory(filePath) : L"default";
		FileCategory* fileCategory = _categoryManager ? _categoryManager->getCategoryById(fileCategoryId) : nullptr;
		std::wstring fileCategoryName = fileCategory ? fileCategory->name : (_categoryManager ? _categoryManager->getDefaultCategoryName() : L"默认分类");
		wchar_t categoryText[MAX_PATH] = { '\0' };
		wcscpy_s(categoryText, fileCategoryName.c_str());
		ListView_SetItemText(_hSelf, itemIndex, ++colIndex, categoryText);
		
		// 第3列：扩展名
		if (isExtColumn)
		{
			wchar_t extText[MAX_PATH] = { '\0' };
			wcscpy_s(extText, ::PathFindExtension(fileNameStatus._fn.c_str()));
			ListView_SetItemText(_hSelf, itemIndex, ++colIndex, extText);
		}
		
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
	
	// 生成示例文档名称
	wchar_t exampleName[MAX_PATH] = { '\0' };
	int fileIndex = find(bufferID, MAIN_VIEW); // 查找文件在列表中的位置
	if (fileIndex == -1) fileIndex = find(bufferID, SUB_VIEW);
	if (fileIndex == -1) fileIndex = 0;
	
	swprintf_s(exampleName, MAX_PATH, L"示例文档%d", fileIndex + 1);
	
	bool isExtColumn = !(NppParameters::getInstance()).getNppGUI()._fileSwitcherWithoutExtColumn;
	bool isPathColumn = !(NppParameters::getInstance()).getNppGUI()._fileSwitcherWithoutPathColumn;
	if (isExtColumn)
	{
		// 对于示例文档，不需要移除扩展名
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
			
			// 点击文件名时不要更新显示文本，保持原文件名不变
			// 使用原始文件名，不显示完整路径
			wchar_t fileNameOnly[MAX_PATH] = { '\0' };
			const wchar_t* fileName = PathFindFileName(tlfs->_fn.c_str());
			if (fileName) {
				wcscpy_s(fileNameOnly, MAX_PATH, fileName);
				// 移除文件扩展名，只显示文件名主体
				::PathRemoveExtension(fileNameOnly);
			}
			item.pszText = fileNameOnly;
			
			ListView_SetItem(_hSelf, &item);
			int colIndex = 0;
			// 更新分类列（第2列）
			if (_categoryManager)
			{
				std::wstring fileCategoryId = _categoryManager->getFileCategory(tlfs->_fn);
				FileCategory* fileCategory = _categoryManager->getCategoryById(fileCategoryId);
				std::wstring fileCategoryName = fileCategory ? fileCategory->name : _categoryManager->getDefaultCategoryName();
				wchar_t categoryText[MAX_PATH] = { '\0' };
				wcscpy_s(categoryText, fileCategoryName.c_str());
				ListView_SetItemText(_hSelf, i, ++colIndex, categoryText);
			}
			else
			{
				// 如果没有分类管理器，显示默认文本
				wchar_t defaultCategory[] = L"默认分类";
				ListView_SetItemText(_hSelf, i, ++colIndex, defaultCategory);
			}
			
			// 更新扩展名列（第3列）
			if (isExtColumn)
			{
				// 显示文件扩展名
				wchar_t extText[MAX_PATH] = { '\0' };
				wcscpy_s(extText, ::PathFindExtension(tlfs->_fn.c_str()));
				ListView_SetItemText(_hSelf, i, ++colIndex, extText);
			}
			if (isPathColumn)
			{
				// 显示空路径（不显示路径）
				wchar_t emptyStr[] = L"";
				ListView_SetItemText(_hSelf, i, ++colIndex, emptyStr);
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
	bool isPathColumn = !nppGUI._fileSwitcherWithoutPathColumn;
	
	// 保持文件名原样不变，不进行任何处理
	// 直接使用原始文件名
	
	// 复制文件名并移除扩展名
	wchar_t fileNameOnly[MAX_PATH] = { '\0' };
	if (fileName) {
		wcscpy_s(fileNameOnly, MAX_PATH, fileName);
		::PathRemoveExtension(fileNameOnly);
	}
	
	LVITEM item{};
	item.mask = LVIF_TEXT | LVIF_IMAGE | LVIF_PARAM | LVIF_GROUPID;
	
	item.pszText = fileNameOnly;
	item.iItem = _currentIndex;
	item.iSubItem = 0;
	item.iImage = buf->isMonitoringOn()?3:(buf->isReadOnly()?2:(buf->isDirty()?1:0));
	item.lParam = reinterpret_cast<LPARAM>(tl);
	item.iGroupId = (iView == MAIN_VIEW) ? _groupID : _group2ID;
	ListView_InsertItem(_hSelf, &item);
	int colIndex = 0;
	
	// 第1列：分类（新增）
	if (_categoryManager)
	{
		std::wstring fileCategoryId = _categoryManager->getFileCategory(buf->getFullPathName());
		FileCategory* fileCategory = _categoryManager->getCategoryById(fileCategoryId);
		std::wstring fileCategoryName = fileCategory ? fileCategory->name : _categoryManager->getDefaultCategoryName();
		wchar_t categoryText[MAX_PATH] = { '\0' };
		wcscpy_s(categoryText, fileCategoryName.c_str());
		ListView_SetItemText(_hSelf, _currentIndex, ++colIndex, categoryText);
	}
	else
	{
		// 如果没有分类管理器，显示默认文本
		wchar_t defaultCategory[] = L"默认分类";
		ListView_SetItemText(_hSelf, _currentIndex, ++colIndex, defaultCategory);
	}
	
	if (isExtColumn)
	{
		// 显示文件扩展名
		wchar_t extText[MAX_PATH] = { '\0' };
		wcscpy_s(extText, ::PathFindExtension(buf->getFullPathName()));
		ListView_SetItemText(_hSelf, _currentIndex, ++colIndex, extText);
	}
	if (isPathColumn)
	{
		// 显示空路径（不显示路径）
		wchar_t emptyStr[] = L"";
		ListView_SetItemText(_hSelf, _currentIndex, ++colIndex, emptyStr);
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
	// 强制只显示文件名、分类和扩展名三列，忽略路径列配置
	bool isExtColumn = true;  // 总是显示扩展名列
	bool isPathColumn = false; // 从不显示路径列

	const int extWidthDyn = nppParams._dpiManager.scaleX(nppParams.getNppGUI()._fileSwitcherExtWidth);
	int totalColWidthDynExceptName = 0;
	int colIndex = 0;

	// 调整分类列宽度（第2列）
	int categoryWidth = totalWidth / 4; // 分类列宽度
	ListView_SetColumnWidth(_hSelf, ++colIndex, categoryWidth);
	totalColWidthDynExceptName += categoryWidth;

	// 调整扩展列宽度（第3列）
	if (isExtColumn)
	{
		totalColWidthDynExceptName += extWidthDyn;
		ListView_SetColumnWidth(_hSelf, ++colIndex, extWidthDyn);
	}
	// 注释掉路径列的宽度调整，确保只显示三列

	const auto style = ::GetWindowLongPtr(_hSelf, GWL_STYLE);
	if ((style & WS_VSCROLL) == WS_VSCROLL)
	{
		totalColWidthDynExceptName += ::GetSystemMetrics(SM_CXVSCROLL);
	}

	// 调整文件名列宽度（第1列）
	ListView_SetColumnWidth(_hSelf, 0, totalWidth - totalColWidthDynExceptName);
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

// 更新字体
void VerticalFileSwitcherListView::updateFont()
{
	// 删除旧的字体
	if (_hFont != nullptr) {
		DeleteObject(_hFont);
		_hFont = nullptr;
	}

	// 创建新字体
	LOGFONT lf = {};
	lf.lfHeight = -MulDiv(_fontSize, GetDeviceCaps(GetDC(_hSelf), LOGPIXELSY), 72);
	lf.lfWeight = FW_NORMAL;
	lf.lfCharSet = DEFAULT_CHARSET;
	lf.lfOutPrecision = OUT_DEFAULT_PRECIS;
	lf.lfClipPrecision = CLIP_DEFAULT_PRECIS;
	lf.lfQuality = DEFAULT_QUALITY;
	lf.lfPitchAndFamily = DEFAULT_PITCH | FF_DONTCARE;
	wcscpy_s(lf.lfFaceName, L"MS Sans Serif");

	_hFont = CreateFontIndirect(&lf);
	
	// 设置新字体
	if (_hFont != nullptr) {
		SendMessage(_hSelf, WM_SETFONT, reinterpret_cast<WPARAM>(_hFont), TRUE);
		redraw(true);
	}
}

// 初始化统一右键菜单
void VerticalFileSwitcherListView::initContextMenu(HMENU hGlobalMenu)
{
    // 销毁现有的菜单（如果存在）
    if (_hContextMenu)
    {
        ::DestroyMenu(_hContextMenu);
        _hContextMenu = nullptr;
    }
    
    // 使用全局菜单作为基础
    _hContextMenu = hGlobalMenu;
    
    // 添加文件特定的菜单项（如果菜单有效）
    if (_hContextMenu)
    {
        // 添加分隔符
        ::AppendMenu(_hContextMenu, MF_SEPARATOR, 0, NULL);
        
        // 添加标签颜色子菜单
        HMENU hTabColorMenu = ::CreatePopupMenu();
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 0, L"红色标签");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 1, L"绿色标签");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 2, L"蓝色标签");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 3, L"黄色标签");
        ::AppendMenu(hTabColorMenu, MF_STRING, TAB_COLOR_MENU_START + 4, L"紫色标签");
        
        // 添加标签颜色菜单项
        ::AppendMenu(_hContextMenu, MF_STRING | MF_POPUP, (UINT_PTR)hTabColorMenu, L"标签颜色");
        
        // 添加分类选择子菜单（仅在文件列表右键菜单中显示）
        HMENU hCategoryMenu = ::CreatePopupMenu();
        if (_categoryManager)
        {
            const auto& categories = _categoryManager->getCategories();
            
            // 添加所有分类到菜单
            for (size_t i = 0; i < categories.size(); ++i)
            {
                UINT menuId = CATEGORY_MENU_START + static_cast<UINT>(i);
                ::AppendMenu(hCategoryMenu, MF_STRING, menuId, categories[i].name.c_str());
            }
        }
        
        // 添加文档分类菜单项（仅在文件列表右键菜单中显示）
        ::AppendMenu(_hContextMenu, MF_STRING | MF_POPUP, (UINT_PTR)hCategoryMenu, L"文档分类");
        ::AppendMenu(_hContextMenu, MF_SEPARATOR, 0, NULL);
        ::AppendMenu(_hContextMenu, MF_STRING, 1001, L"打开文件所在目录");
        ::AppendMenu(_hContextMenu, MF_STRING, 1002, L"复制文件路径");
    }
}

// 显示统一右键菜单
void VerticalFileSwitcherListView::showContextMenu(int x, int y)
{
    // 显示右键菜单
    if (_hContextMenu)
    {
        ::TrackPopupMenu(_hContextMenu, 
            NppParameters::getInstance().getNativeLangSpeaker()->isRTL() ? TPM_RIGHTALIGN | TPM_LAYOUTRTL : TPM_LEFTALIGN,
            x, y, 0, _hParent, NULL);
        
        debugLog(L"VerticalFileSwitcherListView::showContextMenu - 统一右键菜单已显示");
    }
}

// 处理文件分类变更
void VerticalFileSwitcherListView::onFileCategoryChange(const std::wstring& categoryName)
{
    // 获取选中的文件
    std::vector<BufferViewInfo> selectedFiles = getSelectedFiles();
    if (selectedFiles.empty() || !_categoryManager)
        return;
    
    // 为每个选中的文件设置分类
    for (const auto& fileInfo : selectedFiles)
    {
        // 获取文件路径
        Buffer* buffer = MainFileManager.getBufferByID(fileInfo._bufID);
        if (buffer)
        {
            std::wstring filePath = buffer->getFullPathName();
            
            // 设置文件分类
            if (categoryName == L"全部")
            {
                // 清除分类
                _categoryManager->removeFileFromCategory(filePath);
            }
            else
            {
                // 设置分类
                _categoryManager->addFileToCategory(filePath, categoryName);
            }
            
            // 更新ListView中对应项的分类显示
            int itemIndex = find(fileInfo._bufID, fileInfo._iView);
            if (itemIndex != -1)
            {
                // 获取文件分类信息
                std::wstring fileCategoryId = _categoryManager->getFileCategory(filePath);
                FileCategory* fileCategory = _categoryManager->getCategoryById(fileCategoryId);
                std::wstring fileCategoryName = fileCategory ? fileCategory->name : _categoryManager->getDefaultCategoryName();
                
                // 更新ListView中第2列（分类列）的显示
                wchar_t categoryText[MAX_PATH] = { '\0' };
                wcscpy_s(categoryText, fileCategoryName.c_str());
                ListView_SetItemText(_hSelf, itemIndex, 1, categoryText); // 第2列索引为1
            }
        }
    }
    
    // 刷新显示
    redrawItems();
    
    debugLog(L"VerticalFileSwitcherListView::onFileCategoryChange - 已为%d个文件设置分类: %s", 
        selectedFiles.size(), categoryName.c_str());
}

// 处理标签颜色变更
void VerticalFileSwitcherListView::onTabColorChange(int colorIndex)
{
    // 获取选中的文件
    std::vector<BufferViewInfo> selectedFiles = getSelectedFiles();
    if (selectedFiles.empty())
        return;
    
    // 为每个选中的文件设置标签颜色
    for (const auto& fileInfo : selectedFiles)
    {
        // 获取文件路径
        Buffer* buffer = MainFileManager.getBufferByID(fileInfo._bufID);
        if (buffer)
        {
            // 设置标签颜色
            setItemColor(fileInfo._bufID, colorIndex);
        }
    }
    
    // 刷新显示
    redrawItems();
    
    debugLog(L"VerticalFileSwitcherListView::onTabColorChange - 已为%d个文件设置标签颜色: %d", 
        selectedFiles.size(), colorIndex);
}
