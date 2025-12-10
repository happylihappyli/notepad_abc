
#include <windows.h>
#include <stdio.h>

// 手动实现简单的printf
void my_printf(const char* format, ...) {
    char buffer[256];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    
    DWORD written;
    WriteConsoleA(GetStdHandle(STD_OUTPUT_HANDLE), buffer, strlen(buffer), &written, NULL);
}

int main() {
    my_printf("Hello from static build!\n");
    return 0;
}
