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

#include "../DockingWnd/DockingDlgInterface.h"
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
		_hParent = parent;  // 保存Notepad++ Main Window Handle
		_hImaLst = hImaLst;
	};
	
	// 添加一个方法来获取Notepad++ Main Window Handle
	HWND getNppMainWnd() const { return _hParent; }
    HINSTANCE getHInst() const { return _hInst; }

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
		// When Tab Order Changes, Always Reload File List to Reflect New Tab Order
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

	// Add display Method Declaration
	void display(bool toShow = true) const override;

	// Settings Dialog Related Methods
	void showSettingsDialog();

	// Category Manager Access Method (for Dialog Procedure)
	CategoryManager* getCategoryManager() { return &_categoryManager; }
	const CategoryManager* getCategoryManager() const { return &_categoryManager; }

	// Newly Added Category Related Methods
	void showCategoryMenu();
	void editCategoryFile();
	void refreshCategory();

private:
	bool registerWindowClass(HINSTANCE hInst);

protected:
	static LRESULT CALLBACK wndProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
		// Handle WM_NCCREATE Message, This is the First Message Received When Creating Window
		if (message == WM_NCCREATE) {
			// Get this Pointer from Creation Parameters
			LPCREATESTRUCT lpcs = reinterpret_cast<LPCREATESTRUCT>(lParam);
			void* lpThis = lpcs->lpCreateParams;
			
			// Store this Pointer in Window's Extra Data (Use -21 Instead of GWL_USERDATA)
			::SetWindowLongPtr(hwnd, -21, reinterpret_cast<LONG_PTR>(lpThis));
			
			// Save Window Handle to Object
			VerticalFileSwitcher* pThis = static_cast<VerticalFileSwitcher*>(lpThis);
			pThis->_hSelf = hwnd;
			
			return TRUE; // Allow Window Creation
		}
		
		// Use -21 Instead of GWL_USERDATA
		VerticalFileSwitcher* pThis = reinterpret_cast<VerticalFileSwitcher*>(::GetWindowLongPtr(hwnd, -21));
		if (pThis) {
			LRESULT result = pThis->run_dlgProc(message, wParam, lParam);
			// Return Result if Message is Processed; Otherwise Call Default Window Procedure
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

	// Internal Method, Used for protected Part to Access _fileListView
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
	void initFileListContextMenu();  // New: Initialize File List Right-Click Menu
	void popupMenuCmd(int cmdID);

	static LRESULT CALLBACK listViewStaticProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam) {
		// Use -21 Instead of GWLP_USERDATA
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
	HMENU _hFileListMenu = NULL;  // 新增：File List Right-Click Menu
	VerticalFileSwitcherListView _fileListView;
	CategoryManager _categoryManager; // 分类管理器
	std::vector<HWND> _categoryButtons; // Category Button Handle Array
	HWND _currentCategoryButton = nullptr; // Currently Selected Category按钮

	static COLORREF _bgColor;
	static const UINT_PTR _fileSwitcherNotifySubclassID = 42;

	// Move _defaultListViewProc to public Part for Access in Static Methods
	WNDPROC _defaultListViewProc = nullptr; // Save Original Window Procedure of List View

};
