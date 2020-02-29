def extract_environment_variables(environment_dict):
    """
    This function takes a dictionary with values matching the
    environment variable names and returns the values extracted
    from the environment
    :param environment_dict: Dictionary with pointers to env vars
    :return environment_dict_copy: Dictionary with values of env var
    """
    import os
    import copy
    environment_dict_copy = copy.deepcopy(environment_dict)
    for internal_key in environment_dict_copy.keys():
        environment_var_name = environment_dict_copy[internal_key]
        assert environment_var_name in os.environ.keys(), f"Environment variable " \
                                                          f"{environment_var_name} not" \
                                                          f"found"
        environment_var_value = os.environ[environment_var_name]
        environment_dict_copy[internal_key] = environment_var_value

    return environment_dict_copy