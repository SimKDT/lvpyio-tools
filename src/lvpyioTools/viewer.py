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
    parser.add_argument("--vmin", type=float, default=None, help="Minimum value for image display (default: None)")
    parser.add_argument("--vmax", type=float, default=None, help="Maximum value for image display (default: None)")
    parser.add_argument("--cmap", type=str, default='gray', help="Colormap for image display (default: 'gray')")
    args = parser.parse_args()

    with LVSet(Path(args.set)) as lv_set:
        try:
            frame = lv_set.get_frame(args.buffer, args.frame)
            frame.show(image_number=args.image, 
                       vmin=args.vmin, vmax=args.vmax, 
                       cmap=args.cmap)
        except IndexError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")