# Requirements Document

## Introduction

Bu proje, GamePP benzeri bir sistem izleme ve oyun optimizasyon uygulamasıdır. Uygulama, gerçek zamanlı donanım izleme, oyun içi overlay (OSD), sistem optimizasyonu ve kullanıcı dostu bir arayüz sunacaktır. Python + C++ hibrit mimarisi kullanılarak geliştirilecektir.

## Glossary

- **OSD (On-Screen Display)**: Oyun ekranı üzerinde gösterilen bilgi katmanı
- **Overlay**: Oyun grafiklerinin üzerine çizilen şeffaf bilgi penceresi
- **Hook**: Bir programın fonksiyonlarına müdahale etme tekniği
- **DirectX Hook**: DirectX API fonksiyonlarına bağlanarak overlay çizme yöntemi
- **FPS (Frames Per Second)**: Saniyedeki kare sayısı
- **Frame Time**: İki kare arasındaki süre (milisaniye)
- **VRAM**: Ekran kartı belleği
- **WMI (Windows Management Instrumentation)**: Windows sistem bilgilerine erişim API'si
- **NvAPI**: NVIDIA GPU bilgilerine erişim SDK'sı
- **ADL SDK**: AMD GPU bilgilerine erişim SDK'sı
- **ImGui**: Immediate Mode GUI kütüphanesi
- **SwapChain**: DirectX'te frame buffer yönetim zinciri
- **Timer Resolution**: Windows zamanlayıcı hassasiyeti

## Requirements

### Requirement 1: Sistem İzleme Motoru

**User Story:** As a gamer, I want to monitor my system's hardware metrics in real-time, so that I can track performance and temperatures during gameplay.

#### Acceptance Criteria

1. WHEN the monitoring engine starts, THE System SHALL collect CPU temperature and usage percentage every 500 milliseconds
2. WHEN the monitoring engine starts, THE System SHALL collect GPU temperature and usage percentage every 500 milliseconds
3. WHEN the monitoring engine starts, THE System SHALL collect RAM and VRAM usage in megabytes every 500 milliseconds
4. WHEN the monitoring engine starts, THE System SHALL collect SSD temperature every 2 seconds
5. WHEN the monitoring engine starts, THE System SHALL collect network ping, upload and download speeds every 1 second
6. WHEN hardware data is collected, THE System SHALL store the data in a structured format for display and logging
7. IF a hardware sensor is unavailable, THEN THE System SHALL display "N/A" for that metric and continue monitoring other sensors

### Requirement 2: FPS ve Frame Time Ölçümü

**User Story:** As a gamer, I want to see my current FPS, frame time, and percentile metrics, so that I can evaluate game performance and stability in real-time.

#### Acceptance Criteria

1. WHEN a DirectX 9/11/12 game is running, THE System SHALL hook into the Present() function to measure FPS
2. WHEN measuring FPS, THE System SHALL calculate frames per second by measuring time between consecutive Present() calls
3. WHEN measuring frame time, THE System SHALL display the duration in milliseconds between frames
4. WHEN FPS data is collected, THE System SHALL calculate and display 1% low and 0.1% low FPS values
5. WHEN calculating percentile FPS, THE System SHALL use a rolling window of the last 1000 frames
6. WHEN FPS data is collected, THE System SHALL update the display at minimum 10 times per second
7. IF the game uses a different graphics API, THEN THE System SHALL detect and report the unsupported API type

### Requirement 3: Oyun İçi Overlay (OSD)

**User Story:** As a gamer, I want to see system metrics overlaid on my game screen, so that I can monitor performance without alt-tabbing.

#### Acceptance Criteria

1. WHEN a supported game is running, THE System SHALL inject the overlay DLL into the game process
2. WHEN the overlay is active, THE System SHALL render metrics using ImGui on top of the game graphics
3. WHEN rendering the overlay, THE System SHALL display FPS, CPU usage, GPU usage, temperatures, and RAM usage
4. WHEN the overlay is displayed, THE System SHALL maintain transparency and minimal visual obstruction
5. WHEN the user presses a configurable hotkey, THE System SHALL toggle overlay visibility
6. IF DLL injection fails, THEN THE System SHALL log the error and notify the user without crashing

### Requirement 4: Overlay Tasarım Düzenleyici (HUD Designer)

**User Story:** As a user, I want to customize the overlay appearance with themes and detailed options, so that I can personalize the display to my preferences.

#### Acceptance Criteria

1. WHEN the user opens the HUD designer, THE System SHALL display options for font selection, color, position, size, and opacity
2. WHEN the user selects a font, THE System SHALL apply the selected font to the overlay text
3. WHEN the user selects a color, THE System SHALL apply the selected color to the overlay elements
4. WHEN the user selects a position (top-left, top-right, bottom-left, bottom-right, center), THE System SHALL move the overlay to that screen position
5. WHEN the user adjusts the opacity slider, THE System SHALL update overlay transparency from 0% to 100%
6. WHEN the user selects a theme, THE System SHALL apply a pre-configured set of colors, fonts, and layout styles
7. WHEN the user saves settings, THE System SHALL persist the configuration to a settings file
8. WHEN the application restarts, THE System SHALL load and apply the saved overlay settings
9. WHEN the user creates a custom theme, THE System SHALL allow saving and sharing theme files

### Requirement 5: Sistem Optimizasyon Motoru

**User Story:** As a gamer, I want to optimize my system for gaming, so that I can get better performance during gameplay.

#### Acceptance Criteria

1. WHEN the user activates game mode, THE System SHALL terminate non-essential background processes from a configurable list
2. WHEN the user activates game mode, THE System SHALL set the game process priority to "High" or "Realtime"
3. WHEN the user activates game mode, THE System SHALL set Windows Timer Resolution to 0.5ms for improved input latency
4. WHEN the user activates game mode, THE System SHALL clear standby RAM to free memory
5. WHEN the user deactivates game mode, THE System SHALL restore original process priorities and timer resolution
6. WHEN optimization actions are performed, THE System SHALL log all changes for user review
7. IF a process cannot be terminated, THEN THE System SHALL skip that process and continue with remaining optimizations

### Requirement 6: Kullanıcı Arayüzü (UI)

**User Story:** As a user, I want a modern and intuitive interface, so that I can easily access all features of the application.

#### Acceptance Criteria

1. WHEN the application starts, THE System SHALL display a dashboard with real-time system metrics and graphs
2. WHEN the user navigates to different sections, THE System SHALL display pages for Dashboard, Overlay Editor, System Monitor, Optimizer, and Settings
3. WHEN displaying metrics, THE System SHALL render line graphs for CPU, GPU, and FPS history over the last 60 seconds
4. WHEN the user interacts with the UI, THE System SHALL respond within 100 milliseconds
5. WHEN the application is minimized, THE System SHALL display a system tray icon for quick access
6. WHEN the user clicks the tray icon, THE System SHALL restore the main window

### Requirement 7: Benchmark ve Loglama Sistemi

**User Story:** As a user, I want to log and export performance data, so that I can analyze system performance over time.

#### Acceptance Criteria

1. WHEN logging is enabled, THE System SHALL record FPS, CPU, GPU, temperatures, and RAM usage with timestamps
2. WHEN the user requests an export, THE System SHALL generate a CSV file with all logged data
3. WHEN displaying benchmark results, THE System SHALL show minimum, maximum, average, 1% low, and 0.1% low FPS values
4. WHEN a logging session ends, THE System SHALL save the log file with a timestamp-based filename
5. WHEN the user views history, THE System SHALL display graphs from previously saved log files
6. WHEN displaying FPS graphs, THE System SHALL highlight frame drops and stuttering events visually

### Requirement 8: Servis Modu (Arka Plan Çalışma)

**User Story:** As a user, I want the application to run in the background and start automatically, so that monitoring is always available.

#### Acceptance Criteria

1. WHEN Windows starts, THE System SHALL launch automatically if auto-start is enabled in settings
2. WHILE the application runs in background mode, THE System SHALL consume less than 1% CPU and 100MB RAM
3. WHEN a supported game is detected, THE System SHALL automatically activate the overlay
4. WHEN the user closes the main window, THE System SHALL continue running in the system tray
5. WHEN the user selects "Exit" from the tray menu, THE System SHALL terminate all processes and release resources

### Requirement 9: Ayarlar ve Yapılandırma

**User Story:** As a user, I want to configure application settings, so that I can customize behavior to my needs.

#### Acceptance Criteria

1. WHEN the user opens settings, THE System SHALL display options for auto-start, hotkeys, overlay defaults, and optimization preferences
2. WHEN the user changes a hotkey, THE System SHALL validate that the key combination is not already in use
3. WHEN settings are modified, THE System SHALL save changes immediately to a configuration file
4. WHEN the configuration file is corrupted, THE System SHALL reset to default settings and notify the user
5. WHEN the user requests a settings reset, THE System SHALL restore all options to factory defaults

### Requirement 10: Görsel Filtre ve Renk İyileştirme

**User Story:** As a gamer, I want to enhance game visuals with filters, so that I can improve color vibrancy and image sharpness.

#### Acceptance Criteria

1. WHEN the user enables vibrance filter, THE System SHALL increase color saturation by the specified percentage (0-100%)
2. WHEN the user enables sharpening filter, THE System SHALL apply image sharpening with adjustable intensity (0-100%)
3. WHEN the user adjusts brightness, THE System SHALL modify game brightness from -50% to +50%
4. WHEN the user adjusts contrast, THE System SHALL modify game contrast from -50% to +50%
5. WHEN filters are applied, THE System SHALL render them using DirectX post-processing shaders
6. WHEN the user saves a filter preset, THE System SHALL store the configuration for quick application
7. WHEN the user disables filters, THE System SHALL restore original game rendering without restart
8. IF shader compilation fails, THEN THE System SHALL disable filters and notify the user

### Requirement 11: Stabilite ve Hata Yönetimi

**User Story:** As a user, I want the application to be stable and reliable, so that it doesn't crash or interfere with my games.

#### Acceptance Criteria

1. WHEN an error occurs, THE System SHALL log the error with timestamp, context, and stack trace
2. WHEN a critical error occurs, THE System SHALL attempt graceful recovery without crashing the game
3. WHEN DLL injection fails, THE System SHALL retry up to 3 times with exponential backoff
4. WHEN hardware monitoring fails, THE System SHALL continue operating with available sensors
5. WHEN the application crashes, THE System SHALL generate a crash dump for debugging
6. WHEN the user reports an issue, THE System SHALL provide an option to export logs and diagnostics
7. WHEN the overlay causes FPS drops, THE System SHALL automatically reduce update frequency
8. WHEN memory usage exceeds 200MB, THE System SHALL log a warning and clear cached data
9. IF the game is incompatible, THEN THE System SHALL add it to a blacklist and skip injection

### Requirement 12: Şeffaflık ve Güvenlik

**User Story:** As a user, I want to trust the application and understand what it does, so that I feel safe using it.

#### Acceptance Criteria

1. WHEN the application starts, THE System SHALL display a clear explanation of what processes it monitors
2. WHEN the user views the about page, THE System SHALL show the open-source license and repository link
3. WHEN the application collects data, THE System SHALL only store data locally and never transmit to external servers
4. WHEN the user requests, THE System SHALL display a list of all active hooks and injected DLLs
5. WHEN optimization is performed, THE System SHALL show exactly which processes are terminated and why
6. WHEN the user views permissions, THE System SHALL explain why administrator access is required
7. WHEN updates are available, THE System SHALL display changelog and allow manual update approval
