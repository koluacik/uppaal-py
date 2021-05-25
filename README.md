# uppaal-py
Python library for reading, writing, analyzing, and modifying UPPAAL timed automata files. Works with Python >= 3.8.

## Disclaimer
uppaal-py is a work-in-progress library. For bugs, missing features or documentation please create an issue or send me an email. API is subject to change.

## Dependencies
* [lxml](https://lxml.de/)
* [NetworkX](https://github.com/networkx/networkx)
* [ortools](https://developers.google.com/optimization)

## Installation
Via pip:
```
pip install uppaal-py
```

## License
[MIT](https://mit-license.org/)

## Features
- Reading and writing UPPAAL files.
- LP based path realizability analysis.
- Working with variables of type `int` and a subset of expressions involving `ints` for guards, invariants, and updates during transitions allowed in UPPAAL in addition to clocks during computations.

## TODO:
- [ ] Methods for calling UPPAAL/verifyta.
- [ ] Migrate to [libutap](https://github.com/MASKOR/libutap) for parsing files.
- [ ] Parameter synthesis for safety property.
- [ ] [lxml type annotations](https://github.com/lxml/lxml-stubs) and type annotations for the remaining functions.
- [ ] Auto-generated documentation.

## Non-features
- Analysis involving network of TA — product of two or more TA can be implemented in the future, though.
- Symbolic model checking, UPPAAL does that.
