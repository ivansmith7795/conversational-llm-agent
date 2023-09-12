import aws_cdk.aws_signer as signer
import aws_cdk.aws_s3 as s3

import aws_cdk as cdk
import constants

from constructs import Construct

class S3Buckets(Construct):
    def __init__(self, scope: Construct, id_: str, vpcid: str, **kwargs):
        super().__init__(scope, id_)

        self.s3_source_documents_bucket = s3.Bucket(self, f"{constants.CDK_APP_NAME}-s3-source-document-bucket",
            bucket_name=constants.S3_SOURCE_DOCUMENTS,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )


        self.s3_source_documents_bucket.add_lifecycle_rule(
            abort_incomplete_multipart_upload_after=cdk.Duration.days(1),
            enabled=True,
            expiration=cdk.Duration.days(180),
            expired_object_delete_marker=False,
            id=f"{constants.CDK_APP_NAME}-s3-sagemaker-lifecycle-policy",
            transitions=[s3.Transition(
                storage_class=s3.StorageClass.GLACIER,
                transition_after=cdk.Duration.days(90)
            )]
        )


        self.s3_index_store = s3.Bucket(self, f"{constants.CDK_APP_NAME}-s3-indexer-store-bucket",
            bucket_name=constants.S3_INDEX_STORE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )


        self.s3_index_store.add_lifecycle_rule(
            abort_incomplete_multipart_upload_after=cdk.Duration.days(1),
            enabled=True,
            expiration=cdk.Duration.days(180),
            expired_object_delete_marker=False,
            id=f"{constants.CDK_APP_NAME}-s3-sagemaker-lifecycle-policy",
            transitions=[s3.Transition(
                storage_class=s3.StorageClass.GLACIER,
                transition_after=cdk.Duration.days(90)
            )]
        )