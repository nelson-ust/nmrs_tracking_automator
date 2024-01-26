from mysql.connector import Error
import datetime
from datetime import datetime
from models.obs import Obs 
from typing import List
import uuid
from helpers.uuid_generator import generate_uuid

def tracking_obs_list(connection:str, ids:dict) -> List[Obs]:
    obs_info_list = []
    cursor = connection.cursor(dictionary = True)

    try:
        for patient_id, patient_data in ids.items():
                track_reason, verify_indication, track_date, who_attempt, mode_comm, person_contacted, default_reason, discontinue_care, discontinue_reason, discontinue_date, referred_service, return_date = patient_data


            # Mapping of all the conccepts in a list.
                concepts = [165460, 166138, 165461, 165778, 167221, 167222, 165902, 165463, 165464, 165465, 166139, 165466, 165467, 165586, 165470, 165889, 166349, 166348, 165469, 165775, 165776, 165459, 165777]


                counter = 0
                for concept_id in concepts:

                            # Conditions for some special cocnepts to be executed when True
                    if concept_id == 166138 and get_concept_definition(track_reason) != 5622:
                        continue
                    if concept_id == 166139 and get_concept_definition(default_reason) != 5622:
                        continue
                    if concept_id == 165889 and get_concept_definition(discontinue_reason) != 165889: #Cause of Death
                        continue
                    if concept_id == 166349 and get_concept_definition(discontinue_reason) != 165889: #VA Cause of Death
                        continue
                    if concept_id == 166348 and get_concept_definition(discontinue_reason) != 165889: #Adult Causes
                        continue
                    if concept_id == 165470 and discontinue_reason == '':
                        continue
                    if concept_id == 165469 and discontinue_date == '':
                        continue
                    if concept_id == 165775 and return_date == '':
                        continue
                            

                    query = """ SELECT max(encounter_id) as encounter_id, patient_id, max(encounter_datetime) AS obs_datetime, 
                                    max(date_created) AS date_created  FROM encounter
                                        WHERE form_id = 13 AND patient_id IN (SELECT patient_id FROM patient_identifier 
                                            WHERE identifier_type = 4 and identifier = %s)
                        """
                    
                    cursor.execute(query, (patient_id,))

                    # To loop through the concepts and match concept_id with value when True
                    for row in cursor:

                        obs_info = Obs()
                        obs_info.person_id = row['patient_id']
                        obs_info.concept_id = concept_id
                        obs_info.encounter_id = row['encounter_id']
                        obs_info.obs_datetime = row['obs_datetime'].strftime("%Y-%m-%d %H:%M:%S")
                        obs_info.location_id = 14
                        obs_info.date_created = row['date_created'].strftime("%Y-%m-%d %H:%M:%S")
                        obs_info.uuid = generate_uuid()


                        # Concepts IDs Condition Mapping when True
                        if concept_id == 165460: 
                            obs_info.value_coded = get_concept_definition(track_reason)
                            break
                        if concept_id == 166138:
                            obs_info.value_text = "Client Verification"
                            break
                        if concept_id ==  165461:
                            obs_info.value_datetime = last_appt_date(connection, patient_id).strftime("%Y-%m-%d %H:%M:%S")
                            break
                        if concept_id == 165778:
                            if next_appt_date(connection, patient_id) < row['obs_datetime']:
                                missed_appt_date = next_appt_date(connection, patient_id).strftime("%Y-%m-%d %H:%M:%S")
                                obs_info.value_datetime = missed_appt_date
                            else:
                                missed_appt_date = None
                                obs_info.value_datetime = missed_appt_date
                            break
                        if concept_id == 167221:
                            obs_info.value_coded = 1065
                            break

                            #Trigger Logic
                        if concept_id == 167222:
                            if verify_indication in ['1&3', '1$4', '1&5', '2&3','2&4', '2&5', '3&4', '3&5', '4&5', '2,3&4', '2,3,4&5', '3,4&5']:
                                triggers = get_concept_definition(verify_indication)
                                for concept_value in triggers:

                                    obs_info = Obs()
                                    obs_info.person_id = row['patient_id']
                                    obs_info.concept_id = concept_id
                                    obs_info.encounter_id = row['encounter_id']
                                    obs_info.obs_datetime = row['obs_datetime'].strftime("%Y-%m-%d %H:%M:%S")
                                    obs_info.location_id = 14
                                    obs_info.date_created = row['date_created'].strftime("%Y-%m-%uuid2 %H:%M:%S")
                                    obs_info.uuid = generate_uuid()
                                    obs_info.value_coded = concept_value
                                    obs_info_list.append(obs_info)
                            else:
                                obs_info.value_coded = get_concept_definition(verify_indication)
                                obs_info_list.append(obs_info)
                            break

                        if concept_id == 165463:
                            obs_info.value_datetime = (datetime.strptime(track_date, "%d/%m/%Y")).strftime("%Y-%m-%d %H:%M:%S")
                            break
                        if concept_id == 165464:
                            obs_info.value_text = who_attempt
                            break
                        if concept_id == 165465:
                            obs_info.value_coded = get_concept_definition(mode_comm)
                            break
                        if concept_id == 165466:
                            obs_info.value_coded = get_concept_definition(person_contacted)
                            break
                        if concept_id == 165467:
                            obs_info.value_coded = get_concept_definition(default_reason)
                            break
                        if concept_id == 166139:
                            obs_info.value_text = "Client Verification"
                            break
                        if concept_id == 165586:
                            obs_info.value_coded = get_concept_definition(discontinue_care)
                            break


                        if concept_id == 165470: #Dicontinue Reason
                            obs_info.value_coded = get_concept_definition(discontinue_reason)
                            break
                        if concept_id == 165469: #Discontinue Date
                            obs_info.value_datetime = (datetime.strptime(discontinue_date, "%d/%m/%Y")).strftime("%Y-%m-%d %H:%M:%S")
                            break

                                # Death Concepts_id when True (165889)
                        
                        if concept_id == 165889: #Cause of Death
                            obs_info.value_coded = 165887
                            break
                        if concept_id == 166349: #VA Cause of Death
                            obs_info.value_coded = 166348
                            break
                        if concept_id == 166348: #Adult Causes
                            obs_info.value_coded = 166304
                            break
                        

                        if concept_id == 165776: #Referred_service
                            obs_info.value_coded = get_concept_definition(referred_service)
                            break
                        if concept_id == 165775: #Return Date
                            obs_info.value_datetime = (datetime.strptime(return_date, "%d/%m/%Y")).strftime("%Y-%m-%d %H:%M:%S")
                            break 


                        if concept_id == 165459:
                            obs_info.value_text = who_attempt
                            break
                        if concept_id == 165777:
                            obs_info.value_datetime = row['obs_datetime'].strftime("%Y-%m-%d %H:%M:%S")
                            break
                    
                    counter += 1
                    if concept_id == 167222:
                        continue
                    obs_info_list.append(obs_info)
              
    except Error as e:
        print("MySQL Error:", e)
    finally:
        cursor.close()

    return obs_info_list


# Dictionary of concept names and concept IDs
def get_concept_definition(concept_name):

    try:
        concept_dcitionary = {
            'Yes' : 1065,
            'No' : 1066,
            'Other': 5622,
            'Others(Specify)' : 5622,
            'Couple testing' : 165789,
            'Missed Appointment' : 165462,
            'Missed Pharmacy Refill' : 165473,
            'Consistently had drug pickup by proxy without viral load sample collection for two quarters' : 167223,
            'duplicated demographic and clinical variables' : 167224,
            'No biometrics recapture' : 167225,
            'Batched ARV pickup dates' : 167226,
            'Last clinical visit is over 18 months prior' : 167227,
            'Batched ART start and pickup dates' : 167228,
            'No initial biometric capture' : 167229,
            'Mobile Phone' : 1650,
            'Home Visit' : 165791,
            'Patient' : 162571,
            'Guardian' : 160639,
            'Treatment Supporter' : 161642,
            'No transport fare' : 1737,
            'Transferred to new site' : 159492,
            'Forgot' : 162192,
            'Felt better' : 160586,
            'Not permitted to leave work' : 165896,
            'Lost appointment card' : 165897,
            'Still had drugs' : 165898,
            'Taking herbal treatment' : 165899,
            'Could not verify client' : 167231,
            'Duplicate Record' : 167230,
            'Death' : 165889,
            'Transferred out to another facility' : 159492,
            'Discontinued care' : 165916,
            'Lost_to_followup' : 5240,
            'Adherence Counseling' : 5488,
            '1' : 167229, #No biometrics recapture
            '2' : 167224, #duplicated demographic and clinical variables
            '3' : 167228, #Batched ART start and pickup dates
            '4' : 167223, #Consistently had drug pickup by proxy without viral load sample collection for two quarters
            '5' : 167226, #Batched ARV pickup dates
            '1&3':[167229, 167228],
            '1$4':[167229, 167223],
            '1&5':[167229, 167226],
            '2&3':[167224, 167228],
            '2&4':[167224, 167223],
            '2&5':[167224, 167226],
            '3&4':[167228, 167223],
            '3&5':[167228, 167226],
            '4&5':[167223, 167226],
            '2,3&4':[167224, 167228, 167223],
            '2,3,4&5':[167224, 167228, 167223, 167226],
            '3,4&5':[167228, 167223, 167226],

        }

        for concept_key, concept_value in concept_dcitionary.items():
            if concept_key == concept_name:
                concept_id = concept_value

                return concept_id

    except Error as e:
        print("Function Error:", e)


def last_appt_date(connection:str, pepfar_id:str) -> datetime:
    try:
        cursor = connection.cursor(dictionary = True)

        query = f"""select encounter_datetime from encounter where patient_id in (
                            select patient_id from patient_identifier where identifier = %s and 
                                    identifier_type = 4)order by encounter_datetime desc limit 1,1
                       """
        cursor.execute(query, (pepfar_id,))
                       
        value = cursor.fetchone()
        last_appt_date = value['encounter_datetime']
    except Error as e:
        print("MySQL Error:", e)
    finally:
        cursor.close()

    return last_appt_date


def next_appt_date(connection:str, pepfar_id:str) -> datetime:
    try:
        cursor = connection.cursor(dictionary = True)

        query = f"""select value_datetime from obs where concept_id = 5096 and person_id in (
                                select patient_id from patient_identifier where identifier = %s and 
                                        identifier_type = 4) order by obs_datetime desc limit 1
                       """
        cursor.execute(query, (pepfar_id, ))

        value = cursor.fetchone()
        next_appt_date = value['value_datetime']
    except Error as e:
        print("MySQL Error:", e)
    finally:
        cursor.close()

    return next_appt_date


# To update the obs table with the obs_group_id for tracking attempt
def update_tracking_group_id(connection:str, ids:str): 
    
    try:
        for patient_id in ids:
            cursor = connection.cursor(dictionary=True)
            
            # To pull the group_id and person_id from the dB using nested select statement
            query = ("""SELECT max(obs_id) as group_id, person_id from obs where concept_id = 165902 
                                AND person_id in (select patient_id from patient_identifier where identifier_type = 4 and identifier = %s)""")
            
            cursor.execute(query, (patient_id,))
            for row in cursor:
                group_id = row['group_id']
                patient_id = row['person_id']
                if group_id is not None:

                    # Update of the obs records using place holders to accept value within the query statement
                    cursor.execute(f"UPDATE obs set obs_group_id = {group_id} where person_id = {patient_id} and obs_id > {group_id} and concept_id in (165465, 165463, 165466, 165464, 165467, 166139) LIMIT 6")
                    connection.commit()

    except Error as e:
        print("MySQL Error:", e)
        
    finally:
        cursor.close()
        

# To insert the obs data into the obs table using the commit method.
def insert_obs_data(connection:str, obs_info:list): 
    try:
        cursor = connection.cursor()
        cursor.execute("""
                INSERT INTO obs (person_id, concept_id, encounter_id, order_id, obs_datetime, location_id, obs_group_id, 
                       accession_number, value_group_id, value_coded, value_coded_name_id, value_drug, value_datetime, 
                            value_numeric, value_modifier, value_text, value_complex, comments, creator, date_created, voided, 
                                voided_by, date_voided, void_reason, uuid, previous_version, form_namespace_and_path, status, interpretation
                       
                ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
            obs_info.person_id, obs_info.concept_id, obs_info.encounter_id, obs_info.order_id,obs_info.obs_datetime, obs_info.location_id, 
            obs_info.obs_group_id, obs_info.accession_number, obs_info.value_group_id, obs_info.value_coded, obs_info.value_coded_name_id, 
            obs_info.value_drug, obs_info.value_datetime, obs_info.value_numeric, obs_info.value_modifier, obs_info.value_text, obs_info.value_complex,
            obs_info.comments, obs_info.creator, obs_info.date_created, obs_info.voided, obs_info.voided_by, obs_info.date_voided,
            obs_info.void_reason, obs_info.uuid, obs_info.previous_version, obs_info.form_namespace_and_path, obs_info.status, obs_info.interpretation
            ))
        connection.commit()

    except Error as e:
        print("MySQL Error:", e)
    finally:
        cursor.close()
