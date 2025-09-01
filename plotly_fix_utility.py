# Plotly Fix Utility for Enhanced Dashboard
# This script provides helper functions to avoid common Plotly errors

import pandas as pd

def safe_scatter_plot(df, x, y, **kwargs):
    """
    Create a safe scatter plot that handles DataFrame requirements properly.
    
    Args:
        df: DataFrame containing the data
        x: Column name for x-axis
        y: Column name for y-axis
        **kwargs: Additional arguments for px.scatter
    
    Returns:
        Plotly figure object
    """
    import plotly.express as px
    
    # Ensure we have a proper DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame")
    
    # Check if required columns exist
    if x not in df.columns:
        raise ValueError(f"Column '{x}' not found in DataFrame")
    if y not in df.columns:
        raise ValueError(f"Column '{y}' not found in DataFrame")
    
    # Handle size parameter safely
    if 'size' in kwargs:
        size_col = kwargs['size']
        if isinstance(size_col, str) and size_col not in df.columns:
            raise ValueError(f"Size column '{size_col}' not found in DataFrame")
    
    # Handle color parameter safely
    if 'color' in kwargs:
        color_col = kwargs['color']
        if isinstance(color_col, str) and color_col not in df.columns:
            raise ValueError(f"Color column '{color_col}' not found in DataFrame")
    
    return px.scatter(df, x=x, y=y, **kwargs)

def check_dataframe_columns(df, required_columns):
    """
    Check if a DataFrame has all required columns.
    
    Args:
        df: DataFrame to check
        required_columns: List of required column names
    
    Returns:
        tuple: (bool, list) - (all_present, missing_columns)
    """
    if not isinstance(df, pd.DataFrame):
        return False, ["Not a DataFrame"]
    
    missing = [col for col in required_columns if col not in df.columns]
    return len(missing) == 0, missing

def validate_plotly_data(df, chart_type, **kwargs):
    """
    Validate data before creating Plotly charts.
    
    Args:
        df: DataFrame containing the data
        chart_type: Type of chart ('scatter', 'bar', 'line', etc.)
        **kwargs: Chart-specific arguments
    
    Returns:
        dict: Validation results with 'valid' and 'message' keys
    """
    if not isinstance(df, pd.DataFrame):
        return {'valid': False, 'message': 'Data must be a pandas DataFrame'}
    
    if df.empty:
        return {'valid': False, 'message': 'DataFrame is empty'}
    
    # Chart-specific validations
    if chart_type == 'scatter':
        required = ['x', 'y']
        for param in required:
            if param in kwargs:
                col = kwargs[param]
                if isinstance(col, str) and col not in df.columns:
                    return {'valid': False, 'message': f"Column '{col}' not found for {param} parameter"}
        
        # Check optional parameters
        optional = ['size', 'color', 'hover_data']
        for param in optional:
            if param in kwargs:
                col = kwargs[param]
                if isinstance(col, str) and col not in df.columns:
                    return {'valid': False, 'message': f"Column '{col}' not found for {param} parameter"}
                elif isinstance(col, list):
                    missing = [c for c in col if c not in df.columns]
                    if missing:
                        return {'valid': False, 'message': f"Columns {missing} not found for {param} parameter"}
    
    return {'valid': True, 'message': 'Data validation passed'}

# Example usage patterns for common fixes:

def fix_authorization_scatter(official_freq_df):
    """Fix for authorization pattern scatter plot."""
    validation = validate_plotly_data(
        official_freq_df, 
        'scatter',
        x='Transaction_Count',
        y='Mean_Amount', 
        size='Total_Amount',
        color='CV'
    )
    
    if not validation['valid']:
        raise ValueError(f"Data validation failed: {validation['message']}")
    
    return safe_scatter_plot(
        official_freq_df,
        x='Transaction_Count',
        y='Mean_Amount',
        size='Total_Amount',
        color='CV',
        hover_name=official_freq_df.index,
        title="Official Authorization Patterns",
        labels={
            'Transaction_Count': 'Transaction Count', 
            'Mean_Amount': 'Mean Authorization Amount (R)'
        }
    )

if __name__ == "__main__":
    # Test the fixes
    print("Plotly fix utility loaded successfully!")
    print("Available functions:")
    print("- safe_scatter_plot()")
    print("- check_dataframe_columns()")
    print("- validate_plotly_data()")
    print("- fix_authorization_scatter()")
