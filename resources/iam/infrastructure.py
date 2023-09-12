import aws_cdk.aws_iam as iam

import aws_cdk as cdk
import constants

from constructs import Construct

class IAMRoles(Construct):
    def __init__(self, scope: Construct, id_: str, vpcid: str, **kwargs):
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
        self.lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"))
        self.lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")) 


