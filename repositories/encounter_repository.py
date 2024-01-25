from mysql.connector import Error
from models.encounter import Encounter
from typing import List
import uuid


def generate_uuid():
    return str(uuid.uuid4())


# To create the encounter data mapping each attribute of enct_info instance (Encounter) with a value and append them to form list.
def tracking_encounter_list(connection:str, id:str) -> List:
    enct_list = []
    cursor = connection.cursor(dictionary=True)
    try:
        for pepfar_id in id:

            query = """SELECT max(visit_id) as visit_id, patient_id, max(date_started) as encounter_datetime, 
                            max(date_created) as date_created FROM visit
                                WHERE patient_id IN (SELECT patient_id FROM patient_identifier WHERE identifier_type = 4 and identifier = %s)"""
            
            cursor.execute(query, (pepfar_id,))

            for row in cursor:
                encounter = Encounter()
                encounter.encounter_type = 15
                encounter.patient_id = row['patient_id']
                encounter.location_id = 14
                encounter.form_id = 13
                encounter.encounter_datetime = row['encounter_datetime'].strftime("%Y-%m-%d %H:%M:%S")
                encounter.date_created = row['date_created'].strftime("%Y-%m-%d %H:%M:%S")
                encounter.visit_id = row['visit_id']
                encounter.uuid = generate_uuid()
                enct_list.append(encounter)

    except Error as e:
        print("MySQL Error:", e)
    
    finally:
        cursor.close()

    return enct_list


# To insert the encounter data into the encounter table using the commit method.
def insert_encounter_data(connection:str, encounter:list): 
    try:
        cursor = connection.cursor()

        cursor.execute("""
                INSERT INTO encounter (encounter_type, patient_id, location_id, 
                         form_id, encounter_datetime, creator,date_created, voided, 
                        voided_by, date_voided, void_reason, changed_by, date_changed, visit_id, uuid
                ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                encounter.encounter_type, encounter.patient_id, encounter.location_id, encounter.form_id,
                encounter.encounter_datetime, encounter.creator, encounter.date_created, encounter.voided,
                encounter.voided_by, encounter.date_voided, encounter.void_reason, encounter.changed_by,
                encounter.date_changed, encounter.visit_id, encounter.uuid
            ))
        connection.commit()
    except Error as e:
        print("MySQL Error:", e)

    finally:
        cursor.close()

