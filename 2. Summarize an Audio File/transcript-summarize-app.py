## IMPORTING REQUIRED PACKAGES
import boto3
import json
from jinja2 import Template

def read_file(file_path):
    """Read content from a file and return it."""
    with open(file_path, "r") as file:
        return file.read()

def load_template_and_render(transcript):
    """Load a Jinja2 template, render it with the given transcript, and return the result."""
    template_string = read_file('prompt_template.txt')
    template = Template(template_string)
    return template.render({'transcript': transcript})

def invoke_bedrock_model(prompt):
    """Invoke the AWS Bedrock model with the constructed prompt and return the model's response."""
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    kwargs = {
        "modelId": "amazon.titan-text-express-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0,  # Temperature set to zero for deterministic output
                "topP": 0.9
            }
        })
    }
    response = bedrock_runtime.invoke_model(**kwargs)
    return json.loads(response.get('body').read())

def main():
    """Main function to orchestrate the summarization of transcription."""
    try:
        with open('job_name.txt', 'r') as file:
            job_name = file.read().strip()  # Read and strip any extra whitespace from the job name
    except FileNotFoundError:
        print("Error: Job name file not found. Make sure transcription has been run.")
        return
    
    # Attempt to read the transcript file using the job name
    try:
        transcript = read_file(f'{job_name}.txt')
    except FileNotFoundError:
        print(f"Error: Transcript file {job_name}.txt not found.")
        return

    # Generate the prompt using the transcript
    prompt = load_template_and_render(transcript)
    print(f"Constructed Prompt:\n{prompt}")

    # Invoke the Bedrock model with the generated prompt
    response_body = invoke_bedrock_model(prompt)
    generation = response_body['results'][0]['outputText']
    print(f"Generated Summary:\n{generation}")

if __name__ == '__main__':
    main()
