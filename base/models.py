from django.db import models
from django.contrib.auth.models import User
class Actions(models.Model):
    action_id = models.AutoField(primary_key=True)
    action_taken = models.CharField(max_length=255)

    def __str__(self):
        return self.action_taken

class Records(models.Model):
    records_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey('Documents', on_delete=models.CASCADE)
    action = models.ForeignKey(Actions, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record {self.records_id}: {self.action.action_taken}"

class Approvals(models.Model):
    request_id = models.AutoField(primary_key=True)
    sender_employee = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey('Documents', on_delete=models.CASCADE)  # Add this field
    date = models.DateTimeField(auto_now_add=True)
    def str(self):
        return f"{self.request_id} - {self.sender_employee} - {self.document} - {self.date}"

class Criticality(models.Model):
    criticality_id = models.AutoField(primary_key=True)
    criticality_level = models.CharField(max_length=255)

class Designations(models.Model):
    designation_id = models.AutoField(primary_key=True)
    designation_name = models.CharField(max_length=255)


class Employees(models.Model):
    employee_id = models.CharField(primary_key= True, max_length=100, unique=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    designation = models.ForeignKey(Designations, on_delete=models.CASCADE)

class Departments(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)

class Documents(models.Model):
    document_id = models.AutoField(primary_key=True)
    version = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  
    department = models.ForeignKey('Departments', on_delete=models.CASCADE)
    criticality = models.ForeignKey('Criticality', on_delete=models.CASCADE)
    upload_date_time = models.DateTimeField(auto_now_add=True)
    detail = models.TextField()
    document_name = models.CharField(max_length=255)
    loc_id = models.TextField(default='1')

    

    