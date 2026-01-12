from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from . models import *
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from datetime import datetime, timedelta
import random
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required



def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        if not username or not email or not password or not confirmpassword:
            messages.error(request, 'All fields are required.')
            return render(request, 'signup.html')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'signup.html')
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Account created successfully!")
                return redirect('signin')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'signup.html')
    return render(request, 'signup.html')



def signin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('index')  # redirect to admin page
        else:
            # Check if this is first login for teacher
            try:
                teacher = Teacher.objects.get(email=request.user.username)
                if teacher.last_login is None:
                    return redirect('change_password')
                return redirect('teacher_home')  # redirect to user page
            except Teacher.DoesNotExist:
                return redirect('teacher_home')  # Not a teacher, just redirect

    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'signin.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['username'] = username
            
            # Check if teacher needs to change password
            try:
                teacher = Teacher.objects.get(email=username)
                if teacher.last_login is None:
                    # First time login, redirect to password change
                    return redirect('change_password')
                else:
                    # Update last login time
                    teacher.last_login = timezone.now()
                    teacher.save()
            except Teacher.DoesNotExist:
                # Not a teacher account, could be admin
                pass
                
            if user.is_superuser:
                return redirect('index') 
            else:
                return redirect('teacher_home')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'signin.html')

"""
Now, let's create the change_password view:
"""



@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if the current password is correct
        user = request.user
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return render(request, 'Teacher/change_password.html')
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'Teacher/change_password.html')
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Update last_login for teacher
        try:
            teacher = Teacher.objects.get(email=user.username)
            teacher.last_login = timezone.now()
            teacher.save()
        except Teacher.DoesNotExist:
            pass
        
        # Update session to prevent logout
        update_session_auth_hash(request, user)
        
        messages.success(request, "Password changed successfully.")
        return redirect('teacher_home')
        
    return render(request, 'Teacher/change_password.html')

# -----------------forgot password--------------------------------------------------------------------------

def verifyotp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        otp1 = request.session.get('otp')
        otp_time_str = request.session.get('otp_time')
        if otp_time_str:
            otp_time = datetime.fromisoformat(otp_time_str)
            otp_expiry_time = otp_time + timedelta(minutes=5)
            if datetime.now() > otp_expiry_time:
                messages.error(request, 'OTP has expired. Please request a new one.')
                del request.session['otp']
                del request.session['otp_time']
                return redirect('verifyotp')
        if otp == otp1:
            del request.session['otp']
            del request.session['otp_time']
            return redirect('passwordreset')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    otp = ''.join(random.choices('123456789', k=6))
    request.session['otp'] = otp
    request.session['otp_time'] = datetime.now().isoformat()
    message = f'Your email verification code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.session.get('email')]
    send_mail('Email Verification', message, email_from, recipient_list)
    return render(request, "forgot/verifyotp.html")

def getusername(request):
    if request.method == "POST":
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            request.session['email'] = user.email
            return redirect('verifyotp')
        except User.DoesNotExist:
            messages.error(request, "Username does not exist.")
            return redirect('getusername')
    return render(request, 'forgot/getusername.html')

def passwordreset(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')
        if confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('email')
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                del request.session['email']
                messages.success(request, "Your password has been reset successfully.")
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                return redirect('signin')
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
                return redirect('getusername')
    return render(request, "forgot/passwordreset.html")


# ----------------------------------------------------------------------------------------------------------------------
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('signin')


def index(request):
    teacher_count = Teacher.objects.count()
    student = Student.objects.count()
    classes = Class.objects.all()
    context = {
        'teacher_count': teacher_count,
        'student': student,
        'classes': classes
    }
    return render(request, 'index.html',context) 


def addcourse(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('course')
        description = request.POST.get('description')
        fees = request.POST.get('fees')
        
        # Check if a class with this name already exists
        if not Class.objects.filter(name=name).exists():
            # Create new Class object only if it doesn't exist
            new_class = Class(name=name, description=description, fees=fees)
            new_class.save()
            messages.success(request, f"Class '{name}' added successfully!")
        else:
            messages.warning(request, f"Class '{name}' already exists!")
        
        return HttpResponseRedirect(reverse('addcourse'))
    
    # Get all classes for display
    courses = Class.objects.all()
    context = {
        'courses': courses
    }
    
    return render(request, 'add_course.html', context)

def edit_course(request, course_id):
    # Get the course by ID or return 404 if not found
    course = get_object_or_404(Class, id=course_id)
    
    if request.method == 'POST':
        # Update course data
        course.name = request.POST.get('course')
        course.description = request.POST.get('description')
        course.fees = request.POST.get('fees')
        course.save()
        
        # Redirect back to the main page
        return redirect('addcourse')
    
    # Render edit form with pre-filled data
    return render(request, 'edit_course.html', {'course': course})

def delete_course(request, course_id):
    # Get the course by ID or return 404 if not found
    course = get_object_or_404(Class, id=course_id)   
    # Only process delete if it's a POST request
    if request.method == 'POST':
        course.delete()
        return redirect('addcourse')

def addteacher(request):
    if request.method == 'POST':
        name = request.POST.get('course')
        class_id = request.POST.get('class_id')
        teacher_email = request.POST.get('email')
        photo = request.FILES.get('photo')
        sslc_certificate = request.FILES.get('sslc_certificate')

        if Teacher.objects.filter(email=teacher_email).exists():
            messages.warning(request, f"Teacher with email '{teacher_email}' already exists!")
            return HttpResponseRedirect(reverse('addteacher'))

        random_password = get_random_string(length=12)

        user, created = User.objects.get_or_create(
            username=teacher_email,
            defaults={'email': teacher_email}
        )

        if created:
            user.set_password(random_password)
            user.save()

        class_obj = get_object_or_404(Class, id=class_id)

        new_teacher = Teacher(
            name=name,
            classs=class_obj,
            email=teacher_email,
            photo=photo,
            sslc_certificate=sslc_certificate
        )
        new_teacher.save()

        if created:
            subject = 'Your Account Details for the Tuition Centre'
            message = f'''Hello {name},

Your account has been created in our Tuition Centre system.

Your login details are:
Username: {teacher_email}
Password: {random_password}

Please change your password after your first login.

Regards,
Tuition Centre Administration'''
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [teacher_email],
                    fail_silently=False,
                )
                messages.success(request, f"Teacher '{name}' added successfully and login details sent to their email.")
            except Exception as e:
                messages.success(request, f"Teacher '{name}' added successfully but email sending failed: {str(e)}")
        else:
            messages.success(request, f"Teacher '{name}' added successfully. User account already existed.")

        return HttpResponseRedirect(reverse('addteacher'))

    classes = Class.objects.all()
    teachers = Teacher.objects.all()

    return render(request, 'add_teacher.html', {'classes': classes, 'teachers': teachers})
  


def edit_teacher(request, teacher_id):
    # Get the teacher by ID
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        # Debug: Print what you're receiving
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)

        # Get and update the basic fields
        name_value = request.POST.get('name')
        email = request.POST.get('email')
        class_id = request.POST.get('class_id')

        if not name_value or not email or not class_id:
            # Handle error - missing required fields
            return redirect('addteacher')

        teacher.name = name_value
        teacher.email = email
        teacher.classs = get_object_or_404(Class, id=class_id)

        # Handle file uploads
        if 'photo' in request.FILES:
            teacher.photo = request.FILES['photo']
        if 'sslc_certificate' in request.FILES:
            teacher.sslc_certificate = request.FILES['sslc_certificate']

        # Save the updated teacher
        teacher.save()

        # Redirect to the main page
        return redirect('addteacher')

    # For GET request, prepare data for form
    classes = Class.objects.all()
    return render(request, 'edit_teacher.html', {'teacher': teacher, 'classes': classes})

def delete_teacher(request, teacher_id):
    # Get the teacher by ID
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        # Delete the teacher
        teacher.delete()
    
    # Redirect back to the main page
    return redirect('addteacher')


def addtime(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        start_time = request.POST.get('start')
        end_time = request.POST.get('end')
        
        # Get the Class object
        try:
            class_obj = Class.objects.get(id=class_id)
            
            # Check if a similar time schedule already exists
            if Time.objects.filter(classs=class_obj, start=start_time, end=end_time).exists():
                messages.warning(request, 'This time schedule already exists for this class!')
            else:
                # Create and save the Time object
                time = Time(
                    classs=class_obj,
                    start=start_time,
                    end=end_time
                )
                time.save()
                messages.success(request, 'Time schedule added successfully!')
            
            # Use HttpResponseRedirect for proper POST-redirect-GET pattern
            return HttpResponseRedirect(reverse('addtime'))
        except Class.DoesNotExist:
            messages.error(request, 'Selected class does not exist')
    
    # Get all classes to populate the dropdown
    classes = Class.objects.all()
    # Get all time schedules for display
    times = Time.objects.all()
    
    context = {
        'classes': classes,
        'times': times
    }
    
    return render(request, 'add_time.html', context)

def edit_time(request, time_id):
    time_obj = get_object_or_404(Time, id=time_id)
    
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        start_time = request.POST.get('start')
        end_time = request.POST.get('end')
        
        try:
            class_obj = Class.objects.get(id=class_id)
            
            # Update the Time object
            time_obj.classs = class_obj
            time_obj.start = start_time
            time_obj.end = end_time
            time_obj.save()
            
            messages.success(request, 'Time schedule updated successfully!')
            return redirect('addtime')
        except Class.DoesNotExist:
            messages.error(request, 'Selected class does not exist')
    
    # Get all classes for the dropdown
    classes = Class.objects.all()
    
    context = {
        'time': time_obj,
        'classes': classes
    }
    
    return render(request, 'edit_time.html', context)

def delete_time(request, time_id):
    if request.method == 'POST':
        time_obj = get_object_or_404(Time, id=time_id)
        time_obj.delete()
        messages.success(request, 'Time schedule deleted successfully!')
    
    return redirect('addtime')



def addstudent(request):
    if request.method == 'POST':
        # Handle gender addition
        if 'add_gender' in request.POST:
            gender_name = request.POST.get('new_gender').strip()  # Get new gender name from the POST data
            if gender_name:
                # Check if the gender already exists to avoid duplication
                if not Gender.objects.filter(name__iexact=gender_name).exists():
                    # Add new gender
                    Gender.objects.create(name=gender_name)
                else:
                    # Optional: Display error if the gender already exists
                    error_message = f"Gender '{gender_name}' already exists!"
                    return render(request, 'add_student.html', {'error_message': error_message})
            return redirect('addstudent')  # Redirect to the addstudent page after adding gender

        # Handle student form
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        phno = request.POST.get('phone')
        school = request.POST.get('school')
        class_id = request.POST.get('class_id')
        gender_id = request.POST.get('gender_id')
        image = request.FILES.get('student_image')

        # Create the student entry
        Student.objects.create(
            fname=fname,
            lname=lname,
            phno=phno,
            current_school=school,
            classs_id=class_id,
            gender_id=gender_id,
            image=image
        )
        # Change this line to redirect to an existing page
        return redirect('addstudent')  # Or 'dashboard', 'students', whatever page exists

    # Fetch available classes and genders
    classes = Class.objects.all()
    genders = Gender.objects.all()

    return render(request, 'add_student.html', {'classes': classes, 'genders': genders})


def edit_gender(request, id):
    gender = get_object_or_404(Gender, id=id)
    if request.method == 'POST':
        new_name = request.POST.get('name').strip()
        if new_name:
            gender.name = new_name
            gender.save()
            return redirect('addstudent')  # or gender list view
    return render(request, 'edit_gender.html', {'gender': gender})

def delete_gender(request, id):
    gender = get_object_or_404(Gender, id=id)
    if request.method == 'POST':
        gender.delete()
        return redirect('addstudent')  # or gender list view



def studentlist(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        # Update the student data
        student.fname = request.POST.get('first_name')
        student.lname = request.POST.get('last_name')
        student.phno = request.POST.get('phone')
        student.current_school = request.POST.get('school')
        student.classs_id = request.POST.get('class_id')
        student.gender_id = request.POST.get('gender_id')
        
        # Handle image update if provided
        if 'student_image' in request.FILES:
            student.image = request.FILES['student_image']
        
        student.save()
        return redirect('studentlist')  # Redirect to student list after update
    
    # Fetch available classes and genders for the form
    classes = Class.objects.all()
    genders = Gender.objects.all()
    
    return render(request, 'edit_student_list.html', {
        'student': student,
        'classes': classes,
        'genders': genders
    })

def delete_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        student.delete()
    return redirect('studentlist')

# --------------TEACHER-SECTION------------------------------------------------------------------------------------------------------------------

 
@login_required
def teacher_home(request):
    try:
        # Match teacher by the logged-in user's email
        teacher = Teacher.objects.get(email=request.user.email)
    except Teacher.DoesNotExist:
        # Optional: Redirect or show a friendly message if teacher not found
        return render(request, 'error.html', {'message': 'No teacher profile found for your account.'})

    # Get class name and students
    class_name = teacher.classs.name if teacher.classs else "N/A"
    students = Student.objects.filter(classs=teacher.classs) if teacher.classs else []
    student_count = students.count()

    return render(request, 'Teacher/teacher_home.html', {
        'name': teacher.name,
        'student_count': student_count,
        'students': students,
        'class_name': class_name,
    })

def teacher_class(request):
    # Get the logged-in teacher's classes
    teacher = get_object_or_404(Teacher, email=request.user.email)
    classes = Class.objects.filter(teacher=teacher)
    
    context = {
        'classes': classes
    }
    return render(request, 'Teacher/teacher_class.html',context) 

def teacher_student_list(request):
    user = request.user
    teacher = get_object_or_404(Teacher, email=user.email)
    students = Student.objects.filter(classs=teacher.classs).order_by('fname')
    return render(request, 'Teacher/teacher_student_list.html', {'students': students})


@login_required
def teacher_profile(request):

    teacher = Teacher.objects.get(email=request.user.email)
    return render(request, 'Teacher/teacher_profile.html', {'teacher': [teacher]})

@login_required
def teacher_profile_edit(request):
    teacher = Teacher.objects.get(email=request.user.email)

    if request.method == 'POST':
        # Get form data
        teacher.name = request.POST.get('name')
        teacher.email = request.POST.get('email')

        # Handle file uploads
        if 'photo' in request.FILES:
            teacher.photo = request.FILES['photo']
        if 'sslc_certificate' in request.FILES:
            teacher.sslc_certificate = request.FILES['sslc_certificate']

        teacher.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('teacher_profile')

    return render(request, 'Teacher/teacher_profile_edit.html', {'teacher': teacher})




@login_required
def class_attendance(request, class_id):
    classs = get_object_or_404(Class, id=class_id)
    teacher = get_object_or_404(Teacher, email=request.user.email)
    
    # Make sure the teacher is assigned to this class
    # Since the relationship is from Teacher to Class, we need to check differently
    if not Teacher.objects.filter(id=teacher.id, classs=classs).exists():
        messages.error(request, "You are not authorized to mark attendance for this class.")
        return redirect('teacher_class')
    
    students = Student.objects.filter(classs=classs)
    today = timezone.now().date()
    
    if request.method == 'POST':
        for student in students:
            attendance_status = request.POST.get(f'attendance_{student.id}', 'absent')
            
            # Create or update attendance record
            attendance, created = Attendance.objects.update_or_create(
                student=student,
                classs=classs,
                date=today,
                defaults={
                    'status': attendance_status,
                    'marked_by': teacher
                }
            )
        
        messages.success(request, "Attendance marked successfully.")
        return redirect('teacher_class')
    
    # Check if attendance is already marked for today
    attendance_records = {}
    for student in students:
        try:
            record = Attendance.objects.get(student=student, classs=classs, date=today)
            attendance_records[student.id] = record.status
        except Attendance.DoesNotExist:
            attendance_records[student.id] = ''
    
    context = {
        'classs': classs,
        'students': students,
        'attendance_records': attendance_records,
        'today': today.strftime('%Y-%m-%d')
    }
    return render(request, 'Teacher/teacher_attendance.html', context)

@login_required
def attendance_history(request, class_id):
    classs = get_object_or_404(Class, id=class_id)
    teacher = get_object_or_404(Teacher, email=request.user.email)
    
    # Check if the teacher is assigned to the class
    if not Teacher.objects.filter(id=teacher.id, classs=classs).exists():
        messages.error(request, "You are not authorized to view attendance for this class.")
        return redirect('teacher_class')
    
    students = Student.objects.filter(classs=classs)
    
    # Get date filter if provided
    filter_date = request.GET.get('date')
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            attendance_records = Attendance.objects.filter(classs=classs, date=filter_date).order_by('-date')
        except ValueError:
            messages.error(request, "Invalid date format")
            attendance_records = Attendance.objects.filter(classs=classs).order_by('-date')
    else:
        attendance_records = Attendance.objects.filter(classs=classs).order_by('-date')
    
    context = {
        'classs': classs,
        'students': students,
        'attendance_records': attendance_records,
        'filter_date': filter_date
    }
    return render(request, 'Teacher/attendance_history.html', context)




