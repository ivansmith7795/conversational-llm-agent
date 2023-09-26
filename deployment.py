from multiprocessing.sharedctypes import Value
from unicodedata import name
import constants

from resources.s3.infrastructure import S3Buckets
from resources.iam.infrastructure import IAMRoles
from resources.ecr.infrastructure import ECRImages
from resources.ecs.infrastructure import ECSCluster
from resources.lambdas.infrastructure import LambdaFunctions
from resources.ssm.infrastructure import SSMParameters
from resources.lex.infrastructure import LexBots


from aws_cdk import (
    Stack, Stage
)

from constructs import Construct

class SolutionResources(Stage):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        solution_infrastack = Stack(self, f"infrastructure", env=constants.CDK_ENV)
        s3 = S3Buckets(solution_infrastack, f"{constants.CDK_APP_NAME}-s3-buckets", constants.VPC_ID)
        ssm = SSMParameters(solution_infrastack,  f"{constants.CDK_APP_NAME}-ssm-parameters")
        iam = IAMRoles(solution_infrastack, f"{constants.CDK_APP_NAME}-iam-roles", constants.VPC_ID, s3.s3_index_store.bucket_arn, s3.s3_source_documents_bucket.bucket_arn, ssm.llm_service_ip_param.parameter_arn)
        ecr = ECRImages(solution_infrastack,  f"{constants.CDK_APP_NAME}-ecr-images")
        ecs = ECSCluster(solution_infrastack,  f"{constants.CDK_APP_NAME}-ecs-tasks", constants.VPC_ID, ecr.indexer.image_uri, iam.indexer_execution_iam_role, iam.indexer_task_iam_role, ecr.llm.image_uri, iam.llm_execution_iam_role, iam.llm_task_iam_role)
        lambdas = LambdaFunctions(solution_infrastack,  f"{constants.CDK_APP_NAME}-lambda-functions", constants.VPC_ID, iam.lambda_role, ssm.llm_service_ip_param.parameter_name)
        lex = LexBots(solution_infrastack,  f"{constants.CDK_APP_NAME}-lex-bots", lambdas.inference_function.function_arn, iam.lex_role.role_arn)