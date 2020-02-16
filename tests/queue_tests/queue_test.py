from services.queuingservices.rabbitmq.practice.practice_queue import PracticeQueue

# Start queue with this command
# docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# message = "task_1234,User/aj132/Documents/data"
message = "."

queue_obj = PracticeQueue()

for index in range(0,10):
    queue_obj.establish_connection('localhost')
    queue_obj.create_sample_queue('test_queue')
    queue_obj.create_sample_message('test_queue', message)
    queue_obj.close_connection()
    message += "."
