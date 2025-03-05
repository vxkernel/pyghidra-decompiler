# PyGhidra Decompiler

A simple and efficient Python tool to decompile executables using the power of Ghidra and PyGhidra.

## Features

- Decompile executables to readable C code
- Easy to use command-line interface
- Supports most executable formats that Ghidra supports
- Handles cleanup of temporary Ghidra project files automatically
- Output to files or directories

## Installation

```bash
pip install pyghidra
```

Make sure to set the `GHIDRA_INSTALL_DIR` environment variable to point to your Ghidra installation:

```bash
export GHIDRA_INSTALL_DIR=/path/to/ghidra
```

## Usage

```bash
python main.py executable.exe [output_path]
```

### Arguments

- `executable`: Path to the executable file to decompile
- `output`: (Optional) Output file path or directory (default: same as input with .c extension)

### Options

- `--no-analyze`: Skip Ghidra's analysis phase (faster but less accurate)
- `--verbose`, `-v`: Enable verbose output
- `--no-cleanup`: Keep temporary Ghidra project files


## Requirements

- Python 3.9+
- Ghidra (tested with version 11.3+)
- PyGhidra


## Acknowledgments

- [Ghidra](https://ghidra-sre.org/) - NSA's software reverse engineering framework
