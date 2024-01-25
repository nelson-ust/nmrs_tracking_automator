from fastapi import FastAPI, File, UploadFile, Form, HTTPException,BackgroundTasks
from fastapi.responses import FileResponse
import pandas as pd
import os
import csv
import shutil
import warnings
from datetime import datetime, timedelta
import random
from mysql.connector import Error
from repositories import visit_repository, encounter_repository, obs_repository
from helpers import database as db



app = FastAPI()

# Ensure the upload directory exists
os.makedirs('upload', exist_ok=True)


def file_exists(file_path) -> bool:
    return os.path.exists(file_path) and os.path.isfile(file_path)


def read_patient_ids_from_csv(csv_file): 
    patient_ids = {}

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        for row in reader:
            key = row[0]
            visit_date = row[1]
            track_reason = row[2]
            verify_indication = row[3]
            track_date = row[4]
            who_attempt = row[5]
            mode_comm = row[6]
            person_contacted = row[7]
            default_reason = row[8]
            discontinue_care = row[9]
            discontinue_reason = row[10]
            discontinue_date = row[11]
            referred_service = row[12]
            return_date = row[13]

            patient_ids[key] = {
                'visit_date': visit_date, 
                'track_reason': track_reason, 
                'verify_indication': verify_indication, 
                'track_date': track_date, 
                'who_attempt': who_attempt, 
                'mode_comm': mode_comm, 
                'person_contacted': person_contacted, 
                'default_reason': default_reason, 
                'discontinue_care': discontinue_care, 
                'discontinue_reason': discontinue_reason, 
                'discontinue_date': discontinue_date, 
                'referred_service': referred_service, 
                'return_date': return_date
            }

    return patient_ids

def ingest_data_into_database(csv_file: str):
    connection = db.connect_to_database()
    if not connection:
        print("Database connection failed")
        return

    patient_ids = read_patient_ids_from_csv(csv_file)
    current_time = datetime.now()
    tracking_forms_created = 0

    try:
        for patient_id, patient_data in patient_ids.items():
            # Extracting all fields from the patient data
            visit_date = patient_data['visit_date']
            track_reason = patient_data['track_reason']
            verify_indication = patient_data['verify_indication']
            track_date = patient_data['track_date']
            who_attempt = patient_data['who_attempt']
            mode_comm = patient_data['mode_comm']
            person_contacted = patient_data['person_contacted']
            default_reason = patient_data['default_reason']
            discontinue_care = patient_data['discontinue_care']
            discontinue_reason = patient_data['discontinue_reason']
            discontinue_date = patient_data['discontinue_date']
            referred_service = patient_data['referred_service']
            return_date = patient_data['return_date']

            # Processing visit data
            visit_data = visit_repository.visit_list(connection, {patient_id: visit_date})
            for visit_info in visit_data:
                visit_info.date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                visit_repository.insert_visit_data(connection, visit_info)

            # Processing encounter data
            tracking_encounter_data = encounter_repository.tracking_encounter_list(connection, [patient_id])           
            for encounter_info in tracking_encounter_data:
                encounter_repository.insert_encounter_data(connection, encounter_info)

            # Processing observation data
            tracking_obs_data = obs_repository.tracking_obs_list(connection, {patient_id: [track_reason, verify_indication, track_date, who_attempt, mode_comm, person_contacted, default_reason, discontinue_care, discontinue_reason, discontinue_date, referred_service, return_date]}) 
            for observation_info in tracking_obs_data:
                obs_repository.insert_obs_data(connection, observation_info)

            # Update tracking group ID if required
            obs_repository.update_tracking_group_id(connection, [patient_id])

            tracking_forms_created += 1

        print(f"Number of patients for whom tracking form was created: {tracking_forms_created}")

    except Error as e:
        print("Error during database operation:", e)
    finally:
        connection.close()

@app.post("/ingest-data/")
async def ingest_data(background_tasks: BackgroundTasks, csv_file_path: str):
    background_tasks.add_task(ingest_data_into_database, csv_file_path)
    return {"message": "Data ingestion started"}


@app.post("/process-file/")
async def process_file(file: UploadFile = File(...), who_attempted: str = Form(...)):
    # Validate if the uploaded file is an .xlsx file
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are accepted.")

    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore", category=UserWarning)
            df = pd.read_excel(temp_file_path)

        df = clean_and_process_data(df, who_attempted)
    except KeyError as e:
        os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail=f"Column not found in the file: {e}")
    except Exception as e:
        os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing the file: {e}")

    output_file_path = os.path.join("upload", "verification_outcome.csv")
    df.to_csv(output_file_path, index=False)
    os.remove(temp_file_path)
    return FileResponse(output_file_path, media_type='application/octet-stream', filename="verification_outcome.csv")


'''
def clean_and_process_data(df: pd.DataFrame, who_attempted: str) -> pd.DataFrame:
    # Filter and rename columns as per the original script
    if all(col in df.columns for col in ['Unique ID', 'Triggers Interpretation', 'Tracking Attempt 1(date)', 'Valid or Invalid']):
        df = df[['Unique ID', 'Triggers Interpretation', 'Tracking Attempt 1(date)', 'Valid or Invalid', 'Date of Termination(if yes)', 'Date returned to care(if valid & retained)']]
        df.rename(columns={'Unique ID': 'PatientID', 
                           'Triggers Interpretation': 'Indication for Client Verification', 
                           'Tracking Attempt 1(date)': 'Tracking Date', 
                           'Valid or Invalid': 'Patient Care in Facility Discontinued ?'}, inplace=True)
    else:
        # Handle case where required columns are not present
        raise ValueError("Required columns are missing in the uploaded file")

    # Setting column values as per your script logic
    df['ReasonForTracking'] = 'Other'
    df['Who_Attempted'] = who_attempted
    df['ModeOfCommunication'] = 'Mobile Phone'
    df['Person_contacted'] = 'Patient'
    df['Reason_for_Defaulting'] = 'Others(Specify)'
    df['Reason for Discontinuation'] = None
    df['Referred for'] = None

    # Map values for 'Patient Care in Facility Discontinued ?'
    df['Patient Care in Facility Discontinued ?'] = df['Patient Care in Facility Discontinued ?'].map({'Valid': 'No', 'Invalid': 'Yes'})
    df.loc[df['Patient Care in Facility Discontinued ?'] == 'Yes', 'Reason for Discontinuation'] = 'Could not verify client'
    df.loc[df['Patient Care in Facility Discontinued ?'] == 'No', 'Referred for'] = 'Adherence Counseling'

    # Convert date columns to the desired format
    df['Tracking Date'] = pd.to_datetime(df['Tracking Date'], errors='coerce').dt.strftime("%d/%m/%Y")
    df['Date returned to care(if valid & retained)'] = pd.to_datetime(df['Date returned to care(if valid & retained)'], errors='coerce').dt.strftime("%d/%m/%Y")
    
    df['VisitDate'] = df['Tracking Date']

    # Reorder columns based on the desired index positions
    column_order = [
        'PatientID', 'VisitDate', 'ReasonForTracking', 'Indication for Client Verification', 'Tracking Date',
        'Who_Attempted', 'ModeOfCommunication', 'Person_contacted', 'Reason_for_Defaulting',
        'Patient Care in Facility Discontinued ?', 'Reason for Discontinuation',
        'Date of Termination(if yes)', 'Referred for', 'Date returned to care(if valid & retained)'
    ]
    df = df.reindex(columns=column_order)

    return df
'''

def clean_and_process_data(df: pd.DataFrame, who_attempted: str) -> pd.DataFrame:
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df_processed = df.copy()

    # Renaming columns and handling transformations
    df_processed.rename(columns={
        'Unique ID': 'PatientID',
        'Triggers Interpretation': 'Indication for Client Verification',
        'Tracking Attempt 1(date)': 'Tracking Date',
        'Valid or Invalid': 'Patient Care in Facility Discontinued ?'
    }, inplace=True)

    # Setting new values and handling transformations
    df_processed['ReasonForTracking'] = 'Other'
    df_processed['Who_Attempted'] = who_attempted
    df_processed['ModeOfCommunication'] = 'Mobile Phone'
    df_processed['Person_contacted'] = 'Patient'
    df_processed['Reason_for_Defaulting'] = 'Others(Specify)'
    df_processed['Reason for Discontinuation'] = None
    df_processed['Referred for'] = None

    df_processed['Patient Care in Facility Discontinued ?'] = df_processed['Patient Care in Facility Discontinued ?'].map({'Valid': 'No', 'Invalid': 'Yes'})

    # Handling date transformations
    df_processed['Tracking Date'] = pd.to_datetime(df_processed['Tracking Date'], errors='coerce').dt.strftime("%d/%m/%Y")
    df_processed['Date returned to care(if valid & retained)'] = pd.to_datetime(df_processed['Date returned to care(if valid & retained)'], errors='coerce').dt.strftime("%d/%m/%Y")
    
    df_processed['VisitDate'] = df_processed['Tracking Date']

    # Reorder columns based on the desired index positions
    column_order = [
        'PatientID', 'VisitDate', 'ReasonForTracking', 'Indication for Client Verification', 'Tracking Date',
        'Who_Attempted', 'ModeOfCommunication', 'Person_contacted', 'Reason_for_Defaulting',
        'Patient Care in Facility Discontinued ?', 'Reason for Discontinuation',
        'Date of Termination(if yes)', 'Referred for', 'Date returned to care(if valid & retained)'
    ]
    df_processed = df_processed.reindex(columns=column_order)
    return df_processed


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
