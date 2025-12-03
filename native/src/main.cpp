// GamePP Overlay DLL Entry Point
#define GAMEPP_EXPORTS
#include "../include/exports.h"
#include "dxhook/dx11_hook.h"
#include "overlay/imgui_overlay.h"
#include <windows.h>

static OverlayMetrics g_metrics;
static OverlayConfig g_config;
static const char* VERSION = "1.0.0";

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        DisableThreadLibraryCalls(hModule);
        break;
    case DLL_PROCESS_DETACH:
        Shutdown();
        break;
    }
    return TRUE;
}

// Exported functions
extern "C" {

GAMEPP_API bool Initialize() {
    return DX11Hook::GetInstance().Initialize();
}

GAMEPP_API void Shutdown() {
    ImGuiOverlay::Shutdown();
    DX11Hook::GetInstance().Shutdown();
}

GAMEPP_API void SetMetrics(float cpu_usage, float cpu_temp, 
                           float gpu_usage, float gpu_temp, 
                           int ram_mb, int vram_mb) {
    DX11Hook::GetInstance().SetMetrics(cpu_usage, cpu_temp, gpu_usage, gpu_temp, ram_mb, vram_mb);
    
    g_metrics.cpuUsage = cpu_usage;
    g_metrics.cpuTemp = cpu_temp;
    g_metrics.gpuUsage = gpu_usage;
    g_metrics.gpuTemp = gpu_temp;
    g_metrics.ramUsage = ram_mb;
    g_metrics.vramUsage = vram_mb;
    g_metrics.fps = DX11Hook::GetInstance().GetFPS();
    g_metrics.frameTime = DX11Hook::GetInstance().GetFrameTime();
}

GAMEPP_API float GetCurrentFPS() {
    return DX11Hook::GetInstance().GetFPS();
}

GAMEPP_API float GetFrameTime() {
    return DX11Hook::GetInstance().GetFrameTime();
}

GAMEPP_API void SetOverlayVisible(bool visible) {
    ImGuiOverlay::SetVisible(visible);
}

GAMEPP_API void SetOverlayPosition(int x, int y) {
    ImGuiOverlay::SetPosition(x, y);
}

GAMEPP_API void SetOverlayOpacity(float opacity) {
    ImGuiOverlay::SetOpacity(opacity);
}

GAMEPP_API bool IsOverlayVisible() {
    return ImGuiOverlay::IsVisible();
}

GAMEPP_API void SetOverlayColor(float r, float g, float b, float a) {
    g_config.color[0] = r;
    g_config.color[1] = g;
    g_config.color[2] = b;
    g_config.color[3] = a;
    ImGuiOverlay::SetConfig(g_config);
}

GAMEPP_API void SetOverlayFontSize(int size) {
    g_config.fontSize = size;
    ImGuiOverlay::SetConfig(g_config);
}

GAMEPP_API void SetOverlayShowFPS(bool show) {
    g_config.showFPS = show;
    ImGuiOverlay::SetConfig(g_config);
}

GAMEPP_API void SetOverlayShowCPU(bool show) {
    g_config.showCPU = show;
    ImGuiOverlay::SetConfig(g_config);
}

GAMEPP_API void SetOverlayShowGPU(bool show) {
    g_config.showGPU = show;
    ImGuiOverlay::SetConfig(g_config);
}

GAMEPP_API void SetOverlayShowRAM(bool show) {
    g_config.showRAM = show;
    ImGuiOverlay::SetConfig(g_config);
}

GAMEPP_API void SetOverlayShowTemps(bool show) {
    g_config.showTemps = show;
    ImGuiOverlay::SetConfig(g_config);
}

GAMEPP_API const char* GetVersion() {
    return VERSION;
}

}
