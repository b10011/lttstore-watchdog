# New product watchdog for LTTStore.com

## Installation

```python3
pip3 install -r requirements.txt
```

## Usage

```python3
python3 main.py loadproducts urls.txt
python3 main.py --browser &lt;browserpath&gt; --existing-products urls.txt --interval 0.5
```

where `<browserpath>` is the path to your browser binary, e. g. `/usr/bin/google-chrome-stable`
