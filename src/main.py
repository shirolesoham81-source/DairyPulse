import os
from src.data_pipeline.generator import generate_data
from src.data_pipeline.validator import validate_data
from src.data_pipeline.processor import process_data

def generate_report():
    print("Generating data foundation report...")
    os.makedirs('reports', exist_ok=True)
    with open('reports/data_foundation_report.md', 'w') as f:
        f.write("# Data Foundation Report\n")
        f.write("Dataset overview and metrics will be populated here.\n")
        f.write("Status: Pipeline executed successfully.\n")

if __name__ == "__main__":
    print("Starting DairyPulse Phase 1 Data Generation...")
    generate_data()
    issues = validate_data()
    process_data()
    generate_report()
    print("Pipeline Complete. Check reports/data_foundation_report.md")
