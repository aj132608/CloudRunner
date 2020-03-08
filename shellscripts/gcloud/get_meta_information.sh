metadata_url="http://metadata.google.internal/computeMetadata/v1/instance"

# Downloading Metadata
echo "################ Downloading Metadata ################"
curl "$metadata_url/attributes/queue-config" -H  "Metadata-Flavor: Google" > /.mineai/configs/queue_config.json
curl "$metadata_url/attributes/storage-config" -H  "Metadata-Flavor: Google" > /.mineai/configs/storage_config.json
