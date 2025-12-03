// DX11 Hook Implementation
#include "dx11_hook.h"
#include "../overlay/imgui_overlay.h"

DX11Hook& DX11Hook::GetInstance() {
    static DX11Hook instance;
    return instance;
}

bool DX11Hook::Initialize() {
    if (initialized) return true;
    
    // Create dummy window and device for vtable access
    WNDCLASSEX wc = { sizeof(WNDCLASSEX), CS_CLASSDC, DefWindowProc, 0, 0, 
                     GetModuleHandle(NULL), NULL, NULL, NULL, NULL, 
                     L"DX11Hook", NULL };
    RegisterClassEx(&wc);
    HWND hwnd = CreateWindow(wc.lpszClassName, L"", WS_OVERLAPPEDWINDOW, 
                            0, 0, 100, 100, NULL, NULL, wc.hInstance, NULL);
    
    DXGI_SWAP_CHAIN_DESC scd = {};
    scd.BufferCount = 1;
    scd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    scd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    scd.OutputWindow = hwnd;
    scd.SampleDesc.Count = 1;
    scd.Windowed = TRUE;
    
    D3D_FEATURE_LEVEL featureLevel;
    HRESULT hr = D3D11CreateDeviceAndSwapChain(
        NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, 0, NULL, 0,
        D3D11_SDK_VERSION, &scd, &swapChain, &device, &featureLevel, &context
    );
    
    if (FAILED(hr)) {
        DestroyWindow(hwnd);
        UnregisterClass(wc.lpszClassName, wc.hInstance);
        return false;
    }
    
    // Get Present function pointer from vtable
    void** vtable = *reinterpret_cast<void***>(swapChain);
    originalPresent = reinterpret_cast<PresentFunc>(vtable[8]); // Present is at index 8
    
    // Hook would be installed here using MinHook or similar
    // For now, store the original for reference
    
    lastFrameTime = std::chrono::high_resolution_clock::now();
    initialized = true;
    
    // Cleanup dummy resources
    swapChain->Release();
    context->Release();
    device->Release();
    DestroyWindow(hwnd);
    UnregisterClass(wc.lpszClassName, wc.hInstance);
    
    return true;
}

void DX11Hook::Shutdown() {
    // Restore original Present if hooked
    initialized = false;
}

void DX11Hook::CalculateFPS() {
    auto now = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(now - lastFrameTime);
    frameTime = duration.count() / 1000.0f; // Convert to ms
    lastFrameTime = now;
    
    frameCount++;
    fpsAccumulator += frameTime;
    
    // Update FPS every 500ms
    if (fpsAccumulator >= 500.0f) {
        currentFPS = (frameCount * 1000.0f) / fpsAccumulator;
        frameCount = 0;
        fpsAccumulator = 0.0f;
    }
}

HRESULT __stdcall DX11Hook::HookedPresent(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags) {
    auto& hook = GetInstance();
    hook.CalculateFPS();
    
    // Render overlay here
    // ImGuiOverlay::Render(...)
    
    // Call original Present
    return hook.originalPresent(pSwapChain, SyncInterval, Flags);
}

float DX11Hook::GetFPS() const {
    return currentFPS;
}

float DX11Hook::GetFrameTime() const {
    return frameTime;
}

void DX11Hook::SetMetrics(float cpu, float cpuT, float gpu, float gpuT, int ram, int vram) {
    cpuUsage = cpu;
    cpuTemp = cpuT;
    gpuUsage = gpu;
    gpuTemp = gpuT;
    ramUsage = ram;
    vramUsage = vram;
}
