
'''

import os
import pandas as pd

def read_excel_file(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def clean_data() ->None:
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.realpath(__file__))

    print("Current working directory:", os.getcwd())
    print("Script directory:", script_directory)

    # Move up one level in the directory structure
    parent_directory = os.path.dirname(script_directory)
    os.chdir(parent_directory)

    print("Updated working directory:", os.getcwd())

    # Construct the correct file path
    file_path = os.path.join("upload", "amachara_tracking_outcome.xlsx")

    print("Full file path:", file_path)

    verification_list = read_excel_file(file_path)

    if verification_list is None:
        return

    #Filter out Data from linelist
    verification_data = verification_list[['Unique ID', 'Triggers Interpretation', 'Tracking Attempt 1(date)', 'Valid or Invalid', 'Date of Termination(if yes)', 'Date returned to care(if valid & retained)' ]].rename(columns={'Unique ID':'PatientID','Triggers Interpretation':'Indication for Client Verification', 'Tracking Attempt 1(date)':'Tracking Date', 'Valid or Invalid':'Patient Care in Facility Discontinued ?'})

    #Additional columns
    visit_date = pd.to_datetime(input("Type in your Visit Date (dd/mm/YYYY): "), format="%d/%m/%Y")
    who_attempted = input("Name of the Facility Tracker: ")

    verification_data.insert(1, 'VisitDate', visit_date)
    verification_data.insert(2, 'ReasonForTracking', 'Other')
    verification_data.insert(5, 'Who_Attempted', who_attempted)
    verification_data.insert(6, 'ModeOfCommunication', 'Mobile Phone')
    verification_data.insert(7, 'Person_contacted', 'Patient')
    verification_data.insert(8, 'Reason_for_Defaulting', 'Others(Specify)')
    verification_data.insert(10, 'Reason for Discontinuation', None)
    verification_data.insert(12, 'Referred for', None)
    verification_data.loc[:, 'Patient Care in Facility Discontinued ?'] = verification_data['Patient Care in Facility Discontinued ?'].replace('Valid', 'No')
    verification_data.loc[:, 'Patient Care in Facility Discontinued ?'] = verification_data['Patient Care in Facility Discontinued ?'].replace('Invalid', 'Yes')
    verification_data.loc[verification_data['Patient Care in Facility Discontinued ?'] == 'Yes', 'Reason for Discontinuation'] = verification_data['Reason for Discontinuation'].fillna('Could not verify client')
    verification_data.loc[verification_data['Patient Care in Facility Discontinued ?'] == 'No', 'Referred for'] = verification_data['Referred for'].fillna('Adherence Counseling')
    verification_data['Tracking Date'] = pd.to_datetime(verification_data['Tracking Date'], format="%d/%m/%Y")
    verification_data['Tracking Date'] = verification_data['Tracking Date'].dt.strftime("%d/%m/%Y")
    verification_data['Date returned to care(if valid & retained)'] = pd.to_datetime(verification_data['Date returned to care(if valid & retained)'], format="%d/%m/%Y")
    verification_data['Date returned to care(if valid & retained)'] = verification_data['Date returned to care(if valid & retained)'].dt.strftime("%d/%m/%Y")

    #Data Export as CSV file
    verification_data.to_csv(os.path.join("upload", "verification_outcome.csv"), index=False)

    print("Data has been cleaned and exported successfully")

clean_data()
'''

import os
import pandas as pd
import warnings
''' 
def read_excel_file(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
'''
def read_excel_file(file_path):
    try:
        with warnings.catch_warnings():
            # Suppress the Data Validation warning
            warnings.simplefilter("ignore", category=UserWarning)
            return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def set_column_values(df):
    # Additional columns
    df['VisitDate'] = pd.to_datetime(input("Type in your Visit Date (dd/mm/YYYY): "), format="%d/%m/%Y")
    df['ReasonForTracking'] = 'Other'
    df['Who_Attempted'] = input("Name of the Facility Tracker: ")
    df['ModeOfCommunication'] = 'Mobile Phone'
    df['Person_contacted'] = 'Patient'
    df['Reason_for_Defaulting'] = 'Others(Specify)'
    df['Reason for Discontinuation'] = None
    df['Referred for'] = None

    # Map values for 'Patient Care in Facility Discontinued ?'
    df['Patient Care in Facility Discontinued ?'] = df['Patient Care in Facility Discontinued ?'].map({'Valid': 'No', 'Invalid': 'Yes'})

    # Set specific values based on conditions
    df.loc[df['Patient Care in Facility Discontinued ?'] == 'Yes', 'Reason for Discontinuation'] = df['Reason for Discontinuation'].fillna('Could not verify client')
    df.loc[df['Patient Care in Facility Discontinued ?'] == 'No', 'Referred for'] = df['Referred for'].fillna('Adherence Counseling')

    # Convert date columns to the desired format
    df['Tracking Date'] = pd.to_datetime(df['Tracking Date'], format="%d/%m/%Y").dt.strftime("%d/%m/%Y")
    df['Date returned to care(if valid & retained)'] = pd.to_datetime(df['Date returned to care(if valid & retained)'], format="%d/%m/%Y").dt.strftime("%d/%m/%Y")

    return df

def clean_and_export_data(file_path:str)->None:
    verification_list = read_excel_file(file_path)

    if verification_list is None:
        return

    # Filter out relevant columns
    verification_data = verification_list[['Unique ID', 'Triggers Interpretation', 'Tracking Attempt 1(date)', 'Valid or Invalid', 'Date of Termination(if yes)', 'Date returned to care(if valid & retained)']] \
        .rename(columns={'Unique ID': 'PatientID', 'Triggers Interpretation': 'Indication for Client Verification', 'Tracking Attempt 1(date)': 'Tracking Date', 'Valid or Invalid': 'Patient Care in Facility Discontinued ?'})

    verification_data = set_column_values(verification_data)

    # Data Export as CSV file
    output_path = os.path.join("upload", "verification_outcome.csv")
    verification_data.to_csv(output_path, index=False)

    print(f"Data has been cleaned and exported successfully to {output_path}")

def main() ->None:
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.realpath(__file__))

    print("Current working directory:", os.getcwd())
    print("Script directory:", script_directory)

    # Move up one level in the directory structure
    parent_directory = os.path.dirname(script_directory)
    os.chdir(parent_directory)

    print("Updated working directory:", os.getcwd())

    # Prompt user for the Excel file name
    file_name = input("Enter the Excel file name (including extension, e.g., example.xlsx): ")
    file_path = os.path.join("upload", file_name)

    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_name}' not found in the 'upload' directory.")
        return

    clean_and_export_data(file_path)

if __name__ == "__main__":
    main()

