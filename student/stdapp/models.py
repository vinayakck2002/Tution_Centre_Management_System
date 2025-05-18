from django.db import models

# Create your models here.
class Class(models.Model):
    name=models.CharField(max_length=250)
    description=models.TextField()
    fees=models.IntegerField()

    def __str__(self):
        return self.name
class Gender(models.Model):
    name=models.CharField(max_length=250)

class Teacher(models.Model):
    name=models.CharField(max_length=250)
    classs=models.ForeignKey(Class,on_delete=models.CASCADE,null=True)
    email=models.CharField(max_length=250)
    photo = models.ImageField(upload_to='teacher_photos/', null=True, blank=True)
    sslc_certificate = models.FileField(upload_to='teacher_certificates/', null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

class Time(models.Model):
    classs=models.ForeignKey(Class,on_delete=models.CASCADE,null=True) 
    start=models.CharField(max_length=250)
    end=models.CharField(max_length=250)

class Student(models.Model):
    fname=models.CharField(max_length=250)
    lname=models.CharField(max_length=250)
    phno=models.IntegerField(max_length=12)
    current_school=models.CharField(max_length=250)
    classs=models.ForeignKey(Class,on_delete=models.CASCADE,null=True)
    image= models.ImageField(upload_to='profile/')
    gender=models.ForeignKey(Gender,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.fname

# Add this to your models.py file
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classs = models.ForeignKey(Class, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')], default='present')
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ['student', 'classs', 'date']
        
    def __str__(self):
        return f"{self.student.fname} {self.student.lname} - {self.date} - {self.status}"
