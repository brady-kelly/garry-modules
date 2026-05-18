def print_hello_world():
    print("Hello...")
    
def test_print_hello_world(capsys):
    print_hello_world()
    captured = capsys.readouterr()
    assert captured.out == "Hello...\n"