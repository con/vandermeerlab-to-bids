"""Reader for the custom 'ExpKey' structured text metadata file used by the van der Meer Lab."""

import pathlib
import pydantic
import re
import json


@pydantic.validate_call
def read_experiment_keys_file(file_path: str | pathlib.Path) -> dict[str, str]:
    """
    Reads the experiment keys (.m) file and returns a dictionary of keys and values.

    Works by coercing the structured text into a JSON string, which is then converted into dictionary using
    built-in JSON parsing.

    Improved from https://github.com/vandermeerlab/mvdmlab_npx_to_nwb/blob/15c85df2803293f8de331caf34980d9f239727bc/src/manimoh_utils/parse_expkeys.py#L4

    Parameters
    ----------
    file_path : str
        The path to the experiment keys file.

    Returns
    -------
    dict[str, str]
        The metadata dictionary.
    """
    content = file_path.read_text()

    # Remove comments
    comment_stripped_content = re.sub(
        pattern=r'("([^"\\]|\\.)*")|(%.*$)', repl=_comment_replacer, string=content, flags=re.MULTILINE
    )

    # Remove excessive line breaks
    collapsed_content = re.sub(pattern=r"\n+", repl="\n", string=comment_stripped_content)

    # Remove trailing semicolons
    clipped_content = re.sub(pattern=r";.*$", repl="", string=collapsed_content, flags=re.MULTILINE)

    # Remove the 'ExpKeys' prefix and format keys as JSON
    cleaned_content = (
        re.sub(pattern=r"ExpKeys\.", repl='"', string=clipped_content, flags=re.MULTILINE)
        # Only remove '+ <integer>' patterns
        .replace(" = ", '": ')
    )

    # Remove leading '+' symbols from integers but leave it for strings
    plus_stripped_content = re.sub(pattern=r"\+\s*(\d+)", repl=r"\1", string=cleaned_content)

    # Format spaces after colons
    formatted_content = re.sub(pattern=r":\s+", repl=": ", string=plus_stripped_content)

    # Replace single quotes with unique character (chose caret) only within double-quoted strings
    # E.g., for the "notes" field
    quote_fixed_content = re.sub(
        pattern=r'"([^"]*)"', repl=lambda m: f'"{m.group(1).replace("'", "^")}"', string=formatted_content
    )

    # Wrap all in JSON object (dictionary)
    json_content = f"{{{quote_fixed_content.replace("\n", ", ").replace("{", "[").replace("}", "]").replace("\'", '\"').replace("^", "'")}}}"
    # Delete trailing commas
    proper_json_content = re.sub(pattern=r",\s*}", repl="}", string=json_content)

    experiment_keys = json.loads(s=proper_json_content)
    return experiment_keys


def _comment_replacer(match: re.Match[str, str, ...]) -> str:
    quoted, _ = match.group(1), match.group(2)
    if quoted:
        return quoted
    else:
        return ""
