# Python module for control of Colorific bluetooth LED bulbs
#
# Copyright 2016 Matthew Garrett <mjg59@srcf.ucam.org>
#
# This code is released under the terms of the MIT license. See the LICENSE file
# for more details.

import BDAddr
from BluetoothSocket import BluetoothSocket, hci_devba
import random
import socket
import sys
import time

def get_handles(sock):
  start = 1
  handles = {}
  while True:
    response = []
    data = bytearray([0x00])
    startlow = start & 0xff
    starthigh = (start >> 8) & 0xff
    packet = bytearray([0x08, startlow, starthigh, 0xff, 0xff, 0x03, 0x28])
    sock.send(packet)
    data = sock.recv(32)
    for d in data:
      response.append(ord(d))
    if response[0] == 1:
      return handles
    position = 2
    while position < len(data):
      handle = response[position+3] | (response[position+4] << 8)
      handle_id = response[position+5] | (response[position+6] << 8)
      handles[handle_id] = handle
      if handle > start:
        start = handle + 1
      position += 7

def send_packet(sock, handle, data):
  packet = bytearray([0x12, handle, 0x00])
  for item in data:
    packet.append(item)
  sock.send(packet)
  data = sock.recv(32)
  response = []
  for d in data:
    response.append(ord(d))
  return response

def checksum(data):
    value = 0
    for i in range(1, len(data)-2):
        value = value + data[i]
    value = value + 85
    return value & 0xff

def read_packet(sock, handle):
  packet = bytearray([0x0a, handle, 0x00])
  sock.send(packet)
  data = sock.recv(32)
  response = []
  for d in data:
    response.append(ord(d))
  return response

class zengge:
  def __init__(self, mac):
    self.mac = mac
  def connect(self):
    my_addr = hci_devba(0) # get from HCI0
    dest = BDAddr.BDAddr(self.mac)
    addr_type = BDAddr.TYPE_LE_PUBLIC
    self.sock = BluetoothSocket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
    self.sock.bind_l2(0, my_addr, cid=4, addr_type=BDAddr.TYPE_LE_RANDOM)
    self.sock.connect_l2(0, dest, cid=4, addr_type=addr_type)
    
    handles = get_handles(self.sock)
    self.statehandle = handles[0xffe4]
    self.redhandle = handles[0xffe6]
    self.greenhandle = handles[0xffe7]
    self.bluehandle = handles[0xffe8]
    self.whitehandle = handles[0xffea]
    self.rgbwhandle = handles[0xffe9]

    state = self.get_state()
    print state
    self.mode = state[8]
    self.red = state[9]
    self.green = state[10]
    self.blue = state[11]
    self.white = state[12]
    if self.mode > 2:
      self.power = True
    else:
      self.power = False

  def off(self):
    self.power = False
    packet = bytearray([0xcc, 0x24, 0x33])
    send_packet(self.sock, self.rgbwhandle, packet)

  def on(self):
    self.power = True
    packet = bytearray([0xcc, 0x23, 0x33])
    send_packet(self.sock, self.rgbwhandle, packet)

  def set_rgb(self, red, green, blue):
    self.red = red
    self.green = green
    self.blue = blue
    self.white = 0
    packet = bytearray([0x56, red, green, blue, 0x00, 0xf0, 0xaa])
    send_packet(self.sock, self.rgbwhandle, packet)

  def set_white(self, white):
    self.red = 0
    self.green = 0
    self.blue = 0
    self.white = white
    packet = bytearray([0x56, 0x00, 0x00, 0x00, white, 0x0f, 0xaa])
    send_packet(self.sock, self.rgbwhandle, packet)

  def set_rgbw(self, red, green, blue, white):
    self.red = red
    self.green = green
    self.blue = blue
    self.white = white
    send_packet(self.sock, self.redhandle, bytearray([red]))
    send_packet(self.sock, self.greenhandle, bytearray([green]))
    send_packet(self.sock, self.bluehandle, bytearray([blue]))
    send_packet(self.sock, self.whitehandle, bytearray([white]))

  def get_state(self):
    return send_packet(self.sock, self.rgbwhandle, bytearray([0xef, 0x01, 0x77]))

  def get_on(self):
    return self.power

  def get_colour(self):
    return (self.red, self.green, self.blue)

  def get_white(self):
    return self.white
