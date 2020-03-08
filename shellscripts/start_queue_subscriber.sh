#touch /.mineai/worker_init.sh
#
#echo "cd /.mineai/CloudRunner" >> /.mineai/worker_init.sh
#echo "queue_config_path='/.mineai/configs/queue_config.json'" >> /.mineai/worker_init.sh
#echo "while [ ! -f $queue_config_path ]; do sleep 1; done" >> /.mineai/worker_init.sh
#echo "python3 -m worker.initialize_worker >> /.mineai/subscriber_logs.txt" >> /.mineai/worker_init.sh
#
#chmod +x /.mineai/worker_init.sh
#/.mineai/worker_init.sh

cd /.mineai/CloudRunner
queue_config_path="/.mineai/configs/queue_config.json"
while [ ! -f $queue_config_path ]; do sleep 1; done

chmod +x worker/initialize_worker.py
python3 -m worker.initialize_worker >> /.mineai/subscriber_logs.txt 2>&1