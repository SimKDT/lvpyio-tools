Set files
=========


Structure
---------

Take the following example file structure for an experiment (``.exp`` files):

.. code-block:: bash

    experiment/
    ├── Properties/
    │   ├── Calibration/
    │   │   ├── camera1/
    │   │   │   ├── B00001.im7
    │   │   │   └── ...
    │   │   └── camera1.set
    │   ├── Calibration History/
    │   │   └── ...
    │   ├── Calibration.set
    │   └── Calibration History.set
    ├── Properties.set
    ├── recording/
    │   ├── treatment/
    │   │   └── ...
    │   ├── treatment.set
    │   ├── Camera1.cine
    │   └── ...
    └── recording.set
    experiment.exp

lvpyioTools support opening Set files (``.set``) and Experiment files (``.exp``) using the :py:class:`lvpyioTools.set.LVSet` class. For example:

.. code-block:: python

    from pathlib import Path
    from lvpyioTools.set import LVSet

    # opening an experiment set
    exp_file = Path("experiment.exp")
    experiment_set = LVSet(exp_file)
    print(experiment_set.get_name()) # prints the name of the set, that is the stem

    # alternatively, you can provide the folder instead
    folder = Path("experiment")
    LVSet(folder)

    # or a .set file
    set_file = Path("experiment/Properties/Calibration.set")
    lv_set = LVSet(set_file)


.. warning::

    Only sets which have one of the supported file extensions (:py:class:`lvpyioTools.SetSuffix`) can be opened as a :py:class:`lvpyioTools.set.LVSet`.

Experiment sets (``.exp``) and sets (``.set``) are generally the same, and there's rarely a point to opening an experiment set as you'll usually simply want to open a specific set which holds either images, or directly a set of treated data (e.g. vectors after PIV treatments).

You can access children or the parent of set using the methods :py:meth:`lvpyioTools.set.LVSet.get_children` and :py:meth:`lvpyioTools.set.LVSet.get_parent`.

Set files are simply text files which contain various information which are parsed by lvpyioTools when creating a :py:class:`lvpyioTools.set.LVSet` instance via the :py:mod:`lvpyioTools.setProperties` module. You can access this information through the method :py:meth:`lvpyioTools.set.LVSet.get_properties` but this is generally useless information. The most interesting one is usually the date :py:attr:`lvpyioTools.setProperties.SetProperty.SetTime`.


Reading buffers
---------------

Set camera inforamtion are opened in lvpyio as buffers. In lvpyioTools, the buffer is loaded from the lvpyio Sets only after calling :py:meth:`lvpyioTools.set.LVSet.open`. You need to make sure to close the buffer after use with :py:meth:`lvpyioTools.set.LVSet.close` at the risk of memory leaks (native issue of lvpyio). For example:

.. code-block:: python

    from pathlib import Path
    from lvpyioTools.set import LVSet

    set_file = Path("experiment/Properties/Calibration.set")
    lv_set = LVSet(set_file)
    lv_set.open()  # loads the buffer from the lvpyio Set

    lv_set.close()  # closes the buffer

Alternatively, a safer method is to use the dunder methods ``__enter__`` and ``__exit__`` provided in LVSet which handles it safely and automatically:

.. code-block:: python

    set_file = Path("experiment/Properties/Calibration.set")
    with LVSet(set_file) as lv_set:
        # the buffer is automatically loaded
        pass
    # the buffer is automatically closed upon exiting
    # this also automatically closes if an exception occurs


Another alternative is to wrap the usage of LVSet in a try-finally block to ensure the buffer is closed even if an exception occurs. For example:

.. code-block:: python

    set_file = Path("experiment/Properties/Calibration.set")
    lv_set = LVSet(set_file)
    try:
        lv_set.open()
        # use the buffer
        pass

    # always called even if an exception occurs
    finally:
        lv_set.close()


A buffer corresponds to a specific recording instant of the camera data. You can read a specific buffer using the method :py:meth:`lvpyioTools.set.LVSet.get_buffer`.

.. code-block:: python

    for buffer_index in range(len(lv_set)):
        buffer = lv_set.get_buffer(buffer_index)


Generally you'll be interested in specific frames of that buffer, for that use the method :py:meth:`lvpyioTools.set.LVSet.get_frame` which returns a :py:class:`lvpyioTools.frame.LVFrame` instance, or :py:meth:`lvpyioTools.set.LVSet.get_frames` to get all frames.

.. code-block:: python

    for buffer_index in range(len(lv_set)):
        # by default opens the first frame
        frame = lv_set.get_frame(buffer_index)


And then reading a specific image of that frame using :py:meth:`lvpyioTools.frame.LVFrame.get`, or alternatively directly reading from the set instance using :py:meth:`lvpyioTools.set.LVSet.get_image`.

.. code-block:: python

    for buffer_index in range(len(lv_set)):
        frame = lv_set.get_frame(buffer_index)
        image = frame.get()

        # alternatively
        image = lv_set.get_image(buffer_index)
