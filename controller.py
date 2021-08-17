from binascii import hexlify
import constants


def int2bytes(i, enc):
    """
    Helper function for convert_hex
    :param i:
    :param enc:
    :return:
    """
    return i.to_bytes((i.bit_length() + 7) // 8, enc)


def convert_hex(str, enc1, enc2):
    """
    Convert hex from big to little endian or vice versa
    :param str:
    :param enc1:
    :param enc2:
    :return:
    """
    return int2bytes(int.from_bytes(bytes.fromhex(str), enc1), enc2).hex()


def word2int(byte):
    """
    Convert received word (2bytes) into integer
    :param byte:
    :return:
    """
    # print(byte)
    #print('hexlify', hexlify(byte))
    #print('to str', str(hexlify(byte), encoding="ansi"))
    #print('big -> little', convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little"))
    if convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little") != '':
        return int(convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little"), 16)
        #print('make int', int(convert_hex(str(hexlify(byte), encoding="ansi"), "big",
    # "little"), 16))
    else:
        return 0


def byte2bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] & (1<<shift)) >> shift


def frameversion(byte):
    """
    Convert received bytes into frame version
    :param byte:
    :return:
    """
    return int(convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little"), 10)/100


class UProtocol:
    def __init__(self, devicelist):
        self.devicelist = devicelist

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print(f'Received data from {addr}')
        print(self.devicelist)
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
            if len(data) != word2int(data[2:4]):
                print('   |- WARNING: Frame length differs! Possible UDP packet data lost '
                      'detected!' )
            else:
                print(f'   |- Frame version: {frameversion(data[4:6])}')
                print(f'   |- Package ID: {word2int(data[6:8])}')
                print(f'   |- Project ID: {word2int(data[8:10])}')
                print(f'   |- ?: {word2int(data[10:12])}')
                print(f'   |- Switch ID: {word2int(data[12:14])}')
                #print(f' |- Message: {data[11:]}')
                print(f'   |- Message: {hexlify(data[11:])}')
                if frameversion(data[4:6]) == constants.FRAMEVERSION:
                    message = data[11:]
                    if message[0] == 1:
                        print(f'     |- Lesen/Anfragen der StateFlags')
                #0186 2e00 3202 0000 0000 d001 0300 0100 0801 0000
                # 6600 00000821000000000000080f000001000100060e00000e00
                # send answer to switch
                else:
                    # print warning if the switch protocol version differs to the server version
                    print(f'WARNING: FRAMEVERSION DIFFERS [SERVER: {constants.FRAMEVERSION} - SWITCH: '
                          f'{frameversion(data[4:6])}')
            #self.transport.sendto(data, addr)



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