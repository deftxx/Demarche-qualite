import pandas as pd
import numpy as np

def validate_csv_structure(df, required_columns=None):
    """
    Validate the structure of a CSV file
    
    Args:
        df (pandas.DataFrame): The dataframe to validate
        required_columns (list, optional): List of required column names
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "CSV file is empty."
    
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    return True, ""

def clean_data(df):
    """
    Clean the dataframe by handling missing values and converting data types
    
    Args:
        df (pandas.DataFrame): The dataframe to clean
        
    Returns:
        pandas.DataFrame: The cleaned dataframe
    """
    # Make a copy to avoid modifying the original
    cleaned_df = df.copy()
    
    # Convert numeric columns to numeric type
    for col in cleaned_df.columns:
        try:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col])
        except:
            # If conversion fails, it's probably not a numeric column
            pass
    
    # Handle missing values
    numeric_cols = cleaned_df.select_dtypes(include=np.number).columns
    categorical_cols = cleaned_df.select_dtypes(exclude=np.number).columns
    
    # Fill missing numeric values with the median
    if not numeric_cols.empty:
        cleaned_df[numeric_cols] = cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].median())
    
    # Fill missing categorical values with "Unknown"
    if not categorical_cols.empty:
        cleaned_df[categorical_cols] = cleaned_df[categorical_cols].fillna("Unknown")
    
    return cleaned_df

def sample_data_generator(data_type):
    """
    Generate sample data for demonstration purposes
    
    Args:
        data_type (str): Type of data to generate ("pareto", "histogram", etc.)
        
    Returns:
        pandas.DataFrame: DataFrame with sample data
    """
    if data_type == "pareto":
        # Sample data for Pareto chart
        categories = ["Product Defects", "Late Delivery", "Incomplete Orders", 
                     "Wrong Item", "Damaged Packaging", "Customer Service",
                     "Website Issues", "Payment Problems"]
        
        values = [145, 89, 76, 52, 37, 24, 18, 11]
        
        return pd.DataFrame({
            "Category": categories,
            "Count": values
        })
    
    elif data_type == "histogram":
        # Sample data for histogram - normally distributed
        np.random.seed(42)
        values = np.random.normal(100, 15, 100).round(2)
        
        return pd.DataFrame({
            "Value": values
        })
    
    elif data_type == "5whys":
        # Sample data for 5 Whys
        problem = "Machine stopped working"
        whys = [
            "Overheating",
            "Coolant pump failed",
            "Pump maintenance was missed",
            "Maintenance schedule not followed",
            "No notification system for maintenance tasks"
        ]
        
        return {
            "problem": problem,
            "whys": whys
        }
    
    else:
        return None
