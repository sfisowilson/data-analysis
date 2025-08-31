#!/usr/bin/env python3
"""
Example script showing how to use the Stock Data Processor tool.
"""

from stock_data_processor import StockDataProcessor

def run_basic_analysis():
    """Run the basic stock data processing pipeline."""
    
    # Initialize the processor
    processor = StockDataProcessor(
        data_folder="Data Hand-Over",  # Folder containing your data files
        output_folder="output"         # Where reports will be saved
    )
    
    # Run the complete pipeline
    processor.run()
    
    print("\nProcessing completed! Check the 'output' folder for results.")

def run_custom_analysis():
    """Example of running individual components."""
    
    processor = StockDataProcessor("Data Hand-Over", "custom_output")
    
    # Step 1: Process all files
    processor.process_all_files()
    
    # Step 2: Save consolidated data
    processor.save_consolidated_data()
    
    # Step 3: Generate specific reports (optional - run only what you need)
    processor.generate_objective_1_report()  # Item frequency analysis
    processor.generate_objective_2_report()  # Audit trail
    # ... add other reports as needed
    
    print("Custom analysis completed!")

if __name__ == "__main__":
    # Run the basic analysis
    run_basic_analysis()
    
    # Uncomment below to run custom analysis instead
    # run_custom_analysis()
