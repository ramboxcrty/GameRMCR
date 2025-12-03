"""FPS and frame time calculation module with percentile support."""
from collections import deque
from typing import List, Optional
import time


class FPSCalculator:
    """Calculate FPS, frame time, and percentiles from frame timestamps.
    
    Uses a rolling window of 1000 frames for percentile calculations.
    """
    
    def __init__(self, window_size: int = 1000):
        """Initialize FPS calculator with rolling window.
        
        Args:
            window_size: Number of frames to keep in rolling window (default: 1000)
        """
        self.window_size = window_size
        self._frame_times: deque = deque(maxlen=window_size)
    
    def add_frame(self, frame_time: float) -> None:
        """Add a frame time to the rolling window.
        
        Args:
            frame_time: Frame time in milliseconds
        """
        if frame_time > 0:
            self._frame_times.append(frame_time)
    
    def get_current_fps(self) -> float:
        """Calculate current FPS from average frame time.
        
        FPS = 1000 / average_frame_time_ms
        
        Returns:
            Current FPS value
        """
        if not self._frame_times:
            return 0.0
        
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        if avg_frame_time <= 0:
            return 0.0
        
        return 1000.0 / avg_frame_time
    
    def get_frame_time_avg(self) -> float:
        """Get average frame time in milliseconds.
        
        Returns:
            Average frame time in ms
        """
        if not self._frame_times:
            return 0.0
        return sum(self._frame_times) / len(self._frame_times)
    
    def get_percentile_fps(self, percentile: float) -> float:
        """Calculate FPS at a specific percentile.
        
        Args:
            percentile: Percentile value (0.0 to 100.0)
            
        Returns:
            FPS value at the specified percentile
        """
        if not self._frame_times:
            return 0.0
        
        sorted_times = sorted(self._frame_times, reverse=True)  # Longest times first
        index = int(len(sorted_times) * (percentile / 100.0))
        index = min(index, len(sorted_times) - 1)
        
        frame_time = sorted_times[index]
        if frame_time <= 0:
            return 0.0
        
        return 1000.0 / frame_time
    
    def get_1_percent_low(self) -> float:
        """Get 1% low FPS value.
        
        Returns:
            1% low FPS
        """
        return self.get_percentile_fps(1.0)
    
    def get_0_1_percent_low(self) -> float:
        """Get 0.1% low FPS value.
        
        Returns:
            0.1% low FPS
        """
        return self.get_percentile_fps(0.1)
    
    def reset(self) -> None:
        """Clear all recorded data."""
        self._frame_times.clear()
    
    @staticmethod
    def calculate_fps_from_frame_time(frame_time: float) -> float:
        """Calculate FPS from frame time.
        
        Args:
            frame_time: Frame time in milliseconds
            
        Returns:
            FPS value
        """
        if frame_time <= 0:
            return 0.0
        return 1000.0 / frame_time
    
    @staticmethod
    def calculate_frame_time_from_timestamps(t1: float, t2: float) -> float:
        """Calculate frame time between two timestamps.
        
        Args:
            t1: First timestamp in milliseconds
            t2: Second timestamp in milliseconds
            
        Returns:
            Frame time in milliseconds
        """
        return abs(t2 - t1)
