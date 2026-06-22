from rgb_colour import RgbColour
from person import Person

def test_person_two_names():
    pers = Person("Mickey", "Moose")
    assert pers.first_name == "Mickey"
    assert pers.last_name == "Moose"

def test_person_full_name():
    pers = Person("Mickey", "Moose")
    assert pers.get_full_name() == "Mickey Moose"
    pers.last_name = "Mouse"
    assert pers.get_full_name() == "Mickey Mouse"

# def test_rgb_ctor():    
#     purp = RgbColour(129, 2, 127)
#     assert purp.red == 129
#     assert purp.green == 2
#     assert purp.blue == 127
    