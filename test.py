from unittest.mock import patch
import io
from hello_world import print_hello_world

def test_output():
    # Capture everything printed to the terminal
    with patch('sys.stdout', new=io.StringIO()) as fake_out:
        print_hello_world()
        output = fake_out.getvalue()
        
    # Check the result and print exactly one simple message
    if output == "Hello...\n":
        print("🟢 TEST PASSED")
    else:
        print("🔴 TEST FAILED")

if __name__ == "__main__":
    test_output()
