# lvpyio-tools
A collection of tools to manipulate lvpyio objects such as Sets.

## Installation

```bash
pip install .
```

## Usage

```python
from pathlib import Path
from lvpyioTools.set import LVSet

set_file = Path("path/to/your/set.set")
with LVSet(set_file) as lv_set:
    print(lv_set)
    print(f"Number of frames: {len(lv_set)}")
    print(f"Properties: {lv_set.properties}")
```

## Doc (build)
```bash
make html
```

Serving the documentation locally:
```bash
make serve
```

## License
See [LICENSE](LICENSE) for details.