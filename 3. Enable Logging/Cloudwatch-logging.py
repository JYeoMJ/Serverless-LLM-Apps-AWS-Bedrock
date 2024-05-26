## IMPORTING REQUIRED PACKAGES
import boto3
import json
import os

## BEDROCK CLIENT SETUP
bedrock = boto3.client('bedrock', region_name="us-west-2")

## CLOUDWATCH HELPER INITIALIZATION
from helpers.CloudWatchHelper import CloudWatch_Helper
cloudwatch = CloudWatch_Helper()

## LOG GROUP CREATION
log_group_name = '/my/amazon/bedrock/logs'
cloudwatch.create_log_group(log_group_name)

## LOGGING CONFIGURATION FOR CLOUDWATCH AND S3
loggingConfig = {
    'cloudWatchConfig': {
        'logGroupName': log_group_name,
        'roleArn': os.environ['LOGGINGROLEARN'],   # Role for accessing CloudWatch
        'largeDataDeliveryS3Config': {
            'bucketName': os.environ['LOGGINGBUCKETNAME'],  # S3 bucket for large data
            'keyPrefix': 'amazon_bedrock_large_data_delivery',
        }
    },
    's3Config': {
        'bucketName': os.environ['LOGGINGBUCKETNAME'],  # S3 bucket for logs
        'keyPrefix': 'amazon_bedrock_logs',
    },
    'textDataDeliveryEnabled': True,    # Enable delivery of text data in logs
}
bedrock.put_model_invocation_logging_configuration(loggingConfig=loggingConfig)
bedrock.get_model_invocation_logging_configuration()

## MODEL INVOCATION
bedrock_runtime = boto3.client('bedrock-runtime', region_name="us-west-2")
prompt = "Write an article about the fictional planet Foobar."
kwargs = {
    "modelId": "amazon.titan-text-express-v1",
    "contentType": "application/json",
    "accept": "*/*",
    "body": json.dumps(
        {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
    )
}
response = bedrock_runtime.invoke_model(**kwargs)
response_body = json.loads(response.get('body').read())
generation = response_body['results'][0]['outputText']
print(generation)

## LOG RETRIEVAL AND DISPLAY
cloudwatch.print_recent_logs(log_group_name)

## LINK TO AWS CONSOLE (within Jupyter Notebook)
from IPython.display import HTML
aws_url = os.environ['AWS_CONSOLE_URL']
HTML(f'<a href="{aws_url}" target="_blank">GO TO AWS CONSOLE</a>')