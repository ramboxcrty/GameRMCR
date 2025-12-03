"""Auto-update system using GitHub Releases API."""
import requests
import json
import webbrowser
from typing import Optional, Dict, Tuple
from pathlib import Path
from datetime import datetime, timedelta

from src.version import (
    __version__,
    __version_info__,
    GITHUB_API_URL,
    GITHUB_REPO_URL,
    CHECK_FOR_UPDATES_ON_STARTUP,
    UPDATE_CHECK_INTERVAL_HOURS
)


class UpdateChecker:
    """Check for updates from GitHub Releases."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.current_version = __version__
        self.current_version_tuple = __version_info__
        self.api_url = f"{GITHUB_API_URL}/releases/latest"
        self.releases_url = f"{GITHUB_REPO_URL}/releases"
        
        # Cache file for last check time
        self.cache_file = Path("config/update_cache.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates based on interval."""
        if not CHECK_FOR_UPDATES_ON_STARTUP:
            return False
        
        # Check cache
        if not self.cache_file.exists():
            return True
        
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            last_check = datetime.fromisoformat(cache.get('last_check', ''))
            interval = timedelta(hours=UPDATE_CHECK_INTERVAL_HOURS)
            
            return datetime.now() - last_check > interval
        except Exception:
            return True
    
    def update_check_cache(self):
        """Update the last check timestamp."""
        try:
            cache = {
                'last_check': datetime.now().isoformat(),
                'last_version_checked': self.current_version
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Failed to update check cache: {e}")
    
    def check_for_updates(self) -> Optional[Dict]:
        """Check GitHub for latest release.
        
        Returns:
            Dict with update info if available, None otherwise
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            
            # Parse version from tag
            tag_name = release_data.get('tag_name', '')
            latest_version = tag_name.lstrip('v')
            
            # Compare versions
            if self._is_newer_version(latest_version):
                return {
                    'version': latest_version,
                    'tag_name': tag_name,
                    'name': release_data.get('name', ''),
                    'body': release_data.get('body', ''),
                    'html_url': release_data.get('html_url', ''),
                    'published_at': release_data.get('published_at', ''),
                    'assets': release_data.get('assets', [])
                }
            
            return None
        
        except requests.RequestException as e:
            print(f"Failed to check for updates: {e}")
            return None
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None
        finally:
            self.update_check_cache()
    
    def _is_newer_version(self, version_str: str) -> bool:
        """Compare version strings.
        
        Args:
            version_str: Version string like "1.2.3"
            
        Returns:
            True if version_str is newer than current version
        """
        try:
            # Parse version string
            parts = version_str.split('.')
            new_version = tuple(int(p) for p in parts[:3])
            
            # Compare tuples
            return new_version > self.current_version_tuple
        except Exception:
            return False
    
    def get_download_url(self, update_info: Dict) -> Optional[str]:
        """Get download URL for the update.
        
        Args:
            update_info: Update information from check_for_updates
            
        Returns:
            Download URL or None
        """
        assets = update_info.get('assets', [])
        
        # Look for Windows executable
        for asset in assets:
            name = asset.get('name', '').lower()
            if name.endswith('.exe') or name.endswith('.zip'):
                return asset.get('browser_download_url')
        
        # Fallback to release page
        return update_info.get('html_url')
    
    def open_download_page(self, update_info: Dict):
        """Open the download page in browser.
        
        Args:
            update_info: Update information from check_for_updates
        """
        url = self.get_download_url(update_info)
        if url:
            webbrowser.open(url)
        else:
            webbrowser.open(self.releases_url)
    
    def format_changelog(self, update_info: Dict) -> str:
        """Format changelog for display.
        
        Args:
            update_info: Update information from check_for_updates
            
        Returns:
            Formatted changelog text
        """
        version = update_info.get('version', 'Unknown')
        name = update_info.get('name', '')
        body = update_info.get('body', 'No changelog available.')
        published = update_info.get('published_at', '')
        
        # Format published date
        try:
            pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
            date_str = pub_date.strftime('%Y-%m-%d')
        except Exception:
            date_str = 'Unknown date'
        
        changelog = f"Version {version}"
        if name:
            changelog += f" - {name}"
        changelog += f"\nReleased: {date_str}\n\n"
        changelog += body
        
        return changelog


def check_for_updates_async(callback, config_manager=None):
    """Check for updates in background thread.
    
    Args:
        callback: Function to call with update info (or None)
        config_manager: Optional config manager
    """
    import threading
    
    def _check():
        checker = UpdateChecker(config_manager)
        if checker.should_check_for_updates():
            update_info = checker.check_for_updates()
            callback(update_info, checker)
    
    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
