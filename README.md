# HR Analytics: Job Change Prediction for Data Scientists

## Project Description

This project analyzes HR data to predict the employment likelihood of data scientist candidates after completing their training program. The company aims to identify candidates who are genuinely interested in working for the company or are actively seeking new job opportunities.

## Data Sources

Data was collected from various sources to create a comprehensive dataset:

1. **Candidate Information (enrollee_df)**: From Google Sheets (ID: 1VCkHwBjJGRJ21asd9pxW4_0z2PWuKhbLR3gUHm-p4GI)
2. **Educational Information (enrollies_education_df)**: From an Excel file at https://assets.swisscoding.edu.vn/company_course/enrollies_education.xlsx
3. **Work Experience (work_experience_df)**: From a CSV file at https://assets.swisscoding.edu.vn/company_course/work_experience.csv
4. **Training Hours (training_hours_df)**: From a MySQL database (table 'training_hours' in database 'company_course')
5. **City Development Index (city_development_index_df)**: From the HTML webpage at https://sca-programming-school.github.io/city_development_index/index.html
6. **Employment Status (employment_df)**: From the MySQL database (table 'employment' in database 'company_course')

## Steps Performed

### 1. Install Libraries
- Install necessary libraries: pandas, numpy, pymysql, sqlalchemy, matplotlib, seaborn, statsmodels

### 2. Load Data
- Create helper functions to load data from different sources (CSV, Excel, JSON, MySQL)
- Load data from Google Sheets, Excel files, CSV, MySQL databases, and HTML webpages

### 3. Clean Data
- Check structure and data types of each dataframe
- Handle missing values
- Convert data types for consistency
- Normalize categorical data (e.g., experience, company types, etc.)

### 4. Build Master Table
- Merge dataframes based on `enrollee_id` to create a master table with all information

### 5. Integrate Dimension Tables
- Merge additional education, work experience, and city development index data

### 6. Correlation Analysis
- Create a heatmap to visualize relationships between numerical features

### 7. Build OLS Regression Model
- Prepare data: separate target variable, apply one-hot encoding for categorical variables
- Split data into training and testing sets
- Train OLS model and evaluate results

### 8. Identify Promising Candidate Groups
- Based on model results, determine characteristics of candidates with highest employment potential

## Files in the Project

### HR_Analytics_Job_Change_of_Data_Scientists.ipynb
The original Jupyter Notebook containing the full analysis with detailed explanations, code cells, and outputs.

### hr_analytics_job_change_of_data_scientists.py
A cleaned and organized Python script version of the notebook, suitable for direct execution. This script has been refactored with:
- Removed old comments and docstrings
- Reorganized code into logical sections
- Added concise new comments for clarity
- Eliminated redundant code and unnecessary prints

### save_to_mysql.py
A standalone Python script to load, clean, and save all data tables (except master_df) to MySQL, creating a star schema with primary keys and foreign keys. This script:
- Loads data from all sources
- Applies data cleaning
- Saves dimension and fact tables to MySQL
- Adds primary keys and foreign keys for star schema relationships

## Key Findings

- **Correlation Analysis**: Heatmap reveals relationships between variables, notably the negative correlation between city development index and employment status.
- **Predictive Model**: OLS regression with R-squared ≈ 23%, explaining 23% of variance in employment status.
- **Important Factors**: City development index, experience, training hours, company type, education level, etc.
- **Promising Candidates**: Those without relevant experience, working at small or 'Other' company types, from cities with low development indices.

## How to Run

### Using the Notebook
1. Open `HR_Analytics_Job_Change_of_Data_Scientists.ipynb` in Google Colab or Jupyter Notebook
2. Execute cells in order
3. Ensure internet connection for downloading online data
4. Provide MySQL credentials for database access

### Using the Python Script (Full Analysis)
1. Ensure all dependencies are installed
2. Run `python hr_analytics_job_change_of_data_scientists.py`
3. The script will execute the full analysis and display results

### Using the Save to MySQL Script
1. Ensure all dependencies are installed
2. Update MySQL credentials in `save_to_mysql.py`
3. Run `python save_to_mysql.py`
4. The script will load, clean, and save all tables to MySQL with star schema structure

## Dependencies

- pandas
- numpy
- pymysql
- sqlalchemy
- matplotlib
- seaborn
- statsmodels
- scikit-learn (for train_test_split)
- openpyxl (for Excel file reading)
- lxml (for HTML parsing)
- html5lib (for HTML parsing)

## Conclusion

This project provides valuable insights into factors influencing post-training employment for data scientist candidates, enabling companies to make informed hiring decisions.