
"""
Read channels 8-15 single ended
- Selvitä 19-bittisen luvun parsiminen
- Muuta binary/hex --> int
- Lisää plottaus
"""

import RPi.GPIO as GPIO
import time
import sys

import plot

CLK = 11
MISO = 9
MOSI = 10
CS = 11


def setupSpiPins(clkPin, misoPin, mosiPin, csPin):
    ''' Set all pins as an output except MISO (Master Input, Slave Output)'''
    GPIO.setup(clkPin, GPIO.OUT)
    GPIO.setup(misoPin, GPIO.IN)
    GPIO.setup(mosiPin, GPIO.OUT)
    GPIO.setup(csPin, GPIO.OUT)


def readAdc(channel, clkPin, misoPin, mosiPin, csPin):
    if (channel < 0) or (channel > 15):
        print("Invalid ADC Channel number, must be between [0,15]")
        return -1

    # Datasheet says chip select must be pulled high between conversions
    GPIO.output(csPin, GPIO.HIGH)

    # Start the read with both clock and chip select low
    GPIO.output(csPin, GPIO.LOW)
    GPIO.output(clkPin, GPIO.HIGH)

    # read command is:
    # start bit = 1
    # single-ended comparison = 1 (vs. pseudo-differential)
    # channel num bit 2
    # channel num bit 1
    # channel num bit 0 (LSB)
    read_command = 0x10         # Alkuperäinen: 0x18 (24 = MOSI)
    read_command |= channel

    sendBits(read_command, 8, clkPin, mosiPin)

    adcValue = recvBits(19, clkPin, misoPin)

    # Set chip select high to end the read
    GPIO.output(csPin, GPIO.HIGH)

    return adcValue


def sendBits(data, numBits, clkPin, mosiPin):
    ''' Sends 1 Byte or less of data'''

    data <<= (8 - numBits)

    for bit in range(numBits):
        # Set RPi's output bit high or low depending on highest bit of data field
        if data & 0x80:         # (0x80 = 128, 1000 0000)
            GPIO.output(mosiPin, GPIO.HIGH)
        else:
            GPIO.output(mosiPin, GPIO.LOW)

        # Advance data to the next bit
        data <<= 1

        # Pulse the clock pin HIGH then immediately low
        GPIO.output(clkPin, GPIO.HIGH)
        GPIO.output(clkPin, GPIO.LOW)


def recvBits(numBits, clkPin, misoPin):
    '''Receives arbitrary number of bits'''
    retVal = 0

    for bit in range(numBits):
        # Pulse clock pin
        GPIO.output(clkPin, GPIO.HIGH)
        GPIO.output(clkPin, GPIO.LOW)

        # Read 1 data bit in
        if GPIO.input(misoPin):
            retVal |= 0x1

        # Advance input to next bit
        retVal <<= 1

    # Divide by two to drop the NULL bit
    return (retVal/2)

def write_data(val):
    with open("/home/pi/Agis_data.txt", "a") as log:
        log.write("{0},{1}\n".format(strftime("%H:%M:%S"),str(val)))

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        setupSpiPins(CLK, MISO, MOSI, CS)

        while True:
            val = readAdc(0, CLK, MISO, MOSI, CS)
            print("ADC Result: ", str(val))
            write_data(val)
            time.sleep(5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit(0)


