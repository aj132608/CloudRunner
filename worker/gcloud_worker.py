import os
from google.oauth2 import service_account
import googleapiclient.discovery


class GCloudWorker:
 
    def __init__(self, credentials_path, number_of_workers, project, zone,
                 bucket, resource_dict):

        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        self.compute = googleapiclient.discovery.build('compute', 'v1',
                                                       credentials=self.credentials)
        self.number_of_workers = number_of_workers
        self.project = project
        self.zone = zone
        self.bucket = bucket
        self.resource_dict = resource_dict
        self.workers = self.get_workers

    def create_workers(self):
        '''
        Creates a number of VM instances to act as workers
        '''
        for num in range(self.number_of_workers):
            self.create_instance(f"worker-{str(num)}")

    def create_instance(self, name):
        '''
        Creates a single VM instance
        '''
        # Configure os image
        image_response = self.compute.images().getFromFamily(
            project='gce-uefi-images', family='ubuntu-1804-lts').execute()
        source_disk_image = image_response['selfLink']

        # Get values from resource config
        num_of_cpu = self.resource_dict['cpu']
        amount_of_memory = self.resource_dict['ram']
        gpu = self.resource_dict['gpu_type']
        num_of_gpu = self.resource_dict['num_of_gpu']
        disk_type = self.resource_dict['disk_type']
        disk_space = self.resource_dict['disk_space']

        # Set VM configuration
        config = {
            'name': name,

            # Machine configuration
            'machineType': f"zones/{self.zone}/machineTypes/custom-{num_of_cpu}-{amount_of_memory}",

            # Gpu configuration
            "guestAccelerators": [
                {
                    "acceleratorCount": num_of_gpu,
                    "acceleratorType": f"zones/{self.zone}/acceleratorTypes/{gpu}"
                }
            ],

            # Disk and image specifications
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        "sourceImage": source_disk_image,
                        "diskType": f"zones/{self.zone}/diskTypes/{disk_type}",
                        "diskSizeGb": f"{disk_space}"
                    }
                }
            ],

            # Network interfaces
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],


            # Misccelaneous settings
            "scheduling": {
                "preemptible": False,
                "onHostMaintenance": "TERMINATE",
                "automaticRestart": True,
                "nodeAffinities": []
            },

            # Metadata for the VM
            'metadata': {
                'items': [{
                    'key': 'bucket',
                    'value': self.bucket
                }]
            }
        }

        return self.compute.instances().insert(
            project=self.project,
            zone=self.zone,
            body=config).execute()

    def get_workers(self):

        result = self.compute.instances().list(project=prlf.oject, zone=zoself.ne).execute()
        return result['items'] if 'items' in result else None

    def delete_worker(self, name):

        return self.compute.instances().delete(
                    project=self.project,
                    zone=self.zone,
                    instance=name).execute()