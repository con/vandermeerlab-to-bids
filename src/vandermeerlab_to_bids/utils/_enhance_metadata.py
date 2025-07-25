import pydantic
import json
import dateutil.tz
import neuroconv.utils.dict
from ._experiment_keys import read_experiment_keys_file


def enhance_metadata(
    *, metadata: neuroconv.utils.DeepDict, preprocessed_data_directory: pydantic.DirectoryPath
) -> None:
    """Operating in-place, enhance the default NeuroConv metadata."""
    session_name = preprocessed_data_directory.name
    session_id = preprocessed_data_directory.name.replace("-", "")  # TODO: temporary

    metadata["NWBFile"]["session_id"] = session_id  # TODO: Might want to adjust later

    if metadata["NWBFile"].get("session_start_time", None) is not None:
        metadata["NWBFile"]["session_start_time"] = metadata["NWBFile"]["session_start_time"].replace(
            tzinfo=dateutil.tz.gettz("US/Eastern")
        )

    for probe_index in range(len(metadata["Ecephys"]["Device"])):
        json_decoded = json.loads(s=metadata["Ecephys"]["Device"][probe_index]["description"])
        json_decoded["probe_type_description"] = "Neuropixels 2.0 - Four Shank"
        json_encoded = json.dumps(obj=json_decoded)
        metadata["Ecephys"]["Device"][probe_index]["description"] = json_encoded

    experiment_keys_file_name = f"{session_name.replace("-", "_")}_keys.m"
    experiment_keys_file_path = preprocessed_data_directory / experiment_keys_file_name

    experiment_keys = read_experiment_keys_file(file_path=experiment_keys_file_path)

    metadata["Subject"]["subject_id"] = experiment_keys["subject"]
    metadata["Subject"]["species"] = "Mus musculus"  # Just hard-coding since they aren't going to change
    metadata["Subject"]["sex"] = experiment_keys["sex"]  # TODO: add validator that theirs are all valid
    metadata["Subject"]["strain"] = experiment_keys["genetics"]

    # TODO: Update electrode group locations from experiment keys
    # Insertion details will have to be attached a different way
    # Perhaps dump JSON to the description of each group
