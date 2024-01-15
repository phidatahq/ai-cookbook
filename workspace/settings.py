from pathlib import Path

from phi.workspace.settings import WorkspaceSettings

#
# -*- Define workspace settings using a WorkspaceSettings object
# these values can also be set using environment variables or a .env file
#
ws_settings = WorkspaceSettings(
    # Workspace name: used for naming resources
    ws_name="ai-cookbook",
    # Path to the workspace root
    ws_root=Path(__file__).parent.parent.resolve(),
    # -*- Dev settings
    dev_env="dev",
    # -*- Dev Apps
    dev_app_enabled=True,
    dev_api_enabled=True,
    dev_db_enabled=True,
    # dev_jupyter_enabled=True,
    # -*- Production settings
    prd_env="prd",
    # -*- Production Apps
    prd_app_enabled=True,
    prd_api_enabled=True,
    prd_db_enabled=True,
    # -*- AWS settings
    # Region for AWS resources
    aws_region="us-east-1",
    # Availability Zones for AWS resources
    aws_az1="us-east-1a",
    aws_az2="us-east-1b",
    # Subnet IDs in the aws_region
    # subnet_ids=["subnet-xyz", "subnet-xyz"],
    # -*- Image Settings
    # Repository for images (for example, to use ECR use the following format)
    # image_repo="[ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com",
    # Build images locally
    build_images=True,
    # Push images after building
    # push_images=True,
)
