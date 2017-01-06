# Python module for control of Zengge bluetooth LED bulbs
#
# Copyright 2016 Matthew Garrett <mjg59@srcf.ucam.org>
#
# This code is released under the terms of the MIT license. See the LICENSE
# file for more details.

import time

from bluepy import btle

class Delegate(btle.DefaultDelegate):
    def __init__(self, bulb):
      self.bulb = bulb
      btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
      if data[5] > 2:
        power = True
      else:
        power = False
      self.bulb.set_state(data[9], data[6], data[7], data[8], power)

class zengge:
  def __init__(self, mac):
    self.mac = mac

  def set_state(self, white, red, green, blue, power):
    self.white = white
    self.red = red
    self.green = green
    self.blue = blue
    self.power = power

  def connect(self):
    self.device = btle.Peripheral(self.mac, addrType=btle.ADDR_TYPE_PUBLIC)
    self.device.setDelegate(Delegate(self))

    handles = self.device.getCharacteristics()
    for handle in handles:
      if handle.uuid == "ffe4":
        self.statehandle = handle
      if handle.uuid == "ffe6":
        self.redhandle = handle
      if handle.uuid == "ffe7":
        self.greenhandle = handle
      if handle.uuid == "ffe8":
        self.bluehandle = handle
      if handle.uuid == "ffe9":
        self.rgbwhandle = handle
      if handle.uuid == "ffea":
        self.whitehandle = handle

    self.get_state()

  def send_packet(self, handle, data):
    initial = time.time()
    while True:
      if time.time() - initial >= 10:
        return False
      try:
        return handle.write(bytes(data), withResponse=True)
      except:
        self.connect()

  def off(self):
    self.power = False
    packet = bytearray([0xcc, 0x24, 0x33])
    self.send_packet(self.rgbwhandle, packet)

  def on(self):
    self.power = True
    packet = bytearray([0xcc, 0x23, 0x33])
    self.send_packet(self.rgbwhandle, packet)

  def set_rgb(self, red, green, blue):
    self.red = red
    self.green = green
    self.blue = blue
    self.white = 0
    packet = bytearray([0x56, red, green, blue, 0x00, 0xf0, 0xaa])
    self.send_packet(self.rgbwhandle, packet)

  def set_white(self, white):
    self.red = 0
    self.green = 0
    self.blue = 0
    self.white = white
    packet = bytearray([0x56, 0x00, 0x00, 0x00, white, 0x0f, 0xaa])
    self.send_packet(self.rgbwhandle, packet)

  def set_rgbw(self, red, green, blue, white):
    self.red = red
    self.green = green
    self.blue = blue
    self.white = white
    self.send_packet(self.redhandle, bytearray([red]))
    self.send_packet(self.greenhandle, bytearray([green]))
    self.send_packet(self.bluehandle, bytearray([blue]))
    self.send_packet(self.whitehandle, bytearray([white]))

  def get_state(self):
    self.send_packet(self.rgbwhandle, bytearray([0xef, 0x01, 0x77]))
    self.device.waitForNotifications(1.0)

  def get_on(self):
    return self.power

  def get_colour(self):
    return (self.red, self.green, self.blue)

  def get_white(self):
    return self.white
