lvpyioTools Documentation
=========================

A collection of tools to manipulate lvpyio objects such as Sets.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Installation
------------

.. code-block:: bash

   pip install .

Quick Start
-----------

.. code-block:: python

   from pathlib import Path
   from lvpyioTools.set import LVSet

   set_file = Path("path/to/your/set.set")
   with LVSet(set_file) as lv_set:
       print(lv_set)
       print(f"Number of frames: {len(lv_set)}")
       print(f"Properties: {lv_set.properties}")

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.

GitHub
------

Repository: `github.com/SimKDT/lvpyio-tools <https://github.com/SimKDT/lvpyio-tools>`_
