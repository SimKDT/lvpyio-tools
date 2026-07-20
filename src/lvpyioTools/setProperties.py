from enum import Enum, StrEnum
from datetime import datetime
import locale

from pylogs import echo

def _read_date(value: str) -> datetime | None:
    """
    Read the .set file date format and convert into datetime object.
    The date uses english format, e.g. "Fri Sep 26 11:25:26 2025",
    so conversion to a specific locale is needed to ensure correct parsing regardless of the system locale.

    See:
    https://stackoverflow.com/questions/38303217/datetime-strptime-unexpected-behavior-locale-issue

    Args:
        value (str): The date string from the .set file.

    Returns:
        datetime | None: The corresponding datetime object, or `None` if parsing failed.
    """
    try:
        # use 'C' locale to ensure parsing works regardless of system locale
        old_locale = locale.setlocale(locale.LC_TIME)
        try:
            locale.setlocale(locale.LC_TIME, 'C')
            return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")
        finally:
            # restore original locale
            try:
                locale.setlocale(locale.LC_TIME, old_locale)
            except locale.Error:
                # restoration fails, just proceed
                pass
    except ValueError:
        echo.error(f"Could not parse date from value '{value}'")
        return None



class SetType(Enum):
    """
    Classifications of the different values of the `SetType` property.
    """
    IMAGE = 256
    """`.im7` images"""
    VECTORS = 512
    """`.vc7` files"""
    CINE = 4352
    """`.cine` file"""
    PROPERTIES = 8192
    """`Properties` folder"""
    FOLDER = 16384
    """Simple folder"""
    CALIBRATION = 131072
    """Calibration set"""

def _read_set_type(value: str) -> SetType | None:
    """
    Convert a string value to a `SetType` enum member.

    Args:
        value (str): The string representation of the set type, which is expected to be an integer in string format.

    Returns:
        SetType: The corresponding `SetType` enum member.
    """
    # convert to int
    try:
        value_int = int(value)
    except ValueError:
        echo.error(f"Could not convert value '{value}' to int for SetType")
        return None
    
    # try to convert to SetType
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
    SetProperty.SetGroups: str,
    SetProperty.SetTime: _read_date,
    SetProperty.SetComments: str,
    SetProperty.SetStart: int,
    SetProperty.SetInc: int,
    SetProperty.SetSourceSet: str,
    SetProperty.SetViewCallback: str,
    SetProperty.SetLoadCallback: str,
    SetProperty.bpInfoString: str,
    SetProperty.SetIdentifier: str,
}
"""Associate each SetProperty to a function or type for convertion to a specific type."""

if __name__ == "__main__":
    print(SetType(256))