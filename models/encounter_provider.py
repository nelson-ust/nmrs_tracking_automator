# To create a Class for the Encounter Provider
class EnounterProvider:
    def __init__(self):
        self.encounter_id = 0
        self.provider_id = 1
        self.encounter_role_id = 1
        self.creator  = 1
        self.date_created= ''
        self.changed_by = None
        self.date_changed = None
        self.voided = 0
        self.date_voided = None
        self.voided_by = None
        self.void_reason = None
        self.uuid = ''
