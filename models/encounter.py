# To create a Class for the Encounter Data
class Encounter: 
    def __init__(self):
        self.encounter_type = 0
        self.patient_id = 0
        self.location_id = ""
        self.form_id = 0
        self.encounter_datetime = ""
        self.creator = 1
        self.date_created = ""
        self.voided = 0
        self.voided_by = None
        self.date_voided = None
        self.void_reason = None
        self.changed_by = None
        self.date_changed = None
        self.visit_id = 0
 