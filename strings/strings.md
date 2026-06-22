## Strings

### String Literals

Strings in Python are sequences of unicode characters, and are handled with objects of the [str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) class. String literals are written using matching pairs of single quotes, double quotes, or *triple quotes*. These are sets of three single quotes or three double quotes.
```py
sm1 = '''their-string'''
sm2 = """your-string"""
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
    def __init__(self, first, last) -> None:
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

Have a look at the `Person` class in `strings/person.py`, not the `BadPerson` class in this file, and try to complete the `get_full_name` method to return the full name. Use the `+` operator and a single space separator, like `__init__` in the example above does when setting the `full_name` property, and use `return` with that value. You can remove the `pass` statement as that is a placeholder that does nothing. The code will work with it there, but it's usually used to mark a TODO, so leaving it is untidy.

Run the tests by using the following command in the build in terminal:
```ps
pytest strings/
```

You can also use the `join` method to combine strings, but it's less intuitive for simple strings, and better for lists, as it's called on the separator, so for a full name with a space, you call in on the space and pass it the two names:
```py
full_name = " ".join(first, last)
```


