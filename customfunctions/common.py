"""Helps Manage Snowflake Connection"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_common.ipynb.

# %% auto 0
__all__ = ['print_hello']

# %% ../nbs/01_common.ipynb 3
def print_hello(name: str) -> str:
    """
    Prints a greeting message for the specified name. DEFAULT FUNCTION

    Parameters
    ----------
    name : str
        The name of the person to greet.

    Returns
    -------
    str
        A greeting message for the provided
    """
    return f"Hello {name}!"


