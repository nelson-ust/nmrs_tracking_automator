from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Request, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import csv
import shutil
import warnings
from datetime import datetime
from mysql.connector import Error
from repositories import visit_repository, encounter_repository, obs_repository
from helpers import database as db

app = FastAPI()

# Setup for static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure the upload directory exists
os.makedirs('upload', exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.post("/ingest-data/")
async def ingest_data(request: Request, background_tasks: BackgroundTasks, websocket: WebSocket, file: UploadFile = File(...)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Accept the WebSocket connection
        await websocket.accept()

        # Add the task of ingesting data into the background with WebSocket
        background_tasks.add_task(ingest_data_into_database, temp_file_path, websocket)

        # Render the HTML template
        return templates.TemplateResponse("data_ingestion_started.html", {"request": request, "message": "Data ingestion started"})
    except Exception as e:
        await websocket.send_text(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def ingest_data_into_database(csv_file: str, websocket: WebSocket):
    connection = db.connect_to_database()
    if not connection:
        await websocket.send_text("Database connection failed")
        return

    patient_ids = read_patient_ids_from_csv(csv_file)
    total_patients = len(patient_ids)
    processed_patients = 0

    try:
        for patient_id, patient_data in patient_ids.items():
            # ... existing processing logic ...
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
            processed_patients += 1
            progress = (processed_patients / total_patients) * 100
            await websocket.send_text(f"Processed {processed_patients}/{total_patients} patients ({progress:.2f}%)")

        await websocket.send_text("Data ingestion completed successfully")

    except Error as e:
        await websocket.send_text(f"Error during database operation: {str(e)}")
    finally:
        connection.close()

# Other helper functions remain unchanged...
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


def clean_and_process_data(df: pd.DataFrame, who_attempted: str) -> pd.DataFrame:
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df_processed = df.copy()

    # Renaming columns and handling transformations
    df_processed.rename(columns={
        'Unique ID': 'PatientID',
        'Triggers': 'Indication for Client Verification',
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

     # Set specific values based on conditions
    df_processed.loc[df_processed['Patient Care in Facility Discontinued ?'] == 'Yes', 'Reason for Discontinuation'] = df_processed['Reason for Discontinuation'].fillna('Could not verify client')
    df_processed.loc[df_processed['Patient Care in Facility Discontinued ?'] == 'No', 'Referred for'] = df_processed['Referred for'].fillna('Adherence Counseling')

    
    # Handling date transformations
    df_processed['Tracking Date'] = pd.to_datetime(df_processed['Tracking Date'], errors='coerce').dt.strftime("%d/%m/%Y")
    df_processed['Date returned to care(if valid & retained)'] = pd.to_datetime(df_processed['Date returned to care(if valid & retained)'], errors='coerce').dt.strftime("%d/%m/%Y")
    df_processed['Date of Termination(if yes)']=pd.to_datetime(df_processed['Date of Termination(if yes)'], errors='coerce').dt.strftime("%d/%m/%Y")

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
