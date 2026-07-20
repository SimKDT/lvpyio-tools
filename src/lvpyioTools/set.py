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

from lvpyioTools import setParser, calibration
from lvpyioTools.frame import LVFrame




class LVSet(): # numpydoc ignore=SA01
    """
    Helper class for working with DaVis sets. 
    
    Set files are simple text files that contain some generic information that were saved on creation. They don't give any information about the actual data, where it is stored, or how to read it but the folder placed in the same directory as the set file contains all the data.

    This provides a simple interface to easily manipulate and read the set files.

    A set of images is handled this way in DaVis:
    1. buffer (set[buffer_frame])
    2. frame (set[buffer_frame][frame_number])
    3. image (set[buffer_frame][frame_number].images[image_number])

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
    frame: LVFrame | None = None

    def __init__(self, file: Path):
        # verify provided file
        if not file.exists():
            raise FileNotFoundError(f"File {file} does not exist.")
        if not file.is_file():
            raise ValueError(f"Provided path {file} is not a file.")
        if not file.suffix in [".set", ".exp"]:
            raise ValueError(f"Provided file {file} is not a .set or .exp file.")

        self.file = file
        self.properties = self.get_properties()

    def __repr__(self):
        if self.is_experiment():
            return f"<LVSet: {self.file.name}, experiment set, properties={len(self.properties)}>"
        if self.is_open():
            return f"<LVSet: {self.file.name}, {len(self)} frames, properties={len(self.properties)}>"
        return f"<LVSet: {self.file.name}, closed, properties={len(self.properties)}>"


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

    def is_open(self) -> bool:
        """
        Check if the set is currently open.

        Returns:
            bool: True if the set is open, False otherwise.
        """
        return self.set is not None

    def open(self):
        """
        Load the set with lvpyio.
        """
        # safeguard to ensure we properly close the set
        self.close()
        if self.is_experiment():
            raise ValueError(f"Cannot open an experiment set (`.exp`) directly.")
        self.set = lv.read_set(self.file)

    def close(self):
        """
        Close the currently opened set. If no set is open, this method does nothing.
        """
        if self.set is None:
            return
        self.set.close()
        self.set = None


## PARENTS / CHILDREN

    def is_experiment(self) -> bool:
        """
        Check if the set is an experiment set (`.exp`).
        """
        return self.file.suffix == ".exp"

    def get_parent(self) -> 'LVSet | None':
        isParent = self.is_experiment()
        if isParent:
            return None

        # get parent theorical path
        set_dir = self.file.parent
        parent_dir = set_dir.parent

        # find .set or .exp file if exists
        for suffix in [".set", ".exp"]:
            # try to access the set file
            parent_set_file = parent_dir / (set_dir.name + suffix)
            if parent_set_file.exists():
                return LVSet(parent_set_file)

        return None
    
    def get_experiment(self, max_iteration=100) -> 'LVSet | None':
        current_set = self
        iteration = 0
        while current_set is not None:
            if current_set.is_experiment():
                return current_set
            current_set = current_set.get_parent()

            # stop after too many iterations to avoid infinite loops
            iteration += 1
            if iteration > max_iteration:
                echo.warning(f"Reached maximum iteration ({max_iteration}) while searching for experiment set. Stopping search.")
                break
        return None
    
    def get_calibration(self):
        experiment = self.get_experiment()
        if experiment is None:
            echo.warning(f"No experiment set found for {self.file}. Cannot retrieve calibration.")
            return None

        # get calibration file
        calibration_file = experiment.file.with_suffix("") / "Properties" / "Calibration" / "Calibration.xml"
        if not calibration_file.exists():
            echo.warning(f"Calibration file {calibration_file} does not exist. Cannot retrieve calibration.")
            return None
        
        return calibration.get_calibration(calibration_file)


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

    def get_buffer(self, buffer_frame: int) -> Buffer:
        """
        Get a specific buffer from the set.

        Args:
            buffer_frame (int): The index of the buffer frame to retrieve.

        Raises:
            RuntimeError: Set is not open.
            IndexError: Buffer frame index is out of range.

        Returns:
            Buffer: The requested buffer object.
        """
        # verify set is open
        if self.set is None:
            raise RuntimeError("Set is not open. Please call `open()` before accessing buffers.")
        
        size = len(self)
        if buffer_frame < 0 or buffer_frame >= size:
            raise IndexError(f"Buffer frame index {buffer_frame} is out of range. Valid range is 0 to {size - 1}.")
        return self.set[buffer_frame]

    def get_frame(self, buffer_frame: int, frame_number: int = 0) -> LVFrame:
        buffer = self.get_buffer(buffer_frame)
        frame: ImageFrame = buffer[frame_number]
        if self.frame is None:
            self.frame = LVFrame(frame, self)
        else:
            self.frame.replace_frame(frame)
        return self.frame

    def get_image(self, buffer_frame: int, 
                  frame_number: int = 0, 
                  image_number: int = 0):
        frame = self.get_frame(buffer_frame, frame_number)
        return frame.get(image_number)




if __name__ == "__main__":
    from pprint import pprint
    from pylogs import echo
    # Example usage
    set_file = Path("example/example.set")
    echo.path(set_file)
    with LVSet(set_file) as set:
        pprint(set.get_properties())
        print(f"Number of frames in the set: {len(set)}")

    print()

    outside_set = Path("/media/scadet03/CADET_MAIN/Manips/2025-10/data.2025-10.piv/DaVis/Upstream/jonc_2/f=0.7, S0=0.05, d=0.06, N=5.0/1/1.set")
    echo.path(outside_set)
    with LVSet(outside_set) as set:
        pprint(set.get_properties())
        print(f"Number of frames in the set: {len(set)}")

        frame = set.get_frame(0)
        print(frame)

    print()

    outside_set = Path("/media/scadet03/CADET_MAIN/Manips/2025-10/data.2025-10.piv/temporary_calibration_ref_data/jonc_1/f=0.8, S0=0.05, d=0.06, N=1.0/Scale.set")
    echo.path(outside_set)
    with LVSet(outside_set) as set:
        pprint(set.get_properties())
        print(f"Number of frames in the set: {len(set)}")

        buffer = set.get_buffer(0)
        frame = set.get_frame(0)
        print(frame)

    print()

    outside_set = Path("/media/scadet03/CADET_MAIN/Manips/2025-10/data.2025-10.piv/DaVis/Upstream/jonc_1/f=0.7, S0=0.05, d=0.06, N=1.0/1/1.set")
    echo.path(outside_set)
    with LVSet(outside_set) as set:
        print(set)
        print(f"Number of frames in the set: {len(set)}")

        buffer = set.get_buffer(0)
        frame = set.get_frame(0)
        print(frame)

        parent = set.get_parent()
        echo.path(parent.file if parent is not None else "No parent set found.")

        experiment = set.get_experiment()
        print(experiment)
        echo.path(experiment.file if experiment is not None else "No experiment set found.")

        calib = set.get_calibration()
        print(calib)