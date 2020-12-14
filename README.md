# uppaal-py
UPPAAL wrapper for Python. Currently supports reading from and writing to .xml files. Works with Python >= 3.8.

## Dependencies
* [NetworkX](https://github.com/networkx/networkx)

## Installation
Via pip:
```
pip install uppaal-py
```

## Usage
```Python
>>> from uppaalpy import core
>>> my_nta = core.NTA.fromXML('test.xml')
>>> my_nta.to_file('test_new.xml', pretty = True)
```

## License
[MIT](https://mit-license.org/)
