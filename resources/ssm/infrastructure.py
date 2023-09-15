import aws_cdk.aws_signer as signer
import aws_cdk.aws_ssm  as ssm

import aws_cdk as cdk
import constants

from constructs import Construct

class SSMParameters(Construct):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_)

        self.llm_service_ip_param = ssm.StringParameter(self, f"{constants.CDK_APP_NAME}-ssm-fargate-parameter",
            allowed_pattern=".*",
            description="The IP address of the running LLM fargate service",
            parameter_name=f"{constants.CDK_APP_NAME}-ssm-fargate-parameter",
            string_value="0.0.0.0"
        )