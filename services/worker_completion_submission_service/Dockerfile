# Specify build time arguments
# that will be substituted by the docker-compose
ARG PYTHON_IMAGE_VERSION

FROM python:$PYTHON_IMAGE_VERSION

WORKDIR /mineai/CloudRunner

COPY . .

RUN ["chmod", "+x", "pip_fail_safe_install.sh"]
RUN ./pip_fail_safe_install.sh

CMD python -m worker.initialize_subscriber --queue_config_path=${BASE_CONFIG_PATH}/queue_config.json --storage_config_path=${BASE_CONFIG_PATH}/storage_config.json



