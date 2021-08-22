import asyncio
from datetime import datetime
from protocol import UluxProtocol
import constants
from functions import get_config
from switch import Switch


SWITCHLIST = []


async def main():
    print('Starting UKM (Ulux-Knx-Middleware) server')

    # load devices from config
    nr_of_devices = 0
    for switch_id in get_config()['devices']:
        SWITCHLIST.append(Switch(switch_id))
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
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UluxProtocol(SWITCHLIST),
        local_addr=('0.0.0.0', constants.PORT))
    print(f'  |- Socket: {transport.get_extra_info("socket")}')
    print(f'  |- Network port: {constants.PORT}')
    while True:
        await asyncio.sleep(100)


# run main function
asyncio.run(main())
