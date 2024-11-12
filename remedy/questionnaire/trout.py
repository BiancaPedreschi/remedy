def trgout(code, numlns):
    """
    Compute the binary input values for controlling the NI trigger system.

    Args:
        code (int): The desired numeric code.
        numlns (int): The number of lines to use.
            Normally 8 (pins 2-9; bits 0-7), but a pin is taken
            for amplifier synchronization in the eego AntNeuro system with
            >64 electrodes used.

    Returns:
        list: The binary representation of the code.

    Raises:
        ValueError: If the requested code cannot be represented with the current configuration.
    """
    binary = bin(code)[2:]  # convert decimal number to binary string
    numdig = len(binary)  # digits in binary number

    maxbin = (2 ** numlns) - 1

    if code > maxbin:
        raise ValueError('This code cannot be used with current configuration!')

    bincode = [int(bit) for bit in binary] + [0] * (numlns - numdig)  # add zeros to non-used lines

    return bincode
