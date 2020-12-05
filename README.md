# uppaal-py
UPPAAL wrapper for Python. Currently supports reading from and writing to .xml files. Works with Python >= 3.8.

## Dependencies
* [NetworkX](https://github.com/networkx/networkx)

## Installation
Via pip:
```
pip install uppaal-py
```

Or you can just install the dependencies and copy the dir `uppaalpy` into your project.

## Usage
```Python
>>> from uppaalpy import nta
>>> my_nta = nta.NTA.fromXML('test.xml')
>>> my_nta.to_file('test_new.xml', pretty = True)
```

## License
[MIT](https://mit-license.org/)
