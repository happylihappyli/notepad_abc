// PowerShell 控制台面板头文件
#pragma once

#include "../DockingWnd/DockingDlgInterface.h"
#include "PowerShellConsolePanel_rc.h"
#include <string>
#include <vector>
#include <thread>
#include <atomic>

class PowerShellConsolePanel : public DockingDlgInterface {
public:
	PowerShellConsolePanel() : DockingDlgInterface(IDD_POWERSHELL_PANEL) {}
	~PowerShellConsolePanel();

	void init(HINSTANCE hInst, HWND hPere) override;

	void create(tTbData* data, bool isRTL = false) override;

protected:
	intptr_t CALLBACK run_dlgProc(UINT message, WPARAM wParam, LPARAM lParam) override;

private:
	void appendOutput(const std::wstring& text);
	// 启动交互式 PowerShell 会话
	void startShell();
	// 发送输入到会话
	void sendInput(const std::wstring& cmd);
	// 停止当前会话
	void stopCommand();
	
	// 编辑框子类化过程
	static LRESULT CALLBACK EditSubclassProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
	
	// 内部辅助
	void initEditControl();
	void replaceCurrentLine(const std::wstring& text);
	std::wstring getCurrentLine();

private:
	std::atomic<bool> _isRunning{ false };
	HANDLE _hChildProcess = nullptr;
	HANDLE _hChildThread = nullptr;
	std::thread _readerThread;
	HANDLE _hStdOutRead = nullptr;
	HANDLE _hStdOutWrite = nullptr;
	HANDLE _hStdInRead = nullptr;
	HANDLE _hStdInWrite = nullptr;

	// UI 状态
	HWND _hEdit = nullptr;
	WNDPROC _oldEditProc = nullptr;
	int _lastOutputEndPos = 0;

	// 历史记录
	std::vector<std::wstring> _history;
	size_t _historyIndex = 0;
	std::wstring _tempInput; // 浏览历史时暂存当前输入
};
