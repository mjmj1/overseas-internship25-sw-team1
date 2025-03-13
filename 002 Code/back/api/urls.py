from django.urls import path
from api import views

urlpatterns = [
    path("table/data/course/import/", views.make_course, name="make_course"),
    path("table/data/resource/import/", views.make_resource, name="make_resource"),
    path("table/assign/create/", views.make_assign_table, name="make_assign_table"),
    path("table/make/", views.make, name="make"),
    path("table/view/", views.get_assign_table, name="get_assign_table"),
    path("courseoffer/view/", views.get_father_course_offer, name="get_father_course_offer"),
]
