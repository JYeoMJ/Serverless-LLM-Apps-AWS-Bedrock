## IMPORTING REQUIRED PACKAGES
import boto3
import json
from IPython.display import Audio     # Note: This works only for Jupyter Environment

## SETUP BEDROCK RUNTIME
bedrock_runtime = boto3.client('bedrock-runtime', region_name = 'us-west-2')

## LOADING AUDIO FILE
audio = Audio(filename="dialog.mp3")
display(audio)

## READING CONTENTS OF TRANSCRIPTION
with open('transcript.txt', "r") as file:
    dialogue_text = file.read()

print(dialogue_text)

## PROMPT FOR SUMMARIZING TRANSCRIPT
prompt = f"""The text between the <transcript> XML tags is a transcript of a conversation. 
Write a short summary of the conversation.

<transcript>
{dialogue_text}
</transcript>

Here is a summary of the conversation in the transcript:"""

## BEDROCK CONFIGURATIONS
kwargs = {
    "modelId": "amazon.titan-text-express-v1",
    "contentType": "application/json",
    "accept": "*/*",
    "body": json.dumps(
        {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0,
                "topP": 0.9
            }
        }
    )
}

## RUNNING INFERENCE
response = bedrock_runtime.invoke_model(**kwargs)
response_body = json.loads(response.get('body').read())
generation = response_body['results'][0]['outputText']

## PRINT SUMMARIZED TRANSCRIPT GENERATION
print(generation)


