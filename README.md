serverless Image Processing Pipeline
A fully serverless image processing application built on AWS that automatically resizes images uploaded to S3.

Architecture
API Gateway - Step Functions - Lambda - S3 

Features
The application uses the following AWS services:
-S3: Storage for original and resized images
-Lambda: Image processing logic
-Step Functions: Workflow orchestration
-API Gateway: REST API endpoint

Setup Explanation
S3 Buckets
-Original Image Bucket: original-images-demo2
-Resized Images Bucket: resized_images-demo2

Lambda Function
-ImageResizeFunction2
-Runtime: Python 3.12
-IAM Role: Must allow S3:GetObject and S3:PutObject on both buckets
-Prebuilt Pillow Layer: arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-Pillow:8
-Region: us-east-1

Lambda Code
see lambda/lambda_function.py
The function expects an event from 
	  "bucket": "original-images-demo2",
	  "fileName": "ThinkingCatMeme.jpg",
	  "resizedBucket": "resized-images-demo2"
	}
It then:
-Downloads the image from bucket using fileName
-Resizes it to a thumbnail with Pillow
-Uploads thumbnail-<ThinkingCatMeme.jpg> to resizedBucket
-Returns a JSON status object used by the state machine


Step Functions State Machine
The state machine:
-Calls the ImageResizeFunction Lambda (ResizeImage state)
-Reads the status field from the Lambda response
-If status == "SUCCESS", goes to SuccessState
-Otherwise, goes to FailState

The definition is stored in
stepfunctions/Image_processing_state_machine

API Gateway (HTTP API)
-Type: HTTP API
-Stage: $default
-Invoke URL example: https://v7k5zivwo1.execute-api.us-east-1.amazonaws.com/resized

Route:
-Method: POST
-Path: /resized
-Integration: AWS Step Functions - StartExecution of the state machine
Request Body:
  "bucket": "original-images-demo2",
  "fileName": "ThinkingCatMeme.jpg",
  "resizedBucket": "resized-images-demo2"
}
When called, this endpoint:
-Starts the Step Functions execution
-Step Functions invokes the Lambda
-Lambda resizes the image and writes the thumbnail to S3

How To Run/Create This Project
Prerequisites
-AWS account
-Access to:
  -S3
  -Lambda
  -Step Functions
  -API Gateway (HTTP API)
-Region: us-east-1

1. Create S3 Buckets

-Create original-images-demo2 in us-east-1
-Create resized-images-demo2 in us-east-1
-Upload a test image to original-images-demo1 (e.g. ThinkingCatMeme.jpg)

2. Create Lambda Function
-Go to Lambda: Create function
-Name: ImageResizeFunction
-Runtime: Python 3.12
-Create function
-In the Code tab, replace the default code with lambda/lambda_function.py content
-Attach the Pillow layer:
    -Go to Layers: Add a layer then Specify an ARN
    -Use: arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-Pillow:8
-Under Configuration: Permissions, attach an IAM policy that allows:
s3:GetObject on original-images-demo2
s3:PutObject on resized-images-demo2
For the demo, AmazonS3FullAccess was used and works, but in production you would restrict it.

Test Locally with this event:
{
"bucket": "original-images-demo2",
  "fileName": "ThinkingCatMeme.jpg",
  "resizedBucket": "resized-images-demo2"
}
You should see: 
{
  "status": "SUCCESS",
  "message": "ThinkingCatMeme.jpg resized successfully!"
}

3. Create the Step Functions State Machine
Go to Step Functions: Create state machine
Choose: Author with code snippets
Choose type: Standard
Paste the JSON from stepfunctions/image_processing_state_machine.json
Make sure the Resource ARN matches your Lambda ARN
Create the state machine
Test with Start Execution and input:
{
"bucket": "original-images-demo2",
  "fileName": "ThinkingCatMeme.jpg",
  "resizedBucket": "resized-images-demo2"
}



4. Create HTTP API (API Gateway)
Go to API Gateway: HTTP APIs-Create
Name: ImageResizeAPI
After creation, go to Routes
Create route: POST /resized
Select the route: Create and attach integration
Integration type: AWS Step Functions
Action: StartExecution
State machine ARN: ARN of ImageProcessingStateMachineDemo
Invocation role: IAM role that allows states:StartExecution
Copy the Invoke URL from the Stage $default: https://v7k5zivwo1.execute-api.us-east-1.amazonaws.com/resized


5. Test the endpoint
   use postman:
   POST to: https://v7k5zivwo1.execute-api.us-east-1.amazonaws.com/resized
   Body (JSON):
   {
"bucket": "original-images-demo2",
  "fileName": "ThinkingCatMeme.jpg",
  "resizedBucket": "resized-images-demo2"
}
Expected:
HTTP 200 with an executionArn and startDate
A new file thumbnail-ThinkingCatMeme.jpg appears in resized-images-demo2

