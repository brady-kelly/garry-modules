class RgbColour:
    
    def __init__(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b
        
    def as_hex(self):
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"
    
