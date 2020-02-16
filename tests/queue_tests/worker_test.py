from services.queuingservices.rabbitmq.practice.practice_worker import PracticeWorker

if __name__ == "__main__":
    queue_name = 'test_queue'
    endpoint = 'localhost'

    worker_obj = PracticeWorker()
    worker_obj.establish_connection(endpoint)
    worker_obj.create_sample_queue(queue_name)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    worker_obj.create_sample_response(queue_name)
    worker_obj.start_consuming()
