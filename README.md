# 🚆 Transit Cost Optimizer

A data pipeline + Streamlit app that parses employee shift schedules from PDFs and calculates the most cost-effective transit fare payment strategy.

## 📌 Overview

This project automates the process of analyzing commuting costs based on real work schedules.

Users can:

- Upload one or more monthly shift schedule PDFs
- Select their name and a month to consider
- Adjust commute time assumptions
- Compare transit fare payment options

The app then:

1. Extracts structured shift data from unstructured PDFs
2. Converts shifts into commute trips
3. Calculates total costs under different fare strategies
4. Displays the cheapest option and compares benifits of other payment strategies

## 🧠 Key Features

- 📄 **PDF Parsing**  
  Extracts shift data using spatial coordinates (`pdfplumber`)

- 🧮 **Commuting Logic**  
  Converts shifts into inbound/outbound trips with configurable commute time

- 💳 **Fare Optimization**  
  Compares three fare payment strategies:
  - Stored Value
  - 1-Zone Monthly Pass
  - 2-Zone Monthly Pass

- 📊 **Interactive Dashboard (Streamlit)**  
  - Cost comparison charts  
  - Savings and benifits breakdown  
  - Trip type analysis  

## 🌐 Deployment

The interactive dashboard is deployed as an app using Streamlit Cloud. You can access it with the following link:

[Streamlit Dashboard](https://compass-dash.streamlit.app/)

## 🏗️ Project Structure

```(text)
compass-dash/
│
├── app/
│ └── streamlit_app.py       # Streamlit UI
│
│── pipeline/                # ETL pipeline
│ └── run_pipeline.py
|
├── src/
│ ├── parser/               # PDF parsing logic
│ │ ├── orchestrator.py        # Wrapper
│ │ |── extractors.py          # Find relevant text
│ │ └── pdf_reader.py          # Read in all text
| |
│ ├── processing/           # Data cleaning
│ │ ├── cleaning.py            # Fix formats
│ │ |── datetime_utils.py      # Convert to datetimes
│ │ └── feature.py             # Add new features
│ │
│ ├── logic/          # Core business logic
│ │ ├── trips.py        # Shift → trip conversion
│ │ ├── costs.py        # Cost calculations
│ │ └── fares.py        # Fare models
│ │
│ ├── config/
│ │ └── fare_prices.py      # Fare constants
│
├── data/               # Optional sample data
├── notebooks/          # Demonstration
├── requirements.txt
├── environment.yml
└── README.md
```

## 💡 Motivation

This project was built to explore:

- parsing semi-structured data
- building robust data pipelines
- turning operational data into decision tools

## ⚙️ How It Works

### 1. PDF Parsing

- Extract words with coordinates
- Identify employee row
- Match shifts to date columns
- Handle multi-format layouts (e.g. split lines, merged tokens)

### 2. Data Pipeline

raw → cleaned → datetime → enriched

- Split time ranges
- Convert to datetime
- Add features (weekday, weekend, month)

### 3. Trip Generation

Each shift becomes:

- Home → Work trip (before shift)
- Work → Home trip (after shift)

Includes:

- configurable commute buffer

### 4. Cost Calculation

Trips are categorized into:

- 1-zone trips
- 2-zone trips
- YVR add-fare trips

Then evaluated across fare payment strategies.

## 🚀 Running Locally

```bash
# clone repo
git clone https://github.com/yourusername/compass-dash.git
cd compass-dash

# install dependencies
pip install -r requirements.txt

# run app
streamlit run app/streamlit_app.py
```

## 🧩 Challenges & Solutions

### PDF Parsing Variability

- Different schedule formats (multi-line, merged text)
- Solved using:
  - regex extraction
  - spatial matching (x/y coordinates)
  - row-based grouping

### Ambiguous Text Matching

- Names overlapping with shift types
- Solved using:
  - directional filtering (right-of-shift logic)
  - distance-based ranking

### Time Arithmetic

- Original HHMM integers caused issues
- Refactored to full datetime objects

### Streamlit Caching Pitfalls

- Function signature changes caused stale cache errors
- Fixed by making all inputs explicit cache arguments

## 📈 Future Improvements

- 📅 Calendar-style schedule view
- 👤 Dynamic Employee Selection (no manual input)
- 📍 Zone detection via location input
- 📊 Historical cost tracking
- 🧪 Unit tests for parsing pipeline

## 🛠️ Tech Stack

- Python
- pandas
- pdfplumber
- Streamlit

## 👤 Author

Ian MacCarthy

[GitHub](https://github.com/imax37)

## 🧠 Architecture Overview

The system is structured as a modular data pipeline:

PDF → Parser → DataFrame → Trip Logic → Cost Engine → UI


### Layers

**1. Parser (`src/parser/`)**
- Extracts structured data from PDFs using positional metadata
- Handles layout inconsistencies via spatial heuristics

**2. Pipeline (`src/pipeline/`)**
- Cleans and standardizes raw data
- Converts strings → datetime objects
- Adds derived features

**3. Business Logic (`src/logic/`)**
- Transforms shifts into commute trips
- Categorizes trips by fare rules
- Evaluates multiple pricing strategies

**4. Config (`src/config/`)**
- Centralized fare definitions

**5. UI (`app/`)**
- Streamlit dashboard
- Handles user inputs and visualization
