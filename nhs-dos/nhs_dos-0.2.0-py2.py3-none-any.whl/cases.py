class Case:

    __attrs__ = [
        'case_ref', 'case_id', 'postcode', 'surgery', 'age',
        'age_format', 'disposition', 'symptom_group',
        'symptom_discriminator', 'search_distance', 'sex'
    ]

    def __init__(self):
        self.case_ref = 'TEST'

        self.case_id = 'TEST'

        self.postcode = 'ME11DA'

        self.surgery = 'UNK'

        self. age = '1'

        self.age_format = 'AgeGroup'

        self.disposition = '1020'

        self.symptom_group = '1169'

        self.symptom_discriminator = '4047'

        self.search_distance = '60'

        self.sex = 'M'
