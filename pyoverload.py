import inspect

class FuncList(list):
    """
    a list (of callables), that is supposed to be used as a descriptor.
    __get__ returns a callable, that when called with arguments will return the return value of the first element of self
    with a compatible signature and annotations.
    See help(OverloadedMethods)
    """

    def __get__(self, instance, owner):
        """
        return a callable, curry 'instance' as the first argument
        the callable will then take any arguments and try to figure which element of self to dispatch work to
        """

        def dispatch(instance, *args, **kwargs):
            for fun in self:
                sig = inspect.signature(fun)
                try:
                    # check if signatures match - number and names of arguments work
                    bound = sig.bind(instance, *args, **kwargs)
                    bound_with_annotation = {
                        arg: [bound.arguments[arg], sig.parameters[arg].annotation]
                        for arg in bound.arguments.keys()
                    }

                    try:
                        # see if annotations are used, if so use them to convert arguments to the expected type
                        for arg, (value, annotation) in bound_with_annotation.items():
                            if (callable(annotation)
                                    and not annotation is inspect.Signature.empty):

                                bound.arguments[args] = annotation(value)
                        # found a proper match!
                        return fun(*bound.args, **bound.kwargs)
                    except ValueError as e:
                        # annotations used, argument types mismatch - try the next function
                        pass

                except TypeError as e:
                    # signatures don't match - try the next function
                    pass

            raise ValueError(
                "no method found to handle passed arguments {} {} {}\n{}".format(
                    instance, args, kwargs,
                    "\n".join(str(inspect.signature(fun)) for fun in self)
                )
            )

        return dispatch.__get__(instance, owner) # curry in instance as self, make 'dispatch' work like a proper method

class CollectFuns(dict):
    """
    a Dictionary that will behave normally for values that are not callable,
    and collect multiple callable values for the same key in a FuncList, instead of overwriting previous values
    does not work for mixtures of callable / non-callables for the same key
    """

    def __setitem__(self, key, val):
        if callable(val):
            if key not in self:
                super().__setitem__(key, FuncList())
            self[key].append(val)
        else:
            super().__setitem__(key, val)


class OverloadedMethods(type):
    """
    enables overloaded Methods

    checks if signatures match arguments and optionally calls a parameter's annotation on an argument.
    That is, annotations have to be callable,
    if an annotation supplied, its return value is passed as an argument to the function

    def identity(self, x: int):
        return x

    assert identity("1") == 1
    """

    @staticmethod
    def __prepare__(name, bases, **kwargs):
        return CollectFuns()
