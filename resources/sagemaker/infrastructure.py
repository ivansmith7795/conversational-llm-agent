import aws_cdk.aws_signer as signer
import aws_cdk.aws_sagemaker  as sagemaker

import aws_cdk as cdk
import constants

from constructs import Construct

class Sagemaker(Construct):
    def __init__(self, scope: Construct, id_: str, vpcid: str, **kwargs):
        super().__init__(scope, id_)
        
        self.cfn_endpoint_config = sagemaker.CfnEndpointConfig(self, f"{constants.CDK_APP_NAME}-sm-endpoint",
        production_variants=[sagemaker.CfnEndpointConfig.ProductionVariantProperty(
            initial_variant_weight=123,
            model_name="modelName",
            variant_name="variantName",

            # the properties below are optional
            accelerator_type="acceleratorType",
            container_startup_health_check_timeout_in_seconds=123,
            enable_ssm_access=False,
            initial_instance_count=123,
            instance_type="instanceType",
            model_data_download_timeout_in_seconds=123,
            serverless_config=sagemaker.CfnEndpointConfig.ServerlessConfigProperty(
                max_concurrency=123,
                memory_size_in_mb=123,

                # the properties below are optional
                provisioned_concurrency=123
            ),
            volume_size_in_gb=123
        )],

        # the properties below are optional
        async_inference_config=sagemaker.CfnEndpointConfig.AsyncInferenceConfigProperty(
            output_config=sagemaker.CfnEndpointConfig.AsyncInferenceOutputConfigProperty(
                kms_key_id="kmsKeyId",
                notification_config=sagemaker.CfnEndpointConfig.AsyncInferenceNotificationConfigProperty(
                    error_topic="errorTopic",
                    include_inference_response_in=["includeInferenceResponseIn"],
                    success_topic="successTopic"
                ),
                s3_failure_path="s3FailurePath",
                s3_output_path="s3OutputPath"
            ),

            # the properties below are optional
            client_config=sagemaker.CfnEndpointConfig.AsyncInferenceClientConfigProperty(
                max_concurrent_invocations_per_instance=123
            )
        ),
        data_capture_config=sagemaker.CfnEndpointConfig.DataCaptureConfigProperty(
            capture_options=[sagemaker.CfnEndpointConfig.CaptureOptionProperty(
                capture_mode="captureMode"
            )],
            destination_s3_uri="destinationS3Uri",
            initial_sampling_percentage=123,

            # the properties below are optional
            capture_content_type_header=sagemaker.CfnEndpointConfig.CaptureContentTypeHeaderProperty(
                csv_content_types=["csvContentTypes"],
                json_content_types=["jsonContentTypes"]
            ),
            enable_capture=False,
            kms_key_id="kmsKeyId"
        ),
        endpoint_config_name="endpointConfigName",
        explainer_config=sagemaker.CfnEndpointConfig.ExplainerConfigProperty(
            clarify_explainer_config=sagemaker.CfnEndpointConfig.ClarifyExplainerConfigProperty(
                shap_config=sagemaker.CfnEndpointConfig.ClarifyShapConfigProperty(
                    shap_baseline_config=sagemaker.CfnEndpointConfig.ClarifyShapBaselineConfigProperty(
                        mime_type="mimeType",
                        shap_baseline="shapBaseline",
                        shap_baseline_uri="shapBaselineUri"
                    ),

                    # the properties below are optional
                    number_of_samples=123,
                    seed=123,
                    text_config=sagemaker.CfnEndpointConfig.ClarifyTextConfigProperty(
                        granularity="granularity",
                        language="language"
                    ),
                    use_logit=False
                ),

                # the properties below are optional
                enable_explanations="enableExplanations",
                inference_config=sagemaker.CfnEndpointConfig.ClarifyInferenceConfigProperty(
                    content_template="contentTemplate",
                    feature_headers=["featureHeaders"],
                    features_attribute="featuresAttribute",
                    feature_types=["featureTypes"],
                    label_attribute="labelAttribute",
                    label_headers=["labelHeaders"],
                    label_index=123,
                    max_payload_in_mb=123,
                    max_record_count=123,
                    probability_attribute="probabilityAttribute",
                    probability_index=123
                )
            )
        ),
        kms_key_id="kmsKeyId",
        shadow_production_variants=[sagemaker.CfnEndpointConfig.ProductionVariantProperty(
            initial_variant_weight=123,
            model_name="modelName",
            variant_name="variantName",

            # the properties below are optional
            accelerator_type="acceleratorType",
            container_startup_health_check_timeout_in_seconds=123,
            enable_ssm_access=False,
            initial_instance_count=123,
            instance_type="instanceType",
            model_data_download_timeout_in_seconds=123,
            serverless_config=sagemaker.CfnEndpointConfig.ServerlessConfigProperty(
                max_concurrency=123,
                memory_size_in_mb=123,

                # the properties below are optional
                provisioned_concurrency=123
            ),
            volume_size_in_gb=123
        )],
        tags=[CfnTag(
            key="key",
            value="value"
        )]
    )