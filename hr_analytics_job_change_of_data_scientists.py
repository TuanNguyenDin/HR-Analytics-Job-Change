# Import necessary libraries
import pandas as pd
import numpy as np
import pymysql
import sqlalchemy
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split

# Install pymysql if not already installed
# !pip install pymysql

# Define utility functions for data loading
def load_data(file_path, file_type=None):
    """Load data from various file formats."""
    df = None
    if file_type is None:
        if isinstance(file_path, str):
            if file_path.endswith('.csv'):
                file_type = 'csv'
            elif file_path.endswith(('.xls', '.xlsx')):
                file_type = 'excel'
            elif file_path.endswith('.json'):
                file_type = 'json'
            else:
                print(f"Could not infer file type from extension for '{file_path}'. Please provide 'file_type' argument.")
                return None
        else:
            print("Invalid file_path type. Must be a string.")
            return None

    print(f"Attempting to load data from: {file_path} as {file_type.upper()}")

    try:
        if file_type.lower() == 'csv':
            df = pd.read_csv(file_path)
        elif file_type.lower() == 'excel':
            df = pd.read_excel(file_path)
        elif file_type.lower() == 'json':
            df = pd.read_json(file_path)
        else:
            print(f"Unsupported file type: {file_type}")
            return None
        print(f"Successfully loaded data from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None

def read_sql_table(db_name, db_table):
    """Read data from MySQL database table."""
    db_type = 'mysql'
    db_host = '112.213.86.31'
    db_port = '3360'
    db_user = 'etl_practice'
    db_password = '550814'

    print(f'Connecting to sql server: {db_host}:{db_port}')
    engine = create_engine(f'{db_type}+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    return pd.read_sql_table(db_table, engine)

def fill_missing_values(df, col, val):
    """Fill missing values in a DataFrame column."""
    df[col].fillna(val, inplace=True)
    return df

def convert_columns_to_dtype(df, columns_to_convert, target_dtype):
    """Convert specified columns to a target data type."""
    print(f"\nConverting applicable columns to '{target_dtype}' dtype...")
    for col in columns_to_convert:
        if col in df.columns:
            if df[col].dtype != target_dtype:
                try:
                    df[col] = df[col].astype(target_dtype)
                    print(f"  Converted column '{col}' to '{target_dtype}' dtype.")
                except Exception as e:
                    print(f"  Could not convert column '{col}' to '{target_dtype}' dtype: {e}")
            else:
                print(f"  Column '{col}' is already of '{target_dtype}' dtype.")
        else:
            print(f"  Column '{col}' not found in DataFrame.")
    print(f"\nUpdated DataFrame info after conversion:")
    df.info()
    return df

# Load data from various sources
google_sheet_id = '1VCkHwBjJGRJ21asd9pxW4_0z2PWuKhbLR3gUHm-p4GI'
enrollee_df = pd.read_excel(f'https://docs.google.com/spreadsheets/d/{google_sheet_id}/export?format=xlsx')

file_url = 'https://assets.swisscoding.edu.vn/company_course/enrollies_education.xlsx'
enrollies_education_df = load_data(file_url)

url_file = 'https://assets.swisscoding.edu.vn/company_course/work_experience.csv'
work_experience_df = load_data(url_file, file_type='csv')

db_name = 'company_course'
training_hours_df = read_sql_table(db_name, 'training_hours')

url = 'https://sca-programming-school.github.io/city_development_index/index.html'
city_development_index_df = pd.read_html(url)[0]

employment_df = read_sql_table(db_name, 'employment')

# Data cleaning section
# Clean enrollee_df
columns_to_convert_enrollee = [col for col in enrollee_df.columns if col != 'enrollee_id']
enrollee_df = convert_columns_to_dtype(enrollee_df, columns_to_convert_enrollee, 'string')
fill_missing_values(enrollee_df, 'gender', 'Non-binary')

# Clean enrollies_education_df
columns_to_convert_edu = [col for col in enrollies_education_df.columns if col != 'enrollee_id']
enrollies_education_df = convert_columns_to_dtype(enrollies_education_df, columns_to_convert_edu, 'string')
fill_missing_values(enrollies_education_df, 'enrolled_university', 'no_enrollment')
fill_missing_values(enrollies_education_df, 'education_level', 'Primary School')
fill_missing_values(enrollies_education_df, 'major_discipline', 'STEM')

# Clean work_experience_df
work_experience_df['company_type'].fillna('Other', inplace=True)
col_string = ['company_type', 'relevent_experience']
work_experience_df = convert_columns_to_dtype(work_experience_df, col_string, 'string')

work_experience_df['experience'] = work_experience_df['experience'].fillna(-1)
work_experience_df['experience'] = work_experience_df['experience'].replace({'<1': 0, '>20': 99})
work_experience_df['experience'] = work_experience_df['experience'].astype(int)

company_size_mapping = {
    '<10': 'Very Small',
    '10/49': 'Small',
    '50-99': 'Small-Medium',
    '100-500': 'Medium',
    '500-999': 'Medium-Large',
    '1000-4999': 'Large',
    '5000-9999': 'Very Large',
    '10000+': 'Extra Large'
}
work_experience_df['company_size_category'] = work_experience_df['company_size'].replace(company_size_mapping)
work_experience_df['company_size_category'] = work_experience_df['company_size_category'].fillna('Unknown')
work_experience_df['company_size_category'] = work_experience_df['company_size_category'].astype('string')

work_experience_df['last_new_job'] = work_experience_df['last_new_job'].replace({'never': 0, '>4': 5})
work_experience_df['last_new_job'] = work_experience_df['last_new_job'].fillna(-1)
work_experience_df['last_new_job'] = work_experience_df['last_new_job'].astype(int)

# Clean city_development_index_df
city_development_index_df['City'] = city_development_index_df['City'].astype('string')

# Construct master DataFrame by merging all data sources
master_df = pd.merge(enrollee_df, training_hours_df, on='enrollee_id', how='inner')
master_df = pd.merge(master_df, employment_df, on='enrollee_id', how='inner')
master_df = pd.merge(master_df, enrollies_education_df, on='enrollee_id', how='inner')
master_df = pd.merge(master_df, work_experience_df, on='enrollee_id', how='inner')

city_development_index_df = city_development_index_df.rename(columns={'City': 'city'})
master_df = pd.merge(master_df, city_development_index_df, on='city', how='inner')

master_df = master_df.drop('company_size', axis=1)

# Correlation analysis
numerical_cols = master_df.select_dtypes(include=['int64', 'float64'])
correlation_matrix = numerical_cols.corr()

plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix of Numerical Features in Master DataFrame')
plt.show()

# OLS Regression Model
y = master_df['employed']
X = master_df.drop(['employed', 'enrollee_id', 'full_name'], axis=1)

categorical_cols = X.select_dtypes(include='string').columns.tolist()
X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
X = X.astype(float)
X = sm.add_constant(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = sm.OLS(y_train, X_train)
results = model.fit()
print(results.summary())