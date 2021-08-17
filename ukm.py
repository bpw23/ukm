import asyncio
from datetime import datetime
import socket
from controller import UProtocol
import constants
from functions import get_config
from switch import Switch


def createdgram(message):
    msg_len = len(message) + 16
    # datagram = Buffer.concat([headerbuffer,message],len)
    # packid = packid + 1
    # if packid == 65536:
    #    packid = 1
    # datagram.writeUInt16LE(len, 2)
   #
   # datagram.writeUInt16LE(packid, 6)
   # return datagram


def createdateaimemessage():
    mes = []
    d = datetime.now()
    mes.append(0x0c)
    mes.append(0x2f)
    mes.append(0x00)
    mes.append(0x00)
    mes.append(d.Seconds())
    mes.append(d.Minutes())
    mes.append(d.Hours())
    mes.append(d.UTCDay())
    mes.append(d.UTCDate())
    mes.append(d.Month()+1)
    #mes.writeUInt16LE(d.getFullYear(), 10)
    return mes


def switch_init():
    config = get_config()
    for device in config['devices']:
        print(f" |- sending init to {device} [{config['devices'][device]['IP']}]")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # message description:
        # Little-Endian Format (LSB zuerst)
        # FrameID 0x8601 for messages
        # FrameLength 0x0018
        # FrameVersion 0x3202
        # PackageID 0x007C ID des Paketes
            # Dieses Feld beinhaltet einen frei wählbaren Wert, der jedoch
            # nicht 0 sein darf. Wenn eine Antwort auf einen Befehl gesendet
            # wird, so wird in der Antwort der gleiche Wert vergeben. So
            # kann überprüft werden, ob das Datenpaket korrekt
            # entgegengenommen wurde.
            # Sendet ein Teilnehmer ein Ereignis (also keine Antwort auf
            # einen Befehl) so hat der PackageID den Wert 0
        # ProjectID 0x0000 ID des Projektes
            # Beim Konfigurieren des u::Lux Switch mittels u::Lux Config
            # wird dieser Wert zugewiesen. Dies dient zur Überprüfung, ob
            # der Teilnehmer das richtige Projekt verwendet.
        # Switch ID 0x0003 ID des Schalters
            # Beim Konfigurieren des u::Lux Switch mittels u::Lux Config
            # wird dieser Wert zugewiesen. Jeder Schalter in einem Projekt
            # hat einen eindeutigen ID. Der Schalter sendet immer mit seiner eindeutigen ID und
            # nimmt nur Pakete an, bei denen die ID 0 ist oder die ID mit der
            # internen ID übereinstimmt.
        # DesignID 0x0000 ID des Designs
            # Beim Konfigurieren des u::Lux Switch mittels u::Lux Config
            # wird dieser Wert zugewiesen. Jedes Design in einem Projekt hat
            # einen eindeutigen ID.
        # Messages
            # MessageLenght 0x01
            # MessageID 0x01  ID-State-Lesen/Anfragen der StateFlags
            # ActorID 0x0400  hat bei allgemeinen Aufgaben immer 0
        message = bytes.fromhex("86 01 00 18 02 32 00 7C 00 00 00 00 03 00 00 01 01 04 "
                                "00 00 21 04 00 00")
        sent = sock.sendto(message, (config['devices'][device]['IP'], constants.PORT))


async def main():
    print('Starting UKM (Ulux-Knx-Middleware) server')

    # load devices from config
    nr_of_devices = 0
    for device in get_config()['devices']:
        DEVICELIST.append(Switch(device))
        nr_of_devices += 1
    print(f'  |- {nr_of_devices} configured switches:')
    for device in DEVICELIST:
        print(f'    |- {device.name}   [{device.ip}]')

    print(f'  |- Starttime: {datetime.now().strftime("%d.%m.%y %H:%M:%S")}')

    # start server for requests
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UProtocol(DEVICELIST),
        local_addr=('0.0.0.0', constants.PORT))
    print(f'  |- Socket: {transport.get_extra_info("socket")}')
    print(f'  |- Network port: {constants.PORT}')
    while True:
        await asyncio.sleep(100)


# run main function
DEVICELIST = []
asyncio.run(main())
