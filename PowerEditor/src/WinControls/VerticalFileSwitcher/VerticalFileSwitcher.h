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

#define FS_PROJECTPANELTITLE		L"Document List"

struct sortCompareData {
  HWND hListView = nullptr;
  int columnIndex = 0;
  int sortDirection = 0;
};

LRESULT run_listViewProc(WNDPROC oldEditProc, HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam);

class VerticalFileSwitcher : public DockingDlgInterface
{
private:
	// 私有成员变量
	bool colHeaderRClick = false;
	int _lastSortingColumn = 0;
	int _lastSortingDirection = SORT_DIRECTION_NONE;
	HIMAGELIST _hImaLst = nullptr;
	WNDPROC _defaultWindowProc = nullptr;
	HMENU _hGlobalMenu = NULL;
	VerticalFileSwitcherListView _fileListView;
	HWND _hFontSizeCombo = nullptr; // 字体大小下拉框句柄
	HWND _hFontSizeLabel = nullptr; // 字体大小标签句柄

	static COLORREF _bgColor;
	static const UINT_PTR _fileSwitcherNotifySubclassID = 42;

public:
	// 将_defaultListViewProc移到public部分，以便在静态方法中访问
	WNDPROC _defaultListViewProc = nullptr; // 保存列表视图的原始窗口过程

	// 使用IDD_DOCLIST作为资源ID
	VerticalFileSwitcher(): DockingDlgInterface(IDD_DOCLIST) {};

	void init(HINSTANCE hInst, HWND hPere, HIMAGELIST hImaLst) {
		DockingDlgInterface::init(hInst, hPere);
		_hImaLst = hImaLst;
	};

	// 重写create方法，使用资源文件创建对话框
	virtual void create(tTbData* data, bool isRTL = false) override;

	virtual void create(tTbData* data, std::array<int, 3> iconIDs, bool isRTL = false) override;

	virtual void display(bool toShow = true) const override;

	// 颜色设置方法需要保持公共访问权限
	virtual void setBackgroundColor(COLORREF bgColour) override {
		_fileListView.setBackgroundColor(bgColour);
		
		auto r = GetRValue(bgColour);
		auto g = GetGValue(bgColour);
		auto b = GetBValue(bgColour);

		constexpr int luminenceIncrementBy = 333; // 33.3 %

		// main color is blue
		// but difference must be high
		// can have similar blue color as header
		constexpr int difference = 12;
		const auto bAdjusted = static_cast<BYTE>(std::max<int>(0, static_cast<int>(b) - difference));
		if (bAdjusted > r && bAdjusted > g)
		{
			// using values from NppDarkMode.cpp
			// from double calculatePerceivedLighness(COLORREF c)
			// double luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
			// values multiplied by 1024 and then shift result by 10 - "fake" divide by 1024
			// for performance
			const auto grayscale = static_cast<BYTE>((r * 218 + g * 732 + b * 74) >> 10);
			_bgColor = ::ColorAdjustLuma(RGB(grayscale, grayscale, grayscale), luminenceIncrementBy, TRUE);
		}
		else
		{
			_bgColor = ::ColorAdjustLuma(bgColour, luminenceIncrementBy, TRUE);
		}
	}

	virtual void setForegroundColor(COLORREF fgColour) override {
		_fileListView.setForegroundColor(fgColour);
    }

	// 设置字体大小
	void setFontSize(int fontSize) {
		_fileListView.setFontSize(fontSize);
	}

	// 获取当前字体大小
	int getFontSize() const {
		return _fileListView.getFontSize();
	}

	// 以下方法需要保持公共访问权限，因为被外部调用
	void closeItem(BufferID bufferID, int iView) {
		_fileListView.closeItem(bufferID, iView);
	}

	void setItemColor(BufferID bufferID) {
		_fileListView.setItemColor(bufferID);
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
		if (_lastSortingDirection == SORT_DIRECTION_NONE) {
			_fileListView.reload();
		}
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

private:
	// 注册自定义窗口类
	bool registerWindowClass(HINSTANCE hInst);

protected:
	// 窗口过程
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

	void setItemColorInternal(BufferID bufferID) {
		_fileListView.setItemColor(bufferID);
	}

	std::wstring getFullFilePathInternal(size_t i) const {
		return _fileListView.getFullFilePath(i);
	}

	int setHeaderOrder(int columnIndex);
	void updateHeaderArrow();

	intptr_t CALLBACK run_dlgProc(UINT message, WPARAM wParam, LPARAM lParam);
	void initPopupMenus();
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
};
