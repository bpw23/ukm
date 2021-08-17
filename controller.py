from binascii import hexlify
import constants
from functions import word2int, byte2int, byte2bit, frameversion


class UProtocol:
    def __init__(self, devicelist):
        self.devicelist = devicelist

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        """
        Act on received data

        Take a look on https://www.u-lux.com/fileadmin/user_upload/Downloads/PDF
        /Technische_Downloads/de/uLux_Switch_UMP.pdf for the used protocol

        :param data: the data
        :param addr: the ip adress from which the data came
        :return:
        """
        print(f'Received data from {addr}')
        device_found = False
        for device in self.devicelist:
            if device.ip == addr[0]:
                print(f' |- Using config: {device.name}')
                device_found = True
        if not device_found:
                print(' |- WARNING: There is no config for this device!')

        print(f' |- Data: {hexlify(data)}')
        if data[0:2] == b'\x01\x86':
            print(f'   |- Frame length: {len(data)} bytes')
            print(f'   |- Awaited frame lenght: {word2int(data[2:4])} bytes')
            # check frame length for data loss
            if len(data) != word2int(data[2:4]):
                print('   |- WARNING: Frame length differs! Possible UDP packet data loss'
                      ' detected!' )
            else:
                print(f'   |- Frame version: {frameversion(data[4:6])}')
                print(f'   |- Package ID: {word2int(data[6:8])}')
                print(f'   |- Project ID: {word2int(data[8:10])}')
                print(f'   |- Firmware version: {word2int(data[10:12])}')
                print(f'   |- Switch ID: {word2int(data[12:14])}')
                print(f'   |- Design ID: {word2int(data[14:16])}')
                print(f'   |- Message: {hexlify(data[16:])}')

                # check if the switch uses the same protocol version as this software
                if frameversion(data[4:6]) == constants.FRAMEVERSION:
                    message = data[16:]
                    message_length = len(message)
                    message_start = 0
                    print(f'     |- full message length: {len(message)} bytes')
                    while message_length != 0:

                        print(f'     |- part message length:'
                              f' {byte2int(message[0 + message_start:1 + message_start])} '
                              f'bytes')
                        print(f'       |- message ID:'
                              f' {byte2int(message[1 + message_start:2 + message_start])}')
                        print(f'       |- actor ID:'
                              f' {word2int(message[2 + message_start:4 + message_start])}')
                        print(f'       |- message: '
                              f'{hexlify(message)[8+message_start:8 + message_start + byte2int(message[0 + message_start:1 + message_start])]}')

                        # act on message types
                        if byte2int(message[1+message_start:2+message_start]) == 1:
                            print(f'         |- Lesen/Anfragen der StateFlags')
                            print(f'         |- message: '
                                  f'{hexlify(message)[8 + message_start:8 + message_start + byte2int(message[0 + message_start:1 + message_start])]}')

                            # if init flag is set, send init data to switch
                            # self.transport.sendto(data, addr)
                        elif byte2int(message[1+message_start:2+message_start]) == 14:
                            print(f'         |- Lesen/Anfragen der Seitenanzahl')
                        elif byte2int(message[1 + message_start:2 + message_start]) == 15:
                            print(f'         |- Lesen/Anfragen der ActorID Liste')
                        elif byte2int(message[1+message_start:2+message_start]) == 33:
                            print(f'         |- Lesen/Anfragen/Schreiben der ControlFlags')
                        else:
                            print(f'         |- WARNING: Unknown message type!')

                        message_length -= byte2int(message[0+message_start:1+message_start])
                        message_start += byte2int(message[0+message_start:1+message_start])
                else:
                    # print warning if the switch protocol version differs to the server version
                    print(f'WARNING: FRAMEVERSION DIFFERS [SERVER: {constants.FRAMEVERSION} - '
                          f'SWITCH: {frameversion(data[4:6])}')

