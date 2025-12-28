// 番茄提醒对话框实现文件
#include "TomatoTimerDlg.h"
#include "TomatoTimer.h"
#include "resource.h"
#include <windows.h>
#include <sstream>
#include <functional>
#include <commctrl.h>
#pragma comment(lib, "comctl32.lib")

void TomatoTimerDlg::doDialog(bool isRTL) {
	if (!isCreated()) {
		create(IDD_TOMATO_TIMER, isRTL);
		// 注册回调函数以更新UI
		_timer.setOnReminderCallback([this]() {
			this->updateUI();
		});
	}
	else {
		goToCenter();
		display();
	}
}

void TomatoTimerDlg::destroy() {
	_timer.stop();
	StaticDialog::destroy();
}

intptr_t CALLBACK TomatoTimerDlg::run_dlgProc(UINT message, WPARAM wParam, LPARAM lParam) {
	switch (message) {
		case WM_INITDIALOG:
		{
			initDialog();
			return TRUE;
		}

		case WM_COMMAND:
		{
			switch (LOWORD(wParam)) {
				case IDOK:
					saveConfig();
					display(false);
					return TRUE;

				case IDCANCEL:
					display(false);
					return TRUE;

				case IDC_START_TIMER:
					saveConfig();
					_timer.start();
					updateTimerState();
					return TRUE;

				case IDC_PAUSE_TIMER:
					_timer.pause();
					updateTimerState();
					return TRUE;

				case IDC_STOP_TIMER:
					_timer.stop();
					updateTimerState();
					return TRUE;

				case IDC_TEST_TTS:
					_timer.testTTS();
					return TRUE;

				default:
					return FALSE;
			}
		}

		case WM_TIMER:
		{
			updateUI();
			return TRUE;
		}

		default:
			return FALSE;
	}
}

void TomatoTimerDlg::initDialog() {
	// 获取当前配置
	TomatoConfig config = _timer.getConfig();

	// 设置工作时间
	std::wstringstream workStream;
	workStream << config.workMinutes;
	::SetDlgItemText(_hSelf, IDC_WORK_MINUTES, workStream.str().c_str());

	// 设置短休息时间
	std::wstringstream shortRestStream;
	shortRestStream << config.shortRestMinutes;
	::SetDlgItemText(_hSelf, IDC_SHORT_REST_MINUTES, shortRestStream.str().c_str());

	// 设置长休息时间
	std::wstringstream longRestStream;
	longRestStream << config.longRestMinutes;
	::SetDlgItemText(_hSelf, IDC_LONG_REST_MINUTES, longRestStream.str().c_str());

	// 设置长休息周期
	std::wstringstream longRestAfterStream;
	longRestAfterStream << config.longRestAfterPomodoros;
	::SetDlgItemText(_hSelf, IDC_LONG_REST_AFTER_POMODOROS, longRestAfterStream.str().c_str());

	// 设置TTS复选框
	::CheckDlgButton(_hSelf, IDC_ENABLE_TTS, config.enableTTS ? BST_CHECKED : BST_UNCHECKED);

	// 设置短休息提醒文本
	::SetDlgItemText(_hSelf, IDC_SHORT_REST_REMINDER_TEXT, config.shortRestReminderText.c_str());

	// 设置长休息提醒文本
	::SetDlgItemText(_hSelf, IDC_LONG_REST_REMINDER_TEXT, config.longRestReminderText.c_str());

	// 设置工作提醒文本
	::SetDlgItemText(_hSelf, IDC_WORK_REMINDER_TEXT, config.workReminderText.c_str());

	// 更新定时器状态
	updateTimerState();

	// 设置定时器用于更新UI
	::SetTimer(_hSelf, 1, 1000, nullptr);
}

void TomatoTimerDlg::saveConfig() {
	TomatoConfig config;

	// 获取工作时间
	wchar_t workText[10];
	::GetDlgItemText(_hSelf, IDC_WORK_MINUTES, workText, sizeof(workText) / sizeof(wchar_t));
	config.workMinutes = _wtoi(workText);

	// 获取短休息时间
	wchar_t shortRestText[10];
	::GetDlgItemText(_hSelf, IDC_SHORT_REST_MINUTES, shortRestText, sizeof(shortRestText) / sizeof(wchar_t));
	config.shortRestMinutes = _wtoi(shortRestText);

	// 获取长休息时间
	wchar_t longRestText[10];
	::GetDlgItemText(_hSelf, IDC_LONG_REST_MINUTES, longRestText, sizeof(longRestText) / sizeof(wchar_t));
	config.longRestMinutes = _wtoi(longRestText);

	// 获取长休息周期
	wchar_t longRestAfterText[10];
	::GetDlgItemText(_hSelf, IDC_LONG_REST_AFTER_POMODOROS, longRestAfterText, sizeof(longRestAfterText) / sizeof(wchar_t));
	config.longRestAfterPomodoros = _wtoi(longRestAfterText);

	// 获取TTS状态
	config.enableTTS = (::IsDlgButtonChecked(_hSelf, IDC_ENABLE_TTS) == BST_CHECKED);

	// 获取短休息提醒文本
	wchar_t shortRestReminderText[256];
	::GetDlgItemText(_hSelf, IDC_SHORT_REST_REMINDER_TEXT, shortRestReminderText, sizeof(shortRestReminderText) / sizeof(wchar_t));
	config.shortRestReminderText = shortRestReminderText;

	// 获取长休息提醒文本
	wchar_t longRestReminderText[256];
	::GetDlgItemText(_hSelf, IDC_LONG_REST_REMINDER_TEXT, longRestReminderText, sizeof(longRestReminderText) / sizeof(wchar_t));
	config.longRestReminderText = longRestReminderText;

	// 获取工作提醒文本
	wchar_t workReminderText[256];
	::GetDlgItemText(_hSelf, IDC_WORK_REMINDER_TEXT, workReminderText, sizeof(workReminderText) / sizeof(wchar_t));
	config.workReminderText = workReminderText;

	// 保存配置
	_timer.setConfig(config);
}

void TomatoTimerDlg::updateTimerState() {
	TomatoState state = _timer.getState();
	int remainingSeconds = _timer.getRemainingSeconds();
	int completedPomodoros = _timer.getCompletedPomodoros();

	// 更新状态文本
	std::wstring stateText;
	switch (state) {
		case TomatoState::IDLE:
			stateText = L"空闲";
			break;
		case TomatoState::WORKING:
			stateText = L"工作中";
			break;
		case TomatoState::RESTING:
			stateText = L"休息中";
			break;
		case TomatoState::PAUSED:
			stateText = L"暂停";
			break;
	}

	::SetDlgItemText(_hSelf, IDC_TIMER_STATE, stateText.c_str());

	// 更新番茄钟计数
	std::wstringstream pomodoroStream;
	pomodoroStream << completedPomodoros;
	::SetDlgItemText(_hSelf, IDC_POMODORO_COUNT, pomodoroStream.str().c_str());

	// 更新剩余时间
	int minutes = remainingSeconds / 60;
	int seconds = remainingSeconds % 60;
	std::wstringstream timeStream;
	timeStream << minutes << L":" << (seconds < 10 ? L"0" : L"") << seconds;
	::SetDlgItemText(_hSelf, IDC_REMAINING_TIME, timeStream.str().c_str());
}

void TomatoTimerDlg::updateUI() {
	updateTimerState();
}
