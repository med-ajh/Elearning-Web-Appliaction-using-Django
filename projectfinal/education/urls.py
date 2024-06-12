from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard
from . import views 

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('home/', views.home, name='home'),
    path('', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/update/', views.course_update, name='course_update'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/update/', views.assignment_update, name='assignment_update'),
    path('assignments/<int:assignment_id>/delete/', views.assignment_delete, name='assignment_delete'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('submissions/<int:assignment_id>/', views.submission_list, name='submission_list'),
    path('submissions/<int:submission_id>/update/', views.submission_update, name='submission_update'),
    path('submissions/<int:submission_id>/delete/', views.submission_delete, name='submission_delete'),
    path('grade_submission/<int:assignment_id>/', views.grade_submission, name='grade_submission'),
    path('view_performance/', views.view_performance, name='view_performance'),
    path('performance_analysis/', views.performance_analysis, name='performance_analysis'),
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/create/', views.resource_create, name='resource_create'),
    path('resources/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('resources/<int:resource_id>/update/', views.resource_update, name='resource_update'),
    path('resources/<int:resource_id>/delete/', views.resource_delete, name='resource_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
