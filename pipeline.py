import json
import pathlib
import constants
import aws_cdk.aws_iam as iam

import aws_cdk.aws_codepipeline_actions as codebuildactions
import aws_cdk.aws_codepipeline as code_pipeline

from typing import Any

from deployment import SolutionResources

from constructs import Construct

from aws_cdk import (
    Stack, pipelines, aws_codebuild as codebuild
)

class Pipeline(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        self.codepipeline_source = pipelines.CodePipelineSource.connection(
            f"{constants.GITHUB_ORG}/{constants.GITHUB_REPO}",
            constants.GITHUB_TRUNK_BRANCH,
            connection_arn=constants.GITHUB_CONNECTION_ARN,
        )
        self.synth_python_version = {
            "phases": {
                "install": {
                    "runtime-versions": {"python": constants.CDK_APP_PYTHON_VERSION}
                }
            }
        }
       
    
        synth_codebuild_step = pipelines.CodeBuildStep(
            f"{constants.CDK_APP_NAME}-synth",
            input=self.codepipeline_source,
            build_environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0
            ),
            partial_build_spec=codebuild.BuildSpec.from_object(self.synth_python_version),
            project_name=f"{constants.CDK_APP_NAME}-code-build-synth",
            install_commands=["./scripts/install-deps.sh"],
            commands=["npx cdk synth"],
            primary_output_directory="cdk.out",
        )
        codepipeline = pipelines.CodePipeline(
            self,
            f"{constants.CDK_APP_NAME}-codepipe",
            cli_version=Pipeline._get_cdk_cli_version(),
            cross_account_keys=True,
            synth=synth_codebuild_step,
            pipeline_name= f"{constants.CDK_APP_NAME}-code-pipeline-" + f"{constants.DEPLOY_ENV}"
        )

       

        self._add_deploy_solution_stage(codepipeline)

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).resolve().parent.joinpath("package.json")
        )
        with open(package_json_path) as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["dependencies"]["aws-cdk"])
        return cdk_cli_version


    def _add_deploy_solution_stage(self, codepipeline: pipelines.CodePipeline) -> None:
        deploy_stage = SolutionResources(
            self,
            f"{constants.CDK_APP_NAME}-deploy",
            env=constants.DEV_ENV,
        )
        codepipeline.add_stage(deploy_stage)
