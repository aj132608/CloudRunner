# Queuing Service

A standardized system of different queuing services that can be used by specifying in the users configuration file.

### Background

All queuing services on Cloud Runner operate using Publishers and Subscribers. 

**Subscribers**

Subscribers are responsible for processing messages that are held on the queue server. The subscribers in Cloud Runner
listen for messages in real time and process them as they come through callback functions. These functions also remove 
elements from the queue. The subscribers in Cloud Runner will sit in the Cloud instances and initiate the applications
to be run on those instances.

**Publishers**

Publishers are responsible for publishing or sending messages to the queue to be processed. In Cloud Runner, publishers
send information on jobs that need to be run on Cloud instances.

## Getting Started

There are two packages that are required to run all of the different available queues. 
Commands to install dependencies will be provided below.

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

Downloading and setting up Docker is a little bit more involved and can be done from 
[here](https://www.docker.com/products/docker-desktop).

### Queue Configuration

To use the queuing service, the user must create a configuration of what fits their specific problem. 
These configurations are held in a master configuration file called config.json.

**Examples**

**Queue configuration for running a RabbitMQ queue**

```
"queue": {
    "type": "rmq",
    "endpoint": "amqp://guest:guest@localhost",
    "queue_name": "rabbit_queue_1",
    "exchange_name": "rabbit_exchange_1"
}
```

To select RabbitMQ as the queuing service, type must be set equal to rmq.
The endpoint requested here should be pointing to the RabbitMQ queue server.
queue_name and exchange_name are optional but can be set by the user.

**Queue configuration for running an SQS queue**

```
"queue": {
    "type": "sqs",
    "env": {
        "access_key": "YOUR_ACCESS_KEY",
        "secret_key": "YOUR_SECRET_KEY"
    },
    "region": "us-west-2",
    "queue_name": "sqs_queue_1",
    "queue_url": "https://region.queue.amazonaws.com/user_id/queue_name",
}
```
To select SQS as the queuing service, type must be set equal to sqs. The env field is requesting the access key and 
secret key that should be provided by AWS to the user upon the creation of an SQS project with development permissions.
The region field must be filled in by a standard AWS region like the one shown above. 
queue_name and queue_url are not required but can be filled in at the user's discretion.
The queue_url field will, if used, point to an existing SQS queue.

## Running the tests

To look at the source code for the queuing services tests, go to /tests/queue_tests. 
There will be the following tests for different aspects of the queuing service.

### Rabbit MQ Tests
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

### AWS Simple Queuing Service Tests
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

### Queue Manager Interface Tests
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
