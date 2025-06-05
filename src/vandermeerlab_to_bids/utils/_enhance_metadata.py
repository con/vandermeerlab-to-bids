import pydantic
import json
from ._experiment_keys import read_experiment_keys_file

@pydantic.validate_call
def enhance_metadata(*, metadata: dict, directory_path: pydantic.DirectoryPath) -> None:
    """Operating in-place, enhance the default NeuroConv metadata."""
    # TODO: NeuroConv does not accept
    for probe_index in range(len(metadata["Ecephys"]["Device"])):
        json_decoded = json.loads(s=metadata["Ecephys"]["Device"][probe_index]["description"])
        json_decoded["probe_type_description"] = "Neuropixels 2.0 - Four Shank"
        json_encoded = json.dumps(obj=json_decoded)
        metadata["Ecephys"]["Device"][probe_index]["description"] = json_encoded

    subject_id = directory_path.parent.name
    session_name = directory_path.name
    experiment_keys_file_name = f"{session_name.replace("-", "_")}_keys.m"
    experiment_keys_file_path = directory_path / experiment_keys_file_name

    experiment_keys = read_experiment_keys_file(file_path=experiment_keys_file_path)

    # TODO: Update electrode group locations from experiment keys
    # Insertion details will have to be attached a different way
    # Perhaps dump JSON to the description of each group