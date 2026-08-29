# DairyPulse - Phase 1 Data Foundation Layer

## Overview
This repository contains the Data Foundation Layer for Phase 1 of the DairyPulse decision-support system. It simulates a 180-day operational period for a small rural dairy-processing MSME.

## Important Note
**ALL DATA IS DEMO/SIMULATED.** None of the prices, volumes, customer names, or supplier names represent actual real-world MSME data. The data is generated based on configurable business rules.

## Data Pipeline
1. `src/data_pipeline/generator.py`: Simulates 180 days of activity.
2. `src/data_pipeline/validator.py`: Validates the generated raw data.
3. `src/data_pipeline/processor.py`: Cleans data and generates daily business snapshots.
4. `src/data_pipeline/importer.py`: Provides logic for importing legacy CSV/Excel data.

## Configuration
The `config/business_rules.json` file dictates:
- Production limits
- Conversion ratios (e.g., Milk -> Paneer)
- Selling prices
- Safety stock levels

## How to Run
Ensure `pandas` and `pytest` are installed.
```bash
python src/main.py
pytest tests/
```
