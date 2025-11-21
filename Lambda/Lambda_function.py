import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        source_bucket = event['bucket']
        file_name = event['fileName']
        destination_bucket = event['resizedBucket']

        # Get image from S3
        image_file = s3.get_object(Bucket=source_bucket, Key=file_name)
        image_data = image_file['Body'].read()

        # Resize using Pillow
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((200, 200))

        # Save to memory buffer
        buffer = io.BytesIO()
        image.save(buffer, "JPEG")
        buffer.seek(0)

        # Upload resized image to destination bucket
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"thumbnail-{file_name}",
            Body=buffer,
            ContentType='image/jpeg'
        )

        return {
            "status": "SUCCESS",
            "message": f"{file_name} resized successfully!"
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "error": str(e)
        }

