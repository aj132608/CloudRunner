import boto3


class AwsWorker:

    ACCESS_KEY = "AKIAIRZ3GOSUKQNWP6WA"
    SECRET_KEY = "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"
    INSTANCE_SPECS = {
            'c4.large': {
                'cpus': 2,
                'ram': '3.75g',
                'gpus': 0
            },
            'c4.xlarge': {
                'cpus': 4,
                'ram': '7.5g',
                'gpus': 0
            },
            'c4.2xlarge': {
                'cpus': 8,
                'ram': '15g',
                'gpus': 0
            },
            'c4.4xlarge': {
                'cpus': 16,
                'ram': '30g',
                'gpus': 0
            },
            'p2.xlarge': {
                'cpus': 4,
                'ram': '61g',
                'gpus': 1
            },
            'c4.8xlarge': {
                'cpus': 36,
                'ram': '60g',
                'gpus': 0
            },
            'p2.8xlarge': {
                'cpus': 32,
                'ram': '488g',
                'gpus': 8
            },
            'p2.16xlarge': {
                'cpus': 64,
                'ram': '732g',
                'gpus': 16
            }
        }

    def __init__(self, key_path, number_of_workers, region_name, key_name, 
                 resource_dict):
        '''
        Initiates api for amazon vm workers
        '''
        self.compute = boto3.resource('ec2',
                                      region_name=region_name,
                                      aws_access_key_id=AwsWorker.ACCESS_KEY,
                                      aws_secret_access_key=AwsWorker.SECRET_KEY)
        self.number_of_workers = number_of_workers
        self.workers = None
        self.key_path = key_path
        self.key_name = key_name
        self.instance_specs = AwsWorker.INSTANCE_SPECS
        self.instance_type = self._select_instance_type(resource_dict)

    def create_key_pair(self, key_name):
        '''
        creates private key to communicate with aws vm
        '''
        # create a file to store the key locally
        outfile = open(self.key_path, 'w')

        # call the boto ec2 function to create a key pair
        key_pair = self.compute.create_key_pair(KeyName=key_name)

        # capture the key and store it in a file
        KeyPairOut = str(key_pair.key_material)
        print(KeyPairOut)
        outfile.write(KeyPairOut)
        self.key_name = key_name

    def create_workers(self):
        '''
        Creates a set of vm workers 
        '''
        self.workers = self.compute.create_instances(
                    ImageId='ami-08bc77a2c7eb2b1da',
                    MinCount=1,
                    MaxCount=self.number_of_workers,
                    InstanceType=self.instance_type,
                    KeyName=self.key_name,
                )

    def delete_workers(self, ids):
        '''
        Deletes vm worker by id
        '''
        self.compute.instances.filter(InstanceIds=ids).terminate()

    def memstr2int(self, string):
            '''
            Assist function. Turns strings to number equivalent
            ''' 
            conversion_factors = [
                ('Mb', 2**20), ('MiB', 2**20), ('m', 2**20), ('mb', 2**20),
                ('Gb', 2**30), ('GiB', 2**30), ('g', 2**30), ('gb', 2**30),
                ('kb', 2**10), ('k', 2**10)
            ]
            for k, f in conversion_factors:
                if string.endswith(k):
                    return int(float(string.replace(k, '')) * f)
            return int(string)

    def _select_instance_type(self, resources_needed):
        '''
        Makes use of resources to select the instance type'
        '''
        sorted_specs = sorted(self.instance_specs.items(), key=lambda x: x[1]['cpus'])

        for instance in sorted_specs:
            if int(
                instance[1]['cpus']) >= int(
                resources_needed['cpus']) and self.memstr2int(
                instance[1]['ram']) >= self.memstr2int(
                resources_needed['ram']) and int(
                    instance[1]['gpus']) >= int(
                        resources_needed['gpus']):
                return instance[0]


