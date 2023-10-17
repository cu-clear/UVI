#!/bin/bash
# APP_DIR=/data/verbnet-service/
# PATH=$APP_DIR/venv/bin:$PATH

echo "************VENV************"
echo "Creating Virtual Environment"
python3.9 -m venv env_uvi && echo "Virtual Environment Created"

echo "************VENV************"
echo "Activating Virtual Environment"
source /data/verbnet-service/UVI_deployable/uvi_web/env_uvi/bin/activate && echo "Virtual Environment Activated"

echo "************UVI************"
echo "Installing UVI requirements"
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt && echo "UVI requirements installed"