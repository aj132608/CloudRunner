import boto3


class AwsWorker:
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

    IMAGES = {
        "ap-northeast-1": "ami-50eaed51",
        "ap-southeast-1": "ami-f95875ab",
        "eu-central-1": "ami-ac1524b1",
        "eu-west-1": "ami-823686f5",
        "sa-east-1": "ami-c770c1da",
        "us-east-1": "ami-4ae27e22",
        "us-west-1": "ami-d1180894",
        "cn-north-1": "ami-fe7ae8c7",
        "us-gov-west-1": "ami-cf5630ec",
        "ap-southeast-2": "ami-890b62b3",
        "us-west-2": "ami-898dd9b9"
    }

    def __init__(self, aws_credentials, resource_dict, project_id, startup_path=None):
        """
        Initiates api for amazon vm workers
        """
        resource_name = "ec2"

        self.access_key = None
        self.secret_key = None

        self.resource_dict = resource_dict
        self.aws_credentials = aws_credentials
        self.set_credentials()
        self.region = self.resource_dict['region']

        self.compute = boto3.resource(resource_name,
                                      region_name=self.region,
                                      aws_access_key_id=self.access_key,
                                      aws_secret_access_key=self.secret_key)

        self.number_of_workers = self.resource_dict["num_workers"]
        self.image = self.resource_dict.get("image", AwsWorker.IMAGES[self.region])
        self.workers = None
        self.instance_type = self._select_instance_type(resource_dict)

        self.project_id = project_id

    def set_credentials(self):
        """

        Parses the credentials dictionary and populates the following class
        variables:

        :return: Nothing
        """
        self.access_key = self.aws_credentials['access_key']
        self.secret_key = self.aws_credentials['secret_key']

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
        """
        Creates a set of vm workers
        """
        self.workers = self.compute.create_instances(
            ImageId=self.image,
            MinCount=1,
            MaxCount=self.number_of_workers,
            InstanceType=self.instance_type,
            # KeyName=self.key_name
        )

    def delete_workers(self, ids):
        """
        Deletes vm worker by id
        """
        self.compute.instances.filter(
            InstanceIds=ids).terminate()

    def _mem_to_str(self, string):
        '''
        Assist function. Turns strings to number equivalent
        '''
        if not isinstance(string, str):
            string = str(string)
        conversion_factors = [
            ('Mb', 2 ** 20), ('MiB', 2 ** 20), ('m', 2 ** 20), ('mb', 2 ** 20),
            ('Gb', 2 ** 30), ('GiB', 2 ** 30), ('g', 2 ** 30), ('gb', 2 ** 30),
            ('kb', 2 ** 10), ('k', 2 ** 10)
        ]
        for k, f in conversion_factors:
            if string.endswith(k):
                return int(float(string.replace(k, '')) * f)
        return int(string)

    def _select_instance_type(self, resources_needed):
        '''
        Makes use of resources to select the instance type'
        '''
        sorted_specs = sorted(self.INSTANCE_SPECS.items(),
                              key=lambda x: x[1]['cpus'])
        for instance in sorted_specs:
            if int(
                    instance[1]['cpus']) >= int(
                resources_needed['cpus']) and self._mem_to_str(
                instance[1]['ram']) >= self._mem_to_str(
                resources_needed['ram']) and int(
                instance[1]['gpus']) >= int(
                resources_needed['gpus']):
                return instance[0]
