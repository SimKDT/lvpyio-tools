# lvpyio-tools

![License](https://img.shields.io/github/license/SimKDT/lvpyio-tools?label=License)
![Downloads](https://img.shields.io/github/downloads/SimKDT/lvpyio-tools/total?label=Downloads)
![Code Size](https://img.shields.io/github/languages/code-size/SimKDT/lvpyio-tools?label=Code%20Size)
![PyPi Version](https://img.shields.io/pypi/v/lvpyioTools)

A collection of tools to manipulate lvpyio objects such as Sets.

## Installation

<details open>
<summary>PyPi</summary>

```bash
pip install lvpyio-tools
```
</details>

<details>
<summary>Git</summary>

```bash
pip install git+https://github.com/SimKDT/lvpyio-tools.git
```
</details>

<details>
<summary>Local</summary>

```bash
pip install .
```
</details>

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