from machine import I2C, Pin
from micropython import const

class I2CPeripheral:
    """
    Slim class intended to be subclassed by I2C device drivers
    """
    default_address: int = const(0)
    
    def __init__(self, bus: I2C = None, address: int = None, *args, **kwargs):
        self.bus = bus if bus is not None and type(bus) is I2C else I2C(0)
        self.address = address if address is not None else self.default_address
        self.init(*args, **kwargs)
        
    def init(self, *args, **kwargs):
        return
    
    def _read(self, count: int = 1):
        return self.bus.readfrom(self.address, count)
    
    def _readfrom(self, mem_address: int, count: int = 1):
        return self.bus.readfrom_mem(self.address, mem_address, count)
        
    def _write(self, buf: bytes):
        """
        Private method contains the actual write implementation
        in order to ensure writes start with is_connected.
        """
        if type(buf) is not bytes:
            if type(buf) is int:
                buf = [buf]
            buf = bytes(buf)
        try:
            return self.bus.writeto(self.address, buf)
        except OSError as e:
            print("OSError when writing %s: %s" % (buf, e))
            return False


