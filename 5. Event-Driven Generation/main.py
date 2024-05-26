## IMPORT REQUIRED LIBRARIES
import boto3, os
from helpers.Lambda_Helper import Lambda_Helper
from helpers.S3_Helper import S3_Helper

## INITIALIZE HELPER FUNCTIONS
lambda_helper = Lambda_Helper()
s3_helper = S3_Helper()

## SET UP ENVIRONMENT VARIABLES
bucket_name_text = os.environ['LEARNERS3BUCKETNAMETEXT']
bucket_name_audio = os.environ['LEARNERS3BUCKETNAMEAUDIO']

## DEPLOY LAMBDA FUNCTION
lambda_helper.lambda_environ_variables = {'S3BUCKETNAMETEXT' : bucket_name_text}
lambda_helper.deploy_function(["lambda_function.py"], function_name="LambdaFunctionTranscribe")

## CONFIGURE LAMBDA TRIGGER FOR AUDIO BUCKET
lambda_helper.filter_rules_suffix = "mp3"
lambda_helper.add_lambda_trigger(bucket_name_audio, function_name="LambdaFunctionTranscribe")

## S3 OPERATIONS FOR AUDIO BUCKET
s3_helper.upload_file(bucket_name_audio, 'dialog.mp3')
s3_helper.list_objects(bucket_name_audio)

## S3 OPERATIONS FOR TEXT BUCKET
s3_helper.list_objects(bucket_name_text)
s3_helper.download_object(bucket_name_text, 'results.txt')

## DISPLAY TRANSCRIPTION RESULTS
from helpers.Display_Helper import Display_Helper
display_helper = Display_Helper()
display_helper.text_file('results.txt')