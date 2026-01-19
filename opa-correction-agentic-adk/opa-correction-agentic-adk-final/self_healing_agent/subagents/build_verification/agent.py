from google.adk.agents import SequentialAgent
from .terraform_validator import terraform_validator
from .opa_evaluator import opa_evaluator
from .verification_aggregator import verification_aggregator

# Build verification as a SequentialAgent
# This ensures each verification step runs in order:
# 1. Terraform syntax validation
# 2. OPA compliance evaluation  
# 3. Result aggregation and success determination
build_verification = SequentialAgent(
    name="build_verification",
    description="Sequential verification: Terraform validation → OPA evaluation → Result aggregation",
    sub_agents=[
        terraform_validator,      # Step 1: Validate Terraform syntax
        opa_evaluator,            # Step 2: Generate plan and run OPA evaluation
        verification_aggregator   # Step 3: Aggregate results and determine success
    ]
)
