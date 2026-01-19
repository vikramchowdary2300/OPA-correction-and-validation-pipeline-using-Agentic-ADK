"""
Configuration module for Self-Healing Agent.

Loads configuration from .env file and provides access to environment variables.
"""

import os
from pathlib import Path
from typing import Optional


def load_env_file():
    """
    Load environment variables from .env file in the self_healing_agent directory.
    Silently fails if file doesn't exist or can't be read.
    """
    try:
        env_file = Path(__file__).parent / ".env"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Only set if not already in environment and value is not empty
                        if key and value and key not in os.environ:
                            os.environ[key] = value
    except (PermissionError, OSError):
        # Silently ignore if .env file can't be read
        # Will fall back to system environment variables
        pass


# Load .env file on module import
load_env_file()


def get_github_token() -> Optional[str]:
    """
    Get GitHub token from environment.
    
    Returns:
        GitHub token or None if not set
    """
    return os.getenv("GITHUB_TOKEN")


def get_github_repo_url() -> Optional[str]:
    """
    Get default GitHub repository URL from environment.
    
    Returns:
        GitHub repository URL or None if not set
    """
    return os.getenv("GITHUB_REPO_URL")


def get_max_iterations() -> int:
    """
    Get maximum iterations for the fix loop.
    
    Returns:
        Maximum iterations (default: 5)
    """
    try:
        return int(os.getenv("MAX_ITERATIONS", "5"))
    except ValueError:
        return 5


def get_policy_path() -> str:
    """
    Get the absolute path to the policies directory.
    Defaults to 'policies' in the project root.
    """
    # Assuming config.py is in self_healing_agent/
    # Project root is self_healing_agent/../
    project_root = Path(__file__).parent.parent
    default_path = project_root / "policies"
    
    env_path = os.getenv("POLICY_PATH")
    if env_path:
        return str(Path(env_path).resolve())
        
    return str(default_path.resolve())


def get_llm_model() -> str:
    """
    Get the LLM model to use for agents.
    
    Returns:
        LLM model name (default: gemini-2.5-flash)
    """
    return os.getenv("LLM_MODEL", "gemini-2.5-flash")


class Config:
    """Configuration class for Self-Healing Agent."""
    
    def __init__(self):
        self.github_token = get_github_token()
        self.github_repo_url = get_github_repo_url()
        self.max_iterations = get_max_iterations()
        self.policy_path = get_policy_path()
        self.llm_model = get_llm_model()
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that required configuration is present.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.github_token:
            return False, "GITHUB_TOKEN not set in environment or .env file"
        
        return True, None
    
    def __repr__(self):
        return (
            f"Config(github_token={'***' if self.github_token else 'None'}, "
            f"github_repo_url={self.github_repo_url}, "
            f"max_iterations={self.max_iterations}, "
            f"llm_model={self.llm_model})"
        )


# Global config instance
config = Config()

