from lazy_objects.lazy_objects import lazy_init, lazy_property, lazy_attributer, LazyObject


def test_lazy_property():
    class Foo:
        def __init__(self):
            pass

        @lazy_property
        def bar(self):
            """A list of ints."""
            return [1, 2, 3]

    a = Foo()

    assert a.bar == a._bar == [1, 2, 3]

    a.bar = [4, 5, 6]
    assert a.bar == [4, 5, 6]
    assert a._bar == [4, 5, 6]

    del a.bar
    assert a.bar == a._bar == [1, 2, 3]
    assert Foo.bar.__doc__.startswith('A list of ints.')


def test_lazy_init():
    class Foo:
        @lazy_init
        def __init__(self, a: int, b: int = 3, **kwargs):
            pass

    a = Foo(1, b=2, c=4)
    assert a.a == 1
    assert a.b == 2
    assert a.c == 4


def test_lazy_attributer():
    @lazy_attributer(attr_name='bar', func=lambda self: self.a + 4, attr_decorator=property)
    class Foo:
        def __init__(self, a: int):
            self.a = a

    a = Foo(1)
    assert a.bar == 5


def test_lazyobject():
    a = LazyObject(compute_function=lambda x: len(x), constrained_attrs=['a', 'bcd'])
    assert a.bcd == 3
