'''
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException,BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
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

# Setup for static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure the upload directory exists
os.makedirs('upload', exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ingest-data")
@app.post("/ingest-data/")
async def ingest_data(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        # Add the task of ingesting data into the background
        background_tasks.add_task(ingest_data_into_database, temp_file_path, task_id)
        return {"message": "Data ingestion started", "task_id": task_id}
        # Render the HTML template
        # return templates.TemplateResponse("data_ingestion_started.html", {"request": request, "message": "Data ingestion started"})
    except Exception as e:
        # Log the exception
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ingest-progress/{task_id}")
async def get_ingest_progress(task_id: str):
    progress = ingestion_progress.get(task_id, None)
    if progress is not None:
        return {"task_id": task_id, "progress": progress}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.post("/process-file")
@app.post("/process-file/")
async def process_file(file: UploadFile = File(...), who_attempted: str = Form(...)):
    # Validate if the uploaded file is a .xlsx file
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
    #return templates.TemplateResponse("upload_success.html", {"request": Request})

@app.post("/upload-file/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # Temporary file path
        temp_file_path = f"temp_{file.filename}"

        # Save uploaded file to temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file (you can replace this with your specific processing logic)
        df = pd.read_excel(temp_file_path)  # Assuming Excel file input
        df_processed = clean_and_process_data(df)  # Process the DataFrame

        # Save processed DataFrame to 'static' directory
        output_filename = f"processed_{file.filename}".replace('.xlsx', '.csv')
        output_file_path = os.path.join("static", output_filename)
        df_processed.to_csv(output_file_path, index=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the file: {str(e)}")

    finally:
        # Remove temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Return template response with link to download the processed file
    return templates.TemplateResponse("download_file.html", {
        "request": request,
        "filename": output_filename
    })

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

# Global dictionary to track progress
ingestion_progress = {}

def ingest_data_into_database(csv_file: str, task_id: str):
    connection = db.connect_to_database()
    if not connection:
        print("Database connection failed")
        return
    
    patient_ids = read_patient_ids_from_csv(csv_file)
    total_records = len(patient_ids)
    ingestion_progress[task_id] = {'processed': 0, 'total': total_records}

    try:
        for patient_id, patient_data in patient_ids.items():
            # ... (rest of your loop code)
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
            # Update progress
            ingestion_progress[task_id]['processed'] += 1

    except Error as e:
        print("Error during database operation:", e)
    finally:
        connection.close()


def clean_and_process_data(df: pd.DataFrame, who_attempted: str) -> pd.DataFrame:
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df_processed = df.copy()

    # Renaming columns and handling transformations
    df_processed.rename(columns={
        'Unique ID': 'PatientID',
        'Triggers': 'Indication for Client Verification',
        'Tracking Attempt 1(date)': 'Tracking Date',
        'Valid or Invalid': 'Patient Care in Facility Discontinued ?',
        'Reason for termination': 'Reason for Discontinuation'
    }, inplace=True)

    # Setting new values and handling transformations
    df_processed['ReasonForTracking'] = 'Other'
    df_processed['Who_Attempted'] = who_attempted
    df_processed['ModeOfCommunication'] = 'Mobile Phone'
    df_processed['Person_contacted'] = 'Patient'
    df_processed['Reason_for_Defaulting'] = 'Others(Specify)'
    # df_processed['Reason for Discontinuation'] = None
    df_processed['Referred for'] = None

    df_processed['Patient Care in Facility Discontinued ?'] = df_processed['Patient Care in Facility Discontinued ?'].map({'Valid': 'No', 'Invalid': 'Yes'})

     # Set specific values based on conditions
    # df_processed.loc[df_processed['Patient Care in Facility Discontinued ?'] == 'Yes', 'Reason for Discontinuation'] = df_processed['Reason for Discontinuation'].fillna('Could not verify client')
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

'''

import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException,BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
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

# Setup for static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure the upload directory exists
os.makedirs('upload', exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#@app.post("/ingest-data")
@app.post("/ingest-data/")
async def ingest_data(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        # Add the task of ingesting data into the background
        background_tasks.add_task(ingest_data_into_database, temp_file_path, task_id)
        return {"message": "Data ingestion started", "task_id": task_id}
        # Render the HTML template
        # return templates.TemplateResponse("data_ingestion_started.html", {"request": request, "message": "Data ingestion started"})
    except Exception as e:
        # Log the exception
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ingest-progress/{task_id}")
async def get_ingest_progress(task_id: str):
    progress = ingestion_progress.get(task_id, None)
    if progress is not None:
        return {"task_id": task_id, "progress": progress}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

#@app.post("/process-file")
@app.post("/process-file/")
async def process_file(file: UploadFile = File(...), who_attempted: str = Form(...)):
    # Validate if the uploaded file is a .xlsx file
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
    #return templates.TemplateResponse("upload_success.html", {"request": Request})

@app.post("/upload-file/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # Temporary file path
        temp_file_path = f"temp_{file.filename}"

        # Save uploaded file to temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file (you can replace this with your specific processing logic)
        df = pd.read_excel(temp_file_path)  # Assuming Excel file input
        df_processed = clean_and_process_data(df)  # Process the DataFrame

        # Save processed DataFrame to 'static' directory
        output_filename = f"processed_{file.filename}".replace('.xlsx', '.csv')
        output_file_path = os.path.join("static", output_filename)
        df_processed.to_csv(output_file_path, index=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the file: {str(e)}")

    finally:
        # Remove temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Return template response with link to download the processed file
    return templates.TemplateResponse("download_file.html", {
        "request": request,
        "filename": output_filename
    })

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
            verification_status = row[14]

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
                'return_date': return_date,
                'verification_status': verification_status

            }

    return patient_ids

# Global dictionary to track progress
ingestion_progress = {}

def ingest_data_into_database(csv_file: str, task_id: str):
    connection = db.connect_to_database()
    if not connection:
        print("Database connection failed")
        return
    
    patient_ids = read_patient_ids_from_csv(csv_file)
    total_records = len(patient_ids)
    ingestion_progress[task_id] = {'processed': 0, 'total': total_records}

    try:
        for patient_id, patient_data in patient_ids.items():
            # ... (rest of your loop code)
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
            verification_status = patient_data['verification_status']

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
            tracking_obs_data = obs_repository.tracking_obs_list(connection, {patient_id: [track_reason, verify_indication, track_date, who_attempt, mode_comm, person_contacted, default_reason, discontinue_care, discontinue_reason, discontinue_date, referred_service, return_date,verification_status]}) 
            for observation_info in tracking_obs_data:
                obs_repository.insert_obs_data(connection, observation_info)

            # Update tracking group ID if required
            obs_repository.update_tracking_group_id(connection, [patient_id])
            # Update progress
            ingestion_progress[task_id]['processed'] += 1

    except Error as e:
        print("Error during database operation:", e)
    finally:
        connection.close()


def clean_and_process_data(df: pd.DataFrame, who_attempted: str) -> pd.DataFrame:
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df_processed = df.copy()

    # Renaming columns and handling transformations
    df_processed.rename(columns={
        'Unique ID': 'PatientID',
        'Triggers': 'Indication for Client Verification',
        'Tracking Attempt 1(date)': 'Tracking Date',
        'Valid or Invalid': 'Patient Care in Facility Discontinued ?',
        'Reason for termination': 'Reason for Discontinuation'
    }, inplace=True)

    # Setting new values and handling transformations
    df_processed['ReasonForTracking'] = 'Other'
    df_processed['Who_Attempted'] = who_attempted
    df_processed['ModeOfCommunication'] = 'Mobile Phone'
    df_processed['Person_contacted'] = 'Patient'
    df_processed['Reason_for_Defaulting'] = 'Others(Specify)'
    # df_processed['Reason for Discontinuation'] = None
    df_processed['Referred for'] = None

    df_processed['Patient Care in Facility Discontinued ?'] = df_processed['Patient Care in Facility Discontinued ?'].map({'Valid': 'No', 'Invalid': 'Yes'})

     # Set specific values based on conditions
    # df_processed.loc[df_processed['Patient Care in Facility Discontinued ?'] == 'Yes', 'Reason for Discontinuation'] = df_processed['Reason for Discontinuation'].fillna('Could not verify client')
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
        'Date of Termination(if yes)', 'Referred for', 'Date returned to care(if valid & retained)','Verification Status'
    ]
    df_processed = df_processed.reindex(columns=column_order)
    return df_processed


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)