# Script to save cleaned dataframes to MySQL for star schema
# This script loads and cleans the data, then saves all tables except master_df to MySQL

import pandas as pd
import pymysql
import sqlalchemy
from sqlalchemy import create_engine, text

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

db_name = 'company_course'  # Update with actual database name
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

# Save all tables except master_df to MySQL for star schema
# MySQL connection details (update with your actual credentials)
# db_type = 'mysql'
# db_host = 'your_host'  # e.g., '112.213.86.31'
# db_port = 'your_port'  # e.g., '3360'
# db_user = 'your_username'  # e.g., 'etl_practice'
# db_password = 'your_password'  # e.g., '550814'
# db_name = 'your_database'  # e.g., 'company_course'
db_type = 'mysql'
db_host = 'localhost'  # e.g., '112.213.86.31'
db_port = '3306'  # e.g., '3360'
db_user = 'Tuan'  # e.g., 'etl_practice'
db_password = 'Tuan1234'  # e.g., '550814'
db_name = 'HR-Analytics-Job-Change'  # e.g., 'company_course'

engine = create_engine(f'{db_type}+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Save dimension and fact tables to MySQL
enrollee_df.to_sql('enrollee', engine, if_exists='replace', index=False)
enrollies_education_df.to_sql('enrollies_education', engine, if_exists='replace', index=False)
work_experience_df.to_sql('work_experience', engine, if_exists='replace', index=False)
training_hours_df.to_sql('training_hours', engine, if_exists='replace', index=False)
city_development_index_df.to_sql('city_development_index', engine, if_exists='replace', index=False)
employment_df.to_sql('employment', engine, if_exists='replace', index=False)

# Define primary keys and foreign keys for star schema
with engine.connect() as conn:
    # Add primary keys
    conn.execute(text("ALTER TABLE enrollee ADD PRIMARY KEY (enrollee_id)"))
    conn.execute(text("ALTER TABLE enrollies_education ADD PRIMARY KEY (enrollee_id)"))
    conn.execute(text("ALTER TABLE work_experience ADD PRIMARY KEY (enrollee_id)"))
    conn.execute(text("ALTER TABLE training_hours ADD PRIMARY KEY (enrollee_id)"))
    conn.execute(text("ALTER TABLE city_development_index ADD PRIMARY KEY (City(255))"))
    conn.execute(text("ALTER TABLE employment ADD PRIMARY KEY (enrollee_id)"))

    # Modify city column to VARCHAR for foreign key
    conn.execute(text("ALTER TABLE enrollee MODIFY city VARCHAR(255)"))
    conn.execute(text("ALTER TABLE city_development_index MODIFY City VARCHAR(255)"))

    # Add foreign keys
    conn.execute(text("ALTER TABLE enrollies_education ADD CONSTRAINT fk_enrollee_edu FOREIGN KEY (enrollee_id) REFERENCES enrollee(enrollee_id)"))
    conn.execute(text("ALTER TABLE work_experience ADD CONSTRAINT fk_enrollee_work FOREIGN KEY (enrollee_id) REFERENCES enrollee(enrollee_id)"))
    conn.execute(text("ALTER TABLE training_hours ADD CONSTRAINT fk_enrollee_train FOREIGN KEY (enrollee_id) REFERENCES enrollee(enrollee_id)"))
    conn.execute(text("ALTER TABLE employment ADD CONSTRAINT fk_enrollee_emp FOREIGN KEY (enrollee_id) REFERENCES enrollee(enrollee_id)"))
    conn.execute(text("ALTER TABLE enrollee ADD CONSTRAINT fk_city FOREIGN KEY (city) REFERENCES city_development_index(City)"))

print("Primary keys and foreign keys added for star schema.")