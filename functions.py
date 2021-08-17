import json


def get_config():
    """
    Read the config file
    :return:
    """
    try:
        with open("config.json", 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(" |-Problem with config.json detected... can't get configuration!")
    return data
