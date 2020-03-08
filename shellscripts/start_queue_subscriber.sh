cd /.mineai/CloudRunner
queue_config_path="/.mineai/configs/queue_config.json"
while [ ! -f $queue_config_path ]; do sleep 1; done

echo "Starting Queue Server"
python3 -m worker.initialize_worker