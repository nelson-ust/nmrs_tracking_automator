
import os
import pandas as pd
import warnings

def read_excel_file(file_path):
    try:
        with warnings.catch_warnings():
            # Suppress the Data Validation warning
            warnings.simplefilter("ignore", category=UserWarning)
            return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def set_column_values(df: pd.DataFrame) -> pd.DataFrame:
    # If 'VisitDate' column already exists and is in the correct format
    '''
    if 'VisitDate' in df.columns and pd.api.types.is_datetime64_any_dtype(df['VisitDate']):
        df['VisitDate'] = df['VisitDate'].dt.strftime("%d/%m/%Y")
    else:
        # If 'VisitDate' column does not exist or is not in the correct format
        visit_date = input("Visit Date (dd/mm/YYYY): ")
        df['VisitDate'] = pd.to_datetime(visit_date, format="%d/%m/%Y", errors='coerce').strftime("%d/%m/%Y")
    '''
    who_attempted = input("Name of the Facility Tracker: ")

    df['ReasonForTracking'] = 'Other'
    df['Who_Attempted'] = who_attempted
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
    
    df['VisitDate']=df['Tracking Date']

    # Reorder columns based on the desired index positions
    column_order = [
        'PatientID', 'VisitDate', 'ReasonForTracking', 'Indication for Client Verification', 'Tracking Date',
        'Who_Attempted', 'ModeOfCommunication', 'Person_contacted', 'Reason_for_Defaulting',
        'Patient Care in Facility Discontinued ?', 'Reason for Discontinuation',
        'Date of Termination(if yes)', 'Referred for', 'Date returned to care(if valid & retained)'
    ]

    df = df[column_order]

    return df

def clean_and_export_data(file_path: str) -> None:
    verification_list = read_excel_file(file_path)

    if verification_list is None:
        return

    # Filter out relevant columns
    verification_data = verification_list[['Unique ID', 'Triggers', 'Tracking Attempt 1(date)', 'Valid or Invalid', 'Date of Termination(if yes)', 'Date returned to care(if valid & retained)']] \
        .rename(columns={'Unique ID': 'PatientID', 'Triggers': 'Indication for Client Verification', 'Tracking Attempt 1(date)': 'Tracking Date', 'Valid or Invalid': 'Patient Care in Facility Discontinued ?'})

    verification_data = set_column_values(verification_data)

    # Data Export as CSV file
    output_path = os.path.join("upload", "verification_outcome.csv")
    verification_data.to_csv(output_path, index=False)

    print(f"Data has been cleaned and exported successfully to {output_path}")

def main() -> None:
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
# 0703 139 0284