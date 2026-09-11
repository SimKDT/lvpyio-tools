import datetime
from pathlib import Path


MASK_TEMPLATE = r"""
// mask set file created by lvpyioTools

#GROUP Sets
SetType = 256;
SetGroups = "";
SetTime = "{date}";
SetComments = "";
SetStart = 1;
SetInc = 1;
SetSourceSet = "";
SetViewCallback = "";
SetLoadCallback = "";
""".strip()



def create_mask(set_file: Path | str):
    set_file = Path(set_file)
    assert set_file.suffix == ".set", "The set file must have a .set extension"

    # write out the template set file
    template = MASK_TEMPLATE.format(
        # the date uses the format that DaVis set files usually use
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    set_file.write_text(template)

    return template

if __name__ == "__main__":
    set_file_path = Path("test.set")
    create_mask(set_file_path)