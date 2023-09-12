import os
import helper_functions.constant_helpers as const_helpers
import aws_cdk as cdk

CDK_ENV = cdk.Environment(
     account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)

CDK_APP_NAME = "conversational-bot"
CDK_APP_PYTHON_VERSION = "3.10"

CDK_PARTITION="aws"
CDK_ACCOUNT=CDK_ENV.account
CDK_REGION=CDK_ENV.region

GITHUB_CONNECTION_ARN = const_helpers.find_CodeStarARN(CDK_ACCOUNT)
GITHUB_OWNER = "ivansmith7795"
GITHUB_ORG = "ivansmith7795"
GITHUB_REPO = "conversational-bot"
GITHUB_TRUNK_BRANCH = const_helpers.find_repo_branch(CDK_ACCOUNT)

DEPLOY_ENV = const_helpers.find_branch(CDK_ACCOUNT)

PIPELINE_ENV = cdk.Environment(account=CDK_ACCOUNT, region=CDK_REGION)

VPC_ID = const_helpers.find_VPCID(CDK_ACCOUNT)

DEV_ENV = cdk.Environment(account=CDK_ACCOUNT, region=CDK_REGION)

S3_SOURCE_DOCUMENTS = "conversational-bot-source-documents-" + str(CDK_ACCOUNT) + "-" + str(CDK_REGION)
S3_INDEX_STORE = "conversational-bot-index-store-" + str(CDK_ACCOUNT) + "-" + str(CDK_REGION)
