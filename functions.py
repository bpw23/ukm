import json
from binascii import hexlify


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


def byte2int(byte):
    """
    Convert received byte into integer
    :param byte:
    :return:
    """
    # print(byte)
    #print('hexlify', hexlify(byte))
    #print('to str', str(hexlify(byte), encoding="ansi"))
    #print('big -> little', convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little"))
    if convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little") != '':
        return int(convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little"), 16)

    else:
        return 0


def byte2bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] & (1<<shift)) >> shift


def byte2bit2(data, size, signed=False):
    mask = (1 << size) - 1
    number = 0
    for num in data:
        number = (number << size) | num & mask

    if signed and next(iter(data), 0) & 1 << (size - 1):
        return number - (1 << len(data) * size)
    else:
        return number


def frameversion(byte):
    """
    Convert received bytes into frame version
    :param byte:
    :return:
    """
    return int(convert_hex(str(hexlify(byte), encoding="ansi"), "big", "little"), 10)/100

# 0186 1600 3202 0500 0000 0000 0300 0100 06 43 0500 1a00