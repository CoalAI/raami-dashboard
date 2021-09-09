#!/bin/bash
curl https://bootstrap.pypa.io/get-pip.py | python3
pip3 install -r requirements.txt
pre-commit install
