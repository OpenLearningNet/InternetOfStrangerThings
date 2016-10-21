import max7219
from machine import Pin, SPI
spi = SPI(1)
display = max7219.Matrix8x8(spi, Pin(2))
display.test()