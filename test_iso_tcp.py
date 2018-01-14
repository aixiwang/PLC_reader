#!/usr/bin/env python
# -*- coding: utf-8 -*-
from libnodave import *

h = libnodave()
#h.open_socket('192.168.1.10')
h.open_socket('115.29.178.81',port=20002)
h.new_interface('IF1',0, daveProtoISOTCP, daveSpeed187k)
h.set_timeout(5000000)
ret = h.connect_plc(2,0,2)
if ret == 0:
    print 'connected'
else:
    print 'unconnected'


#if h.read_bytes(daveFlags,0,0,16):
#   print 'read 16 bytes ok'
#else:
#   print 'read 16 bytes fail'


#h.outputs()
#h.inputs()
#print h.get_marker_byte(0)
#print h.get_counters()

print 'output:',h.outputs2()
print 'input:',h.inputs2()




