#!/usr/bin/env python
#
# Bitbang'd SPI interface with an MCP3008 ADC device
# MCP3008 is 8-channel 10-bit analog to digital converter
#  Connections are:
#     CLK => SCLK
#     DOUT =>  MISO
#     DIN => MOSI
#     CS => CE0

import time
import sys
import spidev

spi = spidev.SpiDev()
spi.open(0, 0)              # open(bus, device)


def buildReadCommand(channel):
    startBit = 0x01
    singleEnded = 0x19

    return [startBit, singleEnded | (channel << 4), 0]


def processAdcValue(result):
    '''Take in result as array of three bytes.
       Return the two lowest bits of the 2nd byte and
       all of the third byte'''
    byte2 = (result[1] & 0x03)
    return (byte2 << 8) | result[2]
    pass


def readAdc(channel):
    if ((channel > 15) or (channel < 0)):
        return -1
    r = spi.xfer2(buildReadCommand(channel))
    #return processAdcValue(r)
    return r


if __name__ == '__main__':
    try:
        while True:
            bit_val = readAdc(0)
            float_val = int(bit_val[2:15], 2)
            print("ADC Result: ", str(float_val))
            time.sleep(5)
    except KeyboardInterrupt:
        spi.close()
        sys.exit(0)