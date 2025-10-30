import csv
from datetime import date
from Patient import Patient

class Data:
    """Data class."""

    def __init__(self, admission_date_field, delimiter, file_missing_value, data_missing_value, file_name):
        self.data = dict()
        file = open(file_name,'r')
        reader = csv.reader(file,delimiter=delimiter)
        header = next(reader)
        index_of_admission_date_field = header.index(admission_date_field)
        for row in reader:
            d = row[index_of_admission_date_field]
            pt_date = date(int(d[0:4]), int(d[5:7]), int(d[8:10]))
            if not(pt_date in self.data): self.data[pt_date]=[]
            self.data[pt_date].append(Patient(header,row,file_missing_value,data_missing_value))
        self.all_dates = sorted(list(self.data.keys()))
        self.all_fields = header
        self.all_cuis = [field for field in self.all_fields if field[0:4]=='C_D_']
        self.all_luis = [field for field in self.all_fields if field[0:4]=='L_D_']
        file.close()

    def number_of_days(self): return len(self.all_dates)

    def dates(self): return self.all_dates

    def date(self,day): return self.all_dates[day]

    def day(self,date): return self.all_dates.index(date)

    def patients(self,day): return self.data[self.date(day)]

    def number_of_patients(self,day): return len(self.data[self.date(day)])

    def patient(self,day,patient): return self.data[self.date(day)][patient]

# end-of-file

