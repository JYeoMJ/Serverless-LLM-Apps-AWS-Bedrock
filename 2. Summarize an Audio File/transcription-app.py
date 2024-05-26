## IMPORTING REQUIRED PACKAGES
import os
import boto3
import uuid
import time
import json

def setup_s3_client():
    """Set up and return the S3 client."""
    return boto3.client('s3', region_name='us-west-2')

def upload_audio_file(s3_client, bucket_name, file_name):
    """Upload the audio file to an S3 bucket."""
    s3_client.upload_file(file_name, bucket_name, file_name)

def setup_transcribe_client():
    """Set up and return the AWS Transcribe client."""
    return boto3.client('transcribe', region_name='us-west-2')

def start_transcription_job(transcribe_client, bucket_name, file_name):
    """Start the transcription job and return the job name."""
    job_name = 'transcription-job-' + str(uuid.uuid4())
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f's3://{bucket_name}/{file_name}'},
        MediaFormat='mp3',
        LanguageCode='en-US',
        OutputBucketName=bucket_name,
        Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
    )

    # Write the job_name to a file for later retrieval by the summarization script
    with open('job_name.txt', 'w') as file:
        file.write(job_name)
        
    return job_name

def check_job_status(transcribe_client, job_name):
    """Check the transcription job status until it is completed or failed."""
    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            return status
        time.sleep(2)       # Wait 2 seconds before checking again.

def process_transcript(s3_client, bucket_name, job_name):
    """Process the completed transcript and save it as a text file."""

    # Retrieve the completed transcript file from S3
    transcript_key = f"{job_name}.json"
    transcript_obj = s3_client.get_object(Bucket=bucket_name, Key=transcript_key)
    transcript_text = transcript_obj['Body'].read().decode('utf-8')
    transcript_json = json.loads(transcript_text)

    output_text = ""
    current_speaker = None
    items = transcript_json['results']['items']

    for item in items:
        speaker_label = item.get('speaker_label', None)
        content = item['alternatives'][0]['content']

        # Append the speaker label to the output if the speaker changes.
        if speaker_label is not None and speaker_label != current_speaker:
            current_speaker = speaker_label
            output_text += f"\n{current_speaker}: "

        # Append content; handle punctuation by not adding extra space.
        if item['type'] == 'punctuation':
            output_text = output_text.rstrip() + content
        else:
            output_text += content + " "

    # Write the formatted transcript to a local text file.
    with open(f'{job_name}.txt', 'w') as f:
        f.write(output_text)

def main():
    """Main function to run the script."""

    # Retrieve the bucket name from environment variables or use a default.
    bucket_name = os.getenv('BucketName', 'dlai-serverless-llm-bedrock-app')
    file_name = 'dialog.mp3'

    # Setup clients and upload file.
    s3_client = setup_s3_client()
    upload_audio_file(s3_client, bucket_name, file_name)

    # Start transcription and process the result.
    transcribe_client = setup_transcribe_client()
    job_name = start_transcription_job(transcribe_client, bucket_name, file_name)
    
    status = check_job_status(transcribe_client, job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        process_transcript(s3_client, bucket_name, job_name)
        print("Transcription completed and processed successfully.")
    else:
        print("Transcription job failed.")


if __name__ == '__main__':
    main()
