cd /.mineai/CloudRunner
queue_config_path="/.mineai/configs/queue_config.json"
while [ ! -f $queue_config_path ]; do sleep 1; done

chmod +x worker/initialize_subscriber.py
python3.7 worker/initialize_subscriber.py > /.mineai/subscriber_logs.txt 2>&1