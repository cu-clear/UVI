#!/bin/bash
$env:FLASK_APP="uvi_flask.py"
$env:FLASK_DEBUG="1"
./env_uvi/Scripts/activate
python3 -m flask run