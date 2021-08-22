from datetime import datetime
import constants
import math
from binascii import unhexlify


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

# 0186 1800 3202 0200 0000 0000 0200 0100 1235 4356 1435 4135  self
# 0186 1700 3202 0400 0000 0000 0300 0100 0802 0000 bf80 1f
# 0186 1c00 3202 0200 0000 0000 0200 0100 0c2f 0000 5623 2306 2108 2021
# 0186 1700 3202 2900 0000 0000 0300 0100 0802 0000 bf80 1f
# 0186 1c00 3202 0700 0000 0000 0300 0100 0c2f 0000 3631 1706 1508 057e time, aber falsch
# ulux_______
# 0186 2c00 3202 c700 0000 0000 0300 0100 0c2f 0000 1f0c 1706 1508 e507 040e 0000 042e 0000 0821
# 0000 0000 0000  date+time
# 0186 1800 3202 c300 0000 0000 0300 0100 0401 0000 0421 0000 ulux, wohl kein init
# 0186 2000 3202 cb00 0000 0000 0300 0100 040e 0000 042e 0000 0821 0000 0000 0000
# 1) seitenanzahl anfragen 2) page index anfragen  3) lesen der control flags
# 0186 1800 3202 d000 0000 0000 0300 0100 0821 0000 0000 0000 # control flags senden
#1. mal senden
# 0186 1800 3202 d100 0000 0000 0300 0100 0401 0000 0421 0000   anfrage state flags and control
# flags
#2. mal senden
# 0186 2c00 3202 d200 0000 0000 0300 0100 0c2f 0000 2b02 0900 1608 e507 040e 0000 042e 0000
# 0821000000000000  schreiben von zeit datum, lese seitenanzahl, lese page index
# 0186 1c00 3202 0500 0000 0000 0300 0100 0c2f 0000 300d 0907 1608 057e ukm uhrzeit
#3. mal senden
# 0186 2000 3202 d300 0000 0000 0300 0100 040e 0000 042e 0000 0821 0000 0000 0000  control flags
# page index nr of pages
# 0186 1e00 3202 0400 0000 0000 0300 0100 0821 0000 08bf 1f00 062e 0000 0100


def send(function):
    import socket

    # A tuple with server ip and port
    serverAddress = ("192.168.0.42", constants.PORT);

    # Create a datagram socket
    tempSensorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);

    # Get temperature
    if function == 1:
        temperature = "01862c003202d40000000000030001000c2f0000000f10001608e507040e0000042e00000821000000000000"
        temperature = "01861c003202020000000000030001000c2f0000043b14001608e507"
    elif function == 2:
        temperature = "018620003202d5000000000003000100040e0000042e00000821000000000000"
    elif function == 3:
        temperature = "018618003202d60000000000030001000401000004210000"
    else:
        print('fehlerhafte eingabe')
        return

    # Socket is not in connected state yet...sendto() can be used
    # Send temperature to the server
    tempSensorSocket.sendto(temperature.encode(), serverAddress);

    # Read UDP server's response datagram
    response = tempSensorSocket.recv(1024);
    print(response);


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
    set_page = '062e00000100'
    init_datagram = create_datagram([control_flags, set_page], switch)
    print(f'             |- Sending init message: {init_datagram}')
    init_datagram = unhexlify(init_datagram)
    return init_datagram
