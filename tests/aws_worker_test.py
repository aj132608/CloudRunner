from worker.aws_worker import AwsWorker
resource = {'cpus':2, 'ram': '2g', 'gpus':0, "num_workers": 1, "image": "ami-d1180894"}
credential = {
    "region": "us-west-1",
    "access_key": "AKIAWA6NKF4S6U2THRHT",
    "secret_key": "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",
}
worker = AwsWorker(credential, resource, 'startup.sh')
worker.create_workers()

