# -*- coding: utf-8 -*-
import csv
import random
import numpy as np 

#GENERAL SETUP

number_of_participants=4
m_ceil=0
m_floor=0
number_of_heads=1
randomizing_factor=1
encoding_code="cp1252"

#COLUMN DEFINITION

name=0
blocked=1
head=2
department=3
priority=4
gender=5
remainer=6
email=7


#GLOBAL VARIABLES
quota = 0
input_file= "data_source/data.csv"
output_file= "data_source/lunches.csv"
lunch_groups=[]

#Class which reads from CSV file and alters the referenced employee and header lists
class Reader:
    def read_file(self, employee_list, header_list):
        global input_file
        global name
        global blocked
        global head
        global department
        global priority
        global gender
        global remainer
        global email
        
        header_skipped = not self.find_header(employee_list)
        with open(input_file, newline='',encoding=encoding_code) as file:
            reader = csv.reader(file, delimiter=';', quoting=csv.QUOTE_NONE)
    
            for row in reader:
                if header_skipped:
                    employee_list.append(row)
                else:
                    header_list.append(row)
                    header_skipped = True
        
            print("Start Header Mapping...")
            header_list=header_list[0]
            for entry in header_list:

                if entry == "Employee": 
                    name=header_list.index(entry)
                elif entry == "Blocked":
                    blocked=header_list.index(entry)
                elif entry == "Head":
                    head=header_list.index(entry)
                elif entry == "Department":
                    department=header_list.index(entry)
                elif entry == "Prio":
                    priority=header_list.index(entry)
                elif entry == "Gender":
                    gender=header_list.index(entry)
                elif entry == "Remainer":
                    remainer=header_list.index(entry)
                elif entry == "Email":
                    email=header_list.index(entry)
                else:
                    print("ERROR: unknown header")
        
        
    def find_header(self,employee_list):
        global input_file
        with open(input_file, newline='',encoding=encoding_code) as file:
            return csv.Sniffer().has_header(file.read(1024))
        
#Class which writes to CSV files. Coding is retrieved from global encoding_code    
class Writer:
    def write_to_file(self, header_list,original_employee_list,employee_list):
        
        global lunch_groups
        global output_file
        global input_file
        
        with open(output_file, 'w', newline='',encoding=encoding_code) as file:  
            dialect =  csv.QUOTE_NONE
            writer = csv.writer(file,dialect,delimiter=';')       
            for lunch in lunch_groups:
                writer.writerow(lunch)
        
        with open(input_file, 'w', newline='',encoding=encoding_code) as file_2:  
            dialect =  csv.QUOTE_NONE
            writer = csv.writer(file_2,dialect,delimiter=';')
            writer.writerow(header_list.pop())
            for employee in original_employee_list:
                writer.writerow(employee)    

class Generator(Reader,Writer):
    
    def __init__(self):
        self.employees = []
        self.header = []
        self.generate()
        
        
    def generate(self): 
        reader = Reader()
        reader.read_file(self.employees,self.header)
        self.original_employee_list = self.employees.copy()
        
        self.employees = self.eliminate_unsuited_employees(self.employees)
        self.compute_quota(self.employees)
        
        self.employees = self.create_remainer_group(self.employees)
        for employee in self.original_employee_list:
            employee[remainer]=0
        self.left_over_employees = self.create_plan(self.employees)  
        for employee in self.left_over_employees:
            self.original_employee_list[self.original_employee_list.index(employee)][remainer]=1
        writer = Writer()
        writer.write_to_file(self.header, self.original_employee_list, self.employees)   
        
    def compute_quota(self,employees):
        global quota
        
        m = 0
        for employee in employees:
            if employee[gender] == "m":
                m = m+1
        m_ratio = m/len(employees)
        quota = int(number_of_participants-(number_of_participants*m_ratio))
        print("Calculated Quota Person Number:"+str(quota))
        
    def coin_throw(self):
        return int(np.heaviside(random.uniform(-1,1),1))
    
    def randomizer(self):
        global randomizing_factor
        i = 0
        coin_sum = 0
        while(i<randomizing_factor):
            coin_sum = coin_sum + self.coin_throw()
            i=i+1
        return coin_sum

    def eliminate_unsuited_employees(self, employees):
        global blocked
        
        for employee in employees:
            if employee[blocked] == 1:                
                    employees.pop(employees.index(employee))
        return employees    

    def create_remainer_group(self, employees):
        global lunch_groups
        
        group = []
        for employee in employees:
            if '1' == employee[remainer]:
                to_add = str(employees.pop(employees.index(employee))[email])
                group.append(to_add)
        lunch_groups.append(group)
        return employees

    def create_plan(self,employees):
        
        global m_ratio
        global gender
        
        global lunch_groups
        global randomizing_factor
        
        heavi = np.heaviside(len(employees)%number_of_participants, 0)
        number_of_lunches=len(employees)//number_of_participants + heavi
        i=1
        local_employees=employees.copy()
        print("Start to generate "+str(number_of_lunches+1)+" random groups")
        while i<number_of_lunches:
            winners = []
            randomizing_factor = 1
            winners = self.recursive_drawing(winners,local_employees,[],0,0,0)
            if winners == []:
                local_employees=employees.copy()
                i=0
            else:
                lunch_groups.append(winners)
                i=i+1
        print("Finished...") 
        return local_employees
   
        
    def recursive_drawing(self, winners, employees, departments, heads, number_of_drawn,current_quota):
            
        global quota
        global gender
        global randomizing_factor
        
        correct = False
        safety_counter = 0
        if number_of_drawn == number_of_participants:
            return winners
       
        
        
        while(not correct):             
            drawn_employee = self.get_random(employees)
            #Quota
            temp_q=0
                        
            if not drawn_employee[gender] == "m": 
                temp_q=1
            
            if current_quota+temp_q > quota:
                if self.randomizer()==0: continue
            #department
            if drawn_employee[department] in departments:
                if self.randomizer()==0: continue
                
            #head of department
            head_counter = int(drawn_employee[head])
            if head_counter+heads>1:
                continue             
            heads=head_counter+heads
            if not drawn_employee[priority]==1:
                employees.pop(employees.index(drawn_employee))
            winners.append(drawn_employee[email])
            
            #Update conditions
            departments.append(drawn_employee[department])
            current_quota=current_quota+1
            number_of_drawn = number_of_drawn+1
            correct=True
            if safety_counter>=len(employees): 
                safety_counter=0
                departments=[]
                current_quota=0
                randomizing_factor=randomizing_factor+1
            safety_counter = safety_counter+1
        
        return self.recursive_drawing(winners,employees, departments, heads, number_of_drawn, current_quota)
        
    
    def get_random(self, _list):
        return _list[random.randint(0,len(_list)-1)]   
    
    def draw_random(self, _list):
        return _list.pop(random.randint(0,len(_list)-1))
        
def main():
    print("Generate new Mystery Lunch")  
    Generator()
 
if __name__ == "__main__":
    main()