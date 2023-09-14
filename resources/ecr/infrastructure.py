from aws_cdk import aws_ecr_assets as ecr

import aws_cdk as cdk
import constants
import yaml

from constructs import Construct

class ECRImages(Construct):
    def __init__(self, scope: Construct, id_: str,  **kwargs):
        super().__init__(scope, id_)

        self.indexer = ecr.DockerImageAsset(self, f"{constants.CDK_APP_NAME}-indexer-image",
            directory="resources/ecr/runtime/indexer",
            network_mode=ecr.NetworkMode.HOST
        )