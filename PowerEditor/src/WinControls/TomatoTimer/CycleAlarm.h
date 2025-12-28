// 循环闹钟功能头文件
#pragma once

#include <windows.h>
#include <chrono>
#include <functional>

class CycleAlarm {
public:
    CycleAlarm();
    ~CycleAlarm();

    // 初始化循环闹钟
    void initialize(HWND parentWnd);

    // 启动循环闹钟
    void start(int cycleHours);

    // 停止循环闹钟
    void stop();

    // 暂停循环闹钟
    void pause();

    // 继续循环闹钟
    void resume();

    // 注册提醒回调函数
    void setOnAlarmCallback(std::function<void()> callback);

    // 设置循环时间（小时）
    void setCycleHours(int cycleHours);

    // 获取循环时间（小时）
    int getCycleHours() const;

    // 是否正在运行
    bool isRunning() const;

private:
    // 定时器回调函数
    static void CALLBACK timerCallback(PVOID lpParameter, BOOLEAN TimerOrWaitFired);

    // 处理定时器事件
    void handleTimerEvent();

    // 显示提醒
    void showAlarm();

private:
    HWND _parentWnd = nullptr;
    int _cycleHours = 6;
    bool _isRunning = false;
    bool _isPaused = false;
    HANDLE _timer = nullptr;
    std::chrono::system_clock::time_point _startTime;
    std::function<void()> _onAlarmCallback;
};
