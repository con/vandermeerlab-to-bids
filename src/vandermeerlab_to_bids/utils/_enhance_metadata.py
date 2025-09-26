import pydantic
import json
import dateutil.tz
import neuroconv.utils.dict
import neuroconv.converters

from ._experiment_keys import read_experiment_keys_file


def enhance_metadata(
    *,
    metadata: neuroconv.utils.DeepDict,
    preprocessed_data_directory: pydantic.DirectoryPath,
    spikeglx_converter: neuroconv.converters.SpikeGLXConverterPipe,
) -> None:
    """Operating in-place, enhance the default NeuroConv metadata."""
    session_name = preprocessed_data_directory.name
    session_id = preprocessed_data_directory.name.replace("-", "")

    experiment_keys_file_name = f"{session_name.replace("-", "_")}_keys.m"
    experiment_keys_file_path = preprocessed_data_directory / experiment_keys_file_name
    experiment_keys = read_experiment_keys_file(file_path=experiment_keys_file_path)

    metadata["NWBFile"]["session_id"] = session_id
    metadata["NWBFile"]["session_description"] = " | ".join(experiment_keys.get("sessiontype", []))

    experimenter_name = experiment_keys["experimenter"]
    if experimenter_name != "Manish":
        message = f"Observed an unknown experimenter name in key file: {experiment_keys_file_name}."
        raise NotImplementedError(message)

    experimenter_name_map = {
        "Manish": "Mahopatra, Manish",
    }

    experimenter = experimenter_name_map[experimenter_name]
    metadata["NWBFile"]["experimenter"] = [experimenter]

    if metadata["NWBFile"].get("session_start_time", None) is not None:
        metadata["NWBFile"]["session_start_time"] = metadata["NWBFile"]["session_start_time"].replace(
            tzinfo=dateutil.tz.gettz("US/Eastern")
        )

    for probe_index in range(len(metadata["Ecephys"]["Device"])):
        json_decoded = json.loads(s=metadata["Ecephys"]["Device"][probe_index]["description"])
        json_decoded["probe_type_description"] = "Neuropixels 2.0 - Four Shank"
        json_encoded = json.dumps(obj=json_decoded)
        metadata["Ecephys"]["Device"][probe_index]["description"] = json_encoded

    latin_species_map = {
        "mouse": "Mus musculus",
        "rat": "Rattus norvegicus",
    }
    species = experiment_keys.get("species", None)
    if species is None:
        message = f"Species {species} not defined in the Latin binomial map."
        raise ValueError(message)

    latin_species = latin_species_map[species]

    metadata["Subject"]["subject_id"] = experiment_keys["subject"]
    metadata["Subject"]["species"] = latin_species
    metadata["Subject"]["sex"] = experiment_keys["sex"]
    metadata["Subject"]["strain"] = experiment_keys["genetics"]

    probe_to_location = dict()
    for index in range(1, 3):
        probe = experiment_keys[f"probe{index}_ID"]
        location = f"{experiment_keys[f"probe{index}_hemisphere"].lower()} {experiment_keys[f"probe{index}_location"]}"
        probe_to_location[probe] = location

    for group in metadata["Ecephys"]["ElectrodeGroup"]:
        probe = group["device"][-5:].lower()
        group["location"] = probe_to_location[probe]

    for probe_stream, subinterface in spikeglx_converter.data_interface_objects.items():
        probe = probe_stream.split(".")[0]
        if probe == "nidq":
            continue

        subinterface.recording_extractor.set_property(
            key="brain_area", values=[probe_to_location[probe]] * subinterface.recording_extractor.get_num_channels()
        )
