#---------------------------------------------------------------------------------------------
# python communication lib to emulate PLC FX2N
# 
# Copyright by Aixi Wang (aixi.wang@hotmail.com)
#---------------------------------------------------------------------------------------------
import serial
import sys,time

CMD_ENQ = 0x05
CMD_ACK = 0x06
CMD_NAK = 0x15
CMD_STX = 0x02
CMD_ETX = 0x03

plc_ram = [0]*64*1024


#-------------------------------
# mypad
#-------------------------------
def mypad(s,n):
    i = len(s)
    if i >= n:
        return s
    else:
        return '0' * (n - i) + s



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
# verify_checksum
#-------------------------
def verify_checksum(data1,checkusm_s):
    print('verify_checksum,',data1,checkusm_s)

    # checksum    
    d5 = 0
    s1 = data1 + '\x03'
    for d in s1:
        d5 += ord(d)
    d5 = (d5) % 256
    
    # convert checksum to ascii string
    s4 = hex(d5).lstrip('0x').upper()
   
    s4 = mypad(s4,2)
    
    if s4 == checkusm_s:
        return 0
    else:
        return -1


#-------------------------
# hexstr_to_int
#-------------------------       
def hexstr_to_int(hex_str):
    if len(hex_str) == 4:
        d1 = hex2int(hex_str[0])
        d2 = hex2int(hex_str[1])
        d3 = hex2int(hex_str[2])
        d4 = hex2int(hex_str[3])
        i = (d1 * 16 + d2)*256 + (d3 * 16 + d4)
        return i

    elif len(hex_str) == 2:
        d1 = hex2int(hex_str[0])
        d2 = hex2int(hex_str[1])
        i = (d1 * 16 + d2)
        return i

    else:
        return -1
#-------------------------
# hexstr_to_intstr
#-------------------------       
def hexstr_to_intstr(hex_str):
    s = ''
    i = 0
    for c in hex_str:
        if (i % 2) == 0:
            d1 = hex2int(c)
        else:
            d2 = hex2int(c)
            s += chr(d1 * 16 + d2)
        i += 1
    return s

#-----------------------------
# encode_device_read_resp_pkg
#-----------------------------       
def encode_device_read_resp_pkg(dat):
    s1 = '\x02'

    for d in dat:
        s1 += mypad(hex(d).lstrip('0x').upper(),2)
    
    s1 += '\x03'

    # checksum    
    d5 = 0
    for d in s1[1:]:
        d5 += ord(d)
    d5 = (d5) % 256

    # convert checksum to ascii string
    s4 = hex(d5).lstrip('0x').upper()

    s4 = mypad(s4,2)

    s1 += s4
    print('s1:',s1)
    return s1

#------------------------------
# encode_device_write_resp_pkg
#------------------------------       
def encode_device_write_resp_pkg():
    resp = '\x06'
    return resp

#---------------------------------
# encode_device_force_on_resp_pkg
#---------------------------------      
def encode_device_force_on_resp_pkg():
    resp = '\x06'
    return resp

#----------------------------------
# encode_device_force_off_resp_pkg
#----------------------------------           
def encode_device_force_off_resp_pkg():    
    resp = '\x06'
    return resp
    
#-------------------------
# do_handle_cmd
#-------------------------    
def do_handle_cmd(data1,s):
    print('do_handle_cmd:',data1)
    
    if data1[0] == '\x30':
        offset = hexstr_to_int(data1[1:5])
        len_n = hexstr_to_int(data1[5:7])
        print('read d offset:',offset,' len_n:',len_n)
        if offset >= 0 and len_n >= 0 and (offset + len_n) < 0x10000:
            s.write(encode_device_read_resp_pkg(plc_ram[offset:offset+len_n]))
        

    elif data1[0] == '\x31':
        offset = hexstr_to_int(data1[1:5])
        len_n = hexstr_to_int(data1[5:7])
        int_str = hexstr_to_intstr(data1[7:])
        
        print('write d offset:',offset,' len_n:',len_n)
        if offset >= 0 and len_n >= 0 and (offset + len_n) < 0x10000:    

            i = 0
            for d in int_str:
                plc_ram[offset + i] = ord(d)
                i += 1
                
            s.write(encode_device_write_resp_pkg())

        
    elif data1[0] == '\x37':
        offset = hexstr_to_int(data1[1:5])
        print('force on offset:',offset)
        plc_ram[offset/8] |= 1 << (offset%8)
        s.write(encode_device_force_on_resp_pkg())
        
    elif data1[0] == '\x38':
        offset = hexstr_to_int(data1[1:5])
        plc_ram[offset/8] &= 0xff - (1 << (offset%8))
        print('force off offset:',offset)
        s.write(encode_device_force_off_resp_pkg())
        
        
    else:
        return -1;


#-------------------------
# main
#-------------------------
if __name__ == '__main__':

    
    statemachine = 0
    while True:
        try:
        #if 1:
            serialport_path = sys.argv[1]
            print 'COM port:', serialport_path
            s = serial.Serial(serialport_path, baudrate=9600, bytesize=7,parity=serial.PARITY_EVEN,stopbits=1,timeout=0.1,xonxoff=0, rtscts=0)
            #print s
            print 'listening ...'

            #off = 0x080
            # it's state machine
            # 
            
            data1 = ''
            checksum = 0
            chksum_s = ''
            while True:
                c = s.read(1)
          
                
                if len(c) == 1:
                    #print('->',c,statemachine)
                    # response
                    if ord(c) == CMD_ENQ:
                        s.write('\x06')    
                        statemachine = 0

                    if statemachine == 0:           
                        # start
                        if ord(c) == CMD_STX:
                            statemachine = 1
                            data1 = ''

                    elif statemachine == 1:
                        # start
                        if ord(c) == CMD_STX:
                            statemachine = 1
                            
                        # end
                        elif ord(c) == CMD_ETX:
                            statemachine = 3
                        
                        
                        elif (ord(c) >= 0x30 and ord(c) <= 0x39) or (ord(c) >= 0x41 and ord(c) <= 0x46):
                            data1 += c
                            statemachine = 2
                        
                        
                        else:
                            statemachine = 0
                            
                            
                    
                    elif statemachine == 2:
                        # start
                        if ord(c) == CMD_STX:
                            statemachine = 1
                            
                        # end
                        elif ord(c) == CMD_ETX:
                            chksum_s = ''
                            statemachine = 3
                            
                        elif (ord(c) >= 0x30 and ord(c) <= 0x39) or (ord(c) >= 0x41 and ord(c) <= 0x46):
                            data1 += c

                    elif statemachine == 3:
                        # start
                        if ord(c) == CMD_STX:
                            statemachine = 1
                            
                        # end
                            
                        elif (ord(c) >= 0x30 and ord(c) <= 0x39) or (ord(c) >= 0x41 and ord(c) <= 0x46):
                            chksum_s += c
                            statemachine = 4
                            
                    elif statemachine == 4:
                        # start
                        if ord(c) == CMD_STX:
                            statemachine = 1
                            
                        # end
                            
                        elif (ord(c) >= 0x30 and ord(c) <= 0x39) or (ord(c) >= 0x41 and ord(c) <= 0x46):
                            chksum_s += c
                            print('--------------------------------------')
                            if verify_checksum(data1,chksum_s) == 0:
                                do_handle_cmd(data1,s)
                                
                            statemachine = 0
                        else:
                            statemachine = 0
                    
                    else:
                        statemachine = 0
                else:
                    #time.sleep(0.1)
                    pass                
                    #s.write(encoded_tx)

            
        except Exception as e:
            #print 'init serial error!'
            #sys.exit(-1)
            print('exception:',str(e))
            time.sleep(1)
            pass
            
        
