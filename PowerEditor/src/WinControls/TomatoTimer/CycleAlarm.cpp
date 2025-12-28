// 循环闹钟功能实现文件
#include "CycleAlarm.h"
#include <iostream>
#include <sstream>
#include <windows.h>
#include <commctrl.h>
#pragma comment(lib, "user32.lib")

CycleAlarm::CycleAlarm() {
    _cycleHours = 6;
    _isRunning = false;
    _isPaused = false;
}

CycleAlarm::~CycleAlarm() {
    stop();
}

void CycleAlarm::initialize(HWND parentWnd) {
    _parentWnd = parentWnd;
}

void CycleAlarm::start(int cycleHours) {
    if (_isRunning) {
        stop();
    }

    _cycleHours = cycleHours;
    _isRunning = true;
    _isPaused = false;
    _startTime = std::chrono::system_clock::now();

    // 创建定时器（每小时检查一次）
    if (_timer == nullptr) {
        CreateTimerQueueTimer(&_timer, nullptr, timerCallback, this, 3600000, 3600000, 0);
    }
}

void CycleAlarm::stop() {
    if (_timer != nullptr) {
        DeleteTimerQueueTimer(nullptr, _timer, nullptr);
        _timer = nullptr;
    }
    _isRunning = false;
    _isPaused = false;
}

void CycleAlarm::pause() {
    if (_isRunning && !_isPaused) {
        _isPaused = true;
    }
}

void CycleAlarm::resume() {
    if (_isRunning && _isPaused) {
        _isPaused = false;
    }
}

void CycleAlarm::setOnAlarmCallback(std::function<void()> callback) {
    _onAlarmCallback = callback;
}

void CycleAlarm::setCycleHours(int cycleHours) {
    _cycleHours = cycleHours;
}

int CycleAlarm::getCycleHours() const {
    return _cycleHours;
}

bool CycleAlarm::isRunning() const {
    return _isRunning;
}

void CALLBACK CycleAlarm::timerCallback(PVOID lpParameter, BOOLEAN TimerOrWaitFired) {
    CycleAlarm* alarm = static_cast<CycleAlarm*>(lpParameter);
    if (alarm) {
        alarm->handleTimerEvent();
    }
}

void CycleAlarm::handleTimerEvent() {
    if (!_isRunning || _isPaused) {
        return;
    }

    auto now = std::chrono::system_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::hours>(now - _startTime);

    if (duration.count() >= _cycleHours) {
        showAlarm();
        _startTime = now; // 重置开始时间

        // 触发回调
        if (_onAlarmCallback) {
            _onAlarmCallback();
        }
    }
}

void CycleAlarm::showAlarm() {
    std::wstringstream message;
    message << L"已经工作了" << _cycleHours << L"小时，该休息一下了！";
    MessageBox(_parentWnd, message.str().c_str(), L"循环提醒", MB_OK | MB_ICONINFORMATION);
}
