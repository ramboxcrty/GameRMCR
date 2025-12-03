#pragma once

#ifdef GAMEPP_EXPORTS
#define GAMEPP_API __declspec(dllexport)
#else
#define GAMEPP_API __declspec(dllimport)
#endif

extern "C" {
    // Initialization
    GAMEPP_API bool Initialize();
    GAMEPP_API void Shutdown();
    
    // Metrics
    GAMEPP_API void SetMetrics(float cpu_usage, float cpu_temp, 
                               float gpu_usage, float gpu_temp, 
                               int ram_mb, int vram_mb);
    
    // FPS data
    GAMEPP_API float GetCurrentFPS();
    GAMEPP_API float GetFrameTime();
    
    // Overlay control
    GAMEPP_API void SetOverlayVisible(bool visible);
    GAMEPP_API void SetOverlayPosition(int x, int y);
    GAMEPP_API void SetOverlayOpacity(float opacity);
    GAMEPP_API bool IsOverlayVisible();
    
    // Overlay config
    GAMEPP_API void SetOverlayColor(float r, float g, float b, float a);
    GAMEPP_API void SetOverlayFontSize(int size);
    GAMEPP_API void SetOverlayShowFPS(bool show);
    GAMEPP_API void SetOverlayShowCPU(bool show);
    GAMEPP_API void SetOverlayShowGPU(bool show);
    GAMEPP_API void SetOverlayShowRAM(bool show);
    GAMEPP_API void SetOverlayShowTemps(bool show);
    
    // Version info
    GAMEPP_API const char* GetVersion();
}
