"""
Helper class for working with lvpyio sets.
"""
from pathlib import Path
from typing import Any
import warnings

from PIL import Image

import lvpyio as lv
# from lvpyio.types
from lvpyio.types.frame import ImageFrame
from lvpyio.types.buffer import Buffer
from lvpyio.types.scale import Scales
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .stubs.set import Set
else:
    from lvpyio.io.set import Set


if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from lvpyioTools import setParser, calibration
    from lvpyioTools.frame import LVFrame
    from lvpyioTools.mask import create_mask
else:
    from . import setParser, calibration
    from .frame import LVFrame
    from .mask import create_mask


def sanitize_set_path(path: Path | str) -> Path:
    """
    Sanitize the provided set path.

    This function ensures that the provided path points to a valid .set or .exp file.
    If a directory is provided, it attempts to find a .set or .exp file within that directory.

    Args:
        path (Path | str): The path to the .set or .exp file, or a set directory.

    Raises:
        FileNotFoundError: If the provided path does not exist or no .set or .exp file is found in the directory.
        ValueError: If the provided file is not a .set or .exp file.
        FileNotFoundError: If no .set or .exp file is found in the provided directory.

    Returns:
        Path: The sanitized path to the .set or .exp file.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist.")

    # if it's a set file already then we simply return it
    if path.is_file():
        if not path.suffix in [".set", ".exp"]:
            raise ValueError(f"Provided set file {path} is not a .set or .exp file.")

    # if it's a directory then we try to find a .set or .exp file
    # associated to itself
    else:
        set_path = path.parent / (path.stem + ".set")
        exp_path = path.parent / (path.stem + ".exp")
        if set_path.exists():
            path = set_path
        elif exp_path.exists():
            path = exp_path
        else:
            raise FileNotFoundError(f"No .set or .exp file found in directory {path}.")
    return path


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
        from pathlib import Path
        from lvpyioTools.set import LVSet

        set_file = Path("example/example.set")
        with LVSet(set_file) as lvset:
            lvset.show()
            print(f"Number of frames in the set: {len(lvset)}")
    ```
    """
    def __init__(self, set_path: Path | str):
        # sanitize file
        set_path = sanitize_set_path(set_path)

        self.set_file: Path = set_path
        """Path of the set_file."""
        self.file: Path = set_path
        self.properties: dict[setParser.SetProperty, Any] = self.get_properties()

        self.set: Set | None = None
        """Holds the active set instance. If None, needs to be first opened with `open()`."""
        self.frames: tuple[LVFrame, ...] | None = None
        """Holds the frames of the currently opened set. If None, the set is not open."""

    def get_name(self) -> str:
        """
        Get the name of the set file without its extension.

        Returns:
            str: The stem of the set file.
        """
        return self.set_file.stem

    def __repr__(self):
        name = self.get_name()
        if self.is_experiment():
            return f"<LVSet: {name}, experiment set, properties={len(self.properties)}>"
        if self.is_open():
            return f"<LVSet: {name}, {len(self)} frames, properties={len(self.properties)}>"
        return f"<LVSet: {name}, closed, properties={len(self.properties)}>"


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
        self.set = lv.read_set(self.set_file)

    def close(self):
        """
        Close the currently opened set. If no set is open, this method does nothing.
        """
        if self.set is None:
            return
        self.set.close()
        self.set = None
        return self


## PARENTS / CHILDREN

    def is_experiment(self) -> bool:
        """
        Check if the set is an experiment set (`.exp`).
        """
        return self.set_file.suffix == ".exp"

    def get_folder(self, init=True) -> Path:
        """
        Retrieve the folder of the set file, that is the file without the suffix ".set" or ".exp".

        Args:
            init (bool, optional): If True, the folder will be created if it does not exist. Defaults to True.

        Raises:
            FileNotFoundError: If the folder does not exist and `init` is False.
            NotADirectoryError: If the path exists but is not a directory.

        Returns:
            Path: The folder path corresponding to the set file.
        """
        folder = self.set_file.with_suffix('')
        if not folder.exists():
            if init:
                folder.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(f"Folder '{folder}' does not exist.")
        if not folder.is_dir():
            raise NotADirectoryError(f"'{folder}' exists but is not a directory.")
        
        return folder


    def get_parent(self) -> 'LVSet | None':
        """
        Retrieve parent set holding this current set if exists. If the current set is an experiment set, it has no parent and this method will return None.

        Returns:
            LVSet | None: The parent set if it exists, otherwise None.
        """
        isParent = self.is_experiment()
        if isParent:
            return None

        # get parent theorical path
        set_dir = self.set_file.parent
        parent_dir = set_dir.parent

        # find .set or .exp file if exists
        for suffix in [".set", ".exp"]:
            # try to access the set file
            parent_set_file = parent_dir / (set_dir.name + suffix)
            if parent_set_file.exists():
                return LVSet(parent_set_file)

        return None
    
    def get_experiment(self, max_iteration: int = 100) -> 'LVSet | None':
        """
        Retrieve the experiment set holding this current set if exists.

        Args:
            max_iteration (int, optional): Maximum number of iterations to search for the experiment set. Defaults to 100.

        Returns:
            LVSet | None: The experiment set if it exists, otherwise None.
        """
        current_set = self
        iteration = 0
        while current_set is not None:
            if current_set.is_experiment():
                return current_set
            current_set = current_set.get_parent()

            # stop after too many iterations to avoid infinite loops
            iteration += 1
            if iteration > max_iteration:
                warnings.warn(f"Reached maximum iteration ({max_iteration}) while searching for experiment set. Stopping search.")
                break
        return None
    
    def get_children(self) -> list['LVSet']:
        """
        Retrieve all child sets of the current set.

        Returns:
            list[LVSet]: A list of child sets.
        """
        children = []
        set_dir = self.set_file.parent
        for child_dir in set_dir.iterdir():
            if child_dir.is_dir():
                for suffix in [".set", ".exp"]:
                    child_set_file = child_dir / (child_dir.name + suffix)
                    if child_set_file.exists():
                        children.append(LVSet(child_set_file))
        return children

    def get_mask(self, init: bool = False) -> 'LVSet | None':
        """
        Retrieve the mask set associated with the current set.

        If the mask set does not exist and `init` is True, a new mask set will be created.

        A mask is a specifically named set file "MASK.set" inside the set folder. Using some operations you can apply that mask on your current set from within DaVis.

        Args:
            init (bool, optional): Whether to create the mask set if it does not exist. Defaults to False.

        Returns:
            LVSet | None: The mask set if it exists or is created, otherwise None.
        """
        folder = self.get_folder()
        mask_set = folder / "MASK.set"
        if mask_set.exists():
            return LVSet(mask_set)
        if init:
            return self.make_mask()
        return None

    def make_mask(self) -> 'LVSet':
        """
        Create a new mask set for the current set if it does not already exist.

        Returns:
            LVSet: The newly created or existing mask set.
        """
        folder = self.get_folder()
        mask_set = folder / "MASK.set"
        if not mask_set.exists():
            create_mask(mask_set)
        return LVSet(mask_set)

    def get_calibration(self) -> 'Scales | None':
        """
        Retrieve the calibration settings from the experiment set if it exists.

        Returns:
            Scales | None: The calibration settings if they exist, otherwise None.
        """
        experiment = self.get_experiment()
        if experiment is None:
            warnings.warn(f"No experiment set found for {self.set_file}. Cannot retrieve calibration.")
            return None

        # get calibration file
        calibration_file = experiment.set_file.with_suffix("") / "Properties" / "Calibration" / "Calibration.xml"
        if not calibration_file.exists():
            warnings.warn(f"Calibration file {calibration_file} does not exist. Cannot retrieve calibration.")
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
        with open(self.set_file, 'r') as f:
            return f.read().strip()

    def get_properties(self) -> dict[setParser.SetProperty, Any]:
        """
        Read the set file and return its properties as a dictionary.

        Returns:
            dict[SetProperty, Any]: A dictionary containing the set properties and their values.
        """
        return setParser.read(self.set_file)


## READERS

    def __iter__(self):
        for buffer_frame in range(len(self)):
            yield self.get_image(buffer_frame)

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

    def get_frames(self, buffer_frame: int) -> tuple[LVFrame, ...]:
        buffer = self.get_buffer(buffer_frame)
        
        # init LVFrame instances for each frame in the buffer
        if self.frames is None:
            frames_count = len(buffer)
            self.frames = tuple(LVFrame(buffer[i], self) for i in range(frames_count))

        # if already exists, then simply replace the frames in the existing LVFrame instances
        else:
            for i in range(len(buffer)):
                self.frames[i].replace_frame(buffer[i])

        return self.frames

    def get_frame(self, buffer_frame: int, frame_number: int = 0) -> LVFrame:
        """
        Get a specific frame from a buffer in the set.

        Args:
            buffer_frame (int): The index of the buffer frame to retrieve the frame from.
            frame_number (int, optional): The index of the frame within the buffer. Defaults to 0.

        Returns:
            LVFrame: The requested frame object.
        """
        frames = self.get_frames(buffer_frame)
        if frame_number < 0 or frame_number >= len(frames):
            raise IndexError(f"Frame number {frame_number} is out of range. Valid range is 0 to {len(frames) - 1}.")
        return frames[frame_number]

    def get_image(self, buffer_frame: int, 
                  frame_number: int = 0, 
                  image_number: int = 0):
        """
        Get a specific image from a frame in a buffer in the set.

        Args:
            buffer_frame (int): The index of the buffer frame to retrieve the image from.
            frame_number (int, optional): The index of the frame within the buffer. Defaults to 0.
            image_number (int, optional): The index of the image within the frame. Defaults to 0.

        Returns:
            Image: The requested image object.
        """
        frame = self.get_frame(buffer_frame, frame_number)
        return frame.get(image_number)


## EXPORTS

    def export(self, output_dir: Path, extension: str = ".tif"):
        if not self.is_open():
            raise RuntimeError("Set is not open. Please call `open()` before exporting.")
        output_dir.mkdir(parents=True, exist_ok=True)
        for buffer_frame in range(len(self)):
            image = self.get_image(buffer_frame)
            output_file = output_dir / f"buffer_{buffer_frame:05d}{extension}"
            img = Image.fromarray(image)
            img.save(output_file)


## TEST SCRIPTS

if __name__ == "__main__":
    from pprint import pprint
    # Example usage
    set_file = Path("example/example.set")
    print(set_file)
    with LVSet(set_file) as set:
        pprint(set.get_properties())
        print(f"Number of frames in the set: {len(set)}")

    print()

    outside_set = Path("/media/scadet03/CADET_MAIN/Manips/2025-10/data.2025-10.piv/DaVis/Upstream/jonc_2/f=0.7, S0=0.05, d=0.06, N=5.0/1/1.set")
    print(outside_set)
    with LVSet(outside_set) as set:
        pprint(set.get_properties())
        print(f"Number of frames in the set: {len(set)}")

        frame = set.get_frame(0)
        print(frame)

    print()

    outside_set = Path("/media/scadet03/CADET_MAIN/Manips/2025-10/data.2025-10.piv/temporary_calibration_ref_data/jonc_1/f=0.8, S0=0.05, d=0.06, N=1.0/Scale.set")
    print(outside_set)
    with LVSet(outside_set) as set:
        pprint(set.get_properties())
        print(f"Number of frames in the set: {len(set)}")

        buffer = set.get_buffer(0)
        frame = set.get_frame(0)
        print(frame)

    print()

    outside_set = Path("/media/scadet03/CADET_MAIN/Manips/2025-10/data.2025-10.piv/DaVis/Upstream/jonc_1/f=0.7, S0=0.05, d=0.06, N=1.0/1/1.set")
    print(outside_set)
    with LVSet(outside_set) as set:
        print(set)
        print(f"Number of frames in the set: {len(set)}")

        buffer = set.get_buffer(0)
        frame = set.get_frame(0)
        print(frame)

        parent = set.get_parent()
        print(parent.set_file if parent is not None else "No parent set found.")

        experiment = set.get_experiment()
        print(experiment)
        print(experiment.set_file if experiment is not None else "No experiment set found.")

        calib = set.get_calibration()
        print(calib)