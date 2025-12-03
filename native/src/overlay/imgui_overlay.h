#pragma once
#include <d3d11.h>
#include <string>

struct OverlayMetrics {
    float fps = 0.0f;
    float frameTime = 0.0f;
    float cpuUsage = 0.0f;
    float cpuTemp = 0.0f;
    float gpuUsage = 0.0f;
    float gpuTemp = 0.0f;
    int ramUsage = 0;
    int vramUsage = 0;
};

struct OverlayConfig {
    char fontFamily[64] = "Segoe UI";
    int fontSize = 14;
    float color[4] = {0.0f, 1.0f, 0.5f, 1.0f};  // RGBA
    float opacity = 0.8f;
    bool showFPS = true;
    bool showCPU = true;
    bool showGPU = true;
    bool showRAM = true;
    bool showTemps = true;
};

class ImGuiOverlay {
public:
    static void Initialize(ID3D11Device* device, ID3D11DeviceContext* context);
    static void Shutdown();
    static void Render(const OverlayMetrics& metrics);
    static void SetVisible(bool visible);
    static void SetPosition(int x, int y);
    static void SetOpacity(float opacity);
    static void SetConfig(const OverlayConfig& config);
    static bool IsVisible();
    
    // For testing - returns what would be rendered
    static std::string GetRenderedText(const OverlayMetrics& metrics);
    
private:
    static bool isVisible;
    static bool initialized;
    static int posX;
    static int posY;
    static float opacity;
    static OverlayConfig config;
};
