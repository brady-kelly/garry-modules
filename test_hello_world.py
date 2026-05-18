from hello_world import print_hello_world

def test_print_hello_world(capsys):
    print_hello_world()
    captured = capsys.readouterr()
    assert captured.out == "Hello...\n"