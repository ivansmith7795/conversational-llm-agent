import aws_cdk.aws_lex as lex

import aws_cdk as cdk
import constants

from constructs import Construct

class LexBots(Construct):
    def __init__(self, scope: Construct, id_: str, inference_lambda_arn: str, lex_role_arn: str, **kwargs):
        super().__init__(scope, id_)

        ### BOT SETUP

        # alias settings, where we define the lambda function with the ECR container with our LLM dialog code (defined in the lex-gen-ai-demo-docker-image directory)
        # test bot alias for demo, create a dedicated alias for serving traffic
        bot_alias_settings = lex.CfnBot.TestBotAliasSettingsProperty(
                                        bot_alias_locale_settings=[lex.CfnBot.BotAliasLocaleSettingsItemProperty(
                                            bot_alias_locale_setting=lex.CfnBot.BotAliasLocaleSettingsProperty(
                                                enabled=True,
                                                code_hook_specification=lex.CfnBot.CodeHookSpecificationProperty(
                                                    lambda_code_hook=lex.CfnBot.LambdaCodeHookProperty(
                                                        code_hook_interface_version="1.0",
                                                        lambda_arn=inference_lambda_arn
                                                    )
                                                )
                                            ),
                                            locale_id="en_US"
                                        )])
        
        # lambda itself is tied to alias but codehook settings are intent specific
        initial_response_codehook_settings = lex.CfnBot.InitialResponseSettingProperty(
                                        code_hook=lex.CfnBot.DialogCodeHookInvocationSettingProperty(
                                            enable_code_hook_invocation=True,
                                            is_active=True,
                                            post_code_hook_specification=lex.CfnBot.PostDialogCodeHookInvocationSpecificationProperty()
                                        )
                                    )
        
        # placeholder intent to be missed for this demo
        placeholder_intent = lex.CfnBot.IntentProperty(
                                    name="placeHolderIntent",
                                    initial_response_setting=initial_response_codehook_settings,
                                    sample_utterances=[lex.CfnBot.SampleUtteranceProperty(
                                                            utterance="utterance"
                                                        )]
                                )
        
        fallback_intent = lex.CfnBot.IntentProperty(
                                    name="FallbackIntent",
                                    parent_intent_signature="AMAZON.FallbackIntent",
                                    initial_response_setting=initial_response_codehook_settings,
                                    fulfillment_code_hook=lex.CfnBot.FulfillmentCodeHookSettingProperty(
                                        enabled=True,
                                        is_active=True,
                                        post_fulfillment_status_specification=lex.CfnBot.PostFulfillmentStatusSpecificationProperty()
                                    )
                                )

        # Create actual Lex Bot
        cfn_bot = lex.CfnBot(self, f"{constants.CDK_APP_NAME}-lex-bot",
            data_privacy={"ChildDirected":"false"},
            idle_session_ttl_in_seconds=300,
            name=f"{constants.CDK_APP_NAME}-lex-agent",
            description="Bot created for testing LLM.",
            role_arn=lex_role_arn,
            bot_locales=[lex.CfnBot.BotLocaleProperty(
                            locale_id="en_US",
                            nlu_confidence_threshold=0.4,
                            intents=[placeholder_intent, fallback_intent])
                        ],
            test_bot_alias_settings = bot_alias_settings,
            auto_build_bot_locales=True
        )



