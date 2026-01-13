// 番茄提醒功能实现文件
#include "TomatoTimer.h"
#include <iostream>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <windows.h>
#include <commctrl.h>
#include <sapi.h>
#include <thread>
#include <shlwapi.h>
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "sapi.lib")
#pragma comment(lib, "shlwapi.lib")

// 简单的日志函数
void Log(const std::wstring& msg) {
    std::wofstream logFile("tomato_debug.log", std::ios::app);
    if (logFile.is_open()) {
        auto now = std::chrono::system_clock::now();
        std::time_t now_time = std::chrono::system_clock::to_time_t(now);
        tm local_tm;
        localtime_s(&local_tm, &now_time);
        logFile << std::put_time(&local_tm, L"%Y-%m-%d %H:%M:%S") << L" - " << msg << std::endl;
    }
}

std::wstring GetConfigFilePath() {
    wchar_t path[MAX_PATH];
    GetModuleFileName(NULL, path, MAX_PATH);
    PathRemoveFileSpec(path);
    PathAppend(path, L"tomato.ini");
    return path;
}

void TomatoTimer::loadConfig() {
    std::wstring path = GetConfigFilePath();
    
    _config.workMinutes = GetPrivateProfileInt(L"Settings", L"WorkMinutes", 25, path.c_str());
    _config.shortRestMinutes = GetPrivateProfileInt(L"Settings", L"ShortRestMinutes", 5, path.c_str());
    _config.longRestMinutes = GetPrivateProfileInt(L"Settings", L"LongRestMinutes", 15, path.c_str());
    _config.longRestAfterPomodoros = GetPrivateProfileInt(L"Settings", L"LongRestAfterPomodoros", 4, path.c_str());
    _config.enableTTS = GetPrivateProfileInt(L"Settings", L"EnableTTS", 1, path.c_str()) != 0;
    _config.autoStart = GetPrivateProfileInt(L"Settings", L"AutoStart", 0, path.c_str()) != 0;

    wchar_t buffer[256];
    GetPrivateProfileString(L"Settings", L"ShortRestReminderText", L"休息时间到了，请休息一下", buffer, 256, path.c_str());
    _config.shortRestReminderText = buffer;
    
    GetPrivateProfileString(L"Settings", L"LongRestReminderText", L"完成了4个番茄钟，进行长休息吧", buffer, 256, path.c_str());
    _config.longRestReminderText = buffer;
    
    GetPrivateProfileString(L"Settings", L"WorkReminderText", L"休息结束，开始工作吧", buffer, 256, path.c_str());
    _config.workReminderText = buffer;
}

void TomatoTimer::saveConfig() {
    std::wstring path = GetConfigFilePath();
    
    WritePrivateProfileString(L"Settings", L"WorkMinutes", std::to_wstring(_config.workMinutes).c_str(), path.c_str());
    WritePrivateProfileString(L"Settings", L"ShortRestMinutes", std::to_wstring(_config.shortRestMinutes).c_str(), path.c_str());
    WritePrivateProfileString(L"Settings", L"LongRestMinutes", std::to_wstring(_config.longRestMinutes).c_str(), path.c_str());
    WritePrivateProfileString(L"Settings", L"LongRestAfterPomodoros", std::to_wstring(_config.longRestAfterPomodoros).c_str(), path.c_str());
    WritePrivateProfileString(L"Settings", L"EnableTTS", std::to_wstring(_config.enableTTS ? 1 : 0).c_str(), path.c_str());
    WritePrivateProfileString(L"Settings", L"AutoStart", std::to_wstring(_config.autoStart ? 1 : 0).c_str(), path.c_str());
    
    WritePrivateProfileString(L"Settings", L"ShortRestReminderText", _config.shortRestReminderText.c_str(), path.c_str());
    WritePrivateProfileString(L"Settings", L"LongRestReminderText", _config.longRestReminderText.c_str(), path.c_str());
    WritePrivateProfileString(L"Settings", L"WorkReminderText", _config.workReminderText.c_str(), path.c_str());
}

// 窗口参数结构体
struct AutoCloseWindowParams {
    std::wstring title;
    std::wstring message;
    int durationMs;
};

TomatoTimer::TomatoTimer() {
    // 默认配置
    _config.workMinutes = 25;
    _config.shortRestMinutes = 5;
    _config.longRestMinutes = 15;
    _config.longRestAfterPomodoros = 4;
    _config.shortRestReminderText = L"休息时间到了，请休息一下";
    _config.longRestReminderText = L"完成了4个番茄钟，进行长休息吧";
    _config.workReminderText = L"休息结束，开始工作吧";
    _config.enableTTS = true;
    
    _comInitialized = false;
    _ttsPlayed = false;
    _completedPomodoros = 0;

    loadConfig();
}

TomatoTimer::~TomatoTimer() {
    stop();
    // 清理COM
    CoUninitialize();
}

void TomatoTimer::initialize(HWND parentWnd) {
    _parentWnd = parentWnd;
}

void TomatoTimer::start() {
    std::lock_guard<std::mutex> lock(_mutex);
    Log(L"尝试启动番茄钟");
    if (_state != TomatoState::IDLE && _state != TomatoState::PAUSED) {
        Log(L"启动失败：状态不是IDLE或PAUSED");
        return;
    }

    if (_state == TomatoState::IDLE) {
        _state = TomatoState::WORKING;
        // 确保时间至少为1分钟，防止逻辑错误
        if (_config.workMinutes <= 0) {
            Log(L"配置的工作时间无效，重置为25分钟");
            _config.workMinutes = 25;
        }
        _remainingSeconds = _config.workMinutes * 60;
        Log(L"状态切换为WORKING，剩余时间: " + std::to_wstring(_remainingSeconds) + L"秒");
    } else {
        _state = (_state == TomatoState::PAUSED) ? _state : TomatoState::WORKING;
        Log(L"从PAUSED恢复");
    }

    _startTime = std::chrono::system_clock::now();

    // 创建定时器
    if (_timer == nullptr) {
        Log(L"创建定时器");
        CreateTimerQueueTimer(&_timer, nullptr, timerCallback, this, 1000, 1000, 0);
    }
}

void TomatoTimer::pause() {
    std::lock_guard<std::mutex> lock(_mutex);
    if (_state == TomatoState::WORKING || _state == TomatoState::RESTING) {
        _state = TomatoState::PAUSED;
    }
}

void TomatoTimer::resume() {
    std::lock_guard<std::mutex> lock(_mutex);
    if (_state == TomatoState::PAUSED) {
        // 根据剩余时间判断之前的状态
        int maxRestSeconds = (_config.longRestMinutes > _config.shortRestMinutes) 
                           ? _config.longRestMinutes * 60 
                           : _config.shortRestMinutes * 60;
        _state = (_remainingSeconds > maxRestSeconds) ? TomatoState::WORKING : TomatoState::RESTING;
    }
}

void TomatoTimer::stop() {
    std::lock_guard<std::mutex> lock(_mutex);
    if (_timer != nullptr) {
        DeleteTimerQueueTimer(nullptr, _timer, nullptr);
        _timer = nullptr;
    }
    _state = TomatoState::IDLE;
    _remainingSeconds = 0;
}

void TomatoTimer::reset() {
    stop(); // stop已经加锁了，这里如果直接调用可能会死锁（std::mutex不可重入）
            // 但是stop加锁是加在函数体内的，如果reset调用stop，reset不加锁？
            // reset需要加锁来保护_remainingSeconds和_completedPomodoros的赋值。
            // 方案：把stop逻辑拆分，或者使用recursive_mutex，或者在reset里手动做。
            // 这里为了简单，把stop的内容展开在reset里，或者修改stop不加锁，搞一个doStop。
            // 鉴于stop被公开调用，必须加锁。
            // 简单起见，reset不加锁调用stop，然后再加锁修改其他。
            // 这样中间会有空隙，但对于reset来说可能接受。
            // 更好的方式：reset也加锁，但是stop如果也加锁就会死锁。
            // 修改：使用 std::recursive_mutex ? 不，C++标准库有，但通常不推荐。
            // 让我们实现一个内部 doStop 
    
    // 实际上，reset 调用的 stop 里面有锁。所以 reset 自身不需要第一行就加锁。
    // 但是 reset 后面的赋值需要保护。
    // 让我们先修改 stop，然后看 reset。
}

TomatoState TomatoTimer::getState() const {
    return _state;
}

int TomatoTimer::getRemainingSeconds() const {
    return _remainingSeconds;
}

int TomatoTimer::getCompletedPomodoros() const {
    return _completedPomodoros;
}

void TomatoTimer::resetCompletedPomodoros() {
    _completedPomodoros = 0;
}

void TomatoTimer::setConfig(const TomatoConfig& config) {
    std::lock_guard<std::mutex> lock(_mutex);
    _config = config;
    if (_state == TomatoState::IDLE) {
        _remainingSeconds = _config.workMinutes * 60;
    }
    saveConfig();
}

TomatoConfig TomatoTimer::getConfig() const {
    return _config;
}

void TomatoTimer::setOnReminderCallback(std::function<void()> callback) {
    _onReminderCallback = callback;
}

void TomatoTimer::setOnStatusBarUpdateCallback(std::function<void(const std::wstring&)> callback) {
    _onStatusBarUpdateCallback = callback;
}

void CALLBACK TomatoTimer::timerCallback(PVOID lpParameter, BOOLEAN TimerOrWaitFired) {
    TomatoTimer* timer = static_cast<TomatoTimer*>(lpParameter);
    if (timer) {
        timer->handleTimerEvent();
    }
}

void TomatoTimer::handleTimerEvent() {
    std::unique_lock<std::mutex> lock(_mutex);
    if (_state == TomatoState::IDLE || _state == TomatoState::PAUSED) {
        return;
    }

    _remainingSeconds--;

    // 调试日志：每10秒或最后5秒打印一次，避免日志过大
    if (_remainingSeconds % 10 == 0 || _remainingSeconds < 5) {
        // Log(L"Tick: 剩余 " + std::to_wstring(_remainingSeconds) + L" 秒");
    }

    // 准备回调需要的数据，避免持锁调用回调
    auto onStatusBarUpdateCallback = _onStatusBarUpdateCallback;
    int remainingSeconds = _remainingSeconds;
    TomatoState state = _state;
    
    // 临时解锁以调用状态栏回调，防止死锁
    lock.unlock();
    
    // 更新状态栏显示剩余时间
    if (onStatusBarUpdateCallback) {
        int minutes = remainingSeconds / 60;
        int seconds = remainingSeconds % 60;
        std::wstringstream ss;
        if (state == TomatoState::WORKING) {
            ss << L"工作: " << minutes << L":" << (seconds < 10 ? L"0" : L"") << seconds;
        } else {
            ss << L"休息: " << minutes << L":" << (seconds < 10 ? L"0" : L"") << seconds;
        }
        onStatusBarUpdateCallback(ss.str());
    }

    // 重新加锁检查时间是否到
    lock.lock();
    
    // 再次检查状态，防止在解锁期间被修改
    if (_state == TomatoState::IDLE || _state == TomatoState::PAUSED) {
        return;
    }
    
    // 检查剩余时间。注意：如果_remainingSeconds在解锁期间被reset修改了，这里会读取到新值。
    // 但是我们之前已经 _remainingSeconds-- 了。
    // 如果其他线程 reset 了，_remainingSeconds 变大了，这里就不会进 if。
    // 如果没有其他线程干扰，这里 _remainingSeconds 应该还是我们刚才减过的值（或者更小，如果有并发tick，但我们加了锁，handleTimerEvent串行化了？
    // 不，handleTimerEvent是每次tick调用的。如果上一次tick因为锁阻塞了，这一次会接着执行。
    // 关键是：_remainingSeconds 是共享变量。
    
    if (_remainingSeconds <= 0) {
        Log(L"时间到，当前状态: " + std::to_wstring(static_cast<int>(_state)));
        
        // 准备执行的动作
        std::wstring reminderMsg;
        std::wstring ttsMsg;
        bool doPlayTTS = false;
        bool stateChanged = false;
        auto onReminderCallback = _onReminderCallback;

        // 时间到，切换状态
        if (_state == TomatoState::WORKING) {
            // 工作时间到，判断是否需要长休息
            _completedPomodoros++;
            Log(L"完成一个番茄钟，总数: " + std::to_wstring(_completedPomodoros));
            
            bool needLongRest = (_completedPomodoros % _config.longRestAfterPomodoros == 0);
            
            if (needLongRest) {
                Log(L"触发长休息");
                reminderMsg = L"工作时间到！已完成4个番茄钟，进行长休息吧。";
                ttsMsg = _config.longRestReminderText;
                
                switchState(TomatoState::RESTING);
                _remainingSeconds = _config.longRestMinutes * 60;
            } else {
                Log(L"触发短休息");
                reminderMsg = L"工作时间到！该休息一下了。";
                ttsMsg = _config.shortRestReminderText;
                
                switchState(TomatoState::RESTING);
                _remainingSeconds = _config.shortRestMinutes * 60;
            }
            stateChanged = true;
        } else if (_state == TomatoState::RESTING) {
            Log(L"休息结束，开始工作");
            reminderMsg = L"休息时间到！该开始工作了。";
            ttsMsg = _config.workReminderText;
            
            switchState(TomatoState::WORKING);
            _remainingSeconds = _config.workMinutes * 60;
            stateChanged = true;
        }
        
        if (stateChanged) {
            doPlayTTS = _config.enableTTS && !_ttsPlayed;
            if (doPlayTTS) _ttsPlayed = true;
        }
        
        // 解锁后执行耗时操作
        lock.unlock();

        if (stateChanged) {
            showReminder(reminderMsg);
            if (doPlayTTS) {
                playTTS(ttsMsg);
            }
            // 触发回调
            if (onReminderCallback) {
                onReminderCallback();
            }
        }
    } else {
        // 剩余时间大于0，重置TTS播放标志
        _ttsPlayed = false;
    }
}

void TomatoTimer::showReminder(const std::wstring& message) {
    // 显示自动消失的提醒窗口，持续5秒
    createAutoCloseWindow(L"番茄提醒", message, 5000);
}

void TomatoTimer::playTTS(const std::wstring& text) {
    // 初始化COM（如果还没有初始化）
    if (!_comInitialized) {
        HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
        if (SUCCEEDED(hr)) {
            _comInitialized = true;
        } else if (hr == RPC_E_CHANGED_MODE) {
            // COM已经以不同的模式初始化，继续使用
            _comInitialized = false;
        } else {
            // COM初始化失败，返回
            return;
        }
    }
    
    ISpVoice* pVoice = nullptr;
    HRESULT hr = CoCreateInstance(CLSID_SpVoice, nullptr, CLSCTX_ALL, IID_ISpVoice, (void**)&pVoice);
    
    if (SUCCEEDED(hr) && pVoice) {
        // 设置语音属性
        pVoice->SetVolume(100);  // 设置音量为最大
        // 使用同步播放，确保语音播放完成后再释放对象
        pVoice->Speak(text.c_str(), SPF_PURGEBEFORESPEAK, nullptr);
        pVoice->Release();
    }
}

void TomatoTimer::switchState(TomatoState newState) {
    _state = newState;
}

// 测试TTS功能
void TomatoTimer::testTTS() {
    playTTS(L"这是TTS语音测试，如果您能听到这段话，说明TTS功能正常工作。");
}

// 自动关闭窗口的定时器回调
void CALLBACK AutoCloseTimerProc(HWND hwnd, UINT uMsg, UINT_PTR idEvent, DWORD dwTime) {
    KillTimer(hwnd, idEvent);
    DestroyWindow(hwnd);
}

// 自动关闭窗口的消息处理
LRESULT CALLBACK AutoCloseWndProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_CREATE: {
            CREATESTRUCT* pCreate = reinterpret_cast<CREATESTRUCT*>(lParam);
            int duration = reinterpret_cast<int>(pCreate->lpCreateParams);
            SetTimer(hwnd, 1, duration, AutoCloseTimerProc);
            
            // 设置窗口为顶层窗口
            SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
            
            // 居中显示
            RECT rc;
            GetWindowRect(hwnd, &rc);
            int screenWidth = GetSystemMetrics(SM_CXSCREEN);
            int screenHeight = GetSystemMetrics(SM_CYSCREEN);
            int x = (screenWidth - (rc.right - rc.left)) / 2;
            int y = (screenHeight - (rc.bottom - rc.top)) / 2;
            SetWindowPos(hwnd, HWND_TOPMOST, x, y, 0, 0, SWP_NOSIZE);
            
            return 0;
        }
        
        case WM_CTLCOLORSTATIC: {
            HDC hdcStatic = reinterpret_cast<HDC>(wParam);
            SetBkMode(hdcStatic, TRANSPARENT);
            SetTextColor(hdcStatic, RGB(0, 0, 0));
            return reinterpret_cast<LRESULT>(GetStockObject(NULL_BRUSH));
        }
        
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            
            // 绘制圆角矩形背景
            RECT rc;
            GetClientRect(hwnd, &rc);
            
            HBRUSH hBrush = CreateSolidBrush(RGB(255, 255, 200));
            HPEN hPen = CreatePen(PS_SOLID, 2, RGB(200, 150, 50));
            
            HPEN hOldPen = reinterpret_cast<HPEN>(SelectObject(hdc, hPen));
            HBRUSH hOldBrush = reinterpret_cast<HBRUSH>(SelectObject(hdc, hBrush));
            
            RoundRect(hdc, rc.left, rc.top, rc.right, rc.bottom, 20, 20);
            
            SelectObject(hdc, hOldPen);
            SelectObject(hdc, hOldBrush);
            DeleteObject(hPen);
            DeleteObject(hBrush);
            
            EndPaint(hwnd, &ps);
            return 0;
        }
        
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
            
        default:
            return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
}

// 创建自动消失的提醒窗口（在独立线程中运行）
void TomatoTimer::createAutoCloseWindow(const std::wstring& title, const std::wstring& message, int durationMs) {
    // 创建参数结构体的副本
    AutoCloseWindowParams* params = new AutoCloseWindowParams{title, message, durationMs};
    
    // 在独立线程中显示窗口
    std::thread([params]() {
        static const wchar_t CLASS_NAME[] = L"TomatoAutoCloseWindow";
        
        // 注册窗口类
        WNDCLASSW wc = {};
        wc.lpfnWndProc = AutoCloseWndProc;
        wc.hInstance = GetModuleHandle(nullptr);
        wc.lpszClassName = CLASS_NAME;
        wc.hbrBackground = reinterpret_cast<HBRUSH>(GetStockObject(NULL_BRUSH));
        wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
        
        static bool classRegistered = false;
        if (!classRegistered) {
            RegisterClassW(&wc);
            classRegistered = true;
        }
        
        // 计算窗口大小
        HDC hdc = GetDC(nullptr);
        HFONT hFont = CreateFont(20, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                                 DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                                 DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, L"Microsoft YaHei");
        HFONT hOldFont = reinterpret_cast<HFONT>(SelectObject(hdc, hFont));
        
        SIZE textSize;
        GetTextExtentPoint32W(hdc, params->message.c_str(), static_cast<int>(params->message.length()), &textSize);
        
        SelectObject(hdc, hOldFont);
        DeleteObject(hFont);
        ReleaseDC(nullptr, hdc);
        
        int windowWidth = textSize.cx + 60;
        int windowHeight = textSize.cy + 60;
        
        // 创建窗口
        HWND hwnd = CreateWindowExW(
            WS_EX_TOPMOST | WS_EX_TOOLWINDOW,
            CLASS_NAME,
            params->title.c_str(),
            WS_POPUP,
            0, 0, windowWidth, windowHeight,
            nullptr, nullptr, GetModuleHandle(nullptr), reinterpret_cast<LPVOID>(params->durationMs)
        );
        
        if (hwnd) {
            // 创建静态文本控件
            HWND hStatic = CreateWindowExW(
                0, L"STATIC", params->message.c_str(),
                WS_CHILD | WS_VISIBLE | SS_CENTER,
                30, 30, textSize.cx, textSize.cy,
                hwnd, nullptr, GetModuleHandle(nullptr), nullptr
            );
            
            if (hStatic) {
                HFONT hFont = CreateFont(20, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                                         DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                                         DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, L"Microsoft YaHei");
                SendMessage(hStatic, WM_SETFONT, reinterpret_cast<WPARAM>(hFont), TRUE);
            }
            
            ShowWindow(hwnd, SW_SHOW);
            UpdateWindow(hwnd);
            
            // 消息循环
            MSG msg;
            while (GetMessage(&msg, nullptr, 0, 0)) {
                TranslateMessage(&msg);
                DispatchMessage(&msg);
            }
        }
        
        // 清理参数
        delete params;
    }).detach();
}
