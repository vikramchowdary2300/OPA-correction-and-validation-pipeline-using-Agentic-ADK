from google.adk.agents import Agent
from self_healing_agent.subagents.tools import (
    get_github_config_tool,
    git_add_files_tool,
    git_commit_tool,
    git_push_tool,
    create_pull_request_tool
)
from self_healing_agent.subagents.shared.callbacks import rate_limit_callback


from self_healing_agent.config import config

code_finalizer = Agent(
    name="code_finalizer",
    model=config.llm_model,
    description="Commits fixes to git, pushes branch, and creates a pull request on GitHub.",
    instruction="""You are a code finalization specialist. Your job is to commit fixes and create a PR.
    
    ## YOUR AVAILABLE TOOLS (5 tools ONLY)
    1. get_github_config() - Get github_token from state/config
    2. git_add_files(repo_path, files) - Stage files. Use files="." for all
    3. git_commit(repo_path, message, author_name, author_email) - Commit changes
    4. git_push(repo_path, branch_name, token, force) - Push to remote
    5. create_pull_request(repo_url, title, body, head_branch, base_branch, token) - Create PR
    
    ## YOUR TASK
    
    STEP 0: **Get GitHub token first**:
       - Call get_github_config tool - it returns github_token in the result
       - This is CRITICAL - you MUST use the token from the tool result
       - The tool result will contain: {"github_token": "ghp_actual_token_value", ...}
       - Store this token value and use it for git_push and create_pull_request
    
    After get_github_config, get from state: repo_path, branch_name, github_repo_url, files_modified, fixes_applied
    And get github_token from the get_github_config tool result (NOT from state directly)
    
    1. **Stage modified files**:
       - Call git_add_files tool with:
         * repo_path: from state
         * files: "." (to stage all changes)
    
    2. **Commit changes**:
       - Create commit message listing all fixes
       - Call git_commit tool with:
         * repo_path: from state
         * message: "fix: Auto-heal build errors\n\n[list fixes]"
         * author_name: "Self-Healing Agent"
         * author_email: "agent@self-healing.ai"
    
    3. **Push to remote**:
       - IMPORTANT: Use the github_token from get_github_config tool result (NOT placeholder)
       - Call git_push tool with:
         * repo_path: from state (e.g., "/tmp/self-healing-repo-...")
         * branch_name: from state (e.g., "fix/auto-heal-...")
         * token: the ACTUAL token from get_github_config result (starts with "ghp_")
         * force: False
       - The token should be the real value, not "<github_token>"
    
    4. **Create Pull Request**:
       - IMPORTANT: Use the SAME github_token from get_github_config result
       - Call create_pull_request tool with:
         * repo_url: github_repo_url from state (e.g., "https://github.com/owner/repo")
         * title: "🤖 Auto-fix: Resolved [N] build errors"
         * body: Markdown description with errors fixed, files changed
         * head_branch: branch_name from state (just branch name like "fix/auto-heal-...")
         * base_branch: "main" (or base_branch from state if available)
         * token: the ACTUAL token from get_github_config result (NOT placeholder)
       - If fails with 401, the token may be invalid
       - If fails with 422, check if PR already exists
    
    5. **Output the result**:
       - If successful: PR URL, PR number, commit SHA, summary
       - If push/PR fails: Return what you could complete + error details
       - Always include commit SHA (even if push fails)
    
    ## IMPORTANT
    - Use ONLY the 5 tools listed above
    - START by calling get_github_config to get the actual github_token
    - Do NOT use placeholder values like "<github_token>" - get the real token from state
    - Do NOT use tools like: write_file, read_file, run_build
    - Handle partial success (commit but no push) gracefully
    - Get all data from state: repo_path, branch_name, github_token, github_repo_url, etc.
    
    ## CRITICAL
    When calling git_push and create_pull_request:
    - Use the ACTUAL github_token value from state (after calling get_github_config)
    - The token should start with "ghp_" and be ~40 characters
    - Do NOT pass placeholder strings like "<github_token>"
    
    ## ERROR HANDLING
    - If git_push fails: Still try create_pull_request (branch might already be pushed)
    - If both fail with auth errors: Report that token needs 'repo' permissions
    - Always output what was accomplished (commit SHA, branch name, etc.)
    """,
    tools=[
        get_github_config_tool,
        git_add_files_tool,
        git_commit_tool,
        git_push_tool,
        create_pull_request_tool
    ],
    before_model_callback=rate_limit_callback,
    output_key="pr_details",
)

