#pragma once
#include <d3d11.h>
#include <dxgi.h>
#include <chrono>

typedef HRESULT(__stdcall* PresentFunc)(IDXGISwapChain*, UINT, UINT);

class DX11Hook {
public:
    static DX11Hook& GetInstance();
    
    bool Initialize();
    void Shutdown();
    float GetFPS() const;
    float GetFrameTime() const;
    void SetMetrics(float cpu, float cpuTemp, float gpu, float gpuTemp, int ram, int vram);
    
    // Hook callback
    static HRESULT __stdcall HookedPresent(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags);
    
private:
    DX11Hook() = default;
    void CalculateFPS();
    
    ID3D11Device* device = nullptr;
    ID3D11DeviceContext* context = nullptr;
    IDXGISwapChain* swapChain = nullptr;
    
    PresentFunc originalPresent = nullptr;
    bool initialized = false;
    
    // FPS calculation
    std::chrono::high_resolution_clock::time_point lastFrameTime;
    float currentFPS = 0.0f;
    float frameTime = 0.0f;
    int frameCount = 0;
    float fpsAccumulator = 0.0f;
    
    // Metrics for overlay
    float cpuUsage = 0.0f;
    float cpuTemp = 0.0f;
    float gpuUsage = 0.0f;
    float gpuTemp = 0.0f;
    int ramUsage = 0;
    int vramUsage = 0;
};
