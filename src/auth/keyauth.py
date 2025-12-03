"""
KeyAuth integration for GameRMCR.
License verification and authentication system.
"""
import hashlib
import json
import os
import platform
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import requests


def getchecksum() -> str:
    """Get the checksum of the current executable/script."""
    try:
        path = os.path.abspath(__file__)
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def get_hwid() -> str:
    """Get hardware ID for license binding."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'csproduct', 'get', 'uuid'],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return lines[1].strip()
        return str(uuid.getnode())
    except Exception:
        return str(uuid.getnode())


class KeyAuthApp:
    """KeyAuth API wrapper for Python applications."""
    
    def __init__(
        self,
        name: str = "GameRMCR",
        ownerid: str = "0iCFhlZO0W",
        version: str = "1.0",
        hash_to_check: str = ""
    ):
        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check
        self.url = "https://keyauth.win/api/1.3/"
        
        # Session data
        self.session_id: Optional[str] = None
        self.initialized = False
        self.logged_in = False
        
        # User data
        self.user_data: Dict[str, Any] = {}
        self.subscription_name: Optional[str] = None
        self.expiry: Optional[datetime] = None
        
        # App secret (from your KeyAuth dashboard)
        self.app_secret = "0345639f9168597f98b8572a18c4ebc342dd7fd9e3c7ee1bfe911e8f290ef3b2"
    
    def _make_request(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Make a request to KeyAuth API."""
        try:
            response = requests.post(
                self.url,
                data=data,
                timeout=30,
                headers={
                    "User-Agent": f"KeyAuth/{self.version}"
                }
            )
            return response.json()
        except requests.RequestException as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid response from server"}
    
    def init(self) -> bool:
        """Initialize the KeyAuth session."""
        if self.initialized:
            return True
        
        data = {
            "type": "init",
            "ver": self.version,
            "hash": self.hash_to_check,
            "name": self.name,
            "ownerid": self.ownerid
        }
        
        result = self._make_request(data)
        
        if result.get("success"):
            self.session_id = result.get("sessionid")
            self.initialized = True
            return True
        
        self.error_message = result.get("message", "Initialization failed")
        return False
    
    def login(self, username: str, password: str) -> bool:
        """Login with username and password."""
        if not self.initialized:
            if not self.init():
                return False
        
        data = {
            "type": "login",
            "username": username,
            "pass": password,
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.ownerid,
            "hwid": get_hwid()
        }
        
        result = self._make_request(data)
        
        if result.get("success"):
            self.logged_in = True
            self._parse_user_data(result.get("info", {}))
            return True
        
        self.error_message = result.get("message", "Login failed")
        return False
    
    def register(self, username: str, password: str, license_key: str, email: str = "") -> bool:
        """Register a new account with license key."""
        if not self.initialized:
            if not self.init():
                return False
        
        data = {
            "type": "register",
            "username": username,
            "pass": password,
            "key": license_key,
            "email": email,
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.ownerid,
            "hwid": get_hwid()
        }
        
        result = self._make_request(data)
        
        if result.get("success"):
            self.logged_in = True
            self._parse_user_data(result.get("info", {}))
            return True
        
        self.error_message = result.get("message", "Registration failed")
        return False
    
    def license(self, license_key: str) -> bool:
        """Login with license key only."""
        if not self.initialized:
            if not self.init():
                return False
        
        data = {
            "type": "license",
            "key": license_key,
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.ownerid,
            "hwid": get_hwid()
        }
        
        result = self._make_request(data)
        
        if result.get("success"):
            self.logged_in = True
            self._parse_user_data(result.get("info", {}))
            return True
        
        self.error_message = result.get("message", "License validation failed")
        return False
    
    def upgrade(self, username: str, license_key: str) -> bool:
        """Upgrade existing account with new license."""
        if not self.initialized:
            if not self.init():
                return False
        
        data = {
            "type": "upgrade",
            "username": username,
            "key": license_key,
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.ownerid
        }
        
        result = self._make_request(data)
        
        if result.get("success"):
            return True
        
        self.error_message = result.get("message", "Upgrade failed")
        return False
    
    def check_session(self) -> bool:
        """Check if current session is still valid."""
        if not self.initialized or not self.session_id:
            return False
        
        data = {
            "type": "check",
            "sessionid": self.session_id,
            "name": self.name,
            "ownerid": self.ownerid
        }
        
        result = self._make_request(data)
        return result.get("success", False)
    
    def _parse_user_data(self, info: Dict[str, Any]):
        """Parse user data from API response."""
        self.user_data = info
        self.subscription_name = info.get("subscriptions", [{}])[0].get("subscription") if info.get("subscriptions") else None
        
        expiry_timestamp = info.get("subscriptions", [{}])[0].get("expiry") if info.get("subscriptions") else None
        if expiry_timestamp:
            try:
                self.expiry = datetime.fromtimestamp(int(expiry_timestamp))
            except (ValueError, TypeError):
                self.expiry = None
    
    @property
    def username(self) -> Optional[str]:
        """Get logged in username."""
        return self.user_data.get("username")
    
    @property
    def ip(self) -> Optional[str]:
        """Get user's IP address."""
        return self.user_data.get("ip")
    
    @property
    def hwid(self) -> Optional[str]:
        """Get user's hardware ID."""
        return self.user_data.get("hwid")
    
    @property
    def create_date(self) -> Optional[str]:
        """Get account creation date."""
        return self.user_data.get("createdate")
    
    @property
    def last_login(self) -> Optional[str]:
        """Get last login date."""
        return self.user_data.get("lastlogin")
    
    def get_expiry_string(self) -> str:
        """Get formatted expiry date string."""
        if self.expiry:
            return self.expiry.strftime("%Y-%m-%d %H:%M:%S")
        return "N/A"
    
    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        if not self.expiry:
            return True
        return datetime.now() > self.expiry


# Global instance
keyauth_app: Optional[KeyAuthApp] = None


def get_keyauth() -> KeyAuthApp:
    """Get or create the global KeyAuth instance."""
    global keyauth_app
    if keyauth_app is None:
        keyauth_app = KeyAuthApp(
            name="GameRMCR",
            ownerid="0iCFhlZO0W",
            version="1.0",
            hash_to_check=getchecksum()
        )
    return keyauth_app
