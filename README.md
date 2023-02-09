# lazy_objects

## Presentation

`lazy_objects` is a simple library that allows you to create lazy objects in Python. It provides four main helpers for 
both lazy computation and lazy code writing:

- Lazy computation
    - `LazyObject`: An object which attributes will be evaluated only when accessed and computed only once.
    - `lazy_property`: A decorator which lazyfies properties.

- Lazy writing:
    - `lazy_attributer`: A parameterized class decorator which allows for one liner attributes.
    - `lazy_init`: A decorator for `__init__` methods which automatically creates object attributes.

For more information, have a look at the docstrings.

## Installation

Installation requires no external dependancies.

```bash
python -m pip install git+'https://github.com/sven-nm/lazy_objects'
```

## Let's chat !

Any improvements, suggestions and ideas are welcome !