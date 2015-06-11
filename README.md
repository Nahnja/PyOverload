# PyOverload
metaclass that allows overloaded methods for classes.

This shouldn't be used for anything serious. I just wanted to see how I could make something like this work.

Allows overloaded methods, based on number of arguments and optionally on argument types. Method signatures are checked for a match in the order the methods are defined.

example:

    class Foo(metaclass=OverloadedMethods):
        def add(self, x: int, y: int):
            return x + y

        def add(self, x: float, y: str):
            return str(x) + y

        def add(self, iterable):
            return sum(iterable)

produces

    3
    1b
    6
    ---------------------------------------------------------------------------
    [...]
    ValueError: no method found to handle passed arguments <__main__.Foo object at 0x105490cf8> ('b', 'a') {}
    (self, x:int, y:int)
    (self, x:float, y:str)
    (self, iterable)
