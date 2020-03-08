# Set up Logging
touch worker_bootup_logfile.txt
exec > >(tee -i worker_bootup_logfile.txt)
exec 2>&1
