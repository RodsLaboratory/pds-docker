from collections import defaultdict

class Patient:
    """Patient class."""

    def __init__(self, fields, values, file_missing_value, data_missing_value):
        self.fields_and_values = defaultdict(lambda: data_missing_value)
        for i in range(len(fields)):
            if values[i]!=file_missing_value: self.fields_and_values[fields[i]]=values[i]

    def has_value(self,field): return field in self.fields_and_values

    def get_value(self,field): return self.fields_and_values[field]

    def set_value(self,field,value): self.fields_and_values[field] = value

    def __repr__(self): return self.get_value('ID')


