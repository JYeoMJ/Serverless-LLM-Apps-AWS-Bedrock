## IMPORTING REQUIRED PACKAGES
import boto3, os

from helpers.Lambda_Helper import Lambda_Helper
from helpers.S3_Helper import S3_Helper
from helpers.Display_Helper import Display_Helper

## INITIALIZE HELPER CLASS INSTANCES
lambda_helper = Lambda_Helper()
s3_helper = S3_Helper()
display_helper = Display_Helper()

## S3 BUCKET NAME FROM ENVRIONMENT VARIABLE
bucket_name_text = os.environ['BUCKET_NAME']

## DEPLOY LAMBDA FUNCTION WITH ASSOCIATED FILES
lambda_helper.deploy_function(
    ["lambda_function.py", "prompt_template.txt"],
    function_name="LambdaFunctionSummarize"
)

## CONFIGURE LAMBDA TRIGGER (ACTIVATE ONLY FOR JSON FILES)
lambda_helper.filter_rules_suffix = "json"
lambda_helper.add_lambda_trigger(bucket_name_text)

## ACTIVATE LAMBDA FUNCTION WITH S3 UPLOAD
s3_helper.upload_file(bucket_name_text, 'demo-transcript.json')
s3_helper.list_objects(bucket_name_text)
s3_helper.download_object(bucket_name_text, "results.txt")

## DISPLAY RESULTS FILE CONTENT
display_helper.text_file('results.txt')