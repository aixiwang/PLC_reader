import libnodave

nodave = libnodave()
nodave.set_port('COM2')   
nodave.new_interface(self, 'IF1', 0, daveProtoPPI, daveSpeed187k)
nodave.connect_plc(2, 0, 0)
nodave.read_bytes(self, daveFlags, 0, 0, 16)

