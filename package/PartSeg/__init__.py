import os
import appdirs

__version__ = "0.9b1"

app_name = "PartSeg"
app_lab = "LFSG"
CONFIG_FOLDER = os.path.join(appdirs.user_data_dir(app_name, app_lab), __version__)
