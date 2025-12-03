// ImGui Overlay Implementation
#include "imgui_overlay.h"
#include <cstdio>
#include <cstring>

// Static member initialization
bool ImGuiOverlay::isVisible = true;
bool ImGuiOverlay::initialized = false;
int ImGuiOverlay::posX = 10;
int ImGuiOverlay::posY = 10;
float ImGuiOverlay::opacity = 0.8f;
OverlayConfig ImGuiOverlay::config = {};

void ImGuiOverlay::Initialize(ID3D11Device* device, ID3D11DeviceContext* context) {
    if (initialized) return;
    
    // Default config
    config.fontSize = 14;
    config.showFPS = true;
    config.showCPU = true;
    config.showGPU = true;
    config.showRAM = true;
    config.showTemps = true;
    strncpy(config.fontFamily, "Segoe UI", sizeof(config.fontFamily) - 1);
    config.color[0] = 0.0f;  // R
    config.color[1] = 1.0f;  // G
    config.color[2] = 0.5f;  // B
    config.color[3] = 1.0f;  // A
    
    // ImGui initialization would go here
    // ImGui::CreateContext();
    // ImGui_ImplWin32_Init(hwnd);
    // ImGui_ImplDX11_Init(device, context);
    
    initialized = true;
}

void ImGuiOverlay::Shutdown() {
    if (!initialized) return;
    
    // ImGui cleanup
    // ImGui_ImplDX11_Shutdown();
    // ImGui_ImplWin32_Shutdown();
    // ImGui::DestroyContext();
    
    initialized = false;
}

void ImGuiOverlay::Render(const OverlayMetrics& metrics) {
    if (!isVisible || !initialized) return;
    
    // Begin ImGui frame
    // ImGui_ImplDX11_NewFrame();
    // ImGui_ImplWin32_NewFrame();
    // ImGui::NewFrame();
    
    // Set window position and style
    // ImGui::SetNextWindowPos(ImVec2((float)posX, (float)posY), ImGuiCond_Always);
    // ImGui::SetNextWindowBgAlpha(opacity);
    
    // ImGuiWindowFlags flags = ImGuiWindowFlags_NoDecoration | 
    //                          ImGuiWindowFlags_AlwaysAutoResize |
    //                          ImGuiWindowFlags_NoSavedSettings |
    //                          ImGuiWindowFlags_NoFocusOnAppearing |
    //                          ImGuiWindowFlags_NoNav;
    
    // ImGui::Begin("GamePP Overlay", nullptr, flags);
    
    // Build overlay text
    char buffer[512];
    int offset = 0;
    
    if (config.showFPS) {
        offset += snprintf(buffer + offset, sizeof(buffer) - offset, 
                          "FPS: %.1f\n", metrics.fps);
    }
    
    if (config.showCPU) {
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "CPU: %.1f%%", metrics.cpuUsage);
        if (config.showTemps) {
            offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                              " (%.0f°C)", metrics.cpuTemp);
        }
        offset += snprintf(buffer + offset, sizeof(buffer) - offset, "\n");
    }
    
    if (config.showGPU) {
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "GPU: %.1f%%", metrics.gpuUsage);
        if (config.showTemps) {
            offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                              " (%.0f°C)", metrics.gpuTemp);
        }
        offset += snprintf(buffer + offset, sizeof(buffer) - offset, "\n");
    }
    
    if (config.showRAM) {
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "RAM: %d MB\n", metrics.ramUsage);
        offset += snprintf(buffer + offset, sizeof(buffer) - offset,
                          "VRAM: %d MB\n", metrics.vramUsage);
    }
    
    // ImGui::TextColored(ImVec4(config.color[0], config.color[1], 
    //                          config.color[2], config.color[3]), 
    //                   "%s", buffer);
    
    // ImGui::End();
    
    // Render
    // ImGui::Render();
    // ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());
}

void ImGuiOverlay::SetVisible(bool visible) {
    isVisible = visible;
}

void ImGuiOverlay::SetPosition(int x, int y) {
    posX = x;
    posY = y;
}

void ImGuiOverlay::SetOpacity(float op) {
    opacity = op;
}

void ImGuiOverlay::SetConfig(const OverlayConfig& cfg) {
    config = cfg;
}

bool ImGuiOverlay::IsVisible() {
    return isVisible;
}

std::string ImGuiOverlay::GetRenderedText(const OverlayMetrics& metrics) {
    std::string result;
    
    if (config.showFPS) {
        char buf[64];
        snprintf(buf, sizeof(buf), "FPS: %.1f\n", metrics.fps);
        result += buf;
    }
    
    if (config.showCPU) {
        char buf[64];
        snprintf(buf, sizeof(buf), "CPU: %.1f%%", metrics.cpuUsage);
        result += buf;
        if (config.showTemps) {
            snprintf(buf, sizeof(buf), " (%.0f°C)", metrics.cpuTemp);
            result += buf;
        }
        result += "\n";
    }
    
    if (config.showGPU) {
        char buf[64];
        snprintf(buf, sizeof(buf), "GPU: %.1f%%", metrics.gpuUsage);
        result += buf;
        if (config.showTemps) {
            snprintf(buf, sizeof(buf), " (%.0f°C)", metrics.gpuTemp);
            result += buf;
        }
        result += "\n";
    }
    
    if (config.showRAM) {
        char buf[64];
        snprintf(buf, sizeof(buf), "RAM: %d MB\n", metrics.ramUsage);
        result += buf;
        snprintf(buf, sizeof(buf), "VRAM: %d MB\n", metrics.vramUsage);
        result += buf;
    }
    
    return result;
}
