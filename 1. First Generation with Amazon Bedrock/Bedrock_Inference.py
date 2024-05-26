## IMPORTING REQUIRED PACKAGES
import boto3
import json

## SETUP BEDROCK RUNTIME
bedrock_runtime = boto3.client('bedrock-runtime', region_name = 'us-west-2')
prompt = "Write a one sentence summary of Las Vegas."

## SPECIFY KEYWORD ARGUMENTS FOR BEDROCK SERVICE
kwargs = {
    "modelId": "amazon.titan-text-express-v1",
    "contentType": "application/json",
    "accept": "*/*",
    "body" : json.dumps(
        {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 100,
                "temperature": 0.7,
                "topP": 0.9
            }
        }
    )
}

## RUNNING INFERENCE
response = bedrock_runtime.invoke_model(**kwargs)
response_body = json.loads(response.get('body').read())
generation = response_body['results'][0]['outputText']

## PRINT RESPONSE BODY OUTPUT AND GENERATED TEXT
print(json.dumps(response_body, indent=4))
print(generation)
