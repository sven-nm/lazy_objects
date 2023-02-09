import inspect
from functools import wraps
from typing import Callable, Optional, List


def lazy_property(func):
    """Decorator. Makes property computation lazy by keeping a cache of the result.

    `lazy_property` keeps object instanciations light and swift by computing and storing properties only when they are called.

    Example:
        >>> @lazy_property
        ... def bar(self):
        ...     return [1, 2, 3]

        is equivalent to:

        >>> @property
        ... def bar(self):
        ...     if not hasattr(self, '_bar'):
        ...         self._bar = [1, 2, 3]
        ...     return self._bar

    Args:
        func (Callable): The function to decorate.

    Returns:
        property: The decorated function.
    """

    private_attr = '_' + func.__name__

    @wraps(func)
    def fget(self):
        if not hasattr(self, private_attr):
            setattr(self, private_attr, func(self))
        return getattr(self, private_attr)

    def fset(self, value):
        setattr(self, private_attr, value)

    def fdel(self):
        if hasattr(self, private_attr):
            delattr(self, private_attr)

    return property(fget, fset, fdel, func.__doc__)


def lazy_init(func):
    """Decorates a object's constructor, creating object attributes named after the constructor's arguments.

    Note:
    `lazy_init` creates and names attributes after the  for required arguments and defaulted keyword argument if they are not None
    at instantiation time. Warning, this does not handle `*args`.

    Example:
        >>> @lazy_init
        ... def __init__(self, hello, bonjour, world = None):
        ...    pass

        is actually equivalent to :

        >>> def __init__(self, hello, bonjour, world = None):
        ...    self.hello = hello
        ...    self.bonjour = bonjour
        ...    if world is not None:
        ...        self.world = world


    Args:
        func (Callable): The constructor function to decorate.

    Returns:
        Callable: The decorated function.

    """
    specs = inspect.getfullargspec(func)
    assert specs.varargs is None, "`lazy_init` does not handle *args"

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        defaults_args_len = len(specs.defaults) if specs.defaults else 0
        required_args_len = len(specs.args) - defaults_args_len
        required_args_names = specs.args[1:required_args_len]
        defaults_args_names = specs.args[required_args_len:]

        # Start with required args
        required_from_args = [(name, value) for name, value in zip(required_args_names, args)]
        required_from_kwargs = [(name, value) for name, value in kwargs.items() if name in required_args_names]
        for name, value in required_from_args + required_from_kwargs:
            setattr(self, name, value)

        # For defaulted args and potential **kwargs, only add if not None
        def_from_args = [(n, v) for n, v in zip(defaults_args_names, args[required_args_len:])]
        def_from_kwargs = [(n, v) for n, v in kwargs.items() if n in defaults_args_names]
        for name, value in def_from_args + def_from_kwargs:
            setattr(self, name, value)

        # Add potential **kwargs
        for name, value in kwargs.items():
            if name not in required_args_names + defaults_args_names:
                setattr(self, name, value)

        func(self, *args, **kwargs)

    return wrapper


def lazy_attributer(attr_name: str, func: Callable, attr_decorator: Callable = lambda x: x):
    """Parametrized decorator returning a class decorator which adds the attribute of
    name `attr_name` and of value `func` to the `class_` it decorizes.

    Example:
        >>> @lazy_attributer('greeting', lambda self: f'Bonjour {self.name}', property)
        ... class Student:
        ...    pass

        is actually equivalent to :

        >>> class Student:
        ...    @property
        ...    def greeting(self):
        ...        return f'Bonjour {self.name}'

    Args:
        attr_name (str): The name of the attribute to add.
        func (Callable): The function to call to compute the attribute.
        attr_decorator (Callable): The decorator to apply to the attribute. Defaults to `lambda x: x` (identity).

    Returns:
        Callable: The decorated function.
    """

    def set_attribute(class_):
        setattr(class_, attr_name, attr_decorator(func))
        return class_

    return set_attribute


class LazyObject:
    """An object that computes attributes lazily using `compute_function`.

    The set of possible attributes is infinite by default, but can be constrained by setting `constrained_attrs`.
    Otherwise, any called attribute will be created and computing on the fly.

    Example:
        >>> my_lazy_object = LazyObject(lambda attr_name: attr_name + ' has been computed')
        >>> my_lazy_object.hello
        'hello has been computed'
        >>> my_lazy_object.another_greeting_word
        'another_greeting_word has been computed'
    """

    @lazy_init
    def __init__(self,
                 compute_function: Callable,
                 constrained_attrs: Optional[List[str]] = None,
                 **kwargs):
        """Initializes the object.

        Args:
            compute_function: The function to call to compute the attributes.
            constrained_attrs: Constrains the list of possible attributes. The given attributes will be the only one itered upon.
             If `None`, any attribute can be computed.
            **kwargs: Pass kwargs to manually set attributes.
        """
        pass

    def __getattr__(self, attribute):
        if attribute not in self.__dict__:
            if self.constrained_attrs is None or attribute in self.constrained_attrs:  # If constrained, only compute if in constrained attrs
                self.__dict__[attribute] = self.compute_function(attribute)  # Compute and set attribute lazily
            else:
                raise AttributeError(
                        f"""Attribute {attribute} is not in the list of allowed attributes: {self.constrained_attrs}""")
        return self.__dict__[attribute]

    def __dir__(self):
        return ['compute_function',
                'constrained_attrs'] + self.constrained_attrs if self.constrained_attrs is not None else []

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

    def __iter__(self):
        if self.constrained_attrs is None:
            raise TypeError(
                    f'You are trying to iterate on a {self.__class__.__name__} but the attributes to iter upon are not defined (self.constrained_attrs is None).')
        else:
            for attr in self.constrained_attrs:
                yield attr, getattr(self, attr)
