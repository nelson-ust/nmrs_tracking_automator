
from mysql.connector import Error
import csv
import datetime
from datetime import datetime, timedelta
import random
from tqdm import tqdm
import os
from repositories import visit_repository, encounter_repository, obs_repository
from helpers import database as db
from helpers import data_cleaning as data_clearner

#data_clearner.main()
def file_exists(file_path) ->bool:
    """
    Check if the file exists and is accessible.
    """
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return True
    else:
        return False
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

# This is the Base Function that starts the execution of the program.
def main():

    connection = db.connect_to_database()
    cursor = connection.cursor()
    if connection:
        
        try:
            # Disable ONLY_FULL_GROUP_BY mode for this session
            cursor.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")

            csv_file = 'upload/verification_outcome.csv'
            print("Resolved CSV file path:", os.path.abspath(csv_file))
            # Check if the CSV file exists
            if not file_exists(csv_file):
                print(f"Error: The file '{csv_file}' does not exist or is not accessible.")
                return


            # Read patient IDs from the CSV file
            patient_ids = read_patient_ids_from_csv(csv_file)

            # Record the start time
            current_time = datetime.now() - timedelta(days=0)
            tracking_forms_created = 0

            # Create a tqdm progress bar
            progress_bar = tqdm(patient_ids.items(), desc="Processing tracking form Data")

            # Iteration of the Dictionary to access key and value of each patients records.
            for patient_id, patient_data in progress_bar:
                #visit_date, track_reason, verify_indication, track_date, who_attempt, mode_comm, person_contacted, default_reason, discontinue_care, discontinue_reason, discontinue_date, referred_service, return_date = patient_data
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

                visit_data = visit_repository.visit_list(connection, {patient_id: visit_date})
                delay_minutes=random.uniform(8, 12)
                date_created = (current_time + timedelta(minutes=delay_minutes)).strftime("%Y-%m-%d %H:%M:%S")
                
                for visit_info in visit_data:
                    delay_seconds = random.uniform(8, 12)
                    current_time += timedelta(seconds=delay_seconds)

                    visit_info.date_created = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    visit_repository.insert_visit_data(connection, visit_info)


                # To Create Tracking Form using same Visit ID
                tracking_encounter_data = encounter_repository.tracking_encounter_list(connection, [patient_id])           
                for encounter_info in tracking_encounter_data:
                    encounter_repository.insert_encounter_data(connection, encounter_info)
 
                # To Create the obs data
                tracking_obs_data = obs_repository.tracking_obs_list(connection, {patient_id: [track_reason, verify_indication, track_date,  who_attempt, mode_comm, person_contacted, default_reason, discontinue_care, discontinue_reason, discontinue_date, referred_service, return_date]}) 
                for observation_info in tracking_obs_data:
                    obs_repository.insert_obs_data(connection, observation_info)

                obs_repository.update_tracking_group_id(connection, [patient_id])
               

               
                tracking_forms_created +=1
                current_time = datetime.strptime(date_created, "%Y-%m-%d %H:%M:%S")

            progress_bar.set_postfix(Patients_Processed=tracking_forms_created)

            print(f"Number of patients that tracking form was Created: {tracking_forms_created}")

        except Error as e:
            print("Error:", e)
        finally:
            connection.close()
   

if __name__ == "__main__":
    main()