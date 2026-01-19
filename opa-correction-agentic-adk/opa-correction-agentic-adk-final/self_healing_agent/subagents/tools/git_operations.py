"""
Git operations tools for repository management.
"""

import os
import subprocess
from typing import Optional
from google.adk.tools import FunctionTool, ToolContext


def git_clone(
    tool_context: ToolContext,
    repo_url: str,
    target_path: str,
    token: Optional[str] = None
) -> dict:
    """
    Clone a GitHub repository to local filesystem.
    
    Args:
        tool_context: ADK tool context
        repo_url: GitHub repository URL (https://github.com/owner/repo)
        target_path: Local path where repo should be cloned
        token: Optional GitHub personal access token for private repos
        
    Returns:
        dict with status, repo_path, and message
    """
    try:
        # Prepare authenticated URL if token provided
        if token and "github.com" in repo_url:
            # Convert https://github.com/owner/repo to https://token@github.com/owner/repo
            auth_url = repo_url.replace("https://", f"https://{token}@")
        else:
            auth_url = repo_url
        
        # Create target directory if it doesn't exist
        os.makedirs(os.path.dirname(target_path) if os.path.dirname(target_path) else ".", exist_ok=True)
        
        # Clone repository
        result = subprocess.run(
            ["git", "clone", auth_url, target_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Store repo path in state
            tool_context.state["repo_path"] = target_path
            tool_context.state["github_repo_url"] = repo_url
            
            return {
                "status": "success",
                "repo_path": target_path,
                "message": f"Successfully cloned repository to {target_path}"
            }
        else:
            return {
                "status": "error",
                "message": f"Git clone failed: {result.stderr}",
                "error_details": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Git clone operation timed out after 5 minutes"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to clone repository: {str(e)}",
            "error_type": type(e).__name__
        }


def git_create_branch(
    tool_context: ToolContext,
    repo_path: str,
    branch_name: str,
    base_branch: str = "main"
) -> dict:
    """
    Create and checkout a new git branch.
    
    Args:
        tool_context: ADK tool context
        repo_path: Path to git repository
        branch_name: Name for the new branch
        base_branch: Base branch to create from (default: main)
        
    Returns:
        dict with status, branch_name, and message
    """
    try:
        # First, checkout base branch
        result = subprocess.run(
            ["git", "checkout", base_branch],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            # Try 'master' if 'main' fails
            if base_branch == "main":
                result = subprocess.run(
                    ["git", "checkout", "master"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    base_branch = "master"
        
        # Create and checkout new branch
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Store branch info in state
            tool_context.state["branch_name"] = branch_name
            tool_context.state["base_branch"] = base_branch
            
            return {
                "status": "success",
                "branch_name": branch_name,
                "base_branch": base_branch,
                "message": f"Successfully created and checked out branch '{branch_name}'"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to create branch: {result.stderr}",
                "error_details": result.stderr
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create branch: {str(e)}",
            "error_type": type(e).__name__
        }


def git_add_files(
    tool_context: ToolContext,
    repo_path: str,
    files: str = "."
) -> dict:
    """
    Stage files for git commit.
    
    Args:
        tool_context: ADK tool context
        repo_path: Path to git repository
        files: Files to stage - use "." for all files, or comma-separated paths like "file1.py,file2.js"
        
    Returns:
        dict with status and message
    """
    try:
        # Parse files parameter
        if files == ".":
            file_list = ["."]
        elif "," in files:
            file_list = [f.strip() for f in files.split(",")]
        else:
            file_list = [files] if files else ["."]
        
        # Add files to staging area
        cmd = ["git", "add"] + file_list
        
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Get status to verify
            status_result = subprocess.run(
                ["git", "status", "--short"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "success",
                "message": f"Successfully staged files: {files}",
                "staged_files": status_result.stdout
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to stage files: {result.stderr}",
                "error_details": result.stderr
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to stage files: {str(e)}",
            "error_type": type(e).__name__
        }


def git_commit(
    tool_context: ToolContext,
    repo_path: str,
    message: str,
    author_name: str = "Self-Healing Agent",
    author_email: str = "agent@self-healing.ai"
) -> dict:
    """
    Commit staged changes to git repository.
    
    Args:
        tool_context: ADK tool context
        repo_path: Path to git repository
        message: Commit message
        author_name: Git author name
        author_email: Git author email
        
    Returns:
        dict with status, commit_sha, and message
    """
    try:
        # Configure git identity
        subprocess.run(
            ["git", "config", "user.name", author_name],
            cwd=repo_path,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", author_email],
            cwd=repo_path,
            capture_output=True
        )
        
        # Commit changes
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Get commit SHA
            sha_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            commit_sha = sha_result.stdout.strip()
            
            # Store commit info in state
            tool_context.state["commit_sha"] = commit_sha
            
            return {
                "status": "success",
                "commit_sha": commit_sha,
                "message": f"Successfully committed changes: {commit_sha[:8]}",
                "commit_output": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to commit: {result.stderr}",
                "error_details": result.stderr
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to commit: {str(e)}",
            "error_type": type(e).__name__
        }


def git_push(
    tool_context: ToolContext,
    repo_path: str,
    branch_name: str,
    token: Optional[str] = None,
    force: bool = False
) -> dict:
    """
    Push branch to remote repository.
    
    Args:
        tool_context: ADK tool context
        repo_path: Path to git repository
        branch_name: Branch name to push
        token: Optional GitHub token for authentication
        force: Whether to force push
        
    Returns:
        dict with status and message
    """
    try:
        # ============ DEBUG LOGGING ============
        print("\n" + "=" * 80)
        print("GIT_PUSH DEBUG LOGS")
        print("=" * 80)
        print(f"repo_path: {repo_path}")
        print(f"branch_name: {branch_name}")
        print(f"token provided: {bool(token)}")
        print(f"token type: {type(token)}")
        print(f"token length: {len(token) if token else 0}")
        if token:
            print(f"token starts with: {token[:10]}..." if len(token) > 10 else f"token: {token}")
        print(f"force: {force}")
        print("=" * 80 + "\n")
        # =======================================
        
        # Validate token format
        if token and (len(token) < 20 or '<' in token or '>' in token):
            return {
                "status": "error",
                "message": f"Invalid GitHub token format. Token appears to be a placeholder: '{token}'. "
                          f"Token should start with 'ghp_' and be ~40 characters. "
                          f"Call get_github_config tool first to retrieve the actual token from .env/state.",
                "token_length": len(token) if token else 0,
                "token_preview": token[:20] if token and len(token) > 20 else token
            }
        
        original_url = None
        
        # Set up authentication if token provided
        if token:
            # Get remote URL
            remote_result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if remote_result.returncode == 0:
                original_url = remote_result.stdout.strip()
                
                # ============ DEBUG LOGGING ============
                print(f"Original remote URL: {original_url}")
                # =======================================
                
                # Parse and reconstruct URL with token
                if "github.com" in original_url:
                    # Remove .git suffix and trailing slashes
                    clean_url = original_url.rstrip('/').replace(".git", "")
                    
                    # Strip any existing authentication from URL first!
                    # URL might already have token: https://TOKEN@github.com/owner/repo
                    if "github.com/" in clean_url:
                        # Extract the part after github.com/
                        parts = clean_url.split("github.com/")
                        if len(parts) == 2:
                            owner_repo = parts[1]  # owner/repo
                        else:
                            owner_repo = parts[-1]
                    elif "github.com:" in clean_url:
                        # git@github.com:owner/repo format
                        owner_repo = clean_url.split("github.com:")[1]
                    else:
                        # Fallback
                        owner_repo = clean_url.split("github.com")[-1].lstrip('/:@')
                    
                    # ============ DEBUG LOGGING ============
                    print(f"Extracted owner/repo: {owner_repo}")
                    # =======================================
                    
                    # Reconstruct clean URL with authentication
                    auth_url = f"https://{token}@github.com/{owner_repo}"
                    
                    # Add .git suffix
                    if not auth_url.endswith(".git"):
                        auth_url += ".git"
                    
                    # ============ DEBUG LOGGING ============
                    # Mask token for display
                    display_url = auth_url.replace(token, "***TOKEN***") if token else auth_url
                    print(f"Setting remote URL to: {display_url}")
                    # =======================================
                    
                    # Set remote URL with authentication
                    set_url_result = subprocess.run(
                        ["git", "remote", "set-url", "origin", auth_url],
                        cwd=repo_path,
                        capture_output=True,
                        text=True
                    )
                    
                    # ============ DEBUG LOGGING ============
                    print(f"Set URL result code: {set_url_result.returncode}")
                    if set_url_result.returncode != 0:
                        print(f"Set URL stderr: {set_url_result.stderr}")
                    # =======================================
                    
                    if set_url_result.returncode != 0:
                        return {
                            "status": "error",
                            "message": f"Failed to set remote URL: {set_url_result.stderr}",
                            "error_details": set_url_result.stderr
                        }
        
        # Push branch
        push_cmd = ["git", "push", "-u", "origin", branch_name]
        if force:
            push_cmd.append("--force")
        
        # ============ DEBUG LOGGING ============
        print(f"Push command: {push_cmd}")
        print(f"Working directory: {repo_path}")
        print("Executing git push...")
        # =======================================
        
        result = subprocess.run(
            push_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # ============ DEBUG LOGGING ============
        print(f"Push return code: {result.returncode}")
        print(f"Push stdout: {result.stdout}")
        print(f"Push stderr: {result.stderr}")
        print("=" * 80 + "\n")
        # =======================================
        
        # Restore original URL if token was used
        if token and original_url:
            subprocess.run(
                ["git", "remote", "set-url", "origin", original_url],
                cwd=repo_path,
                capture_output=True
            )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Successfully pushed branch '{branch_name}' to remote",
                "push_output": result.stdout + result.stderr
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to push branch: {result.stderr}",
                "error_details": result.stderr,
                "stdout": result.stdout
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to push branch: {str(e)}",
            "error_type": type(e).__name__
        }


def create_pull_request(
    tool_context: ToolContext,
    repo_url: str,
    title: str,
    body: str,
    head_branch: str,
    base_branch: str,
    token: str
) -> dict:
    """
    Create a pull request on GitHub using the GitHub API.
    
    Args:
        tool_context: ADK tool context
        repo_url: GitHub repository URL (e.g., https://github.com/owner/repo)
        title: PR title
        body: PR description
        head_branch: Source branch name
        base_branch: Target branch name
        token: GitHub personal access token
        
    Returns:
        dict with status, pr_url, pr_number
    """
    try:
        import requests
        
        # ============ DEBUG LOGGING ============
        print("\n" + "=" * 80)
        print("CREATE_PULL_REQUEST DEBUG LOGS")
        print("=" * 80)
        print(f"repo_url: {repo_url}")
        print(f"title: {title}")
        print(f"head_branch: {head_branch}")
        print(f"base_branch: {base_branch}")
        print(f"token provided: {bool(token)}")
        print(f"token type: {type(token)}")
        print(f"token length: {len(token) if token else 0}")
        if token:
            print(f"token starts with: {token[:10]}..." if len(token) > 10 else f"token: {token}")
        print("=" * 80 + "\n")
        # =======================================
        
        # Validate token format
        if not token or len(token) < 20 or '<' in token or '>' in token:
            return {
                "status": "error",
                "message": f"Invalid GitHub token format. Token appears to be a placeholder: '{token}'. "
                          f"Token should start with 'ghp_' and be ~40 characters. "
                          f"Call get_github_config tool first to retrieve the actual token from .env/state.",
                "token_length": len(token) if token else 0,
                "token_preview": token[:20] if token and len(token) > 20 else token
            }
        
        # Clean and parse the repository URL
        clean_url = repo_url.rstrip('/').replace('.git', '')
        
        # Extract owner and repo from URL
        # Handles: https://github.com/owner/repo, git@github.com:owner/repo
        if "github.com" in clean_url:
            if "github.com/" in clean_url:
                # https://github.com/owner/repo
                parts = clean_url.split("github.com/")[1].split("/")
                owner = parts[0]
                repo = parts[1] if len(parts) > 1 else parts[0]
            elif "github.com:" in clean_url:
                # git@github.com:owner/repo
                parts = clean_url.split("github.com:")[1].split("/")
                owner = parts[0]
                repo = parts[1] if len(parts) > 1 else parts[0]
            else:
                return {
                    "status": "error",
                    "message": f"Invalid GitHub URL format: {repo_url}"
                }
        else:
            return {
                "status": "error",
                "message": f"Not a GitHub URL: {repo_url}"
            }
        
        # GitHub API endpoint
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        
        # ============ DEBUG LOGGING ============
        print(f"Extracted owner: {owner}")
        print(f"Extracted repo: {repo}")
        print(f"API URL: {api_url}")
        # =======================================
        
        # Prepare request headers - GitHub prefers "Bearer" or "token" prefix
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Prepare PR data
        data = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch
        }
        
        # ============ DEBUG LOGGING ============
        print(f"Request data: {data}")
        print("Sending PR creation request...")
        # =======================================
        
        # Create PR
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        
        # ============ DEBUG LOGGING ============
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text[:500]}...")  # First 500 chars
        print("=" * 80 + "\n")
        # =======================================
        
        if response.status_code == 201:
            pr_data = response.json()
            pr_url = pr_data.get("html_url")
            pr_number = pr_data.get("number")
            
            # Store PR info in state
            tool_context.state["pr_url"] = pr_url
            tool_context.state["pr_number"] = pr_number
            
            return {
                "status": "success",
                "pr_url": pr_url,
                "pr_number": pr_number,
                "message": f"Successfully created PR #{pr_number}: {pr_url}"
            }
        elif response.status_code == 401:
            return {
                "status": "error",
                "message": f"Authentication failed (401). Check if GitHub token is valid and has 'repo' permissions.",
                "error_details": response.text,
                "status_code": 401
            }
        elif response.status_code == 422:
            return {
                "status": "error",
                "message": f"PR creation failed (422). Possible reasons: PR already exists, invalid branch names, or validation error.",
                "error_details": response.text,
                "status_code": 422
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to create PR: HTTP {response.status_code}",
                "error_details": response.text,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Network error creating PR: {str(e)}",
            "error_type": "NetworkError"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create pull request: {str(e)}",
            "error_type": type(e).__name__
        }


# Create ADK tool instances
git_clone_tool = FunctionTool(func=git_clone)
git_create_branch_tool = FunctionTool(func=git_create_branch)
git_add_files_tool = FunctionTool(func=git_add_files)
git_commit_tool = FunctionTool(func=git_commit)
git_push_tool = FunctionTool(func=git_push)
create_pull_request_tool = FunctionTool(func=create_pull_request)

