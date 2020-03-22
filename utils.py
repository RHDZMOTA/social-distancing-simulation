import os


def list_dir(path="."):
    files = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            files.extend(list_dir(file_path))
        else:
            files.append(file_path)
    return files


def _replace_list_elements(obj):
    if isinstance(obj, list):
        return {str(i): _replace_list_elements(v) for i, v in enumerate(obj)}
    if isinstance(obj, dict):
        return {k: _replace_list_elements(v) for k, v in obj.items()}
    return obj


def flatten_dict(dictionary, sep=".", prefix=""):
    flat_dict = {}
    for key, val in dictionary.items():
        flat_key = f"{prefix}{sep}{key}" if prefix else key
        flat_dict = {
            **flat_dict,
            **(
                flatten_dict(dictionary=val, sep=sep, prefix=flat_key)
                if isinstance(val, dict) else {flat_key: val}
            )
        }
    return flat_dict


def get_dict_hash_key(dictionary, sep=".", prefix=""):
    flatten_dictionary = flatten_dict(_replace_list_elements(dictionary), sep, prefix)
    return hash(frozenset(flatten_dictionary.items()))
