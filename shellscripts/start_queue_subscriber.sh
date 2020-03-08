cd /.mineai/CloudRunner
queue_config_path="/.mineai/configs/queue_config.json"
while [ ! -f $queue_config_path ]; do sleep 1; done

echo "Starting Queue Server"
sudo touch /.mineai/subscriber_logs.txt
python3 -m worker.initialize_worker > /.mineai/subscriber_logs.txt