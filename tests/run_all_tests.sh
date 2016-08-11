#!/bin/bash
. ../.venv/bin/activate
python -m unittest discover
deactivate
