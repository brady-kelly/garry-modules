## Strings

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

You create a string object by assigning a literal to a variable or calling a function that returns a string, or through the `str` constructor, like this:
```py
age_num = 35
age_str = str(35)
```





