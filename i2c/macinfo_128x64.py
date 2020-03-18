#!/usr/bin/env python

# IMPORTS
import time
import datetime
import board
import busio
import digitalio
import psutil
from ssd1306_circuitpython import SSD1306OLED

# CONSTANTS
DELAY = 0.5

# START
if __name__ == '__main__':
    # Set up I2C on the FT232H Breakout
    i2c = busio.I2C(board.SCL, board.SDA)

    # Set up the RST pin
    reset = digitalio.DigitalInOut(board.G0)
    reset.direction = digitalio.Direction.OUTPUT

    display = SSD1306OLED(reset, i2c, 0x3D, 128, 64)
    display.set_inverse()
    display_is_inverse = True

    # Get initial values
    data = psutil.net_io_counters()
    start_out_packets = data.packets_sent
    start_in_packets = data.packets_recv
    out_packets = 0
    in_packets = 0
    head = "**SYSTEM INFORMATION**"
    length = display.length_of_string(head)
    head_centre = int((128 - length) / 2)
    if head_centre < 0: head_centre = 0
    logical_cores = int(psutil.cpu_count())
    physical_cores = int(psutil.cpu_count(False))

    while True:
        # Get the CPU utilization and calculate
        # the Binary-Coded Decimal (BCD) form
        display.clear()
        display.move(head_centre, 0).text(head)
        display.move(1, 8).text("CPU:")
        display.move(58, 8).text("Cores: " + str(logical_cores) + "/" + str(physical_cores))
        display.move(1, 16).text("Mem:")
        display.move(58, 16).text("Swap:")
        display.move(1, 24).text("Disk:")
        display.move(1, 32).text("Booted:")
        display.move(1, 40).text("Pkts in:")
        display.move(1, 48).text("Pkts out:")

        cpu = int(psutil.cpu_percent())
        display.move(30, 8).text(str(cpu) + "%")

        data = psutil.virtual_memory()
        mem = (data.used / data.total) * 100
        display.move(24, 16).text("{:.1f}%".format(mem))

        data = psutil.swap_memory()
        mem = 0 if data.total == 0 else (data.used / data.total) * 100
        display.move(90, 16).text("{:.1f}%".format(mem))

        data = psutil.disk_usage('/')
        display.move(58, 24).text("{:.1f}%".format(data.percent))

        data = psutil.boot_time()
        boot = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m @ %H:%M")
        display.move(58, 32).text(boot)

        data = psutil.net_io_counters()
        in_packets = data.packets_recv - start_in_packets
        if in_packets > 9999999:
            start_in_packets = data.packets_recv
            in_packets = 0
        display.move(58, 40).text(str(in_packets))

        out_packets = data.packets_sent - start_out_packets
        if out_packets > 9999999:
            start_out_packets = data.packets_sent
            out_packets = 0
        display.move(58, 48).text(str(out_packets))

        batt = psutil.sensors_battery()
        if batt == None:
            display.move(1, 56).text("No battery (desktop)")
        else:
            display.move(1, 56).text("Battery:")
            display.move(58, 56).text("{:.1f}%".format(batt.percent))

        display.draw()

        # Pause for breath
        time.sleep(DELAY)