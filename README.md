# lvpyio-tools

[![License](https://img.shields.io/github/license/SimKDT/lvpyio-tools?label=License)](LICENSE)
![Code Size](https://img.shields.io/github/languages/code-size/SimKDT/lvpyio-tools?label=Code%20Size)
[![PyPi Version](https://img.shields.io/pypi/v/lvpyioTools)](https://pypi.org/project/lvpyioTools/)
[![Documentation](https://img.shields.io/badge/docs-blue?label=sphinx&logo=sphinx&logoColor=white)](https://simkdt.github.io/lvpyio-tools/)

A collection of helper tools to manipulate lvpyio objects such as Sets by using the [lvpyio](https://pypi.org/project/lvpyio/) library.

## Installation

<details open>
<summary>PyPi</summary>

```bash
pip install lvpyioTools
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

You can find the API documentation in [https://simkdt.github.io/lvpyio-tools/](https://simkdt.github.io/lvpyio-tools/).

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