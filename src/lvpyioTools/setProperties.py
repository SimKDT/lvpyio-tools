from enum import Enum, StrEnum
from datetime import datetime

from pylogs import echo

def _read_str(value: str) -> str:
    return str(value.strip('"').strip("'"))

def _read_date(value: str) -> datetime:
    value = _read_str(value) # remove quotes

    # interpret date with format "Fri Sep 26 11:25:26 2025"
    try:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")
    except ValueError:
        echo.error(f"Could not parse date from value '{value}'")
        raise



class SetType(Enum):
    """
    Classifications of the different values of the `SetType` property.
    """
    IMAGE = 256
    """`.im7` images"""
    FOLDER = 16384
    """Simple folder"""
    CINE = 4352
    """`.cine` file"""
    PROPERTIES = 8192
    """`Properties` folder"""
    CALIBRATION = 131072
    """Calibration set"""
    VECTORS = 512
    """`.vc7` files"""

def _read_set_type(value: str) -> SetType | None:
    """
    Convert a string value to a `SetType` enum member.

    Args:
        value (str): The string representation of the set type, which is expected to be an integer in string format.

    Returns:
        SetType: The corresponding `SetType` enum member.
    """
    value = _read_str(value) # remove quotes
    # convert to int
    try:
        value_int = int(value)
    except ValueError:
        echo.error(f"Could not convert value '{value}' to int for SetType")
        return None
    
    try:
        return SetType(value_int)
    except ValueError:
        echo.error(f"Unknown SetType value '{value_int}'")
        return None

class SetProperty(StrEnum):
    """
    Definitions of the different properties that can be found in a set file.
    """
    SetType = "SetType"
    SetGroups = "SetGroups"
    SetTime = "SetTime"
    SetComments = "SetComments"
    SetStart = "SetStart"
    SetInc = "SetInc"
    SetSourceSet = "SetSourceSet"
    SetViewCallback = "SetViewCallback"
    SetLoadCallback = "SetLoadCallback"
    bpInfoString = "bpInfoString"
    SetIdentifier = "SetIdentifier"


property_types = {
    SetProperty.SetType: _read_set_type,
    SetProperty.SetGroups: _read_str,
    SetProperty.SetTime: _read_date,
    SetProperty.SetComments: _read_str,
    SetProperty.SetStart: int,
    SetProperty.SetInc: int,
    SetProperty.SetSourceSet: _read_str,
    SetProperty.SetViewCallback: _read_str,
    SetProperty.SetLoadCallback: _read_str,
    SetProperty.bpInfoString: _read_str,
    SetProperty.SetIdentifier: _read_str,
}
"""Associate each SetProperty to a function or type for convertion to a specific type."""

if __name__ == "__main__":
    print(SetType(256))