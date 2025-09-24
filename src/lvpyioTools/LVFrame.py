"""
Created on Sep, 2025

@author: S. CADET
"""
import numpy as np





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
        return self.frame.images[image_number]

