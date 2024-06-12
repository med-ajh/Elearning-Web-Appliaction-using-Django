from django.contrib import admin
from .models import Profile, Course, Assignment, Grade, Resource, PerformanceAnalysis

admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Grade)
admin.site.register(Resource)
admin.site.register(PerformanceAnalysis)
