import boto3
import logging
import json
import os
import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)

LLM_SERVICE_ENDPOINT_PARAMETER = os.environ['LLM_SERVICE_ENDPOINT_PARAMETER']

ssm_client = boto3.client('ssm')

response = ssm_client.get_parameters(Names=[LLM_SERVICE_ENDPOINT_PARAMETER])

service_address = response["Parameters"][0]["Value"]

print("Discovered Server IP:")
print(service_address)

LLM_SERVICE_ENDPOINT_ADDRESS = f"http://{service_address}:8080/predict"


def handler(event, context):

    print(event)
    # lamda can only write to /tmp/

    query_input = event["inputTranscript"]

    # api-endpoint
    endpoint_url = LLM_SERVICE_ENDPOINT_ADDRESS

    # defining a params dict for the parameters to be sent to the API
    params = {'query': query_input}

    # sending get request and saving the response as response object
    response = requests.get(url=endpoint_url, params=params)

    json_response = response.json()
    print(json_response['response'])

    lex_response = generate_lex_response(
        event, {}, "Fulfilled", json_response['response'])

    print("Lex Response:")
    print(lex_response)

    jsonified_resp = json.loads(json.dumps(lex_response, default=str))

    return jsonified_resp


def generate_lex_response(intent_request, session_attributes, fulfillment_state, message):
    print("Intent Request:")
    print(intent_request)

    print("Message:")
    print(message)

    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [
            {
                "contentType": "PlainText",
                "content": message
            }
        ],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def main():
    """
    Test the function when called from the commandline.
    """

    test_event = {
        "sessionId": "413034898429619",
        "inputTranscript": "How do you perform an oil change?",
        "interpretations": [
            {
                "intent": {
                    "name": "FallbackIntent",
                    "slots": {},
                    "state": "ReadyForFulfillment",
                    "confirmationState": "None"
                }
            },
            {
                "nluConfidence": "0.35",
                "intent": {
                    "name": "placeHolderIntent",
                    "slots": {},
                    "state": "ReadyForFulfillment",
                    "confirmationState": "None"
                }
            }
        ],
        "bot": {
            "name": "conversational-bot-lex-agent",
            "version": "DRAFT",
            "localeId": "en_US",
            "id": "QPCVWBBA9S",
            "aliasId": "TSTALIASID",
            "aliasName": "TestBotAlias"
        },
        "responseContentType": "text/plain; charset=utf-8",
        "sessionState": {
            "sessionAttributes": {},
            "intent": {
                "name": "FallbackIntent",
                "slots": {},
                "state": "ReadyForFulfillment",
                "confirmationState": "None"
            },
            "originatingRequestId": "a3b2b2a2-4603-4687-9f92-ef2c986dac77"
        },
        "messageVersion": "1.0",
        "invocationSource": "FulfillmentCodeHook",
        "transcriptions": [
            {
                "transcriptionConfidence": "1.0",
                "resolvedContext": {
                    "intent": "FallbackIntent"
                },
                "transcription": "How do you perform an oil change?",
                "resolvedSlots": {}
            }
        ],
        "inputMode": "Text"
    }

    handler(test_event, {})


if __name__ == '__main__':
    main()
