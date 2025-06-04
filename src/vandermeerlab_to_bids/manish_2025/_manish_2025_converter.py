import copy

import neuroconv
import pynwb
from pydantic import FilePath

# from vandermeerlab_to_bids.manish_2025.interfaces import (
# )


class Manish2025Converter(neuroconv.NWBConverter):
    data_interface_classes = {}

    # TODO