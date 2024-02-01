from os import getenv

from phi.aws.app.fastapi import FastApi
from phi.aws.app.streamlit import Streamlit
from phi.aws.resources import AwsResources
from phi.aws.resource.ecs import EcsCluster
from phi.aws.resource.ec2 import SecurityGroup, InboundRule
from phi.aws.resource.rds import DbInstance, DbSubnetGroup
from phi.aws.resource.reference import AwsReference
from phi.aws.resource.s3 import S3Bucket
from phi.aws.resource.secret import SecretsManager
from phi.docker.resources import DockerResources
from phi.docker.resource.image import DockerImage

from workspace.settings import ws_settings

#
# -*- Resources for the Production Environment
#
# Skip resource deletion when running `phi ws down` (set to True after initial deployment)
skip_delete: bool = False
# Save resource outputs to workspace/outputs
save_output: bool = True
# Create load balancer for the application
create_load_balancer: bool = True
# Key used for naming production resources: ai-app-prd
prd_key: str = f"{ws_settings.ws_name}-{ws_settings.prd_env}"

# -*- Production image
prd_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.prd_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    platforms=["linux/amd64", "linux/arm64"],
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
)

# -*- S3 bucket for production data (set enabled=True when needed)
prd_bucket = S3Bucket(
    name=f"{prd_key}-data",
    enabled=False,
    acl="private",
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- Secrets for production application
prd_secret = SecretsManager(
    name=f"{prd_key}-secret",
    group="app",
    # Create secret from workspace/secrets/prd_app_secrets.yml
    secret_files=[ws_settings.ws_root.joinpath("workspace/secrets/prd_app_secrets.yml")],
    skip_delete=skip_delete,
    save_output=save_output,
)
# -*- Secrets for production database
prd_db_secret = SecretsManager(
    name=f"{prd_key}-db-secret",
    group="db",
    # Create secret from workspace/secrets/prd_db_secrets.yml
    secret_files=[ws_settings.ws_root.joinpath("workspace/secrets/prd_db_secrets.yml")],
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- Security Group for the load balancer
prd_lb_sg = SecurityGroup(
    name=f"{prd_key}-lb-security-group",
    enabled=create_load_balancer,
    group="app",
    description="Security group for the load balancer",
    inbound_rules=[
        InboundRule(
            description="Allow HTTP traffic from the internet",
            port=80,
            cidr_ip="0.0.0.0/0",
        ),
        InboundRule(
            description="Allow HTTPS traffic from the internet",
            port=443,
            cidr_ip="0.0.0.0/0",
        ),
    ],
    skip_delete=skip_delete,
    save_output=save_output,
)
# -*- Security Group for the application
prd_sg = SecurityGroup(
    name=f"{prd_key}-security-group",
    enabled=ws_settings.prd_api_enabled or ws_settings.prd_app_enabled,
    group="app",
    description="Security group for the production application",
    inbound_rules=[
        InboundRule(
            description="Allow traffic from LB to the FastAPI server",
            port=8000,
            security_group_id=AwsReference(prd_lb_sg.get_security_group_id),
        ),
        InboundRule(
            description="Allow traffic from LB to the Streamlit app",
            port=8501,
            security_group_id=AwsReference(prd_lb_sg.get_security_group_id),
        ),
    ],
    depends_on=[prd_lb_sg],
    skip_delete=skip_delete,
    save_output=save_output,
)
# -*- Security Group for the database
prd_db_port = 5432
prd_db_sg = SecurityGroup(
    name=f"{prd_key}-db-security-group",
    enabled=ws_settings.prd_db_enabled,
    group="db",
    description="Security group for the production database",
    inbound_rules=[
        InboundRule(
            description="Allow traffic from apps to the database",
            port=prd_db_port,
            security_group_id=AwsReference(prd_sg.get_security_group_id),
        ),
    ],
    depends_on=[prd_sg],
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- RDS Database Subnet Group
prd_db_subnet_group = DbSubnetGroup(
    name=f"{prd_key}-db-sg",
    enabled=ws_settings.prd_db_enabled,
    group="db",
    subnet_ids=ws_settings.subnet_ids,
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- RDS Database Instance
prd_db = DbInstance(
    name=f"{prd_key}-db",
    enabled=ws_settings.prd_db_enabled,
    group="db",
    db_name="app",
    port=prd_db_port,
    engine="postgres",
    engine_version="16.1",
    allocated_storage=64,
    db_instance_class="db.t4g.large",
    db_security_groups=[prd_db_sg],
    db_subnet_group=prd_db_subnet_group,
    availability_zone=ws_settings.aws_az1,
    publicly_accessible=False,
    enable_performance_insights=True,
    aws_secret=prd_db_secret,
    skip_delete=skip_delete,
    save_output=save_output,
    # Do not wait for the db to be deleted
    wait_for_delete=False,
)

# -*- ECS cluster
launch_type = "FARGATE"
prd_ecs_cluster = EcsCluster(
    name=f"{prd_key}-cluster",
    ecs_cluster_name=prd_key,
    capacity_providers=[launch_type],
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- Build container environment
container_env = {
    "RUNTIME_ENV": "prd",
    # Get the OpenAI API key from the local environment
    "OPENAI_API_KEY": getenv("OPENAI_API_KEY"),
    # Database configuration
    "DB_HOST": AwsReference(prd_db.get_db_endpoint),
    "DB_PORT": AwsReference(prd_db.get_db_port),
    "DB_USER": AwsReference(prd_db.get_master_username),
    "DB_PASS": AwsReference(prd_db.get_master_user_password),
    "DB_DATABASE": AwsReference(prd_db.get_db_name),
    # Wait for database to be available before starting the application
    "WAIT_FOR_DB": ws_settings.prd_db_enabled,
    # Migrate database on startup using alembic
    # "MIGRATE_DB": ws_settings.prd_db_enabled,
}

# -*- Streamlit running on ECS
prd_streamlit = Streamlit(
    name=f"app-{ws_settings.ws_name}",
    enabled=ws_settings.prd_app_enabled,
    group="app",
    image=prd_image,
    command="streamlit run app/Home.py",
    port_number=8501,
    ecs_task_cpu="2048",
    ecs_task_memory="4096",
    ecs_service_count=1,
    ecs_cluster=prd_ecs_cluster,
    aws_secrets=[prd_secret],
    subnets=ws_settings.subnet_ids,
    security_groups=[prd_sg],
    # To enable HTTPS, create an ACM certificate and add the ARN below:
    load_balancer_enable_https=True,
    load_balancer_certificate_arn="arn:aws:acm:us-east-1:497891874516:certificate/6598c24a-d4fc-4f17-8ee0-0d3906eb705f",
    load_balancer_security_groups=[prd_lb_sg],
    create_load_balancer=create_load_balancer,
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    skip_delete=skip_delete,
    save_output=save_output,
    # Do not wait for the service to stabilize
    wait_for_create=False,
    # Do not wait for the service to be deleted
    wait_for_delete=False,
)

# -*- HN AI running on ECS
hn_ai = Streamlit(
    name=f"hn-{ws_settings.ws_name}",
    enabled=getenv("HACKERNEWS_AI", False),
    group="hn",
    image=prd_image,
    command="streamlit run hn_ai/app.py",
    port_number=8501,
    ecs_task_cpu="2048",
    ecs_task_memory="4096",
    ecs_service_count=2,
    ecs_cluster=prd_ecs_cluster,
    aws_secrets=[prd_secret],
    subnets=ws_settings.subnet_ids,
    security_groups=[prd_sg],
    # To enable HTTPS, create an ACM certificate and add the ARN below:
    load_balancer_enable_https=True,
    load_balancer_certificate_arn="arn:aws:acm:us-east-1:497891874516:certificate/6598c24a-d4fc-4f17-8ee0-0d3906eb705f",
    load_balancer_security_groups=[prd_lb_sg],
    create_load_balancer=create_load_balancer,
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    skip_delete=skip_delete,
    save_output=save_output,
    # Do not wait for the service to stabilize
    wait_for_create=False,
    # Do not wait for the service to be deleted
    wait_for_delete=False,
)

# -*- PDF AI running on ECS
pdf_ai = Streamlit(
    name=f"pdf-{ws_settings.ws_name}",
    enabled=getenv("PDF_AI", False),
    group="pdf",
    image=prd_image,
    command="streamlit run pdf_ai/app.py",
    # streamlit_server_max_upload_size=10,
    port_number=8501,
    ecs_task_cpu="2048",
    ecs_task_memory="4096",
    ecs_service_count=2,
    ecs_cluster=prd_ecs_cluster,
    aws_secrets=[prd_secret],
    subnets=ws_settings.subnet_ids,
    security_groups=[prd_sg],
    # To enable HTTPS, create an ACM certificate and add the ARN below:
    load_balancer_enable_https=True,
    load_balancer_certificate_arn="arn:aws:acm:us-east-1:497891874516:certificate/6598c24a-d4fc-4f17-8ee0-0d3906eb705f",
    load_balancer_security_groups=[prd_lb_sg],
    create_load_balancer=create_load_balancer,
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    skip_delete=skip_delete,
    save_output=save_output,
    # Do not wait for the service to stabilize
    wait_for_create=False,
    # Do not wait for the service to be deleted
    wait_for_delete=False,
)

# -*- PDF AI running on ECS
arxiv_ai = Streamlit(
    name=f"arxiv-{ws_settings.ws_name}",
    enabled=getenv("ARXIV_AI", False),
    group="arxiv",
    image=prd_image,
    command="streamlit run arxiv_ai/app.py",
    port_number=8501,
    ecs_task_cpu="2048",
    ecs_task_memory="4096",
    ecs_service_count=3,
    ecs_cluster=prd_ecs_cluster,
    aws_secrets=[prd_secret],
    subnets=ws_settings.subnet_ids,
    security_groups=[prd_sg],
    # To enable HTTPS, create an ACM certificate and add the ARN below:
    load_balancer_enable_https=True,
    load_balancer_certificate_arn="arn:aws:acm:us-east-1:497891874516:certificate/6598c24a-d4fc-4f17-8ee0-0d3906eb705f",
    load_balancer_security_groups=[prd_lb_sg],
    create_load_balancer=create_load_balancer,
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    skip_delete=skip_delete,
    save_output=save_output,
    # Do not wait for the service to stabilize
    wait_for_create=False,
    # Do not wait for the service to be deleted
    wait_for_delete=False,
)

# -*- FastApi running on ECS
prd_fastapi = FastApi(
    name=f"api-{ws_settings.ws_name}",
    enabled=ws_settings.prd_api_enabled,
    group="app",
    image=prd_image,
    command="uvicorn api.main:app",
    port_number=8000,
    ecs_task_cpu="2048",
    ecs_task_memory="4096",
    ecs_service_count=1,
    ecs_cluster=prd_ecs_cluster,
    aws_secrets=[prd_secret],
    subnets=ws_settings.subnet_ids,
    security_groups=[prd_sg],
    # To enable HTTPS, create an ACM certificate and add the ARN below:
    load_balancer_enable_https=True,
    load_balancer_certificate_arn="arn:aws:acm:us-east-1:497891874516:certificate/6598c24a-d4fc-4f17-8ee0-0d3906eb705f",
    load_balancer_security_groups=[prd_lb_sg],
    create_load_balancer=create_load_balancer,
    health_check_path="/v1/health",
    env_vars=container_env,
    use_cache=ws_settings.use_cache,
    skip_delete=skip_delete,
    save_output=save_output,
    # Do not wait for the service to stabilize
    wait_for_create=False,
    # Do not wait for the service to be deleted
    wait_for_delete=False,
)

# -*- Production DockerResources
prd_docker_resources = DockerResources(
    env=ws_settings.prd_env,
    network=ws_settings.ws_name,
    resources=[prd_image],
)

# -*- Production AwsResources
prd_aws_resources = AwsResources(
    env=ws_settings.prd_env,
    apps=[prd_streamlit, prd_fastapi, hn_ai, pdf_ai],
    resources=[
        prd_lb_sg,
        prd_sg,
        prd_db_sg,
        prd_secret,
        prd_db_secret,
        prd_db_subnet_group,
        prd_db,
        prd_ecs_cluster,
        prd_bucket,
    ],
)
