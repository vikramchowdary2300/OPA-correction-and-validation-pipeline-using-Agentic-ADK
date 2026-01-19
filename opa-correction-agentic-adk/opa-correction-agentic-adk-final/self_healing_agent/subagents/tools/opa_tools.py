import subprocess
import json
import os
from typing import Dict, Any, List, Optional
from google.adk.tools import ToolContext


def run_opa_eval(
    tool_context: ToolContext,
    policy_path: str,
    repo_path: str
) -> Dict[str, Any]:
    """
    Generates a Terraform plan and runs OPA evaluation against it.
    
    This function:
    1. Ensures Terraform is initialized
    2. Generates a fresh Terraform plan
    3. Converts the plan to JSON
    4. Runs OPA evaluation against the plan
    
    Args:
        tool_context: ADK tool context for state management
        policy_path: Path to the .rego policy file or directory
        repo_path: Path to the Terraform repository
        
    Returns:
        Dictionary containing the OPA evaluation result and plan paths.
    """
    try:
        # Step 1: Check if Terraform is initialized
        terraform_dir = os.path.join(repo_path, ".terraform")
        if not os.path.exists(terraform_dir):
            print(f"Terraform not initialized. Running 'terraform init' in {repo_path}...")
            init_cmd = ["terraform", "init", "-input=false", "-no-color"]
            init_result = subprocess.run(
                init_cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if init_result.returncode != 0:
                return {
                    "error": f"Terraform init failed: {init_result.stderr}",
                    "success": False,
                    "stderr": init_result.stderr,
                    "stdout": init_result.stdout
                }
            
            print("Terraform init successful.")
            tool_context.state["terraform_initialized"] = True
        
        # Step 2: Generate Terraform plan
        plan_file = os.path.join(repo_path, "tfplan")
        print(f"Generating Terraform plan in {repo_path}...")
        plan_cmd = ["terraform", "plan", "-out=tfplan", "-input=false", "-no-color"]
        plan_result = subprocess.run(
            plan_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if plan_result.returncode != 0:
            return {
                "error": f"Terraform plan failed: {plan_result.stderr}",
                "success": False,
                "stderr": plan_result.stderr,
                "stdout": plan_result.stdout
            }
        
        print("Terraform plan generated successfully.")
        tool_context.state["tfplan_path"] = plan_file
        
        # Step 3: Convert plan to JSON
        plan_json_file = os.path.join(repo_path, "tfplan.json")
        print(f"Converting plan to JSON: {plan_json_file}...")
        show_cmd = ["terraform", "show", "-json", "tfplan"]
        show_result = subprocess.run(
            show_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if show_result.returncode != 0:
            return {
                "error": f"Terraform show failed: {show_result.stderr}",
                "success": False,
                "stderr": show_result.stderr,
                "stdout": show_result.stdout
            }
        
        # Write JSON to file
        with open(plan_json_file, 'w') as f:
            f.write(show_result.stdout)
        
        print(f"Plan JSON saved to {plan_json_file}")
        tool_context.state["tfplan_json_path"] = plan_json_file
        
        # Step 4: Run OPA evaluation
        print(f"Running OPA evaluation with policy: {policy_path}...")
        opa_cmd = ["opa", "eval", "-i", plan_json_file, "-d", policy_path, "data", "-f", "json"]
        opa_result = subprocess.run(
            opa_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if opa_result.returncode != 0:
            return {
                "error": f"OPA evaluation failed: {opa_result.stderr}",
                "success": False,
                "stderr": opa_result.stderr,
                "stdout": opa_result.stdout
            }
        
        # Parse OPA output
        opa_output = json.loads(opa_result.stdout)
        
        return {
            "success": True,
            "opa_output": opa_output,
            "plan_path": plan_file,
            "plan_json_path": plan_json_file,
            "message": "OPA evaluation completed successfully"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "exception_type": type(e).__name__
        }


def parse_opa_json(opa_output: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses OPA JSON output to extract violations.
    
    This assumes a specific structure in the Rego policy (e.g., `deny` rules).
    Adjust based on your specific policy structure.
    
    Args:
        opa_output: The JSON output from `opa eval`.
        
    Returns:
        List of violation dictionaries.
    """
    violations = []
    try:
        # Navigate the OPA result structure. 
        # Usually result['result'][0]['expressions'][0]['value'] contains the policy evaluation.
        # If we queried 'data', we get everything.
        
        if 'result' in opa_output:
            for res in opa_output['result']:
                if 'expressions' in res:
                    for expr in res['expressions']:
                        value = expr.get('value', {})
                        # Traverse to find 'deny' or 'violation' rules
                        # This is a heuristic; policies might be structured differently.
                        # We look for any key that looks like a package name, then 'deny'.
                        for pkg_name, pkg_content in value.items():
                            if isinstance(pkg_content, dict):
                                if 'deny' in pkg_content:
                                    denials = pkg_content['deny']
                                    if isinstance(denials, list):
                                        for denial in denials:
                                            violations.append({
                                                "package": pkg_name,
                                                "message": denial,
                                                "severity": "high" # Default
                                            })
                                elif 'violation' in pkg_content:
                                     # Some policies use 'violation' rule
                                    for v in pkg_content['violation']:
                                        violations.append({
                                            "package": pkg_name,
                                            "message": v,
                                            "severity": "high"
                                        })
                                        
    except Exception as e:
        print(f"Error parsing OPA output: {e}")
        
    return violations

def validate_terraform(path: str) -> Dict[str, Any]:
    """
    Runs `terraform validate` in the given directory.
    """
    try:
        cmd = ["terraform", "validate", "-json"]
        result = subprocess.run(cmd, cwd=path, capture_output=True, text=True, check=False)
        
        # Check if validation failed due to missing providers
        # Error can be in stderr or embedded in stdout JSON
        print("stdout: ", result.stdout)
        print("stderr: ", result.stderr)
        combined_output = (result.stderr or "") + (result.stdout or "")
        if result.returncode != 0 and ("Missing required provider" in combined_output or "provider registry.terraform.io" in combined_output):
            print("Missing providers detected. Running 'terraform init'...")
            init_cmd = ["terraform", "init", "-input=false", "-no-color"]
            init_result = subprocess.run(init_cmd, cwd=path, capture_output=True, text=True, check=False)
            
            if init_result.returncode == 0:
                print("Terraform init successful. Retrying validation...")
                # Retry validation
                result = subprocess.run(cmd, cwd=path, capture_output=True, text=True, check=False)
            else:
                return {
                    "success": False,
                    "error": f"Terraform init failed: {init_result.stderr}",
                    "stderr": init_result.stderr,
                    "stdout": init_result.stdout
                }

        output = {}
        try:
            output = json.loads(result.stdout)
        except:
            output = {"raw_output": result.stdout}
            
        return {
            "success": result.returncode == 0,
            "output": output,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"error": str(e), "success": False}

from google.adk.tools import FunctionTool

# Tool definitions for the agent
run_opa_eval_tool = FunctionTool(func=run_opa_eval)
parse_opa_json_tool = FunctionTool(func=parse_opa_json)
validate_terraform_tool = FunctionTool(func=validate_terraform)

