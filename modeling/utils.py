def print_header(header_text: str) -> None:
    """Print something like a banner.

    Arguments:
        header -- Main string.
    """
    decorator = "*"
    decorator_len = 16
    print(f"{decorator * decorator_len}\n{header_text}\n{decorator * decorator_len}")
