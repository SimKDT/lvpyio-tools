"""
Created on Jul 02, 2025

@author: S. CADET



Tools to read and manipulate LaVision sets (.set) files.
"""

import lvpyio as lv
from lvpyio.types.frame import ImageFrame
from lvpyio.types.buffer import Buffer
import os
import numpy as np
from tqdm import tqdm
from typing import Union
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
# import imageio.v2 as imageio


def get_calibration(calibration_file:str) -> dict:
    """
    Get the calibration settings from the given calibration file which should be a XML file. Values are rounded to fit the calibration application of DaVis.

    Args:
        calibration_file (str): Path to the calibration file in XML format.

    Returns:
        dict: A dictionary containing the calibration scales for X and Y axes, 
              including slope, offset, and the unit of measurement. The structure is as follows:
              {
                  "x": {
                      "slope": float,  # Conversion factor for X-axis (mm per pixel)
                      "offset": float  # Offset for X-axis (mm)
                  },
                  "y": {
                      "slope": float,  # Conversion factor for Y-axis (mm per pixel)
                      "offset": float  # Offset for Y-axis (mm)
                  },
                  "unit": str  # Unit of measurement (e.g., "mm")
              }
    """
    # Read and parse the XML file
    tree = ET.parse(calibration_file)
    root = tree.getroot()
    # Search for "Scales" in the XML file
    scales = root.find(".//Scales")

    linearScaleX = scales.find("LinearScaleX")
    linearScaleY = scales.find("LinearScaleY")

    factorX = float(linearScaleX.get("FactorMmPerPixel"))
    factorY = float(linearScaleY.get("FactorMmPerPixel"))
    offsetX = float(linearScaleX.get("OffsetMm"))
    offsetY = float(linearScaleY.get("OffsetMm"))
    return {"x": {"slope": round(factorX, 6), "offset": round(offsetX, 3)},
            "y": {"slope": round(factorY, 6), "offset": round(offsetY, 3)},
            "unit": "mm"}

class LVSet():
    def __init__(self, file):
        self.folder = os.path.dirname(file)
        self.file = file
        self._raw_cache = None
        self._cached_frames = {}

        self.set = lv.read_set(file)

    def __enter__(self):
        """
        Context manager entry point.

        Returns:
            LVSet: The current instance of LVSet.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Safeguard to make sure the set gets closed.
        """
        self.set.close()

    def get_frame_count(self) -> int:
        """
        Get the number of frames in the set.

        Returns:
            int: _description_
        """
        return len(self.set)

    def get_real_time(self,_tqdm=False):
        """
        Gets the real time array of the set.

        Args:
            _tqdm (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if hasattr(self, 'time'):
            return self.time

        # init with first frame
        time = np.array([self.get_frame_time(self.set[0][0])])

        # load remaining frames
        for i in tqdm(range(1, len(self.set)), desc="Loading frames", unit="frame", disable=not _tqdm):
            frame = self.set[i][0]
            time = np.column_stack((time, self.get_frame_time(frame)))

        # correct to start time at 0
        time = (time - np.min(time))*10**-6 # us to s

        self.time = time
        return time

    @staticmethod
    def get_frame_time(frame:ImageFrame) -> float:
        """
        Get the time information in the frame.

        Args:
            frame (lv.Frame): The frame from which to extract time information.

        Returns:
            float: The acquisition time of the frame in microseconds.
        """
        att = frame.attributes
        ATS = float(att['AcqTimeSeries'].split(' ')[0])
        AT = att['Acq.Time'][0][0]
        return ATS + AT

    def get_buffer_frame(self, buffer_number: int, frame_number: int|None = 0) -> Union[ImageFrame, Buffer]:
        """
        Retrieve a specific frame from a buffer in the set. Alternatively, if `frame_number` is None, return the entire buffer.

        Args:
            buffer_number (int): The index of the buffer to retrieve.
            frame_number (int, optional): The index of the frame within the buffer. Defaults to 0. If None, the entire buffer is returned.

        Returns:
            lvpyio.Frame or list[lvpyio.Frame]: A single frame if `frame_number` is specified, or the entire buffer (list of frames) if `frame_number` is None.

        Examples:
            ```
            path = "..."
            sets = LVSet(path)

            # Get the first frame of the first buffer
            frame = sets.get_buffer_frame(0)

            # Get the entire first buffer
            buffer = sets.get_buffer_frame(0, None)

            # Get the second frame of the first buffer
            frame = sets.get_buffer_frame(0, 1)
            ```
        """
        if frame_number is None:
            frame = self.set[buffer_number]
        else:
            frame = self.set[buffer_number][frame_number]
        frame.frame_number = frame_number
        frame.buffer_number = buffer_number
        return frame

    def get_image(self, frame:ImageFrame, image_number:int=0) -> np.ndarray:
        """
        Get the image data from a specific frame and image number.

        Args:
            frame (ImageFrame): The frame from which to extract the image data.
            image_number (int, optional): The index of the image within the frame. Defaults to 0.

        Returns:
            np.ndarray: The image data as a NumPy array.
        """
        return frame.images[image_number]
    
    @DeprecationWarning
    def get_image_cached_folder(self, frame:ImageFrame, image_number:int=0, raw_name="raw_{0}_{1}_{2}.png") -> np.ndarray:
        """
        Not actually faster
        - get_image: 2.155 s
        - get_image_cached_folder: 5.47 s

        ```python
            # Measure time for get_image_cached
            start = time.time()
            for i in range(0,20):
                frame = sets.get_buffer_frame(i)
                image_cached = sets.get_image_cached(frame)
            end = time.time()
            print(f"get_image_cached took {end - start:.6f} seconds")

            # Measure time for get_image
            start = time.time()
            for i in range(0,20):
                frame = sets.get_buffer_frame(i)
                image_cached = sets.get_image(frame)
            end = time.time()
            print(f"get_image took {end - start:.6f} seconds")
        ```
        """
        raw_path = os.path.join(self.folder, "raw")
        os.makedirs(raw_path, exist_ok=True)

        buffer_number = frame.buffer_number
        frame_number = frame.frame_number
        raw_name = raw_name.format(buffer_number, frame_number, image_number)

        # Cache the directory listing
        if self._raw_cache is None:
            self._raw_cache = set(os.listdir(raw_path))

        if raw_name in self._raw_cache:
            return imageio.imread(os.path.join(raw_path, raw_name))
        img = frame.images[image_number]
        imageio.imwrite(os.path.join(raw_path, raw_name), img)
        self._raw_cache.add(raw_name)
        return img
    
    @DeprecationWarning
    def get_image_cached(self, frame:ImageFrame, image_number:int=0, raw_name="raw_{0}_{1}_{2}.png") -> np.ndarray:
        """
        Not faster either even for repeated image access
        - get_image: 4.977 s
        - get_image_cached: 5.480 s

        ```python
            # Measure time for get_image_cached
            start = time.time()
            for i in range(0,20):
                frame = sets.get_buffer_frame(i)
                image_cached = sets.get_image_cached(frame)
            for i in range(0,20):
                frame = sets.get_buffer_frame(i)
                image_cached = sets.get_image_cached(frame)
            end = time.time()
            print(f"get_image_cached took {end - start:.6f} seconds")

            # Measure time for get_image
            start = time.time()
            for i in range(0,20):
                frame = sets.get_buffer_frame(i)
                image_cached = sets.get_image(frame)
            for i in range(0,20):
                frame = sets.get_buffer_frame(i)
                image_cached = sets.get_image(frame)
            end = time.time()
            print(f"get_image took {end - start:.6f} seconds")
        ```
        """
        # id
        buffer_number = frame.buffer_number
        frame_number = frame.frame_number
        raw_name = raw_name.format(buffer_number, frame_number, image_number)
        if raw_name in self._cached_frames:
            return self._cached_frames[raw_name]
        img = frame.images[image_number]
        self._cached_frames[raw_name] = img
        return img
    
    @staticmethod
    def get_frame_shape(frame:ImageFrame) -> tuple[int, int]:
        """
        Get the shape of the frame.

        Args:
            frame (ImageFrame): The frame from which to extract the shape.

        Returns:
            tuple[int, int]: A tuple representing the shape of the frame as (height, width).
        """
        return frame.shape

    def get_XY_calibration(self, frame:ImageFrame) -> dict:
        return {
            "x": {
                "slope": frame.scales.x.slope,
                "offset": frame.scales.x.offset
            },
            "y": {
                "slope": frame.scales.y.slope,
                "offset": frame.scales.y.offset
            },
        }
    
    @staticmethod
    def get_XY_axis(frame:ImageFrame, calibration:dict|None=None) -> tuple[np.ndarray, np.ndarray]:
        """
        Get the X and Y axis values of the frame. If calibration is provided, apply it to the axis values.

        Args:
            frame (ImageFrame): _description_
            calibration (dict | None, optional): _description_. Defaults to None.

        Returns:
            tuple[np.ndarray, np.ndarray]: _description_
        """
        # Get the shape of the frame
        height, width = LVSet.get_frame_shape(frame)
        x_axis = np.arange(width)
        y_axis = np.arange(height)

        # Apply calibration if present
        if calibration is not None:
            x_axis, y_axis = LVSet.ij_2_XY(x_axis, y_axis, calibration)

            # # Get calibration settings for x and y axes
            # x_calibration = calibration['x']
            # y_calibration = calibration['y']

            # x_axis = x_axis * x_calibration['slope'] + x_calibration['offset']
            # y_axis = y_axis * y_calibration['slope'] + y_calibration['offset']

        return x_axis, y_axis
    
    @staticmethod
    def ij_2_XY(i, j, calibration:dict) -> tuple[float, float]:
        """
        Get the physical coordinates (X, Y) of a point in the frame based on its pixel indices (i, j) and the calibration settings.

        Args:
            i (int): The pixel index along the X-axis (horizontal).
            j (int): The pixel index along the Y-axis (vertical).
            calibration (dict): The calibration settings containing slope and offset for X and Y axes.

        Returns:
            tuple[float, float]: The physical coordinates (X, Y) in the calibrated space.
        """
        x_calibration = calibration['x']
        y_calibration = calibration['y']

        x_point = i * x_calibration['slope'] + x_calibration['offset']
        y_point = j * y_calibration['slope'] + y_calibration['offset']
        return x_point, y_point
    
    @staticmethod
    def XY_2_ij(x, y, calibration:dict) -> tuple[int, int]:
        """
        Get the pixel indices (i, j) of a point in the frame based on its physical coordinates (X, Y) and the calibration settings.

        Args:
            x (float): The physical X-coordinate in the calibrated space.
            y (float): The physical Y-coordinate in the calibrated space.
            calibration (dict): The calibration settings containing slope and offset for X and Y axes.

        Returns:
            tuple[int, int]: The pixel indices (i, j) corresponding to the physical coordinates.
        """
        x_calibration = calibration['x']
        y_calibration = calibration['y']

        i = int((x - x_calibration['offset']) / x_calibration['slope'])
        j = int((y - y_calibration['offset']) / y_calibration['slope'])
        return i, j






if __name__ == "__main__":
    import time

    file = "/media/scadet03/T5 EVO/data.piv-wavemaker/DaVis/Upstream/flexible/f=0.9, S0=0.05, d=0.06, N=1.0, eps+=55.0, eps-=0.0/1/1.set"

    sets = LVSet(file)
    print(sets.folder)
    print(sets.file)
    # Measure time for get_image_cached
    start = time.time()
    for i in range(0,20):
        frame = sets.get_buffer_frame(i)
        image_cached = sets.get_image_cached(frame)
    for i in range(0,20):
        frame = sets.get_buffer_frame(i)
        image_cached = sets.get_image_cached(frame)
    end = time.time()
    print(f"get_image_cached took {end - start:.6f} seconds")

    # Measure time for get_image
    start = time.time()
    for i in range(0,20):
        frame = sets.get_buffer_frame(i)
        image_cached = sets.get_image(frame)
    for i in range(0,20):
        frame = sets.get_buffer_frame(i)
        image_cached = sets.get_image(frame)
    end = time.time()
    print(f"get_image took {end - start:.6f} seconds")


    print()



