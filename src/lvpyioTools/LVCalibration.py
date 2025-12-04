"""
Created on Sep, 2025

@author: S. CADET
"""
import numpy as np
import xml.etree.ElementTree as ET
import copy


class LVCalibration:
    """
    Initialize the LVCalibration object with calibration settings.
    
    Args:
        calibration (dict): A dictionary containing the calibration scales for X and Y axes, 
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
    def __init__(self, calibration:dict|None=None):
        if calibration is None:
            calibration = {
                "x": {"slope": 1.0, "offset": 0.0},
                "y": {"slope": 1.0, "offset": 0.0},
                "z": {"slope": 1.0, "offset": 0.0},
                "grid": {"x": 1, "y": 1, "z": 1},
                "unit": "pixel", "automatic": True
            }
        else:
            calibration["automatic"] = False
        
        self.calibration = calibration

    def copy(self) -> 'LVCalibration':
        """
        Create a copy of the current LVCalibration object.

        Returns:
            LVCalibration: A new LVCalibration object with the same calibration settings.
        """
        new_calibration = LVCalibration(calibration=copy.deepcopy(self.calibration))
        return new_calibration

    def set_origin_IJ(self, point: tuple[int, int]):
        self.originIJ = point
        self.originXY = self.ij_2_XY(point[0], point[1])

    def set_origin_XY(self, point: tuple[float, float]):
        self.originXY = point
        self.originIJ = self.XY_2_ij(point[0], point[1])

    def set_offset_XY(self, dx: float|None = None, dy: float|None = None):
        calibration = self.calibration
        x_calibration = calibration['x']
        y_calibration = calibration['y']

        if dx is not None:
            x_calibration['offset'] = dx
        if dy is not None:
            y_calibration['offset'] = dy

    def set_offset_IJ(self, di: int|None = None, dj: int|None = None):
        calibration = self.calibration
        x_calibration = calibration['x']
        y_calibration = calibration['y']
        grid_calibration = calibration["grid"]

        if di is not None:
            x_calibration['offset'] = di * x_calibration['slope'] * grid_calibration["x"]
        if dj is not None:
            y_calibration['offset'] = dj * y_calibration['slope'] * grid_calibration["y"]

    def get(self, name, default=None):
        return self.calibration.get(name, default)

    def get_calibration(self, axis=None, element=None) -> dict:
        if axis is None:
            return self.calibration
        axis_calibration = self.calibration.get(axis, None)
        assert axis_calibration is not None, f"Calibration for axis '{axis}' not found."
        if element is None:
            return axis_calibration
        element_value = axis_calibration.get(element, None)
        assert element_value is not None, f"Element '{element}' not found in calibration for axis '{axis}'."
        return element_value

    def XY_2_ij(self, x, y) -> tuple[int|np.ndarray, int|np.ndarray]:
        """
        Get the pixel indices (i, j) of a point in the frame based on its physical coordinates (X, Y) and the calibration settings.

        Args:
            x (float): The physical X-coordinate in the calibrated space.
            y (float): The physical Y-coordinate in the calibrated space.

        Returns:
            tuple[int, int]: The pixel indices (i, j) corresponding to the physical coordinates.
        """
        calibration = self.calibration
        if calibration is None:
            raise ValueError("Calibration settings are not provided.")
        x_calibration = calibration['x']
        y_calibration = calibration['y']
        grid_calibration = calibration["grid"]

        i = ((x - x_calibration['offset']) / (x_calibration['slope'] * grid_calibration["x"]))
        j = ((y - y_calibration['offset']) / (y_calibration['slope'] * grid_calibration["y"]))
        
        if not isinstance(i, np.ndarray):
            i = int(i)
        else:
            i = i.astype(int)

        if not isinstance(j, np.ndarray):
            j = int(j)
        else:
            j = j.astype(int)

        return i, j

    def ij_2_XY(self, i: float|np.ndarray, j: float|np.ndarray) -> tuple[float|np.ndarray, float|np.ndarray]:
        """
        Get the physical coordinates (X, Y) of a point in the frame based on its pixel indices (i, j) and the calibration settings.

        Args:
            i (int): The pixel index along the X-axis (horizontal).
            j (int): The pixel index along the Y-axis (vertical).

        Returns:
            tuple[float, float]: The physical coordinates (X, Y) in the calibrated space.
        """
        calibration = self.calibration
        if calibration is None:
            raise ValueError("Calibration settings are not provided.")
        x_calibration = calibration['x']
        y_calibration = calibration['y']
        grid_calibration = calibration["grid"]

        x_point = i * x_calibration['slope'] * grid_calibration["x"] + x_calibration['offset']
        y_point = j * y_calibration['slope'] * grid_calibration["y"] + y_calibration['offset']
        return x_point, y_point



def get_calibration(calibration_file:str) -> LVCalibration:
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
    
    calibration_data = {
        "x": {"slope": round(factorX, 6), "offset": round(offsetX, 3)},
        "y": {"slope": round(factorY, 6), "offset": round(offsetY, 3)},
        "grid": {"x": 1, "y": 1, "z": 1},
        "unit": "mm"
    }

    return LVCalibration(calibration_data)
