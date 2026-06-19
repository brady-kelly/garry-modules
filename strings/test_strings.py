from rgb_colour import RgbColour

def test_rgb_ctor():
    
    purp = RgbColour(129, 2, 127)
    assert purp.red == 129
    assert purp.green == 2
    assert purp.blue == 127
    