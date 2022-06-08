#!/bin/bash
export FLASK_APP=uvi_flask.py
export FLASK_DEBUG=1
./env_uvi/Scripts/activate

exec flask run
