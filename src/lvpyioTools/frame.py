"""
Helper class for working lvpyio frames retrieved from a set.
"""

from typing import TYPE_CHECKING
from enum import StrEnum

from lvpyio.types.frame import ImageFrame
from lvpyio.types.scale import Scales

from lvpyioTools.attribute import FrameAttribute
if TYPE_CHECKING:
    from lvpyioTools.set import LVSet

class LVFrame():
    """
    Wrapper class for working with lvpyio frames retrieved from a set. This class provides a convenient interface to access frame attributes, image data, and scale information.
    """
    def __init__(self, frame: ImageFrame, set: 'LVSet'):
        self.frame = frame
        self.set = set

    def replace_frame(self, new_frame: ImageFrame):
        """
        Update the current frame with a new frame. Notably used for performance reasons to not create a new LVFrame object for each frame in a set.

        Args:
            new_frame (ImageFrame): The new frame to update with.
        """
        self.frame = new_frame

    def __len__(self):
        return len(self.frame.images)

    def shape(self):
        """
        Get the images and masks shapes.

        Returns:
            tuple: A tuple containing the shapes of the images and masks.
        """
        return self.frame.shape

    def get(self, image_number: int = 0):
        """
        Read the image data from a specific frame and image number.

        Args:
            image_number (int, optional): The index of the image to retrieve. Defaults to 0.

        Raises:
            IndexError: If the image_number is out of range.

        Returns:
            numpy.ndarray: The image data as a NumPy array.
        """
        if image_number < 0 or image_number >= len(self.frame.images):
            raise IndexError(f"Image number {image_number} is out of range. Available images: 0 to {len(self.frame.images)-1}.")
        return self.frame.images[image_number]

    def scale(self) -> Scales:
        """
        Read the scale information from the frame, that is a class containing the following attributes:
        - `x`: The scale in the x-direction (in meters per pixel).
        - `y`: The scale in the y-direction (in meters per pixel).
        - `z`: The scale in the z-direction (in meters per pixel).
        - `i`: The scale in the intensity direction (generally with a slope of 1).

        Each attributes are `Scale` objects, which contain the following attributes:
        - `slope`: The slope of the scale
        - `offset`: The offset of the scale
        - `unit`: The unit of the scale (mm, counts, etc.)
        - `description`: Mostly just empty

        Returns:
            Scales: A `Scales` object containing the scale information for the frame.
        """
        return self.frame.scales

    def get_attribute(self, attribute: FrameAttribute):
        """
        Get a specific attribute from the frame.

        Args:
            attribute (FrameAttribute): The attribute to retrieve.
        
        Returns:
            Any: The value of the requested attribute, or `None` if the attribute is not found in the frame.
        """
        return self.frame.attributes.get(attribute.value, None)