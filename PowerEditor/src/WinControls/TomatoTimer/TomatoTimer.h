// 番茄提醒功能头文件
// 工作20分钟，休息5分钟，支持用户自定义时间
// 支持TTS声音提醒

#pragma once

#include <windows.h>
#include <string>
#include <chrono>
#include <functional>
#include <mutex>

// 番茄状态枚举
enum class TomatoState {
    IDLE,           // 空闲
    WORKING,        // 工作中
    RESTING,        // 休息中
    PAUSED          // 暂停
};

// 番茄提醒配置结构体
struct TomatoConfig {
    int workMinutes = 25;      // 工作时间（分钟）
    int shortRestMinutes = 5;  // 短休息时间（分钟）
    int longRestMinutes = 15;  // 长休息时间（分钟）
    int longRestAfterPomodoros = 4;  // 多少个番茄钟后进行长休息
    std::wstring shortRestReminderText = L"休息时间到了，请休息一下";  // 短休息提醒文本
    std::wstring longRestReminderText = L"完成了4个番茄钟，进行长休息吧";  // 长休息提醒文本
    std::wstring workReminderText = L"休息结束，开始工作吧";      // 工作提醒文本
    bool enableTTS = true;     // 是否启用TTS声音
};

class TomatoTimer {
public:
    TomatoTimer();
    ~TomatoTimer();

    // 初始化番茄提醒
    void initialize(HWND parentWnd);

    // 启动番茄提醒
    void start();

    // 暂停番茄提醒
    void pause();

    // 继续番茄提醒
    void resume();

    // 停止番茄提醒
    void stop();

    // 重置番茄提醒
    void reset();

    // 获取当前状态
    TomatoState getState() const;

    // 获取剩余时间（秒）
    int getRemainingSeconds() const;

    // 获取已完成的番茄钟数量
    int getCompletedPomodoros() const;

    // 重置已完成的番茄钟数量
    void resetCompletedPomodoros();

    // 设置配置
    void setConfig(const TomatoConfig& config);

    // 获取配置
    TomatoConfig getConfig() const;

    // 注册提醒回调函数
    void setOnReminderCallback(std::function<void()> callback);

    // 注册状态栏更新回调函数
    void setOnStatusBarUpdateCallback(std::function<void(const std::wstring&)> callback);

    // 测试TTS功能
    void testTTS();

private:
    // 定时器回调函数
    static void CALLBACK timerCallback(PVOID lpParameter, BOOLEAN TimerOrWaitFired);

    // 处理定时器事件
    void handleTimerEvent();

    // 显示提醒（自动消失的窗口）
    void showReminder(const std::wstring& message);

    // 播放TTS声音
    void playTTS(const std::wstring& text);

    // 切换状态
    void switchState(TomatoState newState);

    // 创建自动消失的提醒窗口
    static void createAutoCloseWindow(const std::wstring& title, const std::wstring& message, int durationMs);

private:
    HWND _parentWnd = nullptr;
    TomatoState _state = TomatoState::IDLE;
    TomatoConfig _config;

    HANDLE _timer = nullptr;
    std::chrono::system_clock::time_point _startTime;
    int _remainingSeconds = 0;
    int _completedPomodoros = 0;  // 已完成的番茄钟数量

    std::function<void()> _onReminderCallback;
    bool _comInitialized = false;  // COM是否已初始化
    bool _ttsPlayed = false;  // TTS是否已播放
    std::function<void(const std::wstring&)> _onStatusBarUpdateCallback;  // 状态栏更新回调
    mutable std::mutex _mutex; // 互斥锁，保护共享数据
};