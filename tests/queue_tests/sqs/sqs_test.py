from queue.sqs.sqs_worker import SQSWorker
from queue.sqs.create_sqs_queue import SQSQueue
from servicecommon.persistor.local.json.json_persistor import JsonPersistor


def create_queue(obj, queue_name):
    temp_queue = obj.create_queue(queue_name=queue_name)

    return temp_queue


if __name__ == "__main__":
    CREDENTIALS_PATH = "./creds/aws/sqs/"

    restore_obj = JsonPersistor(dict=None,
                                base_file_name='credentials',
                                folder=CREDENTIALS_PATH)

    credentials_dict = restore_obj.restore()

    new_queue_obj = SQSQueue(credentials_dict=credentials_dict)

    my_queue = new_queue_obj.create_queue('myqueue.fifo')

    queue_url = my_queue.url

    worker = SQSWorker(credentials_dict=credentials_dict,
                       queue_url=queue_url)

    worker.start_server()
