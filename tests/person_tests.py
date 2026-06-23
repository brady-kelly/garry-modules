
from strings.person import Person

def test_person_two_names():
    pers = Person("Mickey", "Moose")
    assert pers.first_name == "Mickey"
    assert pers.last_name == "Moose"

def test_person_full_name():
    pers = Person("Mickey", "Moose")
    assert pers.get_full_name() == "Mickey Moose"
    pers.last_name = "Mouse"
    assert pers.get_full_name() == "Mickey Mouse"


def test_person_initials():
    man = Person("Spider", "Man")
    assert man.get_initials() == "S.M."    