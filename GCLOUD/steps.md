# Compute Engine
## Exploration <i><b>INCOMPLETE</i></b>
creating instance
---

Get Project ID

    gcloud projects list

Create and list new instances

    gcloud compute instances create <instance_name>

    gcloud compute instances list
<!-- gcloud compute ssh <instance_name> -->
SSH into the instance

    gcloud compute ssh <instance name>
Copy a py file to the project / Create instance

    gcloud compute scp ~/<fullpath/file> <instancename>:~/remote-destination
    
Example

    gcloud compute scp ~/mineai/CloudRunner/GCLOUD/gcloud_test.py new:~/remote-destination

Delete Instances

    gcloud compute instances delete <instancename>

    gcloud init
    gcloud create projects <projname>

---

# App Engine

For project ID

    gcloud projects list
    gcloud app create --project=[projname]
    gcloud components install app-engine-python

Link billing ac to new proj
cd to proj directory

add app.yaml

    runtime: python27
    api_version: 1
    threadsafe: true

    libraries:
    - name: ssl
    version: latest

    handlers:
    - url: /static
    static_dir: static
    - url: /.*
    script: main.app


run
    python main.py
    OR
    dev_appserver.py app.yaml

Deploy

    gcloud app deploy
    gcloud app browse