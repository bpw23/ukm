from datetime import datetime

import asyncio
import atexit
from xknx import XKNX
from xknx.devices import Sensor
from xknx.io import (
    DEFAULT_MCAST_GRP,
    DEFAULT_MCAST_PORT,
    ConnectionConfig,
    ConnectionType,
    KNXIPInterface,
)
from xknx.dpt.dpt_2byte_float import DPT2ByteFloat
from xknx.dpt.dpt_1byte_uint import DPTValue1ByteUnsigned

import constants
from functions import get_config, word2int
from switch import Switch
from protocol import UluxProtocol
from switch_messages import send_real_value, send_edit_value
from json_read import update_json_sources, update_actor_data


SWITCHLIST = []


def exit_handler(xknx):
    print('Disconnecting from KNX...')
    xknx.stop()

def dev_upda(dev):
    print('DEVICE UPDATE', dev)

async def knx_telegram_received(telegram):
    """
    React on received knx telegrams, write values to switch
    :param telegram:
    :return:
    """
    # filter telegrams that are in use by switches
    try:
        group_address = f"{telegram.destination_address.main}/"\
                        f"{telegram.destination_address.middle}/"\
                        f"{telegram.destination_address.sub}"
        for switch in SWITCHLIST:
            if group_address in switch.config['mapping']:
                print(f"Received KNX telegram for group address {group_address} -"
                      f" {datetime.now().strftime('%d.%m.%y %H:%M:%S')}")
                if constants.DEBUG:
                    print(f" ├Telegram: {telegram}")
        for switch in SWITCHLIST:
            if group_address in switch.config['mapping']:
                print(f" ├SwitchID: {switch.id} - [{switch.name}]")
                print(f"   ├Name: {switch.config['mapping'][group_address]['name']}")
                # convert value on payload type
                if telegram.payload.CODE.value == 64:
                    value = DPT2ByteFloat.from_knx(telegram.payload.value.value)
                elif telegram.payload.CODE.value == 128:
                    value = DPTValue1ByteUnsigned.from_knx(telegram.payload.value.value)
                else:
                    print('PAYLOAD CODE [KNX DATA TYPE] NOT IMPLEMENTED!!!!')
                print(f"   ├Value: {value}")
                actor = switch.config['mapping'][group_address]['actor_id']
                print(f"   ├Actor: {actor}")
                switch.group_address_values[group_address] = telegram.payload.value.value


                # select actor data type
                if switch.config['mapping'][group_address]['actor_value_type'] > 0:
                    send_real_value(switch, actor, value)
                elif switch.config['mapping'][group_address]['actor_value_type'] == 0:
                    send_edit_value(switch, actor, value)
    except Exception as e:
        print(f'[function knx_telegram_received] Error when handling KNX data: {e}')


async def main():
    print('Starting UKM (Ulux-Knx-Middleware) server')

    # get configuration
    config = get_config()

    # KNX
    print(' |- Opening KNX communication...')
    xknx = XKNX(telegram_received_cb=knx_telegram_received,
                daemon_mode=False)
    connection_config = ConnectionConfig(
        connection_type=ConnectionType.TUNNELING,
        gateway_ip="192.168.0.101", gateway_port=3671, )
    xknx.connection_config = connection_config
    await xknx.start()


    # Register atexit for knx disconnect
    atexit.register(exit_handler, xknx)

    # load devices from config
    nr_of_devices = 0
    for switch_id in get_config()['devices']:
        SWITCHLIST.append(Switch(switch_id, xknx))
        nr_of_devices += 1
    print(f'  |- {nr_of_devices} configured switches:')
    for switch in SWITCHLIST:
        print(f'    |- {switch.name}   [{switch.ip}]')

    print(f'  |- Starttime: {datetime.now().strftime("%d.%m.%y %H:%M:%S")}')

    # start server for requests
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    constants.TRANSPORT, protocol = await loop.create_datagram_endpoint(
        lambda: UluxProtocol(SWITCHLIST),
        local_addr=('0.0.0.0', constants.PORT))
    print(f'  |- Socket: {constants.TRANSPORT.get_extra_info("socket")}')
    print(f'  |- Network port: {constants.PORT}')
    while True:
        # update json sources
        update_json_sources()
        update_actor_data(SWITCHLIST)
        # wait 60 seconds for next json update
        await asyncio.sleep(config['settings']['json_refresh'])



# start web server
# thread = Thread.start_new_thread(subprocess.call( ["python", "web.py"]))
# thread.start()

# run main function
asyncio.run(main())
