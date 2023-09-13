import aws_cdk.aws_lambda as lambdafunction
import aws_cdk.aws_iam as iam

import aws_cdk as cdk
import constants
from aws_cdk import Duration

from constructs import Construct

class LambdaFunctions(Construct):
    def __init__(self, scope: Construct, id_: str, lambda_role: iam.IRole, **kwargs):
        super().__init__(scope, id_)

        # lambda function for on demand index creation
        build_index_function = lambdafunction.DockerImageFunction(self, f"{constants.CDK_APP_NAME}-indexer-lambda-function", 
            function_name=f"{constants.CDK_APP_NAME}-indexer-function",
            code=lambdafunction.DockerImageCode.from_image_asset("resources/ecr/runtime/index_creator/"),
            environment={
                    'DEFAULT_ACCOUNT': constants.CDK_ACCOUNT,
                    'DEFAULT_REGION': constants.CDK_REGION,
                    'S3_SOURCE_DOCUMENTS_BUCKET': constants.S3_SOURCE_DOCUMENTS_BUCKET,
                    'S3_INDEX_STORE_BUCKET': constants.S3_INDEX_STORE_BUCKET
            },
            role=lambda_role,
            memory_size=10240,
            timeout=Duration.minutes(5)
        )

        # version = build_index_function.current_version
        # build_index_alias = lambdafunction.Alias(self, f"{constants.CDK_APP_NAME}-indexer-lambda-alias",
        #     alias_name="sandbox",
        #     provisioned_concurrent_executions=1,
        #     version=version
        # )

        #source_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(read_source_and_build_index_function))

        # # # lambda function for our inference
        # inference_function = lambdafunction.DockerImageFunction(self, f"{constants.CDK_APP_NAME}-inference-lambda-function", 
        #     function_name=f"{constants.CDK_APP_NAME}-inference-function",
        #     code=lambdafunction.DockerImageCode.from_image_asset("resources/ecr/runtime/inference/"),
        #      environment={
        #             'S3_SOURCE_DOCUMENTS_BUCKET': constants.S3_SOURCE_DOCUMENTS_BUCKET,
        #             'S3_INDEX_STORE_BUCKET': constants.S3_INDEX_STORE_BUCKET
        #     },
        #     role=lambda_role,
        #     memory_size=10240,
        #     timeout=Duration.minutes(5)
        # )
        # inference_function.grant_invoke(iam.ServicePrincipal("lexv2.amazonaws.com"))