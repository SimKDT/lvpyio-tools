"""
Show a specific image from a DaVis set file.
"""
from pathlib import Path

from .set import LVSet

def main():
    import argparse

    parser = argparse.ArgumentParser(description="LVPyIO Tools Viewer")
    parser.add_argument("set", type=str, help="Path to the DaVis set file")
    parser.add_argument("--buffer", type=int, default=0, help="Buffer frame number to display (default: 0)")
    parser.add_argument("--frame", type=int, default=0, help="Frame number to display (default: 0)")
    parser.add_argument("--image", type=int, default=0, help="Image number to display (default: 0)")
    args = parser.parse_args()

    with LVSet(Path(args.set)) as lv_set:
        try:
            frame = lv_set.get_frame(args.buffer, args.frame)
            frame.show(image_number=args.image)
        except IndexError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")