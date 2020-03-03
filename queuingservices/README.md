# Queuing Service

A standardized system of different queuing services that can be used by specifying in the users configuration file.

## Getting Started

There are two packages that are required to run all of the different available queues. I will provide commands to install all dependencies.

### Dependencies

* pika: RabbitMQ Python Library
* boto3: AWS Python Library
* docker: Technology for containerization and deployment

### Prerequisites

Here are some commands to download the required dependencies.

```
pip install pika
pip install boto3
```

If you wanted to install all dependencies for CloudRunner, just run the following command from the root.

```
pip install -r requirements.txt
```

Downloading and setting up Docker is a little bit more involved and can be done from [here](https://www.docker.com/products/docker-desktop).

## Running the tests

To look at the source code for the queuing services tests, go to /tests/queue_tests. There will be the following tests for different aspects of the queuing service.

###Rabbit MQ Tests
* queue_start_test.py

This file tests the subscriber or worker in the Rabbit MQ queue that will accept messages.
It can be run with the following command.

```
python -m tests.queue_tests.rmq.queue_start_test
```

If the subscriber passes the test, it will return the following message.

```
Queue was successfully created!
Exchange was successfully created and bound!
Test Passed
 [*] Waiting for messages. To exit press CTRL+C
```

If the worker fails the test, it will print the following message.

```
Exception: *whichever exception was thrown*
```

* queue_task_test.py

This file tests the publisher in the Rabbit MQ queue that will send messages. 

queue_start_test.py does have to be running in another terminal so the publisher has something to send messages to.

It can be run with the following command.

```
python -m tests.queue_tests.rmq.queue_task_test
```

If the publisher passes the test, it successfully established a connection to the queue server and sent a message to the subscriber.

It will print the following message.

```
[x] Sent 1
[x] Sent 2
[x] Sent 3
[x] Sent 4
[x] Sent 5
[x] Sent 6
[x] Sent 7
[x] Sent 8
[x] Sent 9
[x] Sent 10
Test Passed
```

In the subscriber's terminal it will print the following.

```
Queue was successfully created!
Exchange was successfully created and bound!
Test Passed
 [*] Waiting for messages. To exit press CTRL+C
 [x] Recieved b'1'
fib(10) = 55
 [x] Done
 [x] Recieved b'2'
fib(10) = 55
 [x] Done
 [x] Recieved b'3'
fib(10) = 55
 [x] Done
 [x] Recieved b'4'
fib(10) = 55
 [x] Done
 [x] Recieved b'5'
fib(10) = 55
 [x] Done
 [x] Recieved b'6'
fib(10) = 55
 [x] Done
 [x] Recieved b'7'
fib(10) = 55
 [x] Done
 [x] Recieved b'8'
fib(10) = 55
 [x] Done
 [x] Recieved b'9'
fib(10) = 55
 [x] Done
 [x] Recieved b'10'
fib(10) = 55
 [x] Done
```

If the publisher fails the test, it will print the following message.

```
Exception: *whichever exception was thrown*
```

###AWS Simple Queuing Service Tests
* sqs_test.py

This file tests the subscriber or worker in the SQS queue that will accept messages.
It can be run with the following command.

```
python -m tests.queue_tests.sqs.sqs_test
```

If the subscriber passes the test, it will return the following message.

```
Waiting for messages...
```

If the worker fails the test, it will print the following message.

```
Exception: *whichever exception was thrown*
Closing Worker
```

* sqs_send_test.py

This file tests the publisher in the SQS queue that will send messages. 

sqs_test.py does have to be running in another terminal so the publisher has something to send messages to.

It can be run with the following command.

```
python -m tests.queue_tests.sqs.sqs_send_test
```

If the publisher passes the test, it successfully established a connection to the queue server and sent a message to the subscriber.

It will print the following message.

```
Message was successfully sent.

```

In the subscriber's terminal it will print the following.

```
Waiting for messages...
message: This is another test
fib(10) = 55
```

If the publisher fails the test, it will print the following message.

```
Message Sending was Unsuccessful.
Exception: *whichever exception was thrown*
```

###Queue Manager Interface Tests
* queue_manager_test.py

This file tests the queue managing interface that utilizes all of the queuing services. For this test, it will send two queue configuration dictionaries to the interface to return objects of each class (RMQ and SQS).

It can be run with the following command.

```
python -m tests.queue_tests.queue_manager_test
```

If the manager passes the test, it has successfully retrieved the respective Subscriber objects from each queuing service.

It will print the following message.

```
rmq subscriber object: <queuingservices.rabbitmq.subscriber.Subscriber object at 0x000002292E9A0808>
sqs subscriber object: <queuingservices.sqs.subscriber.Subscriber object at 0x000002292EF06988>
```

If the manager fails the test, it will print the following message.

```
Test Failed.
Exception: *whichever exception was thrown*
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [PyCharm](https://www.jetbrains.com/pycharm/) - Python IDE used
* [Docker](https://maven.apache.org/) - Containerization and Deployment
* [AWS](https://aws.amazon.com/) - Cloud Platform

## Versioning

We use [GitHub](https://github.com/) for versioning. 

## Authors

* **Alex Jirovsky** - aj132608 -  [github page](https://github.com/aj132608)

All queue implementation and integration.

Other contributors:

* **Mohak Kant** - mohakamg - [github page](https://github.com/mohakamg)
* **Samuel Okei** - Tegasaur - [github page](https://github.com/Tegasaur)
