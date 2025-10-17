# JCAMP-DX Converter for NMR Data

A Python library for converting NMR data to and from JCAMP-DX format.

## Overview

This library provides tools for working with JCAMP-DX formatted spectroscopic data, with a focus on NMR (Nuclear Magnetic Resonance) data. It can:

- Parse existing JCAMP-DX files
- Create new JCAMP-DX files from various input formats
- Convert between JCAMP-DX and other NMR data formats
- Handle 1D and 2D NMR data (both spectra and FIDs)
- Process structural data and peak assignments

The library is particularly useful for working with NMR data from different instrument vendors (Bruker, Varian) and converting them to a standardized format.

## Installation

### Prerequisites

The following Python packages are required:

- numpy: For numerical operations and array handling
- scipy: For scientific computing and signal processing
- nmrglue: For reading and processing vendor-specific NMR data formats
- rdkit: For handling chemical structures and molecular information
- matplotlib: For visualization (optional, but recommended)

### Installation Steps

1. Clone the repository:
   ```
   git clone <repository-url>
   cd jcampdx
   ```

2. Install the required dependencies:
   ```
   pip install numpy scipy matplotlib
   pip install nmrglue
   pip install rdkit
   ```

3. For RDKit installation issues, you may need to use conda:
   ```
   conda install -c conda-forge rdkit
   ```

### Verifying Installation

To verify that the installation was successful, you can run a simple test:

```python
python -c "import jcamp; print('JCAMP-DX library installed successfully')"
```

### Development Installation

For development purposes, you can install the package in development mode:

```
pip install -e .
```

## Usage

### Command Line Interface

The main entry point for creating JCAMP-DX files is `createjcamp.py`. It can be used to convert various NMR data formats to JCAMP-DX.

Basic usage:
```
python createjcamp.py [options...] > output.jdx
```

To see all available options:
```
python createjcamp.py --help
```

#### Command Line Options

The command line interface supports the following options:

**General Options:**
- `--title TITLE`: Set the title for the current block
- `--origin STRING`: Set the origin information
- `--owner STRING`: Set the owner information
- `--link INDEX`: Add a link to a previously added block
- `--block TYPE`: Append a new block of the specified type

**Block Types:**
- `STRUCTURE`: Chemical structure (mol/sdf file)
- `1DSPECTRUM`: 1D NMR spectrum
- `1DFID`: 1D NMR free induction decay
- `1DPEAKS`: 1D NMR peak list
- `ASSIGNMENTS`: Chemical shift assignments
- `2DSPECTRUM`: 2D NMR spectrum
- `2DFID`: 2D NMR free induction decay
- `2DASSIGNMENTS`: 2D chemical shift assignments
- `2DPEAKS`: 2D NMR peak list

**File Options:**
- `--file PATH [format]`: Specify the input file and format
  - Supported formats: `csv`, `tsv`, `json`, `bruk`, `var`, `nmrml`

**Metadata Options:**
- `--frq VALUE`: Observe frequency in MHz
- `--nuc STRING`: Observe nucleus (e.g., `1H`, `13C`)
- `--sol STRING`: Solvent name
- `--temp VALUE`: Temperature in Celsius
- `--reftype [INTERNAL|EXTERNAL]`: Reference type
- `--refcpd STRING`: Reference compound
- `--refppm VALUE`: Reference chemical shift
- `--spectype STRING`: Pulse sequence
- `--mode [SIMULTANEOUS|SEQUENTIAL|SINGLE]`: Acquisition mode
- `--delay VALUE VALUE`: Delay in microseconds
- `--desc STRING`: Sample description
- `--ph VALUE`: pH value
- `--mp VALUE`: Melting point
- `--bp VALUE`: Boiling point
- `--ref VALUE`: Source reference
- `--comment STRING`: Additional comments

#### Converting from NMRML format

NMRML is an XML-based format for NMR data. The library can directly convert NMRML files to JCAMP-DX:

```
python createjcamp.py --fromnmrml input_file.nmrML > output.jdx
```

This is a simplified command that handles all the conversion details automatically.

#### Creating a JCAMP-DX file with multiple blocks

A single JCAMP-DX file can contain multiple blocks of different types. This example creates a file with structure, spectrum, peak list, and assignments:

```
python createjcamp.py --title "TEST FILE" \
--block STRUCTURE   --file structure.mol                --title "STRUCTURE" \
--block 1DSPECTRUM  --file example_1h_spectrum.txt csv  --title "SPECTRUM"      --frq 500 --nuc 1H --refcpd DSS --refppm 0 \
--block 1DPEAKS     --file example_1h_peaklist.txt csv  --title "PEAKS"         --frq 500 --nuc 1H --link 1 \
--block ASSIGNMENTS --file example_1h_peaklist.txt csv  --title "ASSIGNMENTS"   --frq 500 --nuc 1H --link 2 \
> output.jdx
```

The `--link` option creates cross-references between blocks, which is useful for connecting related data (e.g., a spectrum and its peak assignments).

#### Converting Vendor-Specific Data

##### Bruker Data

```
python createjcamp.py --title "FROM BRUKER" --block 1DSPECTRUM --file ./nmr.fid/pdata/1/ bruk > output.jdx
```

For Bruker 2D data:
```
python createjcamp.py --title "BRUKER 2D" --block 2DSPECTRUM --file ./nmr.fid/pdata/1/ bruk > output_2d.jdx
```

##### Varian Data

```
python createjcamp.py --title "FROM VARIAN" --block 1DSPECTRUM --file ./varian_data/ var > output.jdx
```

For Varian 2D data:
```
python createjcamp.py --title "VARIAN 2D" --block 2DSPECTRUM --file ./varian_data/ var > output_2d.jdx
```

### Python API

The library can also be used as a Python API:

```python
import jcamp
from jcamp import FileParser

# Parse a JCAMP-DX file
data = FileParser.parse_jcamp("input.jdx")

# Create a JCAMP-DX object from parsed data
jdx = FileParser.create_jcamp(data)

# Scale the data for optimal representation
jdx.data.scale_x()
jdx.data.scale_y()

# Convert to nmrglue format
udic, d = jdx.to_nmrglue_1d()

# Write to a new JCAMP-DX file
with open("output.jdx", "w") as f:
    f.write(jdx.write())
```

## Supported Data Types and Formats

### Input Formats

- **Bruker**: Raw Bruker NMR data directories
- **Varian**: Raw Varian NMR data directories
- **CSV/TSV**: Simple text files with tabular data
- **JSON**: Structured data in JSON format
- **NMRML**: NMR Markup Language files
- **MOL/SDF**: Chemical structure files

### JCAMP-DX Block Types

- **STRUCTURE**: Chemical structure information
- **1DSPECTRUM**: One-dimensional NMR spectrum
- **1DFID**: One-dimensional NMR free induction decay
- **1DPEAKS**: Peak list for one-dimensional NMR data
- **ASSIGNMENTS**: Chemical shift assignments
- **2DSPECTRUM**: Two-dimensional NMR spectrum
- **2DFID**: Two-dimensional NMR free induction decay
- **2DPEAKS**: Peak list for two-dimensional NMR data
- **2DASSIGNMENTS**: Chemical shift assignments for 2D data

## Algorithm Details

### JCAMP-DX Format and Structure

JCAMP-DX (Joint Committee on Atomic and Molecular Physical Data - Data Exchange) is a standardized format for exchanging spectroscopic data. The format consists of:

- **LDRs (Labeled Data Records)**: Key-value pairs in the format `##KEY=VALUE`
- **Blocks**: Logical sections of data (e.g., a spectrum, a structure, peak assignments)
- **Data Tables**: Encoded numerical data representing spectra or FIDs

This library implements JCAMP-DX versions 4.24, 5.01, and 6.00, with a focus on NMR data as specified in the JCAMP-DX standard.

### JCAMP-DX Encoding

The library supports various JCAMP-DX encoding formats to efficiently represent numerical data:

- **AFFN**: ASCII Free Format Numeric - Simple space-separated values
- **PAC**: Packed - Removes unnecessary spaces
- **SQZ**: Squeezed - Uses special characters to represent single digits
- **DIF**: Difference - Encodes differences between consecutive values
- **SQZDUP**: Squeezed Duplicate - Combines SQZ with run-length encoding
- **DIFDUP**: Difference Duplicate - Combines DIF with run-length encoding

These encoding formats are used to compress the data and reduce file size while maintaining data integrity. The encoding/decoding process is handled by the `encode.py` and `decode.py` modules.

### Data Processing Workflow

The library follows this general workflow:

1. **Parsing**: Read input data from various formats (JCAMP-DX, Bruker, Varian, etc.)
2. **Data Structure Creation**: Create appropriate data structures for the type of data
3. **Processing**: Apply necessary transformations (scaling, normalization, etc.)
4. **Encoding**: Convert data to JCAMP-DX format with appropriate encoding
5. **Output**: Write the formatted data to a file

### Data Processing Features

The library includes functions for:

- **Scaling data**: Optimize data representation for integer encoding
  ```python
  jdx.data.scale_x()  # Scale x-axis data
  jdx.data.scale_y()  # Scale y-axis data to fit in 16-bit integer range
  ```

- **Format conversion**: Convert between JCAMP-DX and other formats
  ```python
  # Convert to nmrglue format
  udic, data = jdx.to_nmrglue_1d()

  # Create JCAMP-DX from nmrglue data
  jdx = NMRSpectrum.from_nmrglue_1d(udic, data)
  ```

- **Complex data handling**: Process both real and imaginary components of NMR data
  ```python
  # For FID data with complex values
  fid = NMRFid()
  fid.data = NTuples1DFIDData(complex_data)
  ```

- **Chemical structure processing**: Handle molecular structures using RDKit
  ```python
  # Add a molecular structure to a JCAMP-DX file
  block = jcamp_dx.blocks[0]
  block.add_mol("structure.mol")
  ```

- **Peak assignments**: Manage chemical shift assignments and coupling constants
  ```python
  # Add peak assignments
  block.add_assignments("assignments.csv", filetype="csv")
  ```

### Digital Filter Removal

For Bruker data, the library can remove the digital filter effects that are present in the raw FID data. This is important for accurate processing of Bruker NMR data:

```python
# Remove digital filter effects
grpdly = remove_digital_filter(dic, data)
```

The algorithm uses the group delay parameter from the Bruker acquisition parameters to correct the phase distortion introduced by the digital filter.

### Multidimensional Data Handling

The library supports both 1D and 2D NMR data:

- **1D data**: Represented as simple x,y pairs
- **2D data**: Represented using the NTUPLES format from JCAMP-DX 6.00
  ```python
  # Create a 2D spectrum
  spec2d = NMRSpectrum2D()
  spec2d.data = NTuplesNDSpectrumData(data2d, ranges)
  ```

## Examples

### Parsing and Visualizing a 1D NMR Spectrum

```python
import jcamp
from jcamp import FileParser
import matplotlib.pyplot as plt
import numpy as np

# Parse a JCAMP-DX file
data = FileParser.parse_jcamp("spectrum.jdx")
jdx = FileParser.create_jcamp(data)

# Convert to nmrglue format
udic, d = jdx.to_nmrglue_1d()

# Create x-axis in ppm
xaxis = np.fft.fftshift(np.fft.fftfreq(udic[0]['size'], 1/udic[0]['sw']))[::-1]
if udic[0]['car'] != 999.99:
    xaxis += udic[0]['car']
    xaxis /= udic[0]['obs']

# Plot the spectrum
plt.figure(figsize=(10, 6))
plt.plot(xaxis, d)
plt.xlabel('Chemical Shift (ppm)')
plt.ylabel('Intensity')
plt.title('NMR Spectrum')
plt.gca().invert_xaxis()  # Conventional NMR display
plt.show()
```

## Contributing

Contributions to improve the library are welcome. Please feel free to submit issues or pull requests.

## License

[Specify the license here]

## Acknowledgments

This library uses the following open-source projects:
- nmrglue: For reading and processing NMR data
- RDKit: For handling chemical structures
- NumPy and SciPy: For numerical operations
