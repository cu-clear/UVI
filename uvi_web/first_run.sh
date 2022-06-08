#!/bin/bash
# APP_DIR=/data/verbnet-service/

echo "************VENV************"
echo "Creating Virtual Environment"
python3 -m venv env_uvi
# PATH=$APP_DIR/venv/bin:$PATH
echo "Virtual Environment Created"

echo "************VENV************"
echo "Activating Virtual Environment"
./env_uvi/Scripts/activate
echo "Virtual Environment Activated"

echo "************UVI************"
echo "Installing UVI requirements"
python3 -m pip install -r requirements.txt
echo "UVI requirements installed"