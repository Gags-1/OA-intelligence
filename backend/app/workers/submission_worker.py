import json
import time

import boto3
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.submission import Submission
from app.services.submission_processor import process_submission


class SubmissionWorker:

    def __init__(self):
        self.sqs = boto3.client(
            "sqs",
            region_name=settings.AWS_REGION,
        )

        self.queue_url = settings.SQS_QUEUE_URL

    def receive_messages(self):
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
            VisibilityTimeout=60,
        )

        return response.get("Messages", [])

    def delete_message(self, receipt_handle: str):
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )

    def process_message(
        self,
        message: dict,
    ):
        body = json.loads(message["Body"])

        submission_id = body["submission_id"]

        print(
            f"Received submission job: "
            f"submission_id={submission_id}"
        )

        db: Session = SessionLocal()

        try:
            submission = db.get(
                Submission,
                submission_id,
            )

            if submission is None:
                print(
                    f"Submission not found: "
                    f"{submission_id}"
                )

                return

            print(
                f"Processing submission: "
                f"{submission_id}"
            )

            process_submission(
                db,
                submission,
            )

            print(
                f"Successfully processed submission: "
                f"{submission_id}"
            )

        finally:
            db.close()

    def run(self):
        print("Submission worker started")

        while True:

            try:
                messages = self.receive_messages()

                if not messages:
                    continue

                for message in messages:

                    try:
                        self.process_message(
                            message
                        )

                        self.delete_message(
                            message["ReceiptHandle"]
                        )

                        print(
                            "SQS message deleted"
                        )

                    except Exception as exc:
                        print(
                            f"Failed to process message: "
                            f"{exc}"
                        )

                        # Do NOT delete the message.
                        #
                        # SQS will make it visible again
                        # after the visibility timeout.
                        continue

            except KeyboardInterrupt:
                print(
                    "Submission worker stopped"
                )
                break

            except Exception as exc:
                print(
                    f"Worker error: {exc}"
                )

                time.sleep(5)


if __name__ == "__main__":
    worker = SubmissionWorker()
    worker.run()
