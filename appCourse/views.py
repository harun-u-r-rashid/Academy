# ======import from Django buildin
from django.shortcuts import render, redirect
from appApi import models
from appApi import serializers

from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)

class CategoryView(generics.ListAPIView):
    queryset = models.Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer
    permission_classes = [AllowAny]


class CourseView(generics.ListAPIView):
    queryset = models.Course.objects.filter(
        platform_status="PUBLISHED", teacher_course_status="PUBLISHED"
    )
    serializer_class = serializers.CourseSerializer
    permission_classes = [AllowAny]


class CourseDetailsView(generics.RetrieveAPIView):
    queryset = models.Course.objects.filter(
        platform_status="PUBLISHED", teacher_course_status="PUBLISHED"
    )
    serializer_class = serializers.CourseSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs["slug"]
        course = models.Course.objects.get(
            slug=slug, platform_status="PUBLISHED", teacher_course_status="PUBLISHED"
        )
        return course
    


class ReviewView(generics.ListAPIView):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [AllowAny]



class SearchCourseView(generics.ListAPIView):
    serializer_class = serializers.CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get("query")
        return models.Course.objects.filter(
            title__icontains=query,
            platform_status="Published",
            teacher_course_status="Published",
        )
