from datetime import datetime
import constants
import math


def create_command(cmds):
    """
    creates a command message
    :param
    cmds: the command
    :return:
    the message
    """
    cmds
    pass


def create_datagram(messages, switch):
    """
    Creats a data package with head an the messages

    :param
    messages: list of messages
    switch: function of switch class

    :return:
    data package
    """

    # message length
    msg_len = 0
    for msg in messages:
        print(len(msg))
        msg_len += len(msg)
    msg_len = int(msg_len / 2) + 16  # length of messages + 16 for headerdata

    # generate packeID
    constants.PACKAGEID += 1
    if constants.PACKAGEID >= 65536:
        constants.PACKAGEID = 1

    header = (str(int('01', 16)).zfill(2)
              + str(int('56', 16))
              + gen_word(msg_len)
              + str(int(round((constants.FRAMEVERSION - math.trunc(constants.FRAMEVERSION))*100,
                              0))).zfill(2)
              + str(math.trunc(constants.FRAMEVERSION)).zfill(2)
              + gen_word(constants.PACKAGEID)
              + gen_word(switch.project_id)
              + '0000'  # firmware version 0000 as answer
              + gen_word(int(switch.id))
              + gen_word(switch.design_id)
              )
    datagram = header
    for msg in messages:
        datagram += msg
    return datagram

# 0186 1800 3202 0200 0000 0000 0200 0100 1235435614354135  self
# 0186 1800 3202 c300 0000 0000 0300 0100 0401000004210000 ulux

def gen_word(int):
    word = str(format(int, '04x'))
    return word[2:4] + word[0:2]

def cm_datetime():
    """
    Creates a set time package. Needs to be send every hour to syncronize the clocks of every
    switch
    :return:
    """
    mes = []
    d = datetime.now()
    mes.append(0x0c)
    mes.append(0x2f)
    mes.append(0x00)
    mes.append(0x00)
    mes.append(d.second)
    mes.append(d.minute)
    mes.append(d.hour)
    mes.append(d.isoweekday())    # or weekday(), needed to be checked
    mes.append(d.day)
    mes.append(d.month)
    mes.append(d.year)
    print(mes)
    #mes.writeUInt16LE(d.getFullYear(), 10)
    return mes


def cm_init():
    # wireshark mitschnitt ukm
    # 0186 2e00 3202 0000 0000 d001 0300 0100 0821000010111111000010000000000000011111

    # wireshark mitschnitt ulux
    # 0186 1800 3202 c200 0000 0000 0300 0100 08 21 0000 86 08 00 04
    # 0186 1800 3202 b100 0000 0000 0300 0100 08 02 0000 00 00 a5 5a
    pass