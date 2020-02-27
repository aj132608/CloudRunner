from services.queuingservices.sqs.sqs_message import SQSMessage

CREDENTIALS_PATH = "./creds/aws/sqs/"


sqs_message = SQSMessage(CREDENTIALS_PATH)

response = sqs_message.get_client_object().get_queue_url(
    QueueName='myqueue.fifo'
)

queue_url = response['QueueUrl']

message = "This is a test"

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

task_id = "Alex12345"

sqs_message.send_message(
    message=message,
    attributes=attributes,
    queue_url=queue_url,
    task_id=task_id
)
