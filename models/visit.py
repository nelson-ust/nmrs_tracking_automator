# To create a Class for the Visit Data
class Visit:
    def __init__(self):
        self.patient_id = 0
        self.visit_type_id = 1
        self.date_started = ""
        self.date_stopped = ""
        self.indication_concept_id = None
        self.location_id = ""
        self.creator = 1
        self.date_created = ""
        self.change_by = None
        self.date_changed = None
        self.voided = 0
        self.voided_by = None
        self.date_voided = None
        self.void_reason = None
        self.uuid = ""

