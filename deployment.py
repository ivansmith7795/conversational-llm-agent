from multiprocessing.sharedctypes import Value
from unicodedata import name
import constants

from resources.s3.infrastructure import S3Buckets
from resources.iam.infrastructure import IAMRoles
from resources.lambdas.infrastructure import LambdaFunctions
from resources.lex.infrastructure import LexBots

from aws_cdk import (
    Stack, Stage
)

from constructs import Construct

class SolutionResources(Stage):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        solution_infrastack = Stack(self, f"infrastructure", env=constants.CDK_ENV)
        iam = IAMRoles(solution_infrastack, f"{constants.CDK_APP_NAME}-iam-roles", constants.VPC_ID)
        s3 = S3Buckets(solution_infrastack, f"{constants.CDK_APP_NAME}-s3-buckets", constants.VPC_ID)
        lambdas = LambdaFunctions(solution_infrastack,  f"{constants.CDK_APP_NAME}-lambda-functions", iam.lambda_role)
        lex = LexBots(solution_infrastack,  f"{constants.CDK_APP_NAME}-lex-bots", lambdas.inference_function.function_arn, iam.lex_role.role_arn)
