from pathlib import Path
from typing import Literal
import xml.etree.ElementTree as ET

from lvpyio.types.scale import Scale, Scales

def _get_for_axis(scales, id: Literal['LinearScaleX', 'LinearScaleY', 'LinearScaleZ', 'LinearScaleI']):
    linearScale = scales.find(id)
    if linearScale is None:
        raise ValueError(f"Could not find {id} in the calibration file.")

    factor = linearScale.get("FactorMmPerPixel")
    offset = linearScale.get("OffsetMm")
    unit = linearScale.get("Unit")
    description = linearScale.get("Description")
    if factor is None or offset is None or unit is None:
        raise ValueError(f"Could not find FactorMmPerPixel, OffsetMm, or Unit in the calibration file for {id}.")
    
    return Scale(slope=float(factor), offset=float(offset), unit=unit, description=description)


def get_calibration(calibration_file: Path) -> Scales:
    """
    Get the calibration settings from the given calibration file which should be a XML file. Values are rounded to fit the calibration application of DaVis.

    Args:
        calibration_file (Path): Calibration file in XML format.

    Returns:
        Scales: A `Scales` object containing the calibration settings for x, y, z, and i axes.
    """
    # Read and parse the XML file
    tree = ET.parse(calibration_file)
    root = tree.getroot()
    # Search for "Scales" in the XML file
    scales = root.find(".//Scales")

    x = _get_for_axis(scales, id='LinearScaleX')
    y = _get_for_axis(scales, id='LinearScaleY')
    z = _get_for_axis(scales, id='LinearScaleZ')
    i = _get_for_axis(scales, id='LinearScaleI')

    return Scales(x, y, z, i)