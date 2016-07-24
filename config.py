import json

def return_config(filename='config.json'):
    with open(filename, 'r') as json_file:
        config = json.load(json_file)
    return config

JSONConfig = return_config()
