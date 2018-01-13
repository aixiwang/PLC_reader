#---------------------------------------------------------------------------------------------
# python lib to read/write PLC FX series from programmer port
# 
# Copyright by Aixi Wang (aixi.wang@hotmail.com)
# Contact me for commercial application
#---------------------------------------------------------------------------------------------
import serial
import sys,time

CMD_ENQ = 0x05
CMD_ACK = 0x06
CMD_NAK = 0x15
CMD_STX = 0x02
CMD_ETX = 0x03
#-------------------------------
# encode_device_read_pkg
#   offset: PLC data offset
#   lens: bytes
#   debug: debug flag
#------------------------------- 
def encode_device_read_pkg(offset,lens,debug = 0):
    if offset > 65535:
        return -1,''
    if lens > 64:
        return -2,''
       
    s1 = '\x02\x30'
    
    # add offset string
    s2 = hex(offset).lstrip('0x').upper()

    if len(s2) == 1:
        s2 = '000' + s2
        
    if len(s2) == 2:
        s2 = '00' + s2

    if len(s2) == 3:
        s2 = '0' + s2
        
    s1 += s2
    
    # add lens string
    s2 = hex(lens).lstrip('0x').upper()
    if len(s2) == 1:
        s2 = '0' + s2

    s1 += s2
    
    s3 = '\x03'
    s1 += s3
    
    d5 = 0
    for d in s1[1:]:
        d5 += ord(d)
    d5 = (d5) % 256
    
    # convert checksum to ascii string
    s4 = hex(d5).lstrip('0x').upper()

    if len(s4) == 1:
        s4 = '0' + s4
    s1 += s4
    if debug == 1:
        print 's1 hex:',s1.encode('hex')    

    return 0,s1

#-------------------------
# hex2int
#-------------------------     
def hex2int(c):
    if ord(c) >= ord('0') and ord(c) <= ord('9'):
        d = ord(c) - ord('0')

    else:
        d = ord(c) - ord('A') + 0x0a
    return d
        
#-------------------------
# decode_device_read_pkg
#------------------------- 
def decode_device_read_pkg(dat,debug = 0):
    lens = len(dat)
    bytes = (lens - 4)/2
    hex_str = dat[1:lens-3]
    if debug == 1:
        print 'hex_str:',hex_str
    s = ''
    i = 0
    if dat[0:1] == '\x02':
        for c in hex_str:
            if (i % 2) == 0:
                d1 = hex2int(c)
            else:
                d2 = hex2int(c)
                s += chr(d1 * 16 + d2)
            i += 1
        return 0,s
    else:
        if debug == 1:
            print 'error, decoded data hex:',dat.encode('hex')
        return -1,''


#-------------------------
# main
#-------------------------
if __name__ == '__main__':

    #try:

    if 1:
        serialport_path = sys.argv[1]
        print 'COM port:', serialport_path
        s = serial.Serial(serialport_path, baudrate=9600, bytesize=8,parity=serial.PARITY_NONE,stopbits=1,timeout=0.1,xonxoff=0, rtscts=0)
        #print s
        print 'start to test...'

        off = 0x080
        while True:        
            # d123
            retcode,encoded_tx = encode_device_read_pkg(off,2,1)
            #off += 1
            s.write(encoded_tx)
            time.sleep(0.1)
            encoded_rx = s.read(1024)
            print '<======== encoded_rx(hex):',encoded_rx.encode('hex')
            # test decode
            # 02 33 35 38 34 03 44 36
            #s = '\x02\x33\x35\x38\x34\x03\x44\x36'
            if retcode == 0:
                retcode, return_bytes = decode_device_read_pkg(encoded_rx)
                if retcode == 0:
                    # do something
                    print 'read test ok =>',return_bytes.encode('hex')
                else:
                    print 'read test fail.','recode:',retcode,'return bytes:',return_bytes.encode('hex')
            else:
                print 'read failed'
            time.sleep(1)
        
    #except:
        #print 'init serial error!'
        #sys.exit(-1)
        
    
