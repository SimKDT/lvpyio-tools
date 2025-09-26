"""
Created on Sep, 2025

@author: S. CADET
"""
import numpy as np

import LVCalibration




class LVFrame:
    def __init__(self,frame):
        self.frame = frame

    def get_frame_time(self):
        frame = self.frame
        """
        Get the time information in the frame.

        Returns:
            float: The acquisition time of the frame in microseconds.
        """
        att = frame.attributes
        ATS = float(att['AcqTimeSeries'].split(' ')[0])
        AT = att['Acq.Time'][0][0]
        return ATS + AT

    def get_image(self, image_number:int=0) -> np.ndarray:
        """
        Get the image data from a specific frame and image number.

        Args:
            image_number (int, optional): The index of the image within the frame. Defaults to 0.

        Returns:
            np.ndarray: The image data as a NumPy array.
        """
        try:
            image = self.frame.images[image_number]
        except IndexError:
            raise IndexError(f"Image number {image_number} is out of range. Available images: 0 to {len(self.frame.images)-1}.")
        return image

    def get_frame_shape(self) -> tuple[int, int]:
        """
        Get the shape of the frame.

        Returns:
            tuple[int, int]: A tuple representing the shape of the frame as (height, width).
        """
        return self.frame.shape
    
    def get_mask(self, mask_number:int=0) -> np.ndarray:
        """
        Get the mask data from a mask number.

        Args:
            mask_number (int, optional): The index of the mask within the frame. Defaults to 0.

        Returns:
            np.ndarray: The mask data as a NumPy mask array.
        """
        try:
            mask = self.frame.masks[mask_number]
        except IndexError:
            raise IndexError(f"Mask number {mask_number} is out of range. Available masks: 0 to {len(self.frame.masks)-1}.")
        return mask
    
    def get_XY_calibration(self) -> dict:
        frame = self.frame
        calibration = {
            "x": {
                "slope": frame.scales.x.slope,
                "offset": frame.scales.x.offset
            },
            "y": {
                "slope": frame.scales.y.slope,
                "offset": frame.scales.y.offset
            },
        }
        return LVCalibration(calibration)

    def get_XY_axis(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Get the X and Y axis values of the frame. If calibration is provided, apply it to the axis values.

        Returns:
            tuple[np.ndarray, np.ndarray]: _description_
        """
        # Get the shape of the frame
        height, width = self.frame.get_frame_shape()
        x_axis = np.arange(width)
        y_axis = np.arange(height)
        calibration = self.get_XY_calibration()

        return calibration.ij_2_XY(x_axis, y_axis)