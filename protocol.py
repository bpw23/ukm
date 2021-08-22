from binascii import hexlify, unhexlify
from datetime import datetime
import constants
from functions import word2int, byte2int, byte2bit, frameversion
from messages import init_switch, send_time


class UluxProtocol:
    def __init__(self, devicelist):
        self.devicelist = devicelist

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, transport):
        print('CONNECTION LOST:', transport)

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
        print(f'Received data from {addr} - {datetime.now().strftime("%d.%m.%y - %H:%M:%S:%f")}')
        device_found = False
        for device in self.devicelist:
            if device.ip == addr[0]:
                print(f' |- Using config: {device.name}')
                actual_switch = device
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
                    print(f'         |- Command: {hexlify(cmd)}')
                    if byte2int(cmd[1:2]) == 1:
                        print(f'         |- Read / request the state flags:')
                        self.state_flags(cmd, actual_switch)
                    elif byte2int(cmd[1:2]) == 2:
                        print(f'         |- set state flags')
                    elif byte2int(cmd[1:2]) == 3:
                        print(f'         |- brightness from switch')
                    elif byte2int(cmd[1:2]) == 4:
                        print(f'         |- Signatur / checksum message')
                    elif byte2int(cmd[1:2]) == 14:
                        print(f'         |- Read / request the number of pages')
                    elif byte2int(cmd[1:2]) == 15:
                        print(f'         |- Read / request the ActorID list')
                    elif byte2int(cmd[1:2]) == 33:
                        print(f'         |- Read / request / write the control flags')
                    elif byte2int(cmd[1:2]) == 45:
                        print(f'         |- activate / deactivate the switch')
                    elif byte2int(cmd[1:2]) == 46:
                        print(f'         |- Read / request / write of pageindex')
                    elif byte2int(cmd[1:2]) == 47:
                        print(f'         |- Read / request / write Date and Time')
                    elif byte2int(cmd[1:2]) == 65:
                        print(f'         |- Read / request / write of real-value, edit-value '
                              f'and LEDs of a specific actor')
                    else:
                        print(f'         |- WARNING: Unknown message type!')
            else:
                print('ERROR: Frameversion from switch differs to server version!')

    def state_flags(self, msg, switch):
        bits = format(int(hexlify(msg)[8:10], 16), '08b')
        print(f'         |- BITS 0-7 {bits}')

        if bits[7] == '1':  # Bit 0 in uLux manual
            if constants.DEBUG:
                print('           ├ Light sensor state: day')
            switch.light_sensor = True
        else:
            if constants.DEBUG:
                print('           ├ Light sensor state: night')
            switch.light_sensor = False

        if bits[6] == '1':
            if constants.DEBUG:
                print('           ├ Proximity sensor state: detected')
            switch.proximity_sensor = True
        else:
            if constants.DEBUG:
                print('           ├ Proximity sensor state: nothing detected')
            switch.proximity_sensor = False

        if bits[5] == '1':
            if constants.DEBUG:
                print('           ├ Display state: active')
            switch.display_active = True
        else:
            if constants.DEBUG:
                print('           ├ Display state: inactive')
            switch.display_active = False

        if bits[4] == '1':
            if constants.DEBUG:
                print('           ├ Audio state: active')
            switch.audio_active = True
        else:
            if constants.DEBUG:
                print('           ├ Audio state: inactive')
            switch.audio_active = False

        if bits[3] == '1':
            if constants.DEBUG:
                print('           ├ Intro: active')
            switch.intro_active = True
        else:
            if constants.DEBUG:
                print('           ├ Intro: not active')
            switch.intro_active = False

        if bits[2] == '1':
            if constants.DEBUG:
                print('           ├ TIME REQUESTED')
            self.transport.sendto(send_time(switch), (switch.ip, constants.PORT))

        if bits[1] == '1':
            if constants.DEBUG:
                print('           ├ INIT REQUESTED')
            self.transport.sendto(init_switch(switch), (switch.ip, constants.PORT))

        if bits[0] == '1':
            if constants.DEBUG:
                print('           ├ DEVICE ERROR DETECTED !!!')
            switch.device_error = True
        else:
            if constants.DEBUG:
                print('           ├ Device is ok')
            switch.device_error = False

        bits = format(int(hexlify(msg)[10:12], 16), '08b')
        print(f'         |- BITS 7-14 BITS {bits}')

        # Bits 8-10 reserved for future usage

        if bits[4] == '1':
            if constants.DEBUG:
                print('           ├ Addon Motion detector: detected')
            switch.audio_active = True
        else:
            if constants.DEBUG:
                print('           ├ Addon Motion detector: nothing detected')
            switch.audio_active = False

        if bits[3] == '1':
            if constants.DEBUG:
                print('           ├ LuxSensor: present')
            switch.intro_active = True
        else:
            if constants.DEBUG:
                print('           ├ LuxSensor: not present')
            switch.intro_active = False

        # Bits 13-23 reserved for future usage

        bits = format(int(hexlify(msg)[12:14], 16), '08b')
        print(f'         |- BITS 15-23 BITS {bits}')
        # Bits 13-23 reserved for future usage

        bits = format(int(hexlify(msg)[14:16], 16), '08b')
        print(f'         |- BITS 24-31 BITS {bits}')

        if bits[7] == '1':  # Bit 24
            if constants.DEBUG:
                print('           ├ Addon Temperature Sensor: present')
            switch.addon_temperature = True
        else:
            if constants.DEBUG:
                print('           ├ Addon Temperature Sensor: not present')
            switch.addon_temperature = False

        if bits[6] == '1':  # Bit 25
            if constants.DEBUG:
                print('           ├ Addon Humidity Sensor: present')
            switch.addon_humidity = True
        else:
            if constants.DEBUG:
                print('           ├ Addon Humidity Sensor: not present')
            switch.addon_humidity = False

        if bits[5] == '1':  # Bit 26
            if constants.DEBUG:
                print('           ├ Addon CO2 Sensor: present')
            switch.addon_co2 = True
        else:
            if constants.DEBUG:
                print('           ├ Addon CO2 Sensor: not present')
            switch.addon_co2 = False

        if bits[4] == '1':  # Bit 27
            if constants.DEBUG:
                print('           ├ Addon IN2 Sensor: present')
            switch.addon_in2 = True
        else:
            if constants.DEBUG:
                print('           ├ Addon IN2 Sensor: not present')
            switch.addon_in2 = False

        if bits[3] == '1':  # Bit 28
            if constants.DEBUG:
                print('           ├ Addon VOC Sensor: present')
            self.addon_voc_sensor = True
        else:
            if constants.DEBUG:
                print('           ├ Addon VOC Sensor: not present')
            self.addon_voc_sensor = False

        if bits[2] == '1':  # Bit 29
            if constants.DEBUG:
                print('           ├ Addon Motion Sensor: present')
            switch.addon_motion_sensor = False
        else:
            if constants.DEBUG:
                print('           ├ Addon Motion Sensor: not present')
            switch.addon_motion_sensor = False

        # Bits 30-31 reserved for future usage


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

                return header, messages

