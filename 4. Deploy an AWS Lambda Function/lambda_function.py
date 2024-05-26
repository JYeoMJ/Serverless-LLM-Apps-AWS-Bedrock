## IMPORTING REQUIRED PACKAGES
import boto3
import json
from jinja2 import Template

## INITIALIZING CLIENTS FOR S3 AND BEDROCK SERVICES
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime', 'us-west-2')

## DEFINE LAMBDA HANDLER FUNCTION
def lambda_handler(event, context):

    # EXTRACT S3 BUCKET NAME AND OBJECT KEY FROM LAMBDA EVENT TRIGGER
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # CHECK TO PREVENT PROCESSING NON-TRANSCRIPT FILES TO AVOID RECURSION
    if "-transcript.json" not in key:
        print("This demo only works with *-transcript.json.")
        return
    
    try:
        # READS FILE CONTENT FROM S3 AND DECODE FROM UTF-8
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        
        # EXTRACT TRANSCRIPT TEXT FROM FILE
        transcript = extract_transcript_from_textract(file_content)

        print(f"Successfully read file {key} from bucket {bucket}.")
        print(f"Transcript: {transcript}")
        
        # GENERATE SUMMARY OF TRANSCRIPT
        summary = bedrock_summarisation(transcript)
        
        # STORE TRANSCRIPT SUMMARY RESULT BACK INTO S3
        s3_client.put_object(
            Bucket=bucket,
            Key='results.txt',
            Body=summary,
            ContentType='text/plain'
        )
        
    # EXCEPTION HANDLING
    except Exception as e:
        print(f"Error occurred: {e}")
        # Return a 500 server error status code with error message
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error occurred: {e}")
        }

    # SUCCESSFUL COMPLETION
    return {
        'statusCode': 200,     # Return a 200 success status code with a success message
        'body': json.dumps(f"Successfully summarized {key} from bucket {bucket}. Summary: {summary}")
    }

## SUPPORTING FUNCTION: PARSING JSON FROM TEXTRACT
def extract_transcript_from_textract(file_content):
    transcript_json = json.loads(file_content)
    output_text = ""
    current_speaker = None
    items = transcript_json['results']['items']

    # Parsing each item in the transcript JSON
    for item in items:
        speaker_label = item.get('speaker_label', None)
        content = item['alternatives'][0]['content']
        
        # Concatenate speaker's name before their dialogue if the speaker changes
        if speaker_label is not None and speaker_label != current_speaker:
            current_speaker = speaker_label
            output_text += f"\n{current_speaker}: "
        
        # If the item is a punctuation, remove the last space and append the punctuation
        if item['type'] == 'punctuation':
            output_text = output_text.rstrip()  # Remove the last space before punctuation
        
        output_text += f"{content} "
        
    return output_text

## SUPPORTING FUNCTION: BEDROCK CALL FOR SUMMARIZATION 
def bedrock_summarisation(transcript):

    with open('prompt_template.txt', "r") as file:
        template_string = file.read()

    # Define data dictionary for prompt template
    data = {
        'transcript': transcript,
        'topics': ['charges', 'location', 'availability']
    }
    
    # Using Jinja2 template to fill data in the prompt template
    template = Template(template_string)
    prompt = template.render(data)
    
    print(prompt)
    
    # Configuring parameters for invoking the Bedrock model
    kwargs = {
        "modelId": "amazon.titan-text-express-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": json.dumps(
            {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 2048,
                    "stopSequences": [],
                    "temperature": 0,
                    "topP": 0.9
                }
            }
        )
    }
    
    # Invoking the Bedrock model and obtaining the response
    response = bedrock_runtime.invoke_model(**kwargs)
    summary = json.loads(response.get('body').read()).get('results')[0].get('outputText')    
    return summary

