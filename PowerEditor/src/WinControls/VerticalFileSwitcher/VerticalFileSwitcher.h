// This file is part of Notepad++ project
// Copyright (C)2021 Don HO <don.h@free.fr>

// This program is free software, you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// at your option any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY, without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.


#pragma once

#include "DockingDlgInterface.h"
#include "VerticalFileSwitcher_rc.h"
#include "VerticalFileSwitcherListView.h"
#include "CategoryManager.h"

#define FS_PROJECTPANELTITLE		L"Document List"

struct sortCompareData {
  HWND hListView = nullptr;
  int columnIndex = 0;
  int sortDirection = 0;
};

LRESULT run_listViewProc(WNDPROC oldEditProc, HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam);

class VerticalFileSwitcher : public DockingDlgInterface {
public:
	VerticalFileSwitcher(): DockingDlgInterface(IDD_DOCLIST) {_fileListView.setCategoryManager(&_categoryManager);};

	void init(HINSTANCE hInst, HWND parent, HIMAGELIST hImaLst) {
		_hInst = hInst;
		_hParent = parent;  // 保存Notepad++主窗口句柄
		_hImaLst = hImaLst;
	};
	
	// 添加一个方法来获取Notepad++主窗口句柄
	HWND getNppMainWnd() const { return _hParent; }

	void create(tTbData* data, bool isRTL = false);
	void create(tTbData* data, std::array<int, 3> iconIDs, bool isRTL = false);
	void destroy() override {
		_fileListView.destroy();
	};

	void setBackgroundColor(COLORREF bgColour) {
		_fileListView.setBackgroundColor(bgColour);
	};
	void setForegroundColor(COLORREF fgColour) {
		_fileListView.setForegroundColor(fgColour);
	};

	void setFontSize(int fontSize) {
		_fileListView.setFontSize(fontSize);
	}

	void createCategoryButtons();
	void onCategoryButtonClick(HWND hButton);
	void updateCategoryButtonState(HWND selectedButton);

	int getFontSize() const {
		return _fileListView.getFontSize();
	}

	void closeItem(BufferID bufferID, int iView) {
		_fileListView.closeItem(bufferID, iView);
	}

	void setItemColor(BufferID bufferID, int colorIndex = -1) {
		_fileListView.setItemColor(bufferID, colorIndex);
	}

	void setItemIconStatus(BufferID bufferID) {
		_fileListView.setItemIconStatus(bufferID);
	}

	void activateItem(BufferID bufferID, int iView) {
		_fileListView.activateItem(bufferID, iView);
	}

	void reload() {
		_fileListView.reload();
		startColumnSort();
	}

	bool isVisible() const {
		return _fileListView.isVisible();
	}

	void updateTabOrder() {
		// 当tab顺序改变时，总是重新加载文件列表以反映新的tab顺序
		_fileListView.reload();
	}

	int nbSelectedFiles() const {
		return _fileListView.nbSelectedFiles();
	}

	void grabFocus() {
		_fileListView.grabFocus();
	}

	void newItem(Buffer *buf, int view) {
		_fileListView.newItem(buf, view);
	}

	std::vector<BufferViewInfo> getSelectedFiles(bool closeOthers = false) {
		return _fileListView.getSelectedFiles(closeOthers);
	}

	void startColumnSort();

	// 添加display方法的声明
	void display(bool toShow = true) const override;

	// 设置对话框相关方法
	void showSettingsDialog();

	// 分类管理器访问方法（用于对话框过程）
	CategoryManager* getCategoryManager() { return &_categoryManager; }
	const CategoryManager* getCategoryManager() const { return &_categoryManager; }

private:
	bool registerWindowClass(HINSTANCE hInst);

protected:
	static LRESULT CALLBACK wndProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
		// 处理WM_NCCREATE消息，这是创建窗口时收到的第一个消息
		if (message == WM_NCCREATE) {
			// 从创建参数中获取this指针
			LPCREATESTRUCT lpcs = reinterpret_cast<LPCREATESTRUCT>(lParam);
			void* lpThis = lpcs->lpCreateParams;
			
			// 将this指针存储在窗口的额外数据中（使用-21替代GWL_USERDATA）
			::SetWindowLongPtr(hwnd, -21, reinterpret_cast<LONG_PTR>(lpThis));
			
			// 将窗口句柄保存到对象中
			VerticalFileSwitcher* pThis = static_cast<VerticalFileSwitcher*>(lpThis);
			pThis->_hSelf = hwnd;
			
			return TRUE; // 允许创建窗口
		}
		
		// 使用-21替代GWL_USERDATA
		VerticalFileSwitcher* pThis = reinterpret_cast<VerticalFileSwitcher*>(::GetWindowLongPtr(hwnd, -21));
		if (pThis) {
			LRESULT result = pThis->run_dlgProc(message, wParam, lParam);
			// 如果消息被处理，返回结果；否则调用默认窗口过程
			if (result != 0 || message == WM_CREATE || message == WM_DESTROY) {
				return result;
			}
		}
		return ::DefWindowProc(hwnd, message, wParam, lParam);
	}

	void setParent(HWND parent2set){
		_hParent = parent2set;
	};
	
	//Activate document in scintilla by using the internal index
	void activateDoc(TaskLstFnStatus *tlfs) const;

	void closeDoc(TaskLstFnStatus *tlfs) const;

	// 内部方法，用于protected部分访问_fileListView
	int newItemInternal(BufferID bufferID, int iView) {
		return _fileListView.newItem(bufferID, iView);
	}

	int closeItemInternal(BufferID bufferID, int iView) {
		return _fileListView.closeItem(bufferID, iView);
	}

	void activateItemInternal(BufferID bufferID, int iView) {
		_fileListView.activateItem(bufferID, iView);
	}

	void setItemIconStatusInternal(BufferID bufferID) {
		_fileListView.setItemIconStatus(bufferID);
	}

	void setItemColorInternal(BufferID bufferID, int colorIndex = -1) {
		_fileListView.setItemColor(bufferID, colorIndex);
	}

	std::wstring getFullFilePathInternal(size_t i) const {
		return _fileListView.getFullFilePath(i);
	}

	int setHeaderOrder(int columnIndex);
	void updateHeaderArrow();

	intptr_t CALLBACK run_dlgProc(UINT message, WPARAM wParam, LPARAM lParam);

	void initPopupMenus();
	void initFileListContextMenu();  // 新增：初始化文件列表右键菜单
	void popupMenuCmd(int cmdID);

	static LRESULT CALLBACK listViewStaticProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
		// 使用-21替代GWLP_USERDATA
		const auto dlg = (VerticalFileSwitcher*)(::GetWindowLongPtr(hwnd, -21));
		return (run_listViewProc(dlg->_defaultListViewProc, hwnd, message, wParam, lParam));
	};

private:
	static LRESULT listViewNotifyCustomDraw(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
	static LRESULT CALLBACK FileSwitcherNotifySubclass(HWND hWnd, UINT uMsg, WPARAM wParam, LPARAM lParam, UINT_PTR uIdSubclass, DWORD_PTR dwRefData);
	void autoSubclassWindowNotify(HWND hParent);

	bool colHeaderRClick = false;
	int _lastSortingColumn = 0;
	int _lastSortingDirection = SORT_DIRECTION_NONE;
	HIMAGELIST _hImaLst = nullptr;
	WNDPROC _defaultWindowProc = nullptr;
	HMENU _hGlobalMenu = NULL;
	HMENU _hFileListMenu = NULL;  // 新增：文件列表右键菜单
	VerticalFileSwitcherListView _fileListView;
	CategoryManager _categoryManager; // 分类管理器
	std::vector<HWND> _categoryButtons; // 分类按钮句柄数组
	HWND _currentCategoryButton = nullptr; // 当前选中的分类按钮

	static COLORREF _bgColor;
	static const UINT_PTR _fileSwitcherNotifySubclassID = 42;

	// 将_defaultListViewProc移到public部分，以便在静态方法中访问
	WNDPROC _defaultListViewProc = nullptr; // 保存列表视图的原始窗口过程

};
