queue_config_path="/.mineai/configs/queue_config"
while [ ! -f $queue_config_path ]; do sleep 1; done

sudo python -m worker.initialize_worker



