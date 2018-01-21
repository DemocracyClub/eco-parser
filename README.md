# ECO Parser

Parse ward lists from Electoral Change Orders on http://www.legislation.gov.uk/

## Installation

```
pip install git+git://github.com/DemocracyClub/eco-parser.git
```

## Usage

### On the console

```
eco_parser "http://www.legislation.gov.uk/uksi/2017/1067/schedule/1/made/data.xml" > out.csv
```

### As a library

```python
from eco_parser import EcoParser
p = EcoParser("http://www.legislation.gov.uk/uksi/2017/1067/schedule/1/made/data.xml")
p.parse()
```
