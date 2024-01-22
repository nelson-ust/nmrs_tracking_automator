# To create a Class for the Obs Data
class Obs: 
    def __init__(self):
        self.person_id = 0
        self.concept_id = 0
        self.encounter_id = ''
        self.order_id = None
        self.obs_datetime = "" 
        self.location_id = None
        self.obs_group_id = None
        self.accession_number = None
        self.value_group_id = None
        self.value_coded = None
        self.value_coded_name_id = None
        self.value_drug = None
        self.value_datetime = None
        self.value_numeric = None
        self.value_modifier = None
        self.value_text = None
        self.value_complex = None
        self.comments = None
        self.creator = 1
        self.date_created = ""
        self.voided = 0    
        self.voided_by = None
        self.date_voided = None
        self.void_reason = None
        self.uuid = ""
        self.previous_version = None
        self.form_namespace_and_path = None
        self.status = "FINAL"
        self.interpretation = None
        