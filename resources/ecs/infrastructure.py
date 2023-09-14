from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_applicationautoscaling as appscaling
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs

import aws_cdk as cdk
import constants
import yaml

from constructs import Construct

class ECSCluster(Construct):
    def __init__(self, scope: Construct, id_: str, vpcid: str, indexer_image_uri:str, indexer_execution_role:iam.IRole, indexer_task_role:iam.IRole, **kwargs):
        super().__init__(scope, id_)

        vpc = ec2.Vpc.from_lookup(self, "VPC",
            vpc_id =vpcid
        )
        
        conversational_cluster = ecs.Cluster(self, f"{constants.CDK_APP_NAME}-ecs-cluster", 
            vpc=vpc,
            cluster_name=f"{constants.CDK_APP_NAME}-ecs-cluster-" + f"{constants.DEPLOY_ENV}"
        )
         
        indexer_task_definition=ecs.FargateTaskDefinition(self, f"{constants.CDK_APP_NAME}-task-definition",
            family=f"{constants.CDK_APP_NAME}-ecs-indexer-task",
            ephemeral_storage_gib=100,
            memory_limit_mib=2048,
            cpu=512,
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
                cpu_architecture=ecs.CpuArchitecture.X86_64
            ),
            execution_role=indexer_execution_role,
            task_role=indexer_task_role
            
        )

        indexer_task_definition.add_container(f"{constants.CDK_APP_NAME}-container-ecs-image",
            image=ecs.ContainerImage.from_registry(indexer_image_uri),
             environment={
                    'DEFAULT_ACCOUNT': constants.CDK_ACCOUNT,
                    'DEFAULT_REGION': constants.CDK_REGION,
                    'SAGEMAKER_MODEL_ENDPOINT_NAME': constants.SAGEMAKER_MODEL_ENDPOINT_NAME,
                    'S3_SOURCE_DOCUMENTS_BUCKET': constants.S3_SOURCE_DOCUMENTS_BUCKET,
                    'S3_INDEX_STORE_BUCKET': constants.S3_INDEX_STORE_BUCKET
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=f"{constants.CDK_APP_NAME}",
                log_retention=logs.RetentionDays.THREE_MONTHS
            )
        )