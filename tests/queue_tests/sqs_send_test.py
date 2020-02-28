from services.queuingservices.sqs.sqs_message import SQSMessage
from servicecommon.persistor.local.json.json_persistor import JsonPersistor


CREDENTIALS_PATH = "./creds/aws/sqs/"

restore_obj = JsonPersistor(dict=None,
                            base_file_name='credentials',
                            folder=CREDENTIALS_PATH)

credentials_dict = restore_obj.restore()

sqs_message = SQSMessage(credentials_dict=credentials_dict)

response = sqs_message.get_client_object().get_queue_url(
    QueueName='myqueue.fifo'
)

queue_url = response['QueueUrl']

message = "This is another test"

attributes = {
    'Title': {
        'DataType': 'String',
        'StringValue': 'Test Message'
    },
    'Author': {
        'DataType': 'String',
        'StringValue': 'Alex Jirovsky'
    },
    'Age': {
        'DataType': 'Number',
        'StringValue': '23'
    }
}

task_id = "Alex123456"

sqs_message.send_message(
    message=message,
    attributes=attributes,
    queue_url=queue_url,
    task_id=task_id
)
