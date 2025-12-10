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

#include "../Window.h"
#include "../TaskList/TaskListDlg.h"
#include "../../ScintillaComponent/Buffer.h"
#include "CategoryManager.h"

#define SORT_DIRECTION_NONE     -1
#define SORT_DIRECTION_UP     0
#define SORT_DIRECTION_DOWN   1

#define FS_ROOTNODE				"DocList"
#define FS_CLMNNAME				"ColumnName"
#define FS_CLMNEXT				"ColumnExt"
#define FS_CLMNPATH				"ColumnPath"
#define FS_CLMNCATEGORY			"ColumnCategory"  // 新增：分类列配置
#define FS_LVGROUPS				"ListGroups"
#define FS_FONTSIZE				"FontSize"
#define FS_SETTINGS				"Settings"

// Column Index Constants
#define COLUMN_INDEX_NAME       0
#define COLUMN_INDEX_EXT        1  
#define COLUMN_INDEX_CATEGORY   2  // 新增：Category Column Index


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
		// Add Debug Information
		//debugLog(L"测试 VerticalFileSwitcherListView::ensureVisibleCurrentItem() called with _currentIndex=%d\n", _currentIndex);
		ListView_EnsureVisible(_hSelf, _currentIndex, false);
		// Add Debug Information
		//sdebugLog(L"VerticalFileSwitcherListView::ensureVisibleCurrentItem() finished\n");
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

	// Set Font Size
	void setFontSize(int fontSize) {
		_fontSize = fontSize;
		updateFont();
	};

	// 获取Current Font Size
	int getFontSize() const { return _fontSize; };

	// Update font
	void updateFont();

	// Category Filtering Related Methods
	void setCategoryManager(CategoryManager* categoryManager) { _categoryManager = categoryManager; }
	void setCurrentCategory(const std::wstring& categoryName) { _currentCategory = categoryName; reload(); }
	const std::wstring& getCurrentCategory() const { return _currentCategory; }
	void clearCategoryFilter() { _currentCategory.clear(); reload(); }
	void refreshDisplay() { redrawItems(); } // 只Refresh display，不重新加载数据
	
	// Right-Click Menu Related Methods
	void initContextMenu(HMENU hGlobalMenu);  // 修改：Initialize Using Global Menu
	void showContextMenu(int x, int y);       // 修改：Unified Right-Click Menu Display Method
	void onFileCategoryChange(const std::wstring& categoryName);
	void onTabColorChange(int colorIndex);

	// 获取文件Category Name（带自动分类逻辑）
	std::wstring getFileCategoryName(const std::wstring& filePath);
	
	// Add Method to Set Notepad++ Main Window Handle
	void setNppMainWnd(HWND nppMainWnd) { _nppMainWnd = nppMainWnd; }

protected:
	HIMAGELIST _hImaLst = nullptr;
	HFONT _hFont = nullptr; // Font Handle
	int _fontSize = 8; // 字体大小
	CategoryManager* _categoryManager = nullptr; // Category Manager Pointer
	std::wstring _currentCategory; // Currently Selected Category
	HMENU _hContextMenu = nullptr; // Unified Right-Click Menu Handle
	HWND _nppMainWnd = nullptr; // Notepad++ Main Window Handle

public:
	// Set Window Handle Directly, Do Not Create New Window
	void setHSelf(HWND hWnd) { _hSelf = hWnd; }
	// Set Image List
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