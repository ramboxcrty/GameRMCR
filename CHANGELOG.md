# Changelog

All notable changes to RMCR will be documented in this file.

## [1.0.0] - 2024-12-03

### Added
- 🎮 Real-time system monitoring (CPU, GPU, RAM, Network)
- 📊 FPS counter with percentile analysis
- 🌡️ Temperature monitoring (CPU & GPU)
  - Multiple detection methods (OpenHardwareMonitor, Intel Power Gadget, AMD, MSR)
  - Estimated temperature fallback
- 🎨 Modern dark theme UI with customizable colors
- 📈 Live performance graphs
- 🔄 Auto-update system via GitHub Releases
- 🎯 Game optimizer with process management
- 🎨 Visual filters per-game
- 📝 Comprehensive logging and diagnostics
- 🔐 KeyAuth authentication system
- 🖥️ System tray integration
- ⚙️ Configurable settings

### Features
- **Dashboard**: Real-time metrics overview
- **System Monitor**: Detailed hardware information
- **Overlay Editor**: Customize in-game overlay
- **Filters**: Per-game visual enhancements
- **Optimizer**: Automatic game optimization
- **Settings**: Full configuration control
- **About**: Version info and diagnostics

### Technical
- Python 3.10+ support
- PySide6 (Qt6) UI framework
- NVIDIA GPU monitoring via pynvml
- Multi-threaded monitoring engine
- Thread-safe UI updates
- Property-based testing with Hypothesis
- Integration tests

### Known Issues
- CPU temperature requires OpenHardwareMonitor/LibreHardwareMonitor
- Overlay injection requires administrator privileges
- DirectX 11 hook not yet implemented

### Requirements
- Windows 10/11 (64-bit)
- Python 3.10+
- NVIDIA GPU (for GPU monitoring)
- Administrator privileges (for full features)

---

## Future Releases

### [1.1.0] - Planned
- DirectX 11 overlay implementation
- Benchmark recording and playback
- Game detection and auto-profiles
- More visual filter options
- Performance optimizations

### [1.2.0] - Planned
- DirectX 12 support
- Vulkan support
- Multi-GPU support
- Cloud sync for settings
- Community profiles
