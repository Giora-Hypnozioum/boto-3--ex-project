#!/bin/bash
# Wrapper to run VPC automation in a virtual environment

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 vpc_automation.py
