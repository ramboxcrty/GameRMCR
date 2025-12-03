// Hook Manager Implementation
#include "dx11_hook.h"

// Global hook instance
static DX11Hook g_hook;

bool InitializeHook() {
    return g_hook.Initialize();
}

void ShutdownHook() {
    g_hook.Shutdown();
}
