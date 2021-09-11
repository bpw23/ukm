from datetime import datetime
import constants
import math
from binascii import unhexlify
import socket


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
        if constants.DEBUG:
            print(f'[FUNCTION create_datagram] MESSAGE LENGTH: {len(msg)}')
        msg_len += len(msg)
    msg_len = int(msg_len / 2) + 16  # length of messages + 16 for headerdata
    if constants.DEBUG:
        print(f'[FUNCTION create_datagram] DATAGRAM LENGTH: {msg_len}')
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


def gen_word(value):
    word = str(format(value, '04x'))
    return word[2:4] + word[0:2]


def send_time(switch):
    """
    Creates a set time package. Needs to be send every hour to syncronize the clocks of every
    switch
    :return:
    """
    d = datetime.now()

    # shift weekday
    if d.isoweekday() == 7:
        weekday = '00'
    else:
        weekday = hex(d.isoweekday())[2:].zfill(2)

    # build time message
    time_data = ('0c2f0000'
                 + hex(d.second)[2:].zfill(2)
                 + hex(d.minute)[2:].zfill(2)
                 + hex(d.hour)[2:].zfill(2)
                 + weekday
                 + hex(d.day)[2:].zfill(2)
                 + hex(d.month)[2:].zfill(2)
                 + hex(datetime.now().year)[2:].zfill(4)[2:4]
                 + hex(datetime.now().year)[2:].zfill(4)[0:2]
                 )
    time_datagram = create_datagram([time_data], switch)
    print(f'             |- message: {time_datagram}')
    time_datagram = unhexlify(time_datagram)
    print(f'             |- Sending date and time message: {time_datagram}')
    return time_datagram


def init_switch(switch):
    # if init flag is set, answer with ID Control message to
    # initialize the switch
    # msg header:
    # msg length (byte) = 0x08 = 08
    # MessageID (byte) = 0x02 = 02
    # ActorID (word) = 0x00 = 0000

    msg_header = '08210000'
    # msg:
    # set all ChangeRequests to on (1) so the switch will send on
    # every toggle of a value
    first_byte = hex(int('10111111', 2))[2:].zfill(2)
    second_byte = hex(int('00001000', 2))[2:].zfill(2)  # move some of these
    # settings to the config
    third_byte = hex(int('00000000', 2))[2:].zfill(2)
    fourth_byte = hex(int('00011111', 2))[2:].zfill(2)
    control_flags = msg_header + second_byte + first_byte + fourth_byte + third_byte
    control_flags = msg_header + first_byte + second_byte + third_byte + fourth_byte
    #control_flags = "0821000000000000"
    print(f'control_flags: {msg_header}-{second_byte}-{first_byte}-{fourth_byte}-{third_byte}')

    # set page 1
    page = format(switch.config['init_page'], 'x').zfill(2)
    set_page = '062e0000' + page + '00'

    init_datagram = create_datagram([control_flags, set_page], switch)
    print(f'             |- Sending init message: {init_datagram}')
    init_datagram = unhexlify(init_datagram)
    return init_datagram


def send_set_page(switch, page):
    """
    Select a page on a switch
    :param switch: The switch
    :param page: the page number
    :return:
    """
    page = format(page, 'x').zfill(2)
    set_page = '062e0000' + page + '00'

    datagram = create_datagram([set_page], switch)
    print(f'             |- Sending set page message: {datagram}')
    # send data to switch
    constants.TRANSPORT.sendto(unhexlify(datagram), (switch.ip, constants.PORT))


def send_real_value(switch, actor, value_1, value_2=None, value_3=None, value_4=None):
    """
    Send value of actor to switch
    :param switch:
    :param actor:
    :param value:
    :return:
    """
    # msg header:
    # 0x00 MessageLength = 0x06, 0x08, 0x0A, 0x0C
    # 0x01 MessageID = 0x43
    # 0x02 - 0x03 ActorID = 0x0001..0xFFFF
    # 0x04 - 0x05 RealValues[0]
    # 0x06 - 0x07 RealValues[1]
    # 0x08 - 0x09 RealValues[2]
    # 0x0A - 0x0B RealValues[3]

    factor = 1

    msg_length = '06'
    msg_id = '43'
    # get the configured factor for the actor, as the switch only uses integer. The integer can
    # devided inside the switch config to show as float
    for block in switch.config['mapping']:
        if switch.config['mapping'][block]['actor_id'] == actor:
            factor = switch.config['mapping'][block]['factor']
    actor = hex(actor)[2:].zfill(4)
    value_1 = hex(round(value_1 * factor))[2:].zfill(4)

    data = msg_length + msg_id + actor[2:4] + actor[0:2] + value_1[2:4] + value_1[0:2]

    datagram = create_datagram([data], switch)
    print(f'             |- Sending realvalue message: {datagram}')
    # send data to switch
    constants.TRANSPORT.sendto(unhexlify(datagram), (switch.ip, constants.PORT))


def send_edit_value(switch, actor, value):
    """
    Send edit value to switch
    :param switch:
    :param actor:
    :param value:
    :return:
    """
    # msg header:
    # 0x00 MessageLength = 0x06, 0x08, 0x0A, 0x0C
    # 0x01 MessageID = 0x43
    # 0x02 - 0x03 ActorID = 0x0001..0xFFFF
    # 0x04 - 0x05 RealValues[0]
    # 0x06 - 0x07 RealValues[1]
    # 0x08 - 0x09 RealValues[2]
    # 0x0A - 0x0B RealValues[3]

    factor = 1

    msg_length = '06'
    msg_id = '42'
    # get the configured factor for the actor, as the switch only uses integer. The integer can
    # devided inside the switch config to show as float
    for block in switch.config['mapping']:
        if switch.config['mapping'][block]['actor_id'] == actor:
            factor = switch.config['mapping'][block]['factor']
    actor = hex(actor)[2:].zfill(4)
    value = hex(round(value * factor))[2:].zfill(4)

    data = msg_length + msg_id + actor[2:4] + actor[0:2] + value[2:4] + value[0:2]

    datagram = create_datagram([data], switch)
    print(f'             |- Sending realvalue message: {datagram}')
    # send data to switch
    constants.TRANSPORT.sendto(unhexlify(datagram), (switch.ip, constants.PORT))


def send_values(switch, actor, e_value=None, r_1_value=None, r_2_value=None, r_3_value=None,
                r_4_value=None):
    """
    Send edit value and all realvalues to a given switch for an actor
    :param switch: The corresponding switch
    :param actor: The actor
    :param e_value: the editvalue
    :param r_1_value: the first realvalue
    :param r_2_value: the second realvalue
    :param r_3_value: the third realvalue
    :param r_4_value: the fourth realvalue
    :return:
    """
    # 0x00 MessageLength = 0x08, 0xA, 0xC, 0xE
    # 0x01 MessageID = 0x41
    # 0x02 - 0x03 ActorID = 0x0001..0xFFFF
    # 0x04 - 0x05 EditValue
    # 0x06 - 0x07 RealValues[0]
    # 0x08 - 0x09 RealValues[1]
    # 0x0A - 0x0B RealValues[2]
    # 0x0C - 0x0D RealValues[3]
    factor = 1

    msg_length = '06'
    msg_id = '42'
    # get the configured factor for the actor, as the switch only uses integer. The integer can
    # devided inside the switch config to show as float
    for block in switch.config['mapping']:
        if switch.config['mapping'][block]['actor_id'] == actor:
            factor = switch.config['mapping'][block]['factor']
    actor = hex(actor)[2:].zfill(4)
    value = hex(round(value * factor))[2:].zfill(4)

    data = msg_length + msg_id + actor[2:4] + actor[0:2] + value[2:4] + value[0:2]

    datagram = create_datagram([data], switch)
    print(f'             |- Sending realvalue message: {datagram}')
    # send data to switch
    constants.TRANSPORT.sendto(unhexlify(datagram), (switch.ip, constants.PORT))
