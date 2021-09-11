import urllib.request
import json
import asyncio

import constants
from switch_messages import send_edit_value, send_real_value
from functions import get_config


def update_json_sources():
    """
    Fetch json data from source list in config
    """
    config = get_config()['sources']['json']
    for source in config:
        if source != "":
            print(f"[SOURCE][JSON]: Fetching data from {config[source]}")
            constants.JSON_SOURCES[source] = read_json(config[source])
            if constants.DEBUG:
                print(f'[SOURCE][JSON] Data from {config[source]}:', constants.JSON_SOURCES[
                    source])
            # write data to switches


def update_actor_data(switchlist):
    if constants.DEBUG:
        print('[SOURCE][JSON] SENDING VALUES TO SWITCHES...')
    for switch in switchlist:
        for actor in switch.actors:
            # update editvalue
            if switch.actors[actor]['ev_type'] == "json":
                if switch.actors[actor]['ev_source'] in constants.JSON_SOURCES:
                    json_string = constants.JSON_SOURCES[switch.actors[actor]['ev_source']]
                    print(json_string)
                    json_value = get_value_from_json(json_string, switch.actors[actor]['editvalue'])
                    if actor in switch.actor_values:
                        if 'editvalue' in switch.actor_values[actor]:
                            if switch.actor_values[actor]['editvalue'] != json_value:
                                switch.actor_values[actor] = {'ev_value': json_value}
                    print(f'[JSON] sending json data to switch {switch.name} for actor'
                          f' {actor} - editvalue: [{json_value}] ')
                    send_edit_value(switch, int(actor), json_value)

            # update realvalue 1
            if switch.actors[actor]['rv_1_type'] == "json":
                if switch.actors[actor]['rv_1_source'] in constants.JSON_SOURCES:
                    json_string = constants.JSON_SOURCES[switch.actors[actor]['rv_1_source']]
                    print(json_string)
                    json_value = get_value_from_json(json_string, switch.actors[actor]['realvalue_1'])
                    if actor in switch.actor_values:
                        if 'realvalue_1' in switch.actor_values[actor]:
                            if switch.actor_values[actor]['realvalue_1'] != json_value:
                                switch.actor_values[actor] = {'rv_1_value': json_value}
                    print(f'[JSON] sending json data to switch {switch.name} for actor'
                          f' {actor} - realvalue_1: {json_value} ')
                    send_edit_value(switch, int(actor), json_value)

            # update realvalue 2
            if switch.actors[actor]['rv_2_type'] == "json":
                    if switch.actors[actor]['rv_2_source'] in constants.JSON_SOURCES:
                        json_string = constants.JSON_SOURCES[switch.actors[actor]['rv_2_source']]
                        print(json_string)
                        json_value = get_value_from_json(json_string,
                                                         switch.actors[actor]['realvalue_2'])
                        if actor in switch.actor_values:
                            if 'realvalue_2' in switch.actor_values[actor]:
                                if switch.actor_values[actor]['realvalue_2'] != json_value:
                                    switch.actor_values[actor] = {'rv_2_value': json_value}
                        print(f'[JSON] sending json data to switch {switch.name} for actor'
                              f' {actor} - realvalue_2: {json_value} ')
                        send_edit_value(switch, int(actor), json_value)


def read_json(url_link):
    """
    Read json from a http source
    :param
    url_link: http-path
        the http link
    :return:
    data: json
        The requested json
    """
    try:
        with urllib.request.urlopen(url_link, timeout=constants.TIMEOUT) as url:
            data = json.loads(url.read().decode())
        return data
    except TimeoutError:
        return None
    except Exception as e:
        print(f'[function read_json] Error: {e}')


def get_value_from_json(json_dict, path):
    """
    Helper function for getting a value from a dict
    :param json_dict: the comlete dict
    :param path: the path to the value inside the dict
    :return:
    """
    for i in path:
        if i in json_dict:
            json_dict = json_dict[i]
        else:
            return 9999
    return json_dict
