# codemao-cloud

A desktop tool for uploading and downloading CodeMao cloud functions

## Project Overview

CodeMao Cloud Functions (codemao-cloud) is a desktop application designed for uploading and downloading files to and from the CodeMao cloud. This project provides a graphical user interface to simplify file management and cloud data transfer.

## Features

- **File Upload**: Supports uploading local files to the CodeMao cloud
- **File Download**: Supports downloading files from the CodeMao cloud to local storage
- **Graphical Interface**: Provides a user-friendly GUI built with PyQt5
- **File Validation**: Built-in domain and file validity checking

## File Descriptions

| File | Description |
|------|-------------|
| `up.py` | Main application entry point containing core GUI code |
| `down.py` | Implementation of download functionality with file download logic |
| `index.py` | Provides functions for cloud data processing (hit_me1/hit_me2/hit_me3) |

## Dependencies

```
PyQt5
Python 3.x
```

## Installation

1. Ensure Python 3.x is installed
2. Install dependencies:

```bash
pip install PyQt5
```

## Usage

### Running the Application

```bash
python up.py
```

### Main Features

- **Select File**: Click the button in the interface to choose a local file
- **Mode Switch**: Toggle between upload and download modes
- **File Validation**: Verify file validity and display relevant information

## Project Structure

```
codemao-cloud/
├── up.py          # Main program (upload functionality + GUI)
├── down.py        # Download module
├── index.py       # Cloud API interface
├── LICENSE        # License
└── format.xml     # Configuration file
```

## License

This project is intended solely for learning and communication purposes. Please comply with relevant laws and regulations and the CodeMao platform's terms of service.

## Author

zwzhaowei

## Feedback

If you encounter any issues, please submit an Issue to the project repository.