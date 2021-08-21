from binascii import hexlify, unhexlify
import constants
from functions import word2int, byte2int, byte2bit, frameversion


class UluxProtocol:
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

        # check if switch (IP) is configured
        print(f'Received data from {addr}')
        device_found = False
        for device in self.devicelist:
            if device.ip == addr[0]:
                print(f' |- Using config: {device.name}')
                device_found = True
        if not device_found:
            print(' |- WARNING: There is no config for this device!')
            return

        # analyse the message from the switch
        datagram = self.analyse_msg(data)
        if constants.DEBUG:
            print(f' |- Data: {hexlify(data)}')
        if datagram:
            if constants.DEBUG:
                print(f'   |- Frame length: {datagram[0][0]} bytes')
                print(f'   |- Awaited frame lenght: {datagram[0][1]} bytes')

            # check frame length for data loss
            if datagram[0][0] != datagram[0][1]:
                print('   |- ERROR: Frame length differs! Possible UDP packet data loss'
                      f' detected! Frame length:{datagram[0][0]}bytes != Awaited length:'
                      f' {datagram[0][1]}bytes')
                return

            if constants.DEBUG:
                print(f'   |- Frame version: {datagram[0][2]}')
                print(f'   |- Package ID: {datagram[0][3]}')
                print(f'   |- Project ID: {datagram[0][4]}')
                print(f'   |- Firmware version: {datagram[0][5]}')
                print(f'   |- Switch ID: {datagram[0][6]}')
                print(f'   |- Design ID: {datagram[0][7]}')
                print(f'   |- Part messages: {datagram[1]}')

            # check if the switch uses the same protocol version as this software
            if datagram[0][2] == constants.FRAMEVERSION:
                # loop through all commands an call their respective functions
                for cmd in datagram[1]:
                    if byte2int(cmd[1:2]) == 1:
                        print(f'         |- Lesen/Anfragen der StateFlags:')
                        self.state_flags(cmd)
                    elif byte2int(cmd[1:2]) == 14:
                        print(f'         |- Lesen/Anfragen der Seitenanzahl')
                    elif byte2int(cmd[1:2]) == 15:
                        print(f'         |- Lesen/Anfragen der ActorID Liste')
                    elif byte2int(cmd[1:2]) == 33:
                        print(f'         |- Lesen/Anfragen/Schreiben der ControlFlags')
                    else:
                        print(f'         |- WARNING: Unknown message type!')
            else:
                print('ERROR: Frameversion from switch differs to server version!')


    def init_switch(self, msg, addr):
        # if init flag is set, answer with ID Control message to
        # initialize the switch
        # msg header:
        # msg length (byte) = 0x08 = 08
        # MessageID (byte) = 0x02 = 02
        # ActorID (word) = 0x00 = 0000
        msg_header = '08020000'
        # msg:
        # set all ChangeRequests to on (1) so the switch will send on
        # every toggle of a value a package
        first_byte = int('10111111', 2)
        second_byte = int('00001000', 2)  # move some of these
        # settings to the config
        third_byte = int('00000000', 2)
        fourth_byte = int('00011111', 2)
        control_flags = msg_header + hex(first_byte)[2:] + hex(
            second_byte)[2:] + hex(third_byte)[2:] + hex(fourth_byte)[2:]
        print('control_flags:', control_flags)
        # init datagram needs to be modified by switch number,
        # degisn number, ...!! the following works only for 1 switch!
        init_datagram = '018618003202b1000000000003000100' + control_flags
        # evtl big und little endian drehen!
        print(f'             |- message: {init_datagram}')
        init_datagram = unhexlify(init_datagram)
        print(f'             |- Sending init message: {init_datagram}')
        # self.transport.sendto(init_datagram, addr)

    def state_flags(self, msg):
        for byte in msg[4:byte2int(msg[0:1])]:
            bits = format(byte, '08b')
            print(f'         |- {bits}')
            if bits[7] == '1':
                print('           |- Light sensor state: day')
            if bits[6] == '1':
                print('           |- Proximity sensor state: detected')
            if bits[5] == '1':
                print('           |- Display state: active')
            if bits[4] == '1':
                print('           |- Audio state: active')
            if bits[3] == '1':
                print('           |- Intro: active')
            if bits[2] == '1':
                print('           |- TIME REQUESTED')
            if bits[1] == '1':
                print('           |- INIT REQUESTED')
            if bits[0] == '1':
                print('           |- DEVICE ERROR DETECTED !!!')

    def analyse_msg(self, msg):
        """
         Read received message an return header and message parts

         Take a look on https://www.u-lux.com/fileadmin/user_upload/Downloads/PDF
         /Technische_Downloads/de/uLux_Switch_UMP.pdf for the used protocol

         :param
         msg: the data

         :return:
         tuple: ((header),(messages))
         header = (frame length, awaited frame length, frame version, package id, project id,
         firmware version, switch, id, design id)
         messages = [m, m+n]
         """

        # if header says: it's a message
        if msg[0:2] == b'\x01\x86':
            header = (len(msg),
                      word2int(msg[2:4]),
                      frameversion(msg[4:6]),
                      word2int(msg[6:8]),
                      word2int(msg[8:10]),
                      str(hexlify(msg[11:12]), encoding="ansi").upper() + '.' +
                      str(hexlify(msg[10:11]), encoding="ansi").upper(),
                      word2int(msg[12:14]),
                      word2int(msg[14:16])
                      )

            # check if the switch uses the same protocol version as this software
            if frameversion(msg[4:6]) == constants.FRAMEVERSION:
                messages = []
                message = msg[16:]
                message_length = len(message)
                message_start = 0

                while message_length > 0:
                    part_message = message[message_start: message_start + byte2int(
                        message[0 + message_start:1 + message_start])]
                    messages.append(part_message)
                    message_length -= byte2int(message[0 + message_start:1 + message_start])
                    message_start += byte2int(message[0 + message_start:1 + message_start])

                return (header, messages)

    def old_style(self, data, addr):
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
                print(f'   |- Full message: {hexlify(data[16:])}')

                # check if the switch uses the same protocol version as this software
                if frameversion(data[4:6]) == constants.FRAMEVERSION:
                    message = data[16:]
                    message_length = len(message)
                    message_start = 0
                    print(f'     |- full message length: {len(message)} bytes')
                    while message_length > 0:
                        part_message = message[message_start: message_start + byte2int(message[0 + message_start:1 + message_start])]
                        print(f'     |- part message: {hexlify(part_message)}')
                        print(f'     |- part message length: {byte2int(part_message[0:1])} bytes')
                        print(f'       |- message ID: {byte2int(part_message[1:2])}')
                        print(f'       |- actor ID: {word2int(part_message[2:4])}')
                        print(f'       |- part message data: '
                              f'{hexlify(part_message[4:byte2int(part_message[0:1])])}')

                        # act on message types
                        if byte2int(part_message[1:2]) == 1:
                            print(f'         |- Lesen/Anfragen der StateFlags:')
                            for byte in part_message[4:byte2int(part_message[0:1])]:
                                bits = format(byte, '08b')
                                print(f'         |- {bits}')
                                if bits[7] == '1':
                                    print('           |- Light sensor state: day')
                                if bits[6] == '1':
                                    print('           |- Proximity sensor state: detected')
                                if bits[5] == '1':
                                    print('           |- Display state: active')
                                if bits[4] == '1':
                                    print('           |- Audio state: active')
                                if bits[3] == '1':
                                    print('           |- Intro: active')
                                if bits[2] == '1':
                                    print('           |- TIME REQUESTED')
                                if bits[1] == '1':
                                    print('           |- INIT REQUESTED')
                                    # if init flag is set, answer with ID Control message to
                                    # initialize the switch
                                    # msg header:
                                    # msg length (byte) = 0x08 = 08
                                    # MessageID (byte) = 0x02 = 02
                                    # ActorID (word) = 0x00 = 0000
                                    msg_header = '08020000'
                                    # msg:
                                    # set all ChangeRequests to on (1) so the switch will send on
                                    # every toggle of a value a package
                                    first_byte = int('10111111', 2)
                                    second_byte = int('00001000', 2)  # move some of these
                                    # settings to the config
                                    third_byte = int('00000000', 2)
                                    fourth_byte = int('00011111', 2)
                                    control_flags = msg_header + hex(first_byte)[2:] + hex(
                                        second_byte)[2:] + hex(third_byte)[2:] + hex(fourth_byte)[2:]
                                    print('control_flags:', control_flags)
                                    # init datagram needs to be modified by switch number,
                                    # degisn number, ...!! the following works only for 1 switch!
                                    init_datagram = '018618003202b1000000000003000100' + control_flags
                                    # evtl big und little endian drehen!
                                    print(f'             |- message: {init_datagram}')
                                    init_datagram = unhexlify(init_datagram)
                                    print(f'             |- Sending init message: {init_datagram}')
                                    self.transport.sendto(init_datagram, addr)
                                if bits[0] == '1':
                                    print('           |- DEVICE ERROR DETECTED !!!')

                        elif byte2int(part_message[1:2]) == 14:
                            print(f'         |- Lesen/Anfragen der Seitenanzahl')
                        elif byte2int(part_message[1:2]) == 15:
                            print(f'         |- Lesen/Anfragen der ActorID Liste')
                        elif byte2int(part_message[1:2]) == 33:
                            print(f'         |- Lesen/Anfragen/Schreiben der ControlFlags')
                        else:
                            print(f'         |- WARNING: Unknown message type!')

                        message_length -= byte2int(message[0+message_start:1+message_start])
                        message_start += byte2int(message[0+message_start:1+message_start])
                else:
                    # print warning if the switch protocol version differs to the server version
                    print(f'WARNING: FRAMEVERSION DIFFERS [SERVER: {constants.FRAMEVERSION} - '
                          f'SWITCH: {frameversion(data[4:6])}')
