from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path('', views.signin, name='signin'),          # login page
    path('signup/', views.signup, name='signup'),   # added trailing slash
    path('index/', views.index, name='index'),  
    path('logout', views.logout_view, name='logout'),


    path('forgot-password/', views.getusername, name='getusername'),
    path('verify-otp/', views.verifyotp, name='verifyotp'),
    path('reset-password/', views.passwordreset, name='passwordreset'),



    path('addcourse', views.addcourse, name='addcourse'),
    path('edit_course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),

    path('addteacher/', views.addteacher, name='addteacher'),
    path('edit_teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),


    path('addstudent', views.addstudent, name='addstudent'),
    path('gender/edit/<int:id>/', views.edit_gender, name='edit_gender'),
    path('gender/delete/<int:id>/', views.delete_gender, name='delete_gender'),


    path('addtime', views.addtime, name='addtime'),
    path('edit_time/<int:time_id>/', views.edit_time, name='edit_time'),
    path('delete_time/<int:time_id>/', views.delete_time, name='delete_time'),

    path('student/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('student/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('students/', views.studentlist, name='studentlist'),  # Assuming you have this view

    #----------------------------------------------------------------------------------------------------------
    path('teacherhome/', views.teacher_home, name='teacher_home'),            
    path('teacherclass/', views.teacher_class, name='teacher_class'),            
    path('teacherstudentlist/', views.teacher_student_list, name='teacher_student_list'),            
    path('teacherprofile/', views.teacher_profile, name='teacher_profile'), 
    path('teacher/profile/edit/', views.teacher_profile_edit, name='teacher_profile_edit'),

    path('teacher/class/<int:class_id>/attendance/', views.class_attendance, name='class_attendance'),
    path('teacher/class/<int:class_id>/attendance/history/', views.attendance_history, name='attendance_history'),          


 path('change-password/', views.change_password, name='change_password'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)