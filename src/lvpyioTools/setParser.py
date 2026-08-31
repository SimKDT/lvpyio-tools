from pathlib import Path
from typing import Any
import warnings

from .setProperties import SetProperty, property_types


_PROPERTY_PATTERN = r"(?P<property>\w+) = \"?(?P<value>[\S\s]*?)\"?;"


def read_property(key: str, value: str):
    """
    Read a property from the set file and convert it to the appropriate type and property key.

    Args:
        key (str): The property key from the set file.
        value (str): The property value from the set file.

    Returns:
        tuple[SetProperty | None, Any]: A tuple containing the property key as a `SetProperty` enum member (or `None` if unknown) and the converted property value (or `None` if conversion failed).
    """
    try:
        prop = SetProperty(key)
    except ValueError:
        warnings.warn(f"Unknown property '{key}' found in the set file.")
        return None, None

    # convert to type
    prop_type = property_types.get(prop, None)
    if prop_type is None:
        warnings.warn(f"Unknown property '{key}' found in the set file.")
    else:
        try:
            value = prop_type(value)  # convert to the appropriate type
        except Exception as e:
            warnings.warn(f"Error converting property '{key}' with value '{value}': {e}")
            return None, None

    return prop, value

def read(file: Path) -> dict[SetProperty, Any]:
    """
    Read the contents of a file.

    Args:
        file (Path): The path to the file to read.

    Returns:
        dict[SetProperty, Any]: A dictionary containing the set properties and their values.
    """
    with open(file, 'r') as f:
        content = f.read().strip()
    lines = content.splitlines()

    # identify line with "#GROUP Sets"
    group_line_index = None
    for i, line in enumerate(lines):
        if line.strip() == "#GROUP Sets":
            group_line_index = i
            break
    
    if group_line_index is None:
        raise ValueError("The file does not contain a '#GROUP Sets' line.")
    
    # extract lines after "#GROUP Sets"
    set_lines = lines[group_line_index + 1:]

    import re
    set_dict = {}
    for line in set_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue  # skip empty lines and comments
        match = re.match(_PROPERTY_PATTERN, line)
        if match:
            key = match.group('property')
            value = match.group('value')

            prop, value = read_property(key, value)
            if prop is None:
                continue

            set_dict[prop] = value
    return set_dict



if __name__ == "__main__":
    from pprint import pprint
    examples = Path("example")
    
    for set_file in examples.rglob("*.set"):
        print(set_file)
        set_dict = read(set_file)
        pprint(set_dict)

        if SetProperty.SetTime in set_dict:
            print(f"SetTime: {set_dict[SetProperty.SetTime].isoformat()}")


    outside_set = Path("/media/scadet03/CADET_MAIN/Manips/2025-10/data.2025-10.piv/temporary_calibration_ref_data/jonc_1/f=0.8, S0=0.05, d=0.06, N=1.0/Scale.set")
    print(outside_set)
    set_dict = read(outside_set)
    pprint(set_dict)