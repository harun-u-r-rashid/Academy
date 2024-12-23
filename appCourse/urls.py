
from django.urls import path
from . import views

urlpatterns = [

    path("category/", views.CategoryView.as_view()),
    path("course_list/", views.CourseView.as_view()),
    path("course_details/<slug>/", views.CourseDetailsView.as_view()),
    path("search/", views.SearchCourseView.as_view()),
    path("review/", views.ReviewView.as_view()),
   

]
