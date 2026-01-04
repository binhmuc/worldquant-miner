"""
Secure Credential Manager
Handles WorldQuant Brain authentication securely

IMPORTANT: Credentials are NEVER embedded in code or executable.
All credentials are loaded from external files or user input only.
"""

import json
import os
import logging
import requests
from pathlib import Path
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from getpass import getpass

logger = logging.getLogger(__name__)


@dataclass
class Credentials:
    """Secure credential container (never logged or stored in code)"""
    cookie: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary (for API calls only)"""
        return {
            'cookie': self.cookie
        }

    def validate(self) -> bool:
        """Basic validation"""
        return bool(self.cookie and len(self.cookie) > 0)


class CredentialManager:
    """
    Secure credential manager

    Features:
    - Loads from cookie.txt
    - Prompts for login if file not found
    - Validates credentials before use
    - NEVER embeds credentials in code
    - Stores credentials only in memory
    """

    # Possible credential file names (checked in order)
    CREDENTIAL_FILE_NAMES = ['cookie.txt']
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize credential manager
        
        Args:
            base_path: Base directory to search for credential files
                      If None, searches current directory and parent directories
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.credentials: Optional[Credentials] = None
        self.authenticated = False
        self.session: Optional[requests.Session] = None
    
    def find_credential_file(self) -> Optional[Path]:
        """
        Find credential file in common locations
        
        Returns:
            Path to credential file if found, None otherwise
        """
        # Search locations (in order of priority):
        search_paths = [
            self.base_path,  # Current/base directory
            self.base_path.parent,  # Parent directory
            Path.home(),  # User home directory
            Path.cwd(),  # Current working directory
        ]
        
        for search_path in search_paths:
            for filename in self.CREDENTIAL_FILE_NAMES:
                credential_file = search_path / filename
                if credential_file.exists() and credential_file.is_file():
                    logger.info(f"Found credential file: {credential_file}")
                    return credential_file
        
        logger.warning("No credential file found in standard locations")
        return None
    
    def load_from_file(self, file_path: Optional[Path] = None) -> bool:
        """
        Load credentials from file

        Args:
            file_path: Path to cookie file. If None, searches automatically.

        Returns:
            True if credentials loaded successfully, False otherwise
        """
        if file_path is None:
            file_path = self.find_credential_file()

        if file_path is None:
            logger.error("No cookie file specified or found")
            return False

        if not file_path.exists():
            logger.error(f"Cookie file not found: {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cookie = f.read().strip()

            if not cookie:
                raise ValueError("Cookie file is empty")

            self.credentials = Credentials(cookie=cookie)

            if not self.credentials.validate():
                logger.error("Invalid credentials: empty cookie")
                self.credentials = None
                return False

            logger.info(f"✅ Cookie loaded from: {file_path}")
            logger.info(f"   Cookie length: {len(self.credentials.cookie)} characters")
            # NEVER log full cookie
            return True

        except Exception as e:
            logger.error(f"Failed to load cookie from {file_path}: {e}")
            self.credentials = None
            return False
    
    def prompt_for_credentials(self) -> bool:
        """
        Prompt user for credentials (interactive)

        Returns:
            True if credentials entered, False if cancelled
        """
        try:
            print("\n" + "="*60)
            print("🔐 WORLDQUANT BRAIN AUTHENTICATION REQUIRED")
            print("="*60)
            print("Please enter your WorldQuant Brain cookie string:")
            print("(You can find this in your browser's developer tools)")
            print()

            cookie = input("Cookie string: ").strip()
            if not cookie:
                logger.warning("Cookie not provided")
                return False

            self.credentials = Credentials(cookie=cookie)

            if not self.credentials.validate():
                logger.error("Invalid credentials: empty cookie")
                self.credentials = None
                return False

            logger.info(f"✅ Cookie entered ({len(self.credentials.cookie)} characters)")
            return True

        except (KeyboardInterrupt, EOFError):
            logger.warning("Credential entry cancelled by user")
            self.credentials = None
            return False
        except Exception as e:
            logger.error(f"Error prompting for credentials: {e}")
            self.credentials = None
            return False
    
    def validate_credentials(self) -> bool:
        """
        Validate credentials by attempting authentication

        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.credentials or not self.credentials.validate():
            logger.error("No valid credentials to validate")
            return False

        try:
            # Create a temporary session for validation
            test_session = requests.Session()

            # Set cookie in session
            logger.info(f"Validating cookie ({len(self.credentials.cookie)} characters)")

            # Parse cookie string and set it in the session
            # The cookie string should be in the format: "key1=value1; key2=value2; ..."
            cookie_dict = {}
            for cookie_part in self.credentials.cookie.split(';'):
                cookie_part = cookie_part.strip()
                if '=' in cookie_part:
                    key, value = cookie_part.split('=', 1)
                    cookie_dict[key.strip()] = value.strip()

            # Set cookies for the WorldQuant Brain domain
            for key, value in cookie_dict.items():
                test_session.cookies.set(key, value, domain='worldquantbrain.com')

            # Test the cookie by making a request to the API
            response = test_session.get(
                'https://api.worldquantbrain.com/users/self',
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✅ Cookie validated successfully")
                self.authenticated = True

                # Store session for reuse
                self.session = test_session

                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                logger.error(f"   Response: {response.text[:200]}")
                self.authenticated = False
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error during credential validation: {e}")
            self.authenticated = False
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during credential validation: {e}")
            self.authenticated = False
            return False
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Get current credentials (if authenticated)
        
        Returns:
            Credentials object if available, None otherwise
        """
        if self.authenticated and self.credentials:
            return self.credentials
        return None
    
    def get_session(self) -> Optional[requests.Session]:
        """
        Get authenticated session
        
        Returns:
            Authenticated requests.Session if available, None otherwise
        """
        if self.authenticated and self.session:
            return self.session
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.authenticated
    
    def authenticate(self, auto_load: bool = True, auto_prompt: bool = True) -> bool:
        """
        Complete authentication flow
        
        Args:
            auto_load: Automatically try to load from file
            auto_prompt: Automatically prompt if file not found
        
        Returns:
            True if authenticated, False otherwise
        """
        # Step 1: Try to load from file
        if auto_load:
            if self.load_from_file():
                if self.validate_credentials():
                    return True
                else:
                    logger.warning("Credentials from file failed validation")
        
        # Step 2: Prompt user if file not found or validation failed
        if auto_prompt:
            if self.prompt_for_credentials():
                if self.validate_credentials():
                    return True
                else:
                    logger.error("Entered credentials failed validation")
        
        logger.error("❌ Authentication failed - cannot proceed without valid credentials")
        return False
    
    def clear_credentials(self):
        """Clear credentials from memory (security)"""
        if self.credentials:
            # Overwrite cookie in memory (best effort)
            self.credentials.cookie = "***CLEARED***"
        self.credentials = None
        self.authenticated = False
        self.session = None
        logger.info("Credentials cleared from memory")


def get_credential_manager(base_path: Optional[str] = None) -> CredentialManager:
    """
    Factory function to get credential manager instance
    
    Args:
        base_path: Base directory to search for credentials
    
    Returns:
        CredentialManager instance
    """
    return CredentialManager(base_path=base_path)
