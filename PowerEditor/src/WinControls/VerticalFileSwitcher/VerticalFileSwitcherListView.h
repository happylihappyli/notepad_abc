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


#pragma once

#include "Window.h"
#include "TaskListDlg.h"
#include "Buffer.h"
#include "CategoryManager.h"

#define SORT_DIRECTION_NONE     -1
#define SORT_DIRECTION_UP     0
#define SORT_DIRECTION_DOWN   1

#define FS_ROOTNODE				"DocList"
#define FS_CLMNNAME				"ColumnName"
#define FS_CLMNEXT				"ColumnExt"
#define FS_CLMNPATH				"ColumnPath"
#define FS_LVGROUPS				"ListGroups"
#define FS_FONTSIZE				"FontSize"
#define FS_SETTINGS				"Settings"


class VerticalFileSwitcherListView : public Window
{
public:
	VerticalFileSwitcherListView() = default;
	virtual ~VerticalFileSwitcherListView() = default;

	virtual void init(HINSTANCE hInst, HWND parent, HIMAGELIST hImaLst);
	virtual void destroy();
	void initList();
	BufferID getBufferInfoFromIndex(int index, int & view) const;
	void setBgColour(int i) {
		ListView_SetItemState(_hSelf, i, LVIS_SELECTED|LVIS_FOCUSED, 0xFF);
	}
	int newItem(BufferID bufferID, int iView);
	int closeItem(BufferID bufferID, int iView);
	void activateItem(BufferID bufferID, int iView);
	void setItemIconStatus(BufferID bufferID);
	std::wstring getFullFilePath(size_t i) const;
	void setItemColor(BufferID bufferID, int colorIndex = -1);
	
	void insertColumn(const wchar_t *name, int width, int index);
	void resizeColumns(int totalWidth);
	void deleteColumn(size_t i) {
		ListView_DeleteColumn(_hSelf, i);
	};
	int nbSelectedFiles() const {
		return static_cast<int32_t>(SendMessage(_hSelf, LVM_GETSELECTEDCOUNT, 0, 0));
	};

	std::vector<BufferViewInfo> getSelectedFiles(bool reverse = false) const;
	void reload();
	void redrawItems();
	void ensureVisibleCurrentItem() const {
		// 添加调试信息
		debugLog(L"测试 VerticalFileSwitcherListView::ensureVisibleCurrentItem() called with _currentIndex=%d\n", _currentIndex);
		ListView_EnsureVisible(_hSelf, _currentIndex, false);
		// 添加调试信息
		debugLog(L"VerticalFileSwitcherListView::ensureVisibleCurrentItem() finished\n");
	};

	void setBackgroundColor(COLORREF bgColour) {
		ListView_SetBkColor(_hSelf, bgColour);
		ListView_SetTextBkColor(_hSelf, bgColour);
		redraw(true);
    };

	void setForegroundColor(COLORREF fgColour) {
		ListView_SetTextColor(_hSelf, fgColour);
		redraw(true);
    };

	// 设置字体大小
	void setFontSize(int fontSize) {
		_fontSize = fontSize;
		updateFont();
	};

	// 获取当前字体大小
	int getFontSize() const { return _fontSize; };

	// 更新字体
	void updateFont();

	// 分类过滤相关方法
	void setCategoryManager(CategoryManager* categoryManager) { _categoryManager = categoryManager; }
	void setCurrentCategory(const std::wstring& categoryName) { _currentCategory = categoryName; reload(); }
	const std::wstring& getCurrentCategory() const { return _currentCategory; }
	void clearCategoryFilter() { _currentCategory.clear(); reload(); }
	void refreshDisplay() { redrawItems(); } // 只刷新显示，不重新加载数据
	
	// 右键菜单相关方法
	void initContextMenu(HMENU hGlobalMenu);  // 修改：使用全局菜单初始化
	void showContextMenu(int x, int y);       // 修改：统一的右键菜单显示方法
	void onFileCategoryChange(const std::wstring& categoryName);
	void onTabColorChange(int colorIndex);

	// 添加设置Notepad++主窗口句柄的方法
	void setNppMainWnd(HWND nppMainWnd) { _nppMainWnd = nppMainWnd; }

protected:
	HIMAGELIST _hImaLst = nullptr;
	HFONT _hFont = nullptr; // 字体句柄
	int _fontSize = 8; // 字体大小
	CategoryManager* _categoryManager = nullptr; // 分类管理器指针
	std::wstring _currentCategory; // 当前选中的分类
	HMENU _hContextMenu = nullptr; // 统一的右键菜单句柄
	HWND _nppMainWnd = nullptr; // Notepad++主窗口句柄

public:
	// 直接设置窗口句柄，不创建新窗口
	void setHSelf(HWND hWnd) { _hSelf = hWnd; }
	// 设置图像列表
	void setHImageList(HIMAGELIST hImaLst) { _hImaLst = hImaLst; ListView_SetImageList(_hSelf, _hImaLst, LVSIL_SMALL); }

	int _currentIndex = 0;

	static const int _groupID = 1;
	static const int _group2ID = 2;

	int find(BufferID bufferID, int iView) const;
	int add(BufferID bufferID, int iView);
	void remove(int index, bool removeFromListview = true);
	void removeAll();
	void selectCurrentItem() const {
		ListView_SetItemState(_hSelf, _currentIndex, LVIS_SELECTED | LVIS_FOCUSED, LVIS_SELECTED | LVIS_FOCUSED);
	};
};