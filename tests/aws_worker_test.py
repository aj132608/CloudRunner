from worker.aws_worker import AwsWorker
resource = {'cpus':2, 'ram': '2g', 'gpus':0}
worker = AwsWorker('ec2-keypair.pem', 2, 'us-east-1', 'ec2-keypair', resource)
worker.create_workers()

