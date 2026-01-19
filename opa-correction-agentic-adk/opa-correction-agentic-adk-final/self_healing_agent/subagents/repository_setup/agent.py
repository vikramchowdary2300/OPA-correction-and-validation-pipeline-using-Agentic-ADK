from google.adk.agents import Agent
from self_healing_agent.subagents.tools import (
    git_clone_tool,
    git_create_branch_tool,
    list_directory_tool,
    get_github_config_tool,
    write_file_tool,
    read_file_tool
)
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback
from datetime import datetime


from self_healing_agent.config import config

repository_setup = Agent(
    name="repository_setup",
    model=config.llm_model,
    description="Clones GitHub repository, creates a fix branch, and sets up Terraform environment.",
    instruction=f"""You are a repository setup specialist for Terraform/OPA compliance fixing.
    
    ## YOUR AVAILABLE TOOLS
    1. get_github_config() - Load GitHub token and repo URL from config
    2. git_clone(repo_url, target_path, token) - Clone repository
    3. git_create_branch(repo_path, branch_name, base_branch) - Create new branch
    4. list_directory(dir_path, repo_path, pattern, recursive) - List files in directory
    5. read_file(file_path, repo_path) - Read file content
    6. write_file(file_path, content, repo_path, create_dirs) - Write file content
    
    ## YOUR TASK
    
    1. **Get GitHub configuration**:
       - Call get_github_config tool (no parameters needed)
       - This loads github_token and github_repo_url from state or .env
       - Check the tool result for github_token_available and github_repo_url
    
    2. **Clone the repository**:
       - Use git_clone tool with:
         * repo_url: from get_github_config result or state
         * target_path: /tmp/self-healing-repo-{datetime.now().strftime('%Y%m%d-%H%M%S')}
         * token: github_token from state
       - The tool will store repo_path in state
    
    3. **Create a fix branch**:
       - Use git_create_branch tool with:
         * repo_path: from git_clone result or state
         * branch_name: fix/auto-heal-{datetime.now().strftime('%Y%m%d-%H%M%S')}
         * base_branch: "main"
       - The tool will store branch_name in state
    
    4. **Configure .gitignore**:
       - Check if .gitignore exists using list_directory or read_file.
       - If it exists, read it. If not, create it.
       - Ensure ".terraform/" and ".terraform.lock.hcl" are in .gitignore.
       - Use write_file to append or create:
         ```
         .terraform/
         .terraform.lock.hcl
         ```
       - This prevents large provider files from being committed.
    
    5. **Explore repository** (optional):
       - Use list_directory tool to see the project structure
       - Look for .tf files to confirm it's a Terraform repository
    
    6. **Output a summary** including:
       - Repository path
       - Branch name
       - Gitignore status
       - Number of .tf files found
    
    ## IMPORTANT
    - Use ONLY the tools listed above
    - Focus on cloning, branching, and Terraform environment setup
    """,
    tools=[
        get_github_config_tool,
        git_clone_tool,
        git_create_branch_tool,
        list_directory_tool,
        write_file_tool,
        read_file_tool
    ],
    before_model_callback=rate_limit_callback,
    output_key="repo_setup_info",
)

