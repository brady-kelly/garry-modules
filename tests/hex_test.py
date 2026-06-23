from strings.rgb_colour import RgbColour


def test_purple():
    purp = RgbColour(130, 4, 124)
    phex = purp.as_hex()
    assert phex == "#82047C"