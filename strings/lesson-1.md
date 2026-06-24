## Strings

### String Literals

Strings in Python are sequences of unicode characters, and are handled with objects of the [str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) class. String literals are written using matching pairs of single quotes, double quotes, or *triple quotes*. These are sets of three single quotes or three double quotes.
```py
single = 'a string'
double = "another"
ts = '''their-string'''
td = """your-string"""
```
This triple-quoted arrangement allows you to include literal line breaks, and other quotes, in strings:
```py
lg = """
These allow "Quotes" inside quotes, and
 Multiple lines,
 and 'more' quotes too!
"""
```

### String Objects

You create a string object by:
- assigning a literal to a variable
- calling a function that returns a string
- calling the `str` constructor:

#### Examples:

```py
def full_name(first, last):
    return first + " " + last

# Assign a literal
first = "Donald"

# Call a function that returns a string
full = full_name(first, "Duck")

# Call the constructor
age_str = str(35)
```

### Strings in Classes

You create string attributes in classes by assigning string values to variables on an instance, using the special `self` variable, in the constructor, i.e. the `__init__` method:

```py
class BadPerson:    
    def __init__(self, first, last):
        self.first_name = first
        self.last_name = last    
        self.full_name = first + " " + last

mick = BadPerson("Mickey", "Mouse")
```
However, storing the full name like this is redundant, and one or two other kinds of bad. Say you want to allow for the correction of capturing errors, like this:
```py
mick = BadPerson("Mickey", "Moose")
# Oops! Fix that.
mick.last_name = "Mouse"
print(mick.full_name)
```
```
Mickey Moose
```
The full name is still stuck with the uncorrected last name.

### Joining Strings

#### Exercise 1

Have a look at the `Person` class in `strings/person.py`, not the `BadPerson` class in this file, and try to complete the `get_full_name` method to return the full name. Use the `+` operator and a single space separator, like `__init__` in the example above does when setting the `full_name` property, and use `return` with that value. You can remove the `pass` statement as that is a placeholder that does nothing. The code will work with it there, but it's usually used to mark a TODO, so leaving it is untidy.

Run the tests by using the following command in the build in terminal:
```ps
pytest strings/
```

You can also use the `join` method to combine strings, but it's less intuitive for simple strings, and better for lists, as it's called on the separator, so for a full name with a space, you call it on the space and pass it the two names:
```py
full_name = " ".join(first, last)
```
It looks better for e.g. CSV strings, e.g:
```py
csv = ",".join(col1, col2, col3, col4)
```
### Splitting Strings

If you are only passed a person's full name, you will want to split it using the `split` method, like this:
```py
full_name = "Donald Duck"
parts = full_name.split()
first = parts[0]
last = parts[-1]
```
Note that using `[-1]` will always return the last element, regardless of how long the sequence is, where using `[1]` would depend on there being at least two elements, and the last name being the second element. So the split shown above will also be correct even for a full name of `Donald Mac Duck`.

Unfortunately Python classes may only have one constructor function, so you can't have one for first and last names and another one that splits a full name onto these two properties. I will cover ways to do this on more practical classes later.

### Indexing Strings
The above example for splitting also shows string indexing. Like all sequences, strings can be indexed starting with `0` up to one less than the string length, so:
```py
first = "Mickey"
letter_m = first[0]
letter_y = first[5]
```

#### Exercise 2

Have another look at the `Person` class in `strings/person.py`, and try to complete the `get_initials` method to return the initials of a person, i.e. the first character of each name followed by a period, e.g:
```py
bill = Person("Bill", "Smith")
inits = bill.get_initials()
print(inits)
```
Should print
```
B.S.
```

Run the tests by using the following command in the build in terminal:
```ps
pytest tests/person_tests.py
```

### Formatting Strings
Calling the `format` method on a string replaces all *replacement fields* in the string with the values passed to the `format` method. A replacement field can be the index of a positional argument passed to `format`, with `0` being the first argument, `1` the next, etc:
```py
print("Superman is: {1} {0}".format("Kent", "Clark"))
```
A replacement field can also be the name of one of the keyword arguments passed to `format`:
```py
print("Superman is: {first} {last}".format(last="Kent", first="Clark"))
```
To format integer values as hex strings, add the hex format specifier to a replacement field:
```py
print("Number as hex is: {num:02X}".format(num=13))
```
The `X` says `num` must be formatted as hex, the `2` says the result must always be padded up to 2 characters, and the `0` says to use a zero for padding, where the default padding character is a space.

#### f-strings
The f-string is a shortcut way of formatting strings. Prepending `f` before a string literal causes the interpreter to format it using values specified directly inside the replacement fields:
```py
num=13
print(f"Number as hex is: {num:02X}")
```

#### Exercise 3
Have a look at the `RgbColour` class in `strings/rgb_colour.py`. Try and complete the `as_hex` method to return a string that starts with a hash, `#`, followed by the 2 character, upper case, hex strings for each of the red, the green, and the blue variables of an instance. 

Check the results of this method by running the script in `strings/run_hex.py`

Test your method by running this test:
```ps
pytest tests/hex_test.py
```
