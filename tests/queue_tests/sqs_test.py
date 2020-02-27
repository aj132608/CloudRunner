from services.queuingservices.sqs.sqs_worker import SQSWorker
from services.queuingservices.sqs.create_sqs_queue import SQSQueue


def create_queue(obj, queue_name):
    temp_queue = obj.create_queue(queue_name=queue_name)

    return temp_queue


if __name__ == "__main__":
    CREDENTIALS_PATH = "./creds/aws/sqs/"

    new_queue_obj = SQSQueue(credentials_path=CREDENTIALS_PATH)

    new_queue_obj.create_queue('myqueue.fifo')

    queue_url = new_queue_obj.get_queue_url()

    # print(queue_url)

    worker = SQSWorker(CREDENTIALS_PATH, queue_url=queue_url)

    worker.start_server()

    # response = create_queue(sqs, 'test')
    #
    # print(response.url)
    #
    # my_queue = sqs.get_queue()
    #
    # print(my_queue.url)

    # try:
    #     queue = create_queue(obj=sqs, queue_name='test.fifo')
    #     print(queue)
    #     print("Queue Successfully Created!")
    # except Exception as e:
    #     print("Queue Creation Failed")
    #     print(f"Exception: {e}")
