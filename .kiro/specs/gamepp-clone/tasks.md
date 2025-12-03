# Implementation Plan

## Phase 1: Project Setup and Core Infrastructure

- [x] 1. Set up project structure and dependencies

  - [x] 1.1 Create directory structure for src/, native/, tests/, config/


    - Create all folders as defined in design document


    - _Requirements: All_
  - [x] 1.2 Set up Python virtual environment and install dependencies


    - Install PyQt6, psutil, wmi, hypothesis, pytest
    - Create requirements.txt
    - _Requirements: All_


  - [x] 1.3 Create base configuration and data model classes


    - Implement all dataclasses from design (CPUMetrics, GPUMetrics, SystemMetrics, etc.)
    - Implement AppConfig, OverlayConfig, OptimizerConfig, FilterConfig, Theme
    - Implement FPSPercentiles, ErrorLog, InjectionAttempt

    - _Requirements: 1.6, 4.1, 9.1, 10.1, 11.1_



- [x] 1.4 Write property test for metrics data structure

  - **Property 1: Metrics Data Structure Validity**
  - **Validates: Requirements 1.6**


## Phase 2: Configuration Manager

- [x] 2. Implement Configuration Manager

  - [x] 2.1 Create ConfigManager class with load/save functionality


    - Implement JSON serialization/deserialization
    - Handle file I/O operations

    - _Requirements: 4.6, 4.7, 9.3_
  - [x] 2.2 Implement config validation and default reset


    - Add validate() method for config integrity

    - Add reset_to_defaults() method
    - _Requirements: 9.4, 9.5_
  - [x] 2.3 Implement hotkey conflict detection

    - Add hotkey validation logic
    - Check for duplicate assignments

    - _Requirements: 9.2_

- [x] 2.4 Write property test for config save/load round-trip

  - **Property 9: Config Save/Load Round-Trip**
  - **Validates: Requirements 4.7, 4.8**



- [x] 2.5 Write property test for config value persistence



  - **Property 6: Config Value Persistence**

  - **Validates: Requirements 4.2, 4.3, 4.4, 4.5**




- [x] 2.6 Write property test for hotkey conflict detection
  - **Property 18: Hotkey Conflict Detection**

  - **Validates: Requirements 9.2**

- [x] 2.7 Write property test for config reset to defaults
  - **Property 19: Config Reset to Defaults**
  - **Validates: Requirements 9.5**

- [x] 3. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: Hardware Monitoring Engine

- [x] 4. Implement Hardware Monitors

  - [x] 4.1 Create CPU monitor using WMI and psutil


    - Implement get_cpu_metrics() returning CPUMetrics
    - Handle sensor unavailability gracefully
    - _Requirements: 1.1, 1.7_
  - [x] 4.2 Create GPU monitor with NvAPI/ADL detection

    - Implement get_gpu_metrics() returning GPUMetrics
    - Detect GPU vendor and use appropriate SDK
    - _Requirements: 1.2, 1.7_
  - [x] 4.3 Create memory monitor for RAM and VRAM

    - Implement get_memory_metrics() returning MemoryMetrics
    - _Requirements: 1.3_

  - [x] 4.4 Create disk temperature monitor


    - Implement get_disk_metrics() returning DiskMetrics

    - _Requirements: 1.4_
  - [x] 4.5 Create network monitor for ping and bandwidth

    - Implement get_network_metrics() returning NetworkMetrics
    - _Requirements: 1.5_


- [x] 5. Implement Monitoring Engine

  - [x] 5.1 Create MonitoringEngine class with polling mechanism

    - Implement start(), stop(), subscribe() methods
    - Use threading for background polling
    - _Requirements: 1.1-1.5_

  - [x] 5.2 Implement subscriber notification system


    - Notify all subscribers when new metrics are collected
    - _Requirements: 1.6_


- [x] 5.3 Write unit tests for hardware monitors

  - Test each monitor with mocked system interfaces
  - _Requirements: 1.1-1.5_

- [x] 6. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 4: FPS Calculator with Percentiles

- [ ] 7. Implement FPS Calculator with Rolling Window

  - [ ] 7.1 Create FPSCalculator class with rolling window


    - Implement deque with maxlen=1000 for frame times
    - Implement add_frame(), get_current_fps(), get_frame_time_avg()
    - _Requirements: 2.2, 2.3, 2.5_

  - [ ] 7.2 Implement percentile FPS calculations

    - Implement get_percentile_fps(), get_1_percent_low(), get_0_1_percent_low()
    - Sort frame times and calculate percentiles
    - _Requirements: 2.4_

- [ ]* 7.3 Write property test for FPS calculation

  - **Property 2: FPS Calculation Correctness**
  - **Validates: Requirements 2.2, 2.3**

- [ ]* 7.4 Write property test for percentile FPS calculation

  - **Property 3: Percentile FPS Calculation**
  - **Validates: Requirements 2.4**

- [ ]* 7.5 Write property test for rolling window size

  - **Property 4: Rolling Window Size Constraint**
  - **Validates: Requirements 2.5**

## Phase 5: Theme Manager

- [ ] 8. Implement Theme Manager

  - [ ] 8.1 Create ThemeManager class

    - Implement load_themes(), get_theme(), apply_theme()
    - Load themes from themes/ directory
    - _Requirements: 4.6_

  - [ ] 8.2 Implement custom theme creation and export

    - Implement save_custom_theme(), export_theme(), import_theme()
    - Handle theme file I/O
    - _Requirements: 4.9_

- [ ]* 8.3 Write property test for theme application

  - **Property 7: Theme Application Completeness**
  - **Validates: Requirements 4.6**

- [ ]* 8.4 Write property test for theme save/load round-trip

  - **Property 8: Theme Save/Load Round-Trip**
  - **Validates: Requirements 4.9**

- [ ] 9. Create Default Themes

  - [ ] 9.1 Create default theme files

    - Create default.json, dark.json, neon.json in themes/
    - Define color schemes, fonts, layouts
    - _Requirements: 4.6_

- [ ] 10. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: Benchmark Logger with Frame Drop Detection



- [ ] 11. Implement Benchmark Logger with Percentiles

  - [ ] 11.1 Update BenchmarkLogger class

    - Update log_entry() to accept FPSPercentiles parameter
    - Store fps_1_percent_low and fps_0_1_percent_low in LogEntry
    - _Requirements: 7.1_

  - [ ] 11.2 Implement frame drop detection

    - Implement detect_frame_drops() method
    - Detect frames where FPS drops below 50% of average
    - _Requirements: 7.6_

  - [ ] 11.3 Update CSV export functionality

    - Include percentile FPS values in CSV export
    - _Requirements: 7.2, 7.4_

  - [ ] 11.4 Update benchmark statistics calculation

    - Include fps_0_1_percent_low in statistics
    - Include frame_drops list
    - _Requirements: 7.3_

- [ ]* 11.5 Write property test for frame drop detection

  - **Property 13: Frame Drop Detection**
  - **Validates: Requirements 7.6**

- [ ]* 11.6 Write property test for log entry completeness

  - **Property 14: Log Entry Completeness**
  - **Validates: Requirements 7.1**

- [ ]* 11.7 Write property test for CSV export round-trip

  - **Property 15: CSV Export Round-Trip**
  - **Validates: Requirements 7.2**

- [ ]* 11.8 Write property test for benchmark statistics

  - **Property 16: Benchmark Statistics Correctness**
  - **Validates: Requirements 7.3**

- [ ]* 11.9 Write property test for log filename timestamp

  - **Property 17: Log Filename Timestamp Format**
  - **Validates: Requirements 7.4**

- [ ] 12. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.


## Phase 7: Filter Manager

- [ ] 13. Implement Filter Manager

  - [ ] 13.1 Create FilterManager class

    - Implement apply_filter_config(), disable_all_filters()
    - Implement validate_filter_values()
    - _Requirements: 10.1-10.4, 10.7_

  - [ ] 13.2 Implement filter preset system

    - Implement save_preset(), load_preset()
    - Store presets in config
    - _Requirements: 10.6_

- [ ]* 13.3 Write property test for vibrance filter

  - **Property 20: Vibrance Filter Application**
  - **Validates: Requirements 10.1**

- [ ]* 13.4 Write property test for brightness adjustment

  - **Property 21: Brightness Adjustment Range**
  - **Validates: Requirements 10.3**

- [ ]* 13.5 Write property test for contrast adjustment

  - **Property 22: Contrast Adjustment Range**
  - **Validates: Requirements 10.4**

- [ ]* 13.6 Write property test for filter preset round-trip

  - **Property 23: Filter Preset Round-Trip**
  - **Validates: Requirements 10.6**

- [ ]* 13.7 Write property test for filter disable restoration

  - **Property 24: Filter Disable Restoration**
  - **Validates: Requirements 10.7**

- [ ] 14. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 8: Error Handler and Stability

- [ ] 15. Implement Error Handler

  - [ ] 15.1 Create ErrorHandler class

    - Implement log_error() with timestamp, context, stack trace
    - Implement export_diagnostics(), generate_crash_dump()
    - _Requirements: 11.1, 11.5, 11.6_

  - [ ] 15.2 Implement injection retry logic

    - Implement log_injection_attempt()
    - Track attempts and implement exponential backoff (1s, 2s, 4s)
    - _Requirements: 11.3_

  - [ ] 15.3 Implement blacklist management

    - Implement add_to_blacklist(), is_blacklisted()
    - Store blacklist in blacklist.json
    - _Requirements: 11.9_

  - [ ] 15.4 Implement memory monitoring

    - Monitor memory usage, log warnings at 200MB threshold
    - Implement cache clearing logic
    - _Requirements: 11.8_

- [ ]* 15.5 Write property test for error log completeness

  - **Property 25: Error Log Completeness**
  - **Validates: Requirements 11.1**

- [ ]* 15.6 Write property test for injection retry logic

  - **Property 26: Injection Retry Logic**
  - **Validates: Requirements 11.3**

- [ ]* 15.7 Write property test for sensor failure graceful degradation

  - **Property 27: Sensor Failure Graceful Degradation**
  - **Validates: Requirements 11.4**

- [ ]* 15.8 Write property test for adaptive update frequency

  - **Property 28: Adaptive Update Frequency**
  - **Validates: Requirements 11.7**

- [ ]* 15.9 Write property test for memory warning threshold

  - **Property 29: Memory Warning Threshold**
  - **Validates: Requirements 11.8**

- [ ]* 15.10 Write property test for blacklist management

  - **Property 30: Blacklist Management**
  - **Validates: Requirements 11.9**

- [ ] 16. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 9: Optimization Engine


- [x] 17. Implement Optimization Engine
  - [x] 17.1 Create OptimizationEngine class

    - Implement activate_game_mode(), deactivate_game_mode()
    - Store original states for restoration
    - _Requirements: 5.1-5.5_

  - [x] 17.2 Implement process termination logic



    - Terminate processes from configurable list
    - Handle access denied errors gracefully
    - Log process names and reasons
    - _Requirements: 5.1, 5.7, 12.5_

  - [x] 17.3 Implement process priority management

    - Set game process to high priority
    - Store and restore original priorities
    - _Requirements: 5.2, 5.5_


  - [x] 17.4 Implement optimization action logging

    - Log all optimization actions with details
    - _Requirements: 5.6_


- [x] 17.5 Write property test for game mode state restoration

  - **Property 10: Game Mode State Restoration**
  - **Validates: Requirements 5.5**



- [x] 17.6 Write property test for optimization logging

  - **Property 11: Optimization Action Logging**
  - **Validates: Requirements 5.6**

- [ ]* 17.7 Write property test for optimization transparency

  - **Property 32: Optimization Transparency**
  - **Validates: Requirements 12.5**

- [x] 18. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

## Phase 10: PyQt6 User Interface


- [x] 19. Create Main Window and Navigation

  - [x] 19.1 Implement MainWindow with sidebar navigation


    - Create QMainWindow with stacked widget for pages
    - Implement navigation between Dashboard, Overlay Editor, Filters, Optimizer, Settings, About

    - _Requirements: 6.1, 6.2_

  - [x] 19.2 Implement system tray icon


    - Create QSystemTrayIcon with context menu

    - Handle minimize to tray and restore
    - _Requirements: 6.5, 6.6, 8.4_



- [x] 20. Implement Dashboard Page

  - [x] 20.1 Create DashboardPage with metric cards


    - Display real-time CPU, GPU, RAM, FPS, 1% low, 0.1% low values
    - _Requirements: 6.1_

  - [x] 20.2 Implement MetricGraph widget for history


    - Create line graphs for CPU, GPU, FPS
    - Maintain 60-second rolling history
    - Highlight frame drops visually
    - _Requirements: 6.3, 7.6_


- [x] 20.3 Write property test for graph history buffer

  - **Property 12: Graph History Buffer Size**

  - **Validates: Requirements 6.3**

- [ ] 21. Implement Overlay Editor Page with Themes

  - [ ] 21.1 Update OverlayEditorPage with theme support

    - Add font selector, color picker, position dropdown
    - Add opacity slider
    - Add theme selector dropdown
    - _Requirements: 4.1-4.6_

  - [ ] 21.2 Implement ThemeEditor widget

    - Allow creating and editing custom themes
    - Save and export theme files
    - _Requirements: 4.9_

  - [ ] 21.3 Implement live preview widget


    - Show preview of overlay with current settings
    - _Requirements: 4.1_

- [ ] 22. Implement Filters Page

  - [ ] 22.1 Create FiltersPage with filter controls

    - Add sliders for vibrance, sharpening, brightness, contrast
    - Add preset selector and save preset button
    - Add enable/disable toggle
    - _Requirements: 10.1-10.7_

- [x] 23. Implement Optimizer Page

  - [x] 23.1 Create OptimizerPage with game mode controls



    - Add activate/deactivate buttons
    - Display optimization status and logs



    - _Requirements: 5.1-5.6_

- [ ] 24. Implement About Page

  - [ ] 24.1 Create AboutPage with transparency features

    - Display open-source license and repository link
    - Show list of active hooks and injected DLLs
    - Add export diagnostics button
    - Explain administrator permissions
    - _Requirements: 12.1-12.7_

- [ ]* 24.2 Write property test for active hooks transparency

  - **Property 31: Active Hooks Transparency**
  - **Validates: Requirements 12.4**

- [x] 25. Implement Settings Page



  - [x] 25.1 Create SettingsPage with all configuration options





    - Add auto-start toggle, hotkey configuration



    - Add reset to defaults button
    - _Requirements: 9.1-9.5_








- [x] 26. Apply Styling


  - [x] 26.1 Create QSS stylesheet for modern dark theme




    - Style all widgets consistently
    - _Requirements: 6.1_


- [ ] 27. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

## Phase 11: Native DirectX Hook with Filters (C++)

- [x] 28. Set up C++ Native Project


  - [x] 28.1 Create CMakeLists.txt and project structure
    - Configure build for DLL output

    - Link DirectX and ImGui libraries
    - _Requirements: 2.1, 3.1_

- [ ] 29. Implement DirectX Hook with Percentiles


  - [ ] 29.1 Update DX11 SwapChain hook with rolling window


    - Hook Present() function using MinHook
    - Implement std::deque<float> for 1000 frame history
    - Measure frame times and calculate percentiles

    - _Requirements: 2.1, 2.2, 2.4, 2.5_

  - [x] 29.2 Implement ImGui overlay rendering
    - Initialize ImGui with DirectX context
    - Render metrics overlay on each frame
    - Display FPS, 1% low, 0.1% low
    - _Requirements: 3.2, 3.3_

  - [ ] 29.3 Update DLL exports for Python integration
    - Export functions for setting metrics and config
    - Export FPS, frame time, and percentile getters
    - Export filter config setter
    - _Requirements: 2.2, 2.3, 3.3, 10.5_


- [x] 29.4 Write property test for overlay render completeness
  - **Property 5: Overlay Render Completeness**

  - **Validates: Requirements 3.3**

- [ ] 30. Implement Post-Processing Filters

  - [ ] 30.1 Create HLSL shaders for filters

    - Write vibrance.hlsl for saturation adjustment
    - Write sharpen.hlsl for image sharpening
    - Write brightness.hlsl for brightness adjustment
    - Write contrast.hlsl for contrast adjustment
    - _Requirements: 10.1-10.4_

  - [ ] 30.2 Implement post-processing pipeline

    - Create PostProcessFilter class
    - Compile and apply shaders based on FilterConfig
    - Render to texture and apply filters
    - _Requirements: 10.5_

  - [ ] 30.3 Implement filter enable/disable logic

    - Allow toggling filters on/off without restart
    - Restore original rendering when disabled
    - _Requirements: 10.7, 10.8_

- [ ] 31. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Phase 12: Integration and Polish

- [ ] 32. Integrate All Components

  - [x] 32.1 Connect MonitoringEngine to UI dashboard

    - Wire up metric updates to UI widgets
    - _Requirements: 6.1_

  - [ ] 32.2 Connect FPSCalculator to native DLL

    - Pass frame times from DLL to FPSCalculator
    - Display percentiles in overlay and dashboard
    - _Requirements: 2.4, 2.5_

  - [ ] 32.3 Connect ThemeManager to Overlay Editor

    - Load and apply themes from UI
    - _Requirements: 4.6, 4.9_

  - [ ] 32.4 Connect FilterManager to Filters Page and native DLL

    - Pass filter config to DLL for shader application
    - _Requirements: 10.1-10.7_

  - [ ] 32.5 Connect ErrorHandler to all components

    - Wire up error logging throughout application
    - Display diagnostics in About page
    - _Requirements: 11.1, 11.5, 11.6, 12.4_

  - [x] 32.6 Connect ConfigManager to all UI pages


    - Load and save settings from UI interactions

    - _Requirements: 4.6, 9.3_
  - [x] 32.7 Connect OptimizationEngine to Optimizer page

    - Wire up game mode activation/deactivation
    - _Requirements: 5.1-5.6_
  - [x] 32.8 Integrate native DLL with Python application
    - Load DLL and call exported functions

    - Pass metrics and filter config to overlay
    - _Requirements: 2.1, 3.1, 10.5_

- [ ] 33. Implement Background Service Mode with Error Handling

  - [x] 33.1 Add auto-start functionality

    - Register with Windows startup
    - _Requirements: 8.1_

  - [ ] 33.2 Implement game detection and auto-overlay with blacklist


    - Detect running games from process list
    - Check blacklist before injection
    - Automatically inject overlay DLL with retry logic

    - _Requirements: 8.3, 11.3, 11.9_

  - [ ] 33.3 Implement adaptive performance monitoring

    - Monitor overlay FPS impact
    - Reduce update frequency if FPS drops
    - _Requirements: 11.7_

- [ ]* 34. Write integration tests

  - Test end-to-end monitoring flow with percentiles
  - Test config persistence across restarts
  - Test theme application and persistence
  - Test filter application and shader compilation
  - Test error handling and recovery
  - _Requirements: All_


- [ ] 35. Final Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.
