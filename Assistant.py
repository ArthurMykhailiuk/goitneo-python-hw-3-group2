import re
from collections import UserDict
from datetime import datetime

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)
        self.name = value

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError("Invalid phone number. Must be 10 digits.")
    def __str__(self):
        return self.value    

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        if not re.fullmatch(r'(\d{2}\.\d{2}\.\d{4})', value):
           raise InvalidDateFormat("Invalid date format. Correct format - DD.MM.YYYY")

        

class Record:
    def __init__(self,name):
        self.name = Name(name)
        self.phones = []
        self.birthday = ''  
    
    def add_phone(self,phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = old_phone
        if phone_to_edit:
           phone_to_edit.value = new_phone

    def add_birthday(self,birthday): 
        self.birthday = Birthday(birthday)      

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def __init__(self):
        """Creates empty address book"""
        self.data = {}
    
    def add_record(self,some_record):
        self.data [some_record.name.value] = {
            "phone": some_record.phones,
            "birthday": some_record.birthday 
        }
        
    def delete(self, key):
        del self.data[key]
    
    def find(self, name_key):
        for name, values in self.data.items():
            if name == name_key: 
               for number in values.get("phone", []):
                   return number
    
    def find_phone(self, phone):
        for name, values in self.data.items():
            if phone in values.get("phone", []):
                return phone

    def find_birth(self, name_key):
        for name, values in self.data.items():
            if name == name_key:
               
               return values.get("birthday") 
    
    def get_keys_for_sort(self, x):
        return x['is_next_week'], x['birthday_weekday'], x['name']

    def get_birthdays_per_week (self,users):

        d = {"weekday":"", "is_next_week":"", "name":""}
    
        s = []
        monday, tuesday, wednesday, thursday, friday = [], [], [], [], []
        ready_list = []

        is_next_week = None
        is_full_monday, is_full_tuesday, is_full_wednesday, is_full_thursday, is_full_friday = False, False, False, False, False

        today = datetime.today().date()

        for user in users:
            name = user["name"]
            birthday = user["birthday"].date()  
            birthday_this_year = birthday.replace(year=today.year)
            birthday_weekday = birthday_this_year.weekday()
        
            if birthday_this_year < today: #found previous birthdays
                if today.weekday() == 0:     #current day - monday
                    delta_if_monday = (today - birthday_this_year).days
                    if delta_if_monday > 3:
                        birthday_this_year = birthday.replace(year=today.year + 1)
                    if delta_if_monday < 3:     #previous birthdays found in previous weekend
                        d = {
                         "birthday_weekday":0,
                         "is_next_week":0,
                         "name":name
                        }
                        s.append(d)
                else:
                    birthday_this_year = birthday.replace(year=today.year + 1)    
            elif birthday_this_year >= today: #found birthdays in current day and next 6 days
                delta_days = (birthday_this_year - today).days
                if delta_days < 7:              #found birthdays in next 7 days 
                    if today.weekday() <= birthday_weekday:
                        if birthday_weekday >= 5:  #found birthdays on weekend 
                            is_next_week = True       #move to next week
                        else:                     
                            is_next_week = False   
                    else:
                        is_next_week = True
                
                    if is_next_week == False:
                        d = {
                         "birthday_weekday":birthday_weekday,
                         "is_next_week":0,
                         "name":name
                        }
                        if birthday_weekday < 7:
                            s.append(d)
                    else:
                        d = {
                         "birthday_weekday":birthday_weekday,
                         "is_next_week":1,
                         "name":name
                        }
                        s.append(d)  
        sorted_dicts_list = sorted(s, key=self.get_keys_for_sort) 

        for dict in sorted_dicts_list:
            birthday_weekday = int(dict["birthday_weekday"])
            #form lists of people with birthday by weekday 
            if birthday_weekday == 0 or birthday_weekday >= 5: #if monday or weekend
                monday.append(dict["name"])
            if birthday_weekday == 1: 
                tuesday.append(dict["name"])
            if birthday_weekday == 2: 
                wednesday.append(dict["name"])
            if birthday_weekday == 3: 
                thursday.append(dict["name"])
            if birthday_weekday == 4: 
                friday.append(dict["name"])
 
        for dict in sorted_dicts_list:
            birthday_weekday = int(dict["birthday_weekday"])
            #vars is_full_... added for remove duplicates
            if (birthday_weekday == 0 or birthday_weekday >= 5) and is_full_monday == False:     #monday or weekend
                ready_list.append({"Monday:":monday})
                is_full_monday = True
            if birthday_weekday == 1 and is_full_tuesday == False: 
                ready_list.append({"Tuesday:":tuesday})
                is_full_tuesday = True
            if birthday_weekday == 2 and is_full_wednesday == False: 
                ready_list.append({"Wednesday:":wednesday})
                is_full_wednesday = True
            if birthday_weekday == 3 and is_full_thursday == False: 
                ready_list.append({"Thursday:":thursday})
                is_full_thursday = True
            if birthday_weekday == 4 and is_full_friday == False: 
                ready_list.append({"Friday:":friday})
                is_full_friday = True
            
        return ready_list
              
    
class PhoneHaveAlphaNumeric(Exception):
    pass
class InvalidDateFormat(Exception):
    pass

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except (IndexError, KeyError):
            return "Enter name please."
        except PhoneHaveAlphaNumeric:
            return "Phone contains not digit.Enter correct phone!"
        except InvalidDateFormat:
            return "Invalid date format. Correct format - DD.MM.YYYY"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, contacts):
    name, phone = args
    if phone.isdigit():
        record = Record(name)
        record.add_phone(phone)
        contacts.add_record(record)
        return "Contact added."
    else:
        raise PhoneHaveAlphaNumeric

@input_error
def change_contact(args, contacts):
    name, new_phone = args
    record = Record(name)
    old_phone = contacts.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact changed."

def show_all(contacts):
    for name, phone in contacts.data.items():
        return f'{name}: {contacts.find(name)}'

def show_all_birth(contacts):
    users = []
    for name, birth in contacts.data.items():
        list = (contacts.find_birth(name).value).split('.')
        print(list)
        day = list[0]
        month = list[1]
        year = list[2]
        dict ={
            "name":name,
            "birthday":datetime(int(year),int(month),int(day))
        }
        users.append(dict)

    list1 =  contacts.get_birthdays_per_week(users)        
    return  list1

@input_error
def show_phone(args, contacts):
    name = args[0]
    return contacts.find(name)

@input_error
def add_birth(args, contacts):
    name, birthday = args
    if  re.fullmatch(r'(\d{2}.\d{2}.\d{4})', birthday):
        number = contacts.find(name).value
        record = Record(name)
        record.add_phone(number)
        record.add_birthday(birthday)
        contacts.add_record(record)
        return "Birthday added."
    else:
        raise InvalidDateFormat

def show_birth(args, contacts):
    name = args[0]
    return contacts.find_birth(name)

def main():
    contacts = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "add-birthday":
            print(add_birth(args,contacts))  
        elif command == "show-birthday":
            print(show_birth(args,contacts))  
        elif command == "birthdays":
            print(show_all_birth(contacts))      
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()