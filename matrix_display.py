# New version for CircuitPython on a microcontroller 2024

# based on
# displayText.py
# (c)2020 robcranfill@gmail.com
#

# todo:
#    - we only need to paint the rightmost 1 new line of pixels; use "shift" to move the old ones!


import board
import time
from adafruit_ht16k33.matrix import Matrix8x8

import led8x8Font


# For the string, create the big list of bit values (columns), left to right.
#
def makeVRasters(string):
    bits = []
    if len(string) == 0: # is there a better way to handle this null-input case?
        string = " "
    else:
        string += string[0] # duplicate the first char onto the end of the data for easier scrolling. TODO: needed?
    for char in string:
        # bl is the list of *horizontal* rasters for the char
        bl = byteListForChar(char)
        for bitIndex in range(7,-1,-1):
            thisVR = 0
            for hRasterIndex in range(7,-1,-1):
                bitVal = ((1 << bitIndex) & bl[hRasterIndex])
                if bitVal > 0:
                    thisVR += (1 << (7-hRasterIndex))
            bits.append(thisVR)

    # print(f"vraster (len {len(bits)}): {bits}")
    return bits


# Rotate the list of vertical rasters thru the display, forever.
# The input data already has the first char duplicated at the end, for ease of rotation.
# Uses global displayDelay_ so we can change that after creating the thread.
#
def display_forever(matrix, vrs, delay):

    # display all 8 of the first char; after that, rotate old oneS and repaint only the new, rightmost, raster.

    display_raster(matrix, vrs[0:8])

    while True:

        matrix.shift(0, -1)
        
        # get the proper 8x8 bits to display
        for i in range(len(vrs)-8):
            display_raster(matrix, vrs[i:i+8])
            time.sleep(delay)


# Display the 8 raster lines
# This is slightly funky because I have my 8x8 matrix mounted sideways - YMMV!
#
def display_raster(matrix, rasters):

    matrix.shift(0, -1)
    
    i = 7
    for j in range(8):

        # rtest = 1 if (rasters[i] & (1 << j)) else 0 # fixme
        # display.set_pixel(j, i, rtest)

        # matrix[j, i, rasters[i] & (1<<j)]
        matrix[j, i] = rasters[i] & (1<<j)


    # matrix.fill(0)
    # for i in range(8):
    #     for j in range(8):
    #         # rtest = 1 if (rasters[i] & (1 << j)) else 0 # fixme
    #         # display.set_pixel(j, i, rtest)
    #         # matrix[j, i, rasters[i] & (1<<j)]
    #         matrix[j, i] = rasters[i] & (1<<j)


# Return a list of the bytes for the given character.
# TODO: catch missing chars?
#
def byteListForChar(char):
    bits = led8x8Font.FontData[char]
    return bits


# Main
#
def main(string, delay):

    i2c = board.STEMMA_I2C()
    matrix = Matrix8x8(i2c)
    matrix.brightness = 1
    # matrix.blink_rate = 3

    matrix.fill(1)
    time.sleep(1)
    matrix.fill(0)
    time.sleep(1)

    rasters = makeVRasters(string)
    print(f"Main: {rasters=}")

    display_forever(matrix, rasters, delay)


# do it
main("Wind 8MPH; Temp 64F   -", 0.1)
