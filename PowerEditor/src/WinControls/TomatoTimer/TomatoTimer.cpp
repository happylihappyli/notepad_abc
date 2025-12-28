// 番茄提醒功能实现文件
#include "TomatoTimer.h"
#include <iostream>
#include <sstream>
#include <windows.h>
#include <commctrl.h>
#include <sapi.h>
#include <thread>
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "sapi.lib")

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
    if (_state != TomatoState::IDLE && _state != TomatoState::PAUSED) {
        return;
    }

    if (_state == TomatoState::IDLE) {
        _state = TomatoState::WORKING;
        _remainingSeconds = _config.workMinutes * 60;
    } else {
        _state = (_state == TomatoState::PAUSED) ? _state : TomatoState::WORKING;
    }

    _startTime = std::chrono::system_clock::now();

    // 创建定时器
    if (_timer == nullptr) {
        CreateTimerQueueTimer(&_timer, nullptr, timerCallback, this, 1000, 1000, 0);
    }
}

void TomatoTimer::pause() {
    if (_state == TomatoState::WORKING || _state == TomatoState::RESTING) {
        _state = TomatoState::PAUSED;
    }
}

void TomatoTimer::resume() {
    if (_state == TomatoState::PAUSED) {
        // 根据剩余时间判断之前的状态
        int maxRestSeconds = (_config.longRestMinutes > _config.shortRestMinutes) 
                           ? _config.longRestMinutes * 60 
                           : _config.shortRestMinutes * 60;
        _state = (_remainingSeconds > maxRestSeconds) ? TomatoState::WORKING : TomatoState::RESTING;
    }
}

void TomatoTimer::stop() {
    if (_timer != nullptr) {
        DeleteTimerQueueTimer(nullptr, _timer, nullptr);
        _timer = nullptr;
    }
    _state = TomatoState::IDLE;
    _remainingSeconds = 0;
}

void TomatoTimer::reset() {
    stop();
    _remainingSeconds = _config.workMinutes * 60;
    _completedPomodoros = 0;
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

void TomatoTimer::setConfig(const TomatoConfig& config) {
    _config = config;
    if (_state == TomatoState::IDLE) {
        _remainingSeconds = _config.workMinutes * 60;
    }
}

TomatoConfig TomatoTimer::getConfig() const {
    return _config;
}

void TomatoTimer::setOnReminderCallback(std::function<void()> callback) {
    _onReminderCallback = callback;
}

void CALLBACK TomatoTimer::timerCallback(PVOID lpParameter, BOOLEAN TimerOrWaitFired) {
    TomatoTimer* timer = static_cast<TomatoTimer*>(lpParameter);
    if (timer) {
        timer->handleTimerEvent();
    }
}

void TomatoTimer::handleTimerEvent() {
    if (_state == TomatoState::IDLE || _state == TomatoState::PAUSED) {
        return;
    }

    _remainingSeconds--;

    if (_remainingSeconds <= 0) {
        // 时间到，切换状态
        if (_state == TomatoState::WORKING) {
            // 工作时间到，判断是否需要长休息
            _completedPomodoros++;
            bool needLongRest = (_completedPomodoros % _config.longRestAfterPomodoros == 0);
            
            std::wcout << L"番茄钟完成数: " << _completedPomodoros << L", 长休息周期: " << _config.longRestAfterPomodoros << L", 是否长休息: " << (needLongRest ? L"是" : L"否") << std::endl;
            
            if (needLongRest) {
                showReminder(L"工作时间到！已完成4个番茄钟，进行长休息吧。");
                if (_config.enableTTS && !_ttsPlayed) {
                    playTTS(_config.longRestReminderText);
                    _ttsPlayed = true;
                }
                switchState(TomatoState::RESTING);
                _remainingSeconds = _config.longRestMinutes * 60;
            } else {
                showReminder(L"工作时间到！该休息一下了。");
                if (_config.enableTTS && !_ttsPlayed) {
                    playTTS(_config.shortRestReminderText);
                    _ttsPlayed = true;
                }
                switchState(TomatoState::RESTING);
                _remainingSeconds = _config.shortRestMinutes * 60;
            }
        } else if (_state == TomatoState::RESTING) {
            showReminder(L"休息时间到！该开始工作了。");
            if (_config.enableTTS && !_ttsPlayed) {
                playTTS(_config.workReminderText);
                _ttsPlayed = true;
            }
            switchState(TomatoState::WORKING);
            _remainingSeconds = _config.workMinutes * 60;
        }

        // 触发回调
        if (_onReminderCallback) {
            _onReminderCallback();
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
