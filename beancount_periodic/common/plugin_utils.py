def read_config(config_string):
    if len(config_string) == 0:
        config = {}
    else:
        config = eval(config_string, {}, {})

    if not isinstance(config, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")
    return config
