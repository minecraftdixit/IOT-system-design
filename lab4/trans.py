#!/usr/bin/python
# -*- coding: UTF-8 -*-

#
#    this is an UART-LoRa device and there is a firmware on the Module
#    users can transfer or receive the data directly by UART and don't
#    need to set parameters like coderate, spread factor, etc.
#    |============================================ |
#    |   It does not support LoRaWAN protocol !!!   |
#    | ============================================|
#   
#    This script is mainly for Raspberry Pi 3B+, 4B, and Zero series
#    Since PC/Laptop does not have GPIO to control HAT, it should be configured by
#    GUI and while setting the jumpers, 
#    Please refer to another script pc_main.py
#

import sys
import sx126x
import threading
import time
import select
import termios
import tty
from threading import Timer
import time

import board
import busio

import adafruit_vl53l0x

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

#
#    Need to disable the serial login shell and have to enable serial interface 
#    command `sudo raspi-config`
#    More details: see https://github.com/MithunHub/LoRa/blob/main/Basic%20Instruction.md
#
#    When the LoRaHAT is attached to RPi, the M0 and M1 jumpers of HAT should be removed.
#

#    The following is to obtain the temperature of the RPi CPU 
def get_cpu_temp():
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp) / 1000

#   serial_num
#       PiZero, Pi3B+, and Pi4B use "/dev/ttyS0"
#
#    Frequency is [850 to 930], or [410 to 493] MHz
#
#    address is 0 to 65535
#        under the same frequency, if set 65535, the node can receive 
#        messages from another node of address 0 to 65534 and similarly,
#        the address 0 to 65534 of node can receive messages while 
#        the another node of address 65535 sends.
#        otherwise two nodes must be the same address and frequency
#
#    The transmit power is {10, 13, 17, and 22} dBm
#
#    RSSI (receive signal strength indicator) is {True or False}
#        It will print the RSSI value when it receives each message
#

node = sx126x.sx126x(serial_num="/dev/ttyS0", freq=868, addr=3, power=22, rssi=True, air_speed=2400, relay=False)

def send_deal():
    get_rec = ""
    print("")
    print("Sending data automatically...")
    
    get_t = [4, 868, str(vl53.range)]
    print(get_t)
    offset_frequency = int(get_t[1]) - (850 if int(get_t[1]) > 850 else 410)
    
    #
    # the sending message format
    #
    #         receiving node              receiving node                   receiving node           own high 8bit           own low 8bit                 own 
    #         high 8bit address           low 8bit address                    frequency                address                 address                  frequency             message payload
    data = bytes([int(get_t[0]) >> 8]) + bytes([int(get_t[0]) & 0xff]) + bytes([offset_frequency]) + bytes([node.addr >> 8]) + bytes([node.addr & 0xff]) + bytes([node.offset_freq]) + get_t[2].encode()

    node.send(data)

def send_cpu_continue(continue_or_not=True):
    if continue_or_not:
        global timer_task
        global seconds
        #
        # broadcast the CPU temperature at 868.125MHz
        #
        data = bytes([255]) + bytes([255]) + bytes([18]) + bytes([255]) + bytes([255]) + bytes([12]) + "CPU Temperature:".encode() + str(get_cpu_temp()).encode() + " C".encode()
        node.send(data)
        time.sleep(0.2)
        timer_task = Timer(seconds, send_cpu_continue)
        timer_task.start()
    else:
        data = bytes([255]) + bytes([255]) + bytes([18]) + bytes([255]) + bytes([255]) + bytes([12]) + "CPU Temperature:".encode() + str(get_cpu_temp()).encode() + " C".encode()
        node.send(data)
        time.sleep(0.2)
        timer_task.cancel()
        pass

try:
    time.sleep(1)
    print("Press \033[1;32mEsc\033[0m to exit")
    print("Data will be sent automatically every 5 seconds.")
    
    seconds = 5  # Adjust the interval as needed

    while True:
        send_deal()  # Call the function to send data continuously
        time.sleep(seconds)  # Wait for the specified interval
        
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            c = sys.stdin.read(1)

            # Detect key Esc
            if c == '\x1b': break
            # Detect key s
            if c == '\x73':
                print("Press \033[1;32mc\033[0m to exit the send task")
                timer_task = Timer(seconds, send_cpu_continue)
                timer_task.start()
                
                while True:
                    if sys.stdin.read(1) == '\x63':
                        timer_task.cancel()
                        print('\x1b[1A', end='\r')
                        print(" " * 100)
                        print('\x1b[1A', end='\r')
                        break

        node.receive()
        
except:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)