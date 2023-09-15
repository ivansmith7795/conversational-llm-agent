import aws_cdk.aws_iam as iam

import aws_cdk as cdk
import constants

from constructs import Construct

class IAMRoles(Construct):
    def __init__(self, scope: Construct, id_: str, vpcid: str, s3_indexer_bucket_arn: str, s3_document_bucket_arn: str, ssm_parameter_arn: str,**kwargs):
        super().__init__(scope, id_)

         # Iam role for bot to invoke lambda
        self.lex_role = iam.Role(self, f"{constants.CDK_APP_NAME}-lex-role",
            assumed_by=iam.ServicePrincipal("lexv2.amazonaws.com")
        )
        self.lex_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaExecute")) 

        # Iam role for lambda to invoke sagemaker
        self.lambda_role = iam.Role(self, f"{constants.CDK_APP_NAME}-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        self.lambda_role.add_to_policy(
            iam.PolicyStatement( 
                actions=["ssm:Get*", "ssm:List*", "ssm:Describe*"],
                resources=[
                    ssm_parameter_arn
                ])
        )

        # Indexer task role #
        self.indexer_task_iam_role = iam.Role(self, f"{constants.CDK_APP_NAME}-indexer-task-role",
            role_name=f"{constants.CDK_APP_NAME}-indexer-task-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for running indexer application"
        )
    
        self.indexer_task_iam_role.add_to_policy(
            iam.PolicyStatement( 
                actions=["s3:Get*", "s3:List*", "s3:Put*"],
                resources=[
                    s3_indexer_bucket_arn +'*',
                    s3_indexer_bucket_arn +'/*'
                ])
        )
       
        self.indexer_task_iam_role.add_to_policy(
            iam.PolicyStatement( 
                actions=["s3:Get*", "s3:List*"],
                resources=[
                    s3_document_bucket_arn +'*',
                    s3_document_bucket_arn +'/*'
                ])
        )

    
        self.indexer_execution_iam_role = iam.Role(self, f"{constants.CDK_APP_NAME}-indexer-execution-role",
            role_name=f"{constants.CDK_APP_NAME}-indexer-execution-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for running indexer ECS task creation"
        )

        self.indexer_execution_iam_role.add_to_policy(
            iam.PolicyStatement( 
                actions=["ecr:GetAuthorizationToken", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=["*"])
        )


        ### LLM Service Role ###
        self.llm_task_iam_role = iam.Role(self, f"{constants.CDK_APP_NAME}-llm-task-role",
            role_name=f"{constants.CDK_APP_NAME}-llm-task-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for running llm application"
        )
    
        self.llm_task_iam_role.add_to_policy(
            iam.PolicyStatement( 
                actions=["s3:Get*", "s3:List*"],
                resources=[
                    s3_indexer_bucket_arn +'*',
                    s3_indexer_bucket_arn +'/*'
                ])
        )

        self.llm_task_iam_role.add_to_policy(
            iam.PolicyStatement( 
                actions=["sagemaker:ListEndpoints", "sagemaker:InvokeEndpoint"],
                resources=[
                    "arn:aws:sagemaker:us-east-1:413034898429:endpoint/jumpstart-dft-meta-textgeneration-llama-2-7b-f"
                ])
        )

    
        self.llm_execution_iam_role = iam.Role(self, f"{constants.CDK_APP_NAME}-llm-execution-role",
            role_name=f"{constants.CDK_APP_NAME}-llm-execution-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for running llm ECS task creation"
        )

        self.llm_execution_iam_role.add_to_policy(
            iam.PolicyStatement( 
                actions=["ecr:GetAuthorizationToken", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=["*"])
        )
