"""Benchmark logging and statistics module."""
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.models.metrics import LogEntry, BenchmarkStatistics, SystemMetrics


class BenchmarkLogger:
    """Logger for benchmark sessions with CSV export."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.entries: List[LogEntry] = []
        self.session_start: Optional[datetime] = None
        self.session_end: Optional[datetime] = None
    
    def start_session(self) -> None:
        """Start a new logging session."""
        self.entries.clear()
        self.session_start = datetime.now()
        self.session_end = None
    
    def log_entry(self, metrics: SystemMetrics, fps: float, frame_time: float, 
                  fps_1_percent_low: float = 0.0, fps_0_1_percent_low: float = 0.0) -> None:
        """Log a single entry with metrics and FPS data.
        
        Args:
            metrics: System metrics
            fps: Current FPS
            frame_time: Current frame time
            fps_1_percent_low: 1% low FPS value
            fps_0_1_percent_low: 0.1% low FPS value
        """
        entry = LogEntry(
            timestamp=datetime.now(),
            fps=fps,
            frame_time=frame_time,
            fps_1_percent_low=fps_1_percent_low,
            fps_0_1_percent_low=fps_0_1_percent_low,
            cpu_usage=metrics.cpu.usage_percent,
            cpu_temp=metrics.cpu.temperature,
            gpu_usage=metrics.gpu.usage_percent,
            gpu_temp=metrics.gpu.temperature,
            ram_usage=metrics.memory.used_mb,
            vram_usage=metrics.gpu.vram_used_mb
        )
        self.entries.append(entry)
    
    def end_session(self) -> BenchmarkStatistics:
        """End the session and return statistics."""
        self.session_end = datetime.now()
        return self.get_statistics()
    
    def detect_frame_drops(self, threshold: float = 0.5) -> List[int]:
        """Detect frame drops where FPS drops below threshold of average.
        
        Args:
            threshold: Percentage threshold (0.5 = 50% of average)
            
        Returns:
            List of frame indices where drops occurred
        """
        if not self.entries:
            return []
        
        fps_values = [e.fps for e in self.entries if e.fps > 0]
        if not fps_values:
            return []
        
        avg_fps = sum(fps_values) / len(fps_values)
        threshold_fps = avg_fps * threshold
        
        frame_drops = []
        for i, entry in enumerate(self.entries):
            if entry.fps > 0 and entry.fps < threshold_fps:
                frame_drops.append(i)
        
        return frame_drops
    
    def get_statistics(self) -> BenchmarkStatistics:
        """Calculate benchmark statistics from logged entries."""
        if not self.entries:
            return BenchmarkStatistics()
        
        fps_values = [e.fps for e in self.entries if e.fps > 0]
        frame_times = [e.frame_time for e in self.entries if e.frame_time > 0]
        
        if not fps_values:
            return BenchmarkStatistics()
        
        # Sort for percentile calculation
        sorted_fps = sorted(fps_values)
        
        # Calculate 1% low (bottom 1% of FPS values)
        idx_1_percent = max(0, int(len(sorted_fps) * 0.01))
        fps_1_percent_low = sorted_fps[idx_1_percent] if sorted_fps else 0.0
        
        # Calculate 0.1% low (bottom 0.1% of FPS values)
        idx_0_1_percent = max(0, int(len(sorted_fps) * 0.001))
        fps_0_1_percent_low = sorted_fps[idx_0_1_percent] if sorted_fps else 0.0
        
        # Detect frame drops
        frame_drops = self.detect_frame_drops()
        
        # Calculate duration
        duration = 0.0
        if self.session_start and self.session_end:
            duration = (self.session_end - self.session_start).total_seconds()
        elif self.session_start and self.entries:
            duration = (self.entries[-1].timestamp - self.session_start).total_seconds()

        
        return BenchmarkStatistics(
            min_fps=min(fps_values),
            max_fps=max(fps_values),
            avg_fps=sum(fps_values) / len(fps_values),
            fps_1_percent_low=fps_1_percent_low,
            fps_0_1_percent_low=fps_0_1_percent_low,
            avg_frame_time=sum(frame_times) / len(frame_times) if frame_times else 0.0,
            duration_seconds=duration,
            total_frames=len(self.entries),
            frame_drops=frame_drops
        )
    
    def export_csv(self, filepath: Optional[Path] = None) -> Path:
        """Export logged data to CSV file."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            filepath = self.output_dir / f"benchmark_{timestamp}.csv"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                'timestamp', 'fps', 'frame_time', 'fps_1_percent_low', 'fps_0_1_percent_low',
                'cpu_usage', 'cpu_temp', 'gpu_usage', 'gpu_temp', 'ram_usage', 'vram_usage'
            ])
            # Data
            for entry in self.entries:
                writer.writerow([
                    entry.timestamp.isoformat(),
                    entry.fps,
                    entry.frame_time,
                    entry.fps_1_percent_low,
                    entry.fps_0_1_percent_low,
                    entry.cpu_usage,
                    entry.cpu_temp,
                    entry.gpu_usage,
                    entry.gpu_temp,
                    entry.ram_usage,
                    entry.vram_usage
                ])
        
        return filepath
    
    def generate_filename(self) -> str:
        """Generate a timestamp-based filename."""
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        return f"benchmark_{timestamp}.csv"
    
    @staticmethod
    def parse_csv(filepath: Path) -> List[LogEntry]:
        """Parse a CSV file back into LogEntry objects."""
        entries = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = LogEntry(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    fps=float(row['fps']),
                    frame_time=float(row['frame_time']),
                    fps_1_percent_low=float(row.get('fps_1_percent_low', 0.0)),
                    fps_0_1_percent_low=float(row.get('fps_0_1_percent_low', 0.0)),
                    cpu_usage=float(row['cpu_usage']),
                    cpu_temp=float(row['cpu_temp']),
                    gpu_usage=float(row['gpu_usage']),
                    gpu_temp=float(row['gpu_temp']),
                    ram_usage=int(row['ram_usage']),
                    vram_usage=int(row['vram_usage'])
                )
                entries.append(entry)
        return entries
