"""
Helper class for working with lvpyio sets.
"""
from pathlib import Path
from typing import Any

import lvpyio as lv
# from lvpyio.types
from lvpyio.types.frame import ImageFrame
from lvpyio.types.buffer import Buffer
from lvpyio.io.set import Set

from lvpyioTools import setParser




class LVSet(): # numpydoc ignore=SA01
    """
    Helper class for working with DaVis sets. 
    
    Set files are simple text files that contain some generic information that were saved on creation. They don't give any information about the actual data, where it is stored, or how to read it but the folder placed in the same directory as the set file contains all the data.

    This provides a simple interface to easily manipulate and read the set files.

    Parameters
    ----------
        file (Path): The path to the .set file.

    Examples
    --------

    ```python
        from lvpyioTools.sets import LVSet
        from pathlib import Path

        set_file = Path("example/example.set")
        with LVSet(set_file) as set:
            set.show()
            print(f"Number of frames in the set: {len(set)}")
    ```
    """
    set: Set | None = None

    def __init__(self, file: Path):
        # verify provided file
        if not file.exists():
            raise FileNotFoundError(f"File {file} does not exist.")
        if not file.is_file():
            raise ValueError(f"Provided path {file} is not a file.")
        if not file.suffix == ".set":
            raise ValueError(f"Provided file {file} is not a .set file.")

        self.file = file
        self.properties = self.get_properties()


## LOADER / SAVER

    def __enter__(self):
        """
        Context manager entry point.

        Returns:
            LVSet: The current instance of LVSet.
        """
        self.open()
        return self
    
    def __exit__(self, *args):
        """
        Safeguard to make sure the set gets closed.
        """
        self.close()

    def __del__(self):
        """
        Safeguard to make sure the set gets closed.
        """
        self.close()

    def open(self):
        """
        Load the set with lvpyio.
        """
        # safeguard to ensure we properly close the set
        self.close()
        self.set = lv.read_set(self.file)

    def close(self):
        """
        Close the currently opened set. If no set is open, this method does nothing.
        """
        if self.set is None:
            return
        self.set.close()
        self.set = None

## GENERIC INFORMATION ABOUT THE SET

    def __len__(self):
        """
        Return the number of frames in the set.
        
        Returns:
            int: The number of frames in the set.

        Raises:
            RuntimeError: Set is not open.
        """
        if self.set is None:
            raise RuntimeError("Set is not open. Please call 'open()' before accessing the length.")
        return len(self.set)

    def read(self) -> str:
        """
        Read the set file and display its content.
        """
        with open(self.file, 'r') as f:
            return f.read().strip()

    def get_properties(self) -> dict[setParser.SetProperty, Any]:
        """
        Read the set file and return its properties as a dictionary.

        Returns:
            dict[SetProperty, Any]: A dictionary containing the set properties and their values.
        """
        return setParser.read(self.file)


## READERS

    def get_frame(self, buffer_frame: int) -> ImageFrame:
        if self.set is None:
            raise RuntimeError("Set is not open. Please call 'open()' before accessing frames.")
        
        size = len(self)
        if buffer_frame < 0 or buffer_frame >= size:
            raise IndexError(f"Buffer frame index {buffer_frame} is out of range. Valid range is 0 to {size - 1}.")
        
        frame = self.set[buffer_frame]
        return frame

    def get_image(self, buffer_frame: int, 
                  frame_number: int = 0, 
                  image_number: int = 0):
        frame = self.get_frame(buffer_frame)
        return frame[frame_number]




if __name__ == "__main__":
    from pprint import pprint
    from pylogs import echo
    # Example usage
    set_file = Path("example/example.set")
    echo.path(set_file)
    with LVSet(set_file) as set:
        pprint(set.get_properties())
        print(f"Number of frames in the set: {len(set)}")

