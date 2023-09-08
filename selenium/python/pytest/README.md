# selenium/python/pytest

## Requirements

- Python 3.9 or higher

## Activate virtual environment

```shell
python3 -m venv .venv

# on Windows powershell
.venv\Scripts\activate.ps1

# on Windows cmd
.venv\Scripts\activate.bat

# on Linux/MacOS
source .venv/bin/activate
```

## Installation

```shell
pip3 install -r requirements.txt
```

## Usage

### Desktop web test

```shell
pytest web/test_web.py --capture=no -x
```
