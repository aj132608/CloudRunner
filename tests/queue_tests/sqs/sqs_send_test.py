import json

from queuingservices.sqs.publisher import Publisher
from servicecommon.persistor.local.json.json_persistor import JsonPersistor
from queuingservices.message_struct import MessageStruct


CREDENTIALS_PATH = "./creds/aws/sqs/"

restore_obj = JsonPersistor(dict=None,
                            base_file_name='credentials',
                            folder=CREDENTIALS_PATH)

credentials_dict = restore_obj.restore()

sqs_message = Publisher(credentials_dict=credentials_dict)

response = sqs_message.get_client_object().get_queue_url(
    QueueName='myqueue.fifo'
)

queue_url = response['QueueUrl']

message_struct = MessageStruct(bucket_name="cloudrunneralex",
                               username="alex.jirovsky",
                               experiment_id="experiment0",
                               project_id="project0",
                               job_id="job0",
                               completion=True,
                               submission=False)

task_id = "Alex12345"

sqs_message.send_message(
    message=message_struct.__dict__,
    queue_url=queue_url,
    task_id=task_id
)
