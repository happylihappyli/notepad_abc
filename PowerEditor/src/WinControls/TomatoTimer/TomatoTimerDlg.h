// 番茄提醒对话框头文件
#pragma once

#include "TomatoTimer.h"
#include "../StaticDialog/StaticDialog.h"

class TomatoTimerDlg : public StaticDialog {
public:
	TomatoTimerDlg() = default;

	void doDialog(bool isRTL = false);
	void destroy() override;

protected:
	intptr_t CALLBACK run_dlgProc(UINT message, WPARAM wParam, LPARAM lParam) override;

private:
	// 初始化对话框
	void initDialog();

	// 保存配置
	void saveConfig();

	// 更新定时器状态
	void updateTimerState();

	// 更新UI显示
	void updateUI();

private:
	TomatoTimer _timer;
};
