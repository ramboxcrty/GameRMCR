# GameRMCR - Game Performance Monitor

A powerful game performance monitoring and optimization tool for Windows.

## Features

- **Real-time Monitoring**: CPU, GPU, RAM, and temperature monitoring
- **FPS Counter**: Accurate frame rate tracking with percentile analysis
- **Overlay**: In-game overlay with customizable metrics
- **Game Optimizer**: Automatic process optimization for better performance
- **Visual Filters**: Per-game color correction and enhancement
- **Benchmarking**: Record and analyze gaming sessions
- **Auto-Update**: Automatic updates via GitHub Releases

## System Requirements

- Windows 10/11 (64-bit)
- Python 3.10 or higher
- NVIDIA GPU (for GPU monitoring)
- Administrator privileges (for overlay injection)

## Installation

1. Download the latest release from [Releases](https://github.com/ramboxcrty/GameRMCR/releases)
2. Extract the archive
3. Run `RMCR.exe` as Administrator

## For Developers

### Setup

```bash
# Clone repository
git clone https://github.com/ramboxcrty/GameRMCR.git
cd GameRMCR

# Install dependencies
pip install -r requirements.txt

# Run application
python -m src.main
```

### Building

```bash
# Build executable
pyinstaller --name RMCR --onefile --windowed src/main.py
```

## Temperature Monitoring

For CPU temperature monitoring, install one of these tools:
- [OpenHardwareMonitor](https://openhardwaremonitor.org/downloads/)
- [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases)

Run it as Administrator before starting RMCR.

## License

MIT License - See LICENSE file for details

## Credits

- Developed by RamboxCRTY
- Inspired by MSI Afterburner and NZXT CAM

## Support

For issues and feature requests, please use [GitHub Issues](https://github.com/ramboxcrty/GameRMCR/issues)
