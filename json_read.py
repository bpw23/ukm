import urllib.request
import json
import asyncio

import constants
from switch_messages import send_values
from functions import get_config


def update_json_sources():
    """
    Fetch json data from source list in config
    """
    config = get_config()['sources']['json']
    for source in config:
        if source != None:
            print(f"[FUNCTION update_json_sources]: Fetching data from {config[source]}")
            constants.JSON_SOURCES[source] = read_json(config[source])
            if constants.DEBUG:
                print(f'[FUNCTION update_json_sources] Data from {config[source]}:',
                      constants.JSON_SOURCES[
                    source])
        else:
            if constants.DEBUG:
                print(f"[FUNCTION update_json_sources]: No data received!")


def update_actor_data(switchlist):
    """
    Updates the switch.actor_values from JSON_SOURCES and sends the values to the switch
    :param switchlist:
    :return:
    """
    if constants.DEBUG:
        print('[FUNCTION update_actor_data] SENDING VALUES TO SWITCHES...')
    for switch in switchlist:
        for actor in switch.actors:
            # update editvalue
            if switch.actors[actor]['ev_type'] == "json":
                # only if the source of the actor is present in JSON_SOURCES(where all actual
                # json data is present)
                if switch.actors[actor]['ev_source'] in constants.JSON_SOURCES:
                    # get the corresponding json from JSON_SOURCES
                    json_string = constants.JSON_SOURCES[switch.actors[actor]['ev_source']]
                    json_value = get_value_from_json(json_string, switch.actors[actor][
                        'editvalue'])
                    # write value to switch actor dict
                    if actor not in switch.actor_values:
                        switch.actor_values[actor] = {}
                    switch.actor_values[actor]['ev_value'] = json_value

                    print(f'[FUNCTION update_actor_data] sending json data to switch '
                          f'{switch.name} for actor {actor} - editvalue: {json_value} ')
                    send_values(switch, actor, ev_value=json_value)

            # update realvalue 1
            if switch.actors[actor]['rv_1_type'] == "json":
                # only if the source of the actor is present in JSON_SOURCES(where all actual
                # json data is present)
                if switch.actors[actor]['rv_1_source'] in constants.JSON_SOURCES:
                    # get the corresponding json from JSON_SOURCES
                    json_string = constants.JSON_SOURCES[switch.actors[actor]['rv_1_source']]
                    json_value = get_value_from_json(json_string, switch.actors[actor][
                        'realvalue_1'])
                    # write value to switch actor dict
                    if actor not in switch.actor_values:
                        switch.actor_values[actor] = {}
                    # write value to actor list of the switch
                    switch.actor_values[actor]['rv_1_value'] = json_value

                    print(f'[FUNCTION update_actor_data] sending json data to switch '
                          f'{switch.name} for actor {actor} - realvalue_1: {json_value} ')
                    send_values(switch, actor, rv_1_value=json_value)

            # update realvalue 2
            if switch.actors[actor]['rv_2_type'] == "json":
                # only if the source of the actor is present in JSON_SOURCES(where all actual
                # json data is present)
                if switch.actors[actor]['rv_2_source'] in constants.JSON_SOURCES:
                    # get the corresponding json from JSON_SOURCES
                    json_string = constants.JSON_SOURCES[switch.actors[actor]['rv_2_source']]
                    json_value = get_value_from_json(json_string, switch.actors[actor][
                        'realvalue_2'])
                    # write value to switch actor dict
                    if actor not in switch.actor_values:
                        switch.actor_values[actor] = {}
                    # write value to actor list of the switch
                    switch.actor_values[actor]['rv_2_value'] = json_value

                    print(f'[FUNCTION update_actor_data] sending json data to switch '
                          f'{switch.name} for actor {actor} - realvalue_2: {json_value} ')
                    send_values(switch, actor, rv_2_value=json_value)

            # update realvalue 3
            if switch.actors[actor]['rv_3_type'] == "json":
                # only if the source of the actor is present in JSON_SOURCES(where all actual
                # json data is present)
                if switch.actors[actor]['rv_3_source'] in constants.JSON_SOURCES:
                    # get the corresponding json from JSON_SOURCES
                    json_string = constants.JSON_SOURCES[switch.actors[actor]['rv_3_source']]
                    json_value = get_value_from_json(json_string, switch.actors[actor][
                        'realvalue_3'])
                    # write value to switch actor dict
                    if actor not in switch.actor_values:
                        switch.actor_values[actor] = {}
                    # write value to actor list of the switch
                    switch.actor_values[actor]['rv_3_value'] = json_value

                    print(f'[FUNCTION update_actor_data] sending json data to switch '
                          f'{switch.name} for actor {actor} - realvalue_3: {json_value} ')
                    send_values(switch, actor, rv_3_value=json_value)

            # update realvalue 4
            if switch.actors[actor]['rv_4_type'] == "json":
                # only if the source of the actor is present in JSON_SOURCES(where all actual
                # json data is present)
                if switch.actors[actor]['rv_4_source'] in constants.JSON_SOURCES:
                    # get the corresponding json from JSON_SOURCES
                    json_string = constants.JSON_SOURCES[switch.actors[actor]['rv_4_source']]
                    json_value = get_value_from_json(json_string, switch.actors[actor][
                        'realvalue_4'])
                    # write value to switch actor dict
                    if actor not in switch.actor_values:
                        switch.actor_values[actor] = {}
                    # write value to actor list of the switch
                    switch.actor_values[actor]['rv_4_value'] = json_value

                    print(f'[FUNCTION update_actor_data] sending json data to switch '
                          f'{switch.name} for actor {actor} - realvalue_4: {json_value} ')
                    send_values(switch, actor, rv_4_value=json_value)


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
    :param json_dict: the complete dict
    :param path: the path to the value inside the dict
    :return:
    """
    for i in path:
        if i in json_dict:
            json_dict = json_dict[i]
        else:
            return 9999
    return json_dict
