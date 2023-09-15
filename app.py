from multiprocessing.sharedctypes import Value
from unicodedata import name
import constants

from aws_cdk import (
    App, Stack
)
from pipeline import Pipeline
from deployment import SolutionResources

app = App()

# Pipeline Infrastructure
Pipeline(app, f"{constants.CDK_APP_NAME}-pipeline-infrastructure", env=constants.PIPELINE_ENV)

# Solution Infrastructure 
SolutionResources(app, f"{constants.CDK_APP_NAME}-solution-infrastructure", env=constants.PIPELINE_ENV)

app.synth()