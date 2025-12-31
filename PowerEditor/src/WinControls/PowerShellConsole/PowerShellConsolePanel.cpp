// PowerShell 控制台面板实现
#include "PowerShellConsolePanel.h"
#include "resource.h"
#include "menuCmdID.h"
#include <windows.h>
#include <string>
#include <vector>
#include <regex>
#include <sstream>

PowerShellConsolePanel::~PowerShellConsolePanel() {
	stopCommand();
	if (_readerThread.joinable()) _readerThread.join();
	if (_hStdOutRead) { CloseHandle(_hStdOutRead); _hStdOutRead = nullptr; }
	if (_hStdOutWrite) { CloseHandle(_hStdOutWrite); _hStdOutWrite = nullptr; }
	if (_hStdInRead) { CloseHandle(_hStdInRead); _hStdInRead = nullptr; }
	if (_hStdInWrite) { CloseHandle(_hStdInWrite); _hStdInWrite = nullptr; }
}

void PowerShellConsolePanel::init(HINSTANCE hInst, HWND hPere) {
	DockingDlgInterface::init(hInst, hPere);
}

void PowerShellConsolePanel::create(tTbData* data, bool isRTL) {
	DockingDlgInterface::create(data, isRTL);
	data->uMask = DWS_DF_CONT_BOTTOM | DWS_ICONTAB | DWS_USEOWNDARKMODE;
	data->pszAddInfo = L"PowerShell Console";
	data->dlgID = IDM_VIEW_POWERSHELL_CONSOLE;
	startShell();
}

void PowerShellConsolePanel::initEditControl() {
	_hEdit = ::GetDlgItem(_hSelf, IDC_PS_OUTPUT);
	if (!_hEdit) return;

	// 设置等宽字体
	HFONT hFont = ::CreateFontW(16, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
		OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, FIXED_PITCH | FF_MODERN, L"Consolas");
	if (hFont) ::SendMessageW(_hEdit, WM_SETFONT, (WPARAM)hFont, TRUE);

	// 子类化
	::SetWindowLongPtrW(_hEdit, GWLP_USERDATA, (LONG_PTR)this);
	_oldEditProc = (WNDPROC)::SetWindowLongPtrW(_hEdit, GWLP_WNDPROC, (LONG_PTR)EditSubclassProc);

	// 移除文本长度限制
	::SendMessageW(_hEdit, EM_LIMITTEXT, 0, 0);
	
	_lastOutputEndPos = 0;
}

LRESULT CALLBACK PowerShellConsolePanel::EditSubclassProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
	auto* self = (PowerShellConsolePanel*)::GetWindowLongPtrW(hWnd, GWLP_USERDATA);
	if (!self) return ::DefWindowProc(hWnd, message, wParam, lParam);

	if (message == WM_CHAR) {
		if (wParam == VK_RETURN) return 0; // 在 WM_KEYDOWN 处理
		
		// 允许 Ctrl+C (3) 通过? 或者处理它
		if (wParam < 32 && wParam != VK_BACK) return 0;

		// 检查光标位置
		int start, end;
		::SendMessageW(hWnd, EM_GETSEL, (WPARAM)&start, (LPARAM)&end);
		
		if (start < self->_lastOutputEndPos) {
			// 如果在只读区域尝试输入，移动光标到末尾
			int len = ::GetWindowTextLengthW(hWnd);
			::SendMessageW(hWnd, EM_SETSEL, len, len);
		}
	}
	else if (message == WM_KEYDOWN) {
		if (wParam == VK_RETURN) {
			std::wstring line = self->getCurrentLine();
			// 本地回显换行
			self->appendOutput(L"\r\n");
			
			// 发送命令
			self->sendInput(line);

			// 更新历史
			if (!line.empty() && (self->_history.empty() || self->_history.back() != line)) {
				self->_history.push_back(line);
			}
			self->_historyIndex = self->_history.size();
			self->_tempInput.clear();

			return 0;
		}
		else if (wParam == VK_UP) {
			if (self->_historyIndex > 0) {
				if (self->_historyIndex == self->_history.size()) {
					self->_tempInput = self->getCurrentLine();
				}
				self->_historyIndex--;
				self->replaceCurrentLine(self->_history[self->_historyIndex]);
			}
			return 0;
		}
		else if (wParam == VK_DOWN) {
			if (self->_historyIndex < self->_history.size()) {
				self->_historyIndex++;
				if (self->_historyIndex == self->_history.size()) {
					self->replaceCurrentLine(self->_tempInput);
				}
				else {
					self->replaceCurrentLine(self->_history[self->_historyIndex]);
				}
			}
			return 0;
		}
		else if (wParam == VK_BACK) {
			int start, end;
			::SendMessageW(hWnd, EM_GETSEL, (WPARAM)&start, (LPARAM)&end);
			if (start <= self->_lastOutputEndPos && end <= self->_lastOutputEndPos) return 0; // 完全在只读区
			if (start < self->_lastOutputEndPos) {
				::SendMessageW(hWnd, EM_SETSEL, self->_lastOutputEndPos, end);
			}
		}
		else if (wParam == VK_HOME) {
			int start, end;
			::SendMessageW(hWnd, EM_GETSEL, (WPARAM)&start, (LPARAM)&end);
			int target = self->_lastOutputEndPos;
			if (GetKeyState(VK_SHIFT) & 0x8000) {
				::SendMessageW(hWnd, EM_SETSEL, target, end); // 保留选择方向? Edit 控件选择方向比较难控制，这里简单处理
			}
			else {
				::SendMessageW(hWnd, EM_SETSEL, target, target);
			}
			return 0;
		}
	}
	else if (message == WM_PASTE) {
		// 粘贴前移动到末尾
		int len = ::GetWindowTextLengthW(hWnd);
		::SendMessageW(hWnd, EM_SETSEL, len, len);
	}
	else if (message == WM_LBUTTONDOWN || message == WM_MOUSEMOVE) {
		// 允许鼠标操作，不拦截
	}

	return CallWindowProc(self->_oldEditProc, hWnd, message, wParam, lParam);
}

std::wstring PowerShellConsolePanel::getCurrentLine() {
	int len = ::GetWindowTextLengthW(_hEdit);
	if (len <= _lastOutputEndPos) return L"";
	
	std::vector<wchar_t> buf(len + 1);
	::GetWindowTextW(_hEdit, buf.data(), len + 1);
	
	if (len > _lastOutputEndPos) {
		return std::wstring(buf.data() + _lastOutputEndPos);
	}
	return L"";
}

void PowerShellConsolePanel::replaceCurrentLine(const std::wstring& text) {
	int len = ::GetWindowTextLengthW(_hEdit);
	::SendMessageW(_hEdit, EM_SETSEL, _lastOutputEndPos, len);
	::SendMessageW(_hEdit, EM_REPLACESEL, TRUE, (LPARAM)text.c_str());
}

void PowerShellConsolePanel::appendOutput(const std::wstring& text) {
	// 简单的 ANSI 清理正则
	static const std::wregex ansi_regex(L"\x1b\\[[0-9;?]*[a-zA-Z]");
	std::wstring clean;
	try {
		clean = std::regex_replace(text, ansi_regex, L"");
	} catch (...) {
		clean = text; // 如果正则失败，回退到原始文本
	}

	// 规范化换行符：PowerShell 可能输出单独的 \n，Edit 控件需要 \r\n
	// 但如果已经是 \r\n 则保留
	// 简单策略：替换所有 \n 为 \r\n，然后修复 \r\r\n -> \r\n
	// 或者更高效：遍历
	
	std::wstring normalized;
	normalized.reserve(clean.size() + 128);
	for (size_t i = 0; i < clean.size(); ++i) {
		if (clean[i] == L'\n') {
			if (i == 0 || clean[i-1] != L'\r') {
				normalized += L"\r\n";
			} else {
				normalized += L'\n';
			}
		} else {
			normalized += clean[i];
		}
	}

	int len = ::GetWindowTextLengthW(_hEdit);
	::SendMessageW(_hEdit, EM_SETSEL, len, len);
	::SendMessageW(_hEdit, EM_REPLACESEL, FALSE, (LPARAM)normalized.c_str());
	
	// 更新只读边界
	_lastOutputEndPos = ::GetWindowTextLengthW(_hEdit);
	
	// 滚动到底部
	::SendMessageW(_hEdit, WM_VSCROLL, SB_BOTTOM, 0);
}

void PowerShellConsolePanel::startShell() {
	if (_isRunning) return;

	SECURITY_ATTRIBUTES sa{};
	sa.nLength = sizeof(SECURITY_ATTRIBUTES);
	sa.bInheritHandle = TRUE;
	sa.lpSecurityDescriptor = nullptr;

	if (!::CreatePipe(&_hStdOutRead, &_hStdOutWrite, &sa, 0)) {
		appendOutput(L"[错误] 创建输出管道失败\r\n");
		return;
	}
	::SetHandleInformation(_hStdOutRead, HANDLE_FLAG_INHERIT, 0);

	if (!::CreatePipe(&_hStdInRead, &_hStdInWrite, &sa, 0)) {
		appendOutput(L"[错误] 创建输入管道失败\r\n");
		return;
	}
	::SetHandleInformation(_hStdInWrite, HANDLE_FLAG_INHERIT, 0);

	STARTUPINFOW si{};
	PROCESS_INFORMATION pi{};
	si.cb = sizeof(si);
	si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
	si.hStdOutput = _hStdOutWrite;
	si.hStdError = _hStdOutWrite;
	si.hStdInput = _hStdInRead;
	si.wShowWindow = SW_HIDE; // 隐藏控制台窗口

	wchar_t envPath[32768];
	DWORD n = ::GetEnvironmentVariableW(L"PATH", envPath, 32768);
	std::wstring newPath = L"C:\\Program Files\\LLVM\\bin;";
	newPath += (n > 0) ? envPath : L"";
	::SetEnvironmentVariableW(L"PATH", newPath.c_str());

	// 强制交互模式，以便显示 Prompt
	std::wstring psCmd = L"powershell.exe -NoLogo -NoExit -Command -"; 

	wchar_t cwdBuf[MAX_PATH];
	::GetCurrentDirectoryW(MAX_PATH, cwdBuf);

	BOOL ok = ::CreateProcessW(
		nullptr,
		LPWSTR(const_cast<wchar_t*>(psCmd.c_str())),
		nullptr,
		nullptr,
		TRUE,
		CREATE_NO_WINDOW,
		nullptr,
		cwdBuf,
		&si,
		&pi
	);

	::CloseHandle(_hStdOutWrite);
	_hStdOutWrite = nullptr;
	::CloseHandle(_hStdInRead);
	_hStdInRead = nullptr;

	if (!ok) {
		appendOutput(L"[错误] 启动 PowerShell 失败\r\n");
		if (_hStdOutRead) { ::CloseHandle(_hStdOutRead); _hStdOutRead = nullptr; }
		if (_hStdInWrite) { ::CloseHandle(_hStdInWrite); _hStdInWrite = nullptr; }
		return;
	}

	_isRunning = true;
	_hChildProcess = pi.hProcess;
	_hChildThread = pi.hThread;

	_readerThread = std::thread([this]() {
		char buffer[1024];
		DWORD read = 0;
		while (_isRunning) {
			if (!::ReadFile(_hStdOutRead, buffer, sizeof(buffer) - 1, &read, nullptr) || read == 0) {
				break;
			}
			buffer[read] = '\0';
			int wlen = ::MultiByteToWideChar(CP_UTF8, 0, buffer, read, nullptr, 0);
			std::wstring wout(wlen, L'\0');
			::MultiByteToWideChar(CP_UTF8, 0, buffer, read, wout.data(), wlen);
			
			// 在 UI 线程更新
			// 注意：这里需要确保线程安全或者使用 SendMessage/PostMessage
			// 由于 appendOutput 操作 HWND，最好是在 UI 线程执行
			// 但直接 SendMessage 可能死锁吗？
			// appendOutput 使用 SendMessage，如果 UI 线程阻塞在 ReadFile (不可能，这是工作线程)
			// 但如果 UI 线程在等待工作线程 (join)，则会死锁。
			// 这里我们直接调用 appendOutput，因为 SendMessage 会切换到 UI 线程上下文执行窗口过程。
			// 只要 UI 线程不阻塞在等待该线程的地方即可。
			
			appendOutput(wout);
		}
		_isRunning = false;
		if (_hChildThread) { ::CloseHandle(_hChildThread); _hChildThread = nullptr; }
		if (_hChildProcess) { ::CloseHandle(_hChildProcess); _hChildProcess = nullptr; }
		if (_hStdOutRead) { ::CloseHandle(_hStdOutRead); _hStdOutRead = nullptr; }
	});

	// 配置编码
	sendInput(L"[Console]::InputEncoding = [System.Text.Encoding]::UTF8");
	sendInput(L"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8");
}

void PowerShellConsolePanel::stopCommand() {
	if (_isRunning) {
		sendInput(L"exit");
		// 稍微等待，不要死等
		WaitForSingleObject(_hChildProcess, 500);
		if (_isRunning && _hChildProcess) {
			::TerminateProcess(_hChildProcess, 1);
		}
	}
	_isRunning = false;
	if (_hStdInWrite) { ::CloseHandle(_hStdInWrite); _hStdInWrite = nullptr; }
}

void PowerShellConsolePanel::sendInput(const std::wstring& cmd) {
	if (!_isRunning || !_hStdInWrite) return;
	int utf8Len = ::WideCharToMultiByte(CP_UTF8, 0, cmd.c_str(), -1, nullptr, 0, nullptr, nullptr);
	if (utf8Len > 0) {
		std::string utf8(utf8Len, '\0');
		::WideCharToMultiByte(CP_UTF8, 0, cmd.c_str(), -1, utf8.data(), utf8Len, nullptr, nullptr);
		if (!utf8.empty() && utf8.back() == '\0') utf8.pop_back();
		std::string withCRLF = utf8 + "\r\n";
		DWORD written = 0;
		::WriteFile(_hStdInWrite, withCRLF.data(), static_cast<DWORD>(withCRLF.size()), &written, nullptr);
	}
}

intptr_t CALLBACK PowerShellConsolePanel::run_dlgProc(UINT message, WPARAM wParam, LPARAM lParam) {
	switch (message) {
		case WM_INITDIALOG:
		{
			initEditControl();
			return TRUE;
		}
		case WM_SIZE:
		{
			if (_hEdit) {
				RECT rc;
				::GetClientRect(_hSelf, &rc);
				::MoveWindow(_hEdit, 0, 0, rc.right, rc.bottom, TRUE);
			}
			return TRUE;
		}
		// 移除旧的命令处理
	}
	return DockingDlgInterface::run_dlgProc(message, wParam, lParam);
}
