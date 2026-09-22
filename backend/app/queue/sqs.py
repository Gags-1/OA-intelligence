import json

import boto3

from app.core.config import settings


class SQSQueue:
    def __init__(self):
        self.client = boto3.client(
            "sqs",
            region_name=settings.AWS_REGION,
        )

        self.queue_url = settings.SQS_QUEUE_URL

    def send_submission_job(
        self,
        submission_id: int,
    ) -> None:

        message = {
            "submission_id": submission_id,
        }

        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
        )
