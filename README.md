# Code for Dialogs Re-enacted Across Languages (DRAL)

This repository contains the code used in creating the DRAL corpus. The code can be generalized to work for other language pairs. See technical report for more details.

> Nigel G. Ward, Jonathan E. Avila, and Emilia Rivas. 2022. Dialogs Re-enacted Across Languages. University of Texas at El Paso. Retrieved from <https://cs.utep.edu/nigel/papers/dral-techreport.pdf>

## Setup

1. Install Python 3.10.4 or create a Python virtual environment (recommended).
2. Clone this repository, then navigate to its root.
3. Install the required Python modules with pip: `pip install -r requirements.txt`

## Make a DRAL release

```zsh
python make_release.py -i <path_to_input_directory> -o <path_to_output_directory>
```

See documentation in `make_release.py` for more details.
