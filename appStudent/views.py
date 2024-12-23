# ======import from Django buildin

from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)

from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response


# =======import from custom app=============#
from appAuth.models import User
from appApi import models
from appApi import serializers



class StudentSummaryAPIView(generics.ListAPIView):
    serializer_class = serializers.StudentSummarySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = User.objects.get(id=user_id)

        total_courses = models.EnrolledCourse.objects.filter(user=user).count()
        completed_lessons = models.CompletedLesson.objects.filter(user=user).count()
        achieved_certificates = models.Certification.objects.filter(user=user).count()

        return [
            {
                "total_courses": total_courses,
                "completed_lessons": completed_lessons,
                "achieved_certificates": achieved_certificates,
            }
        ]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StudentCourseListAPIView(generics.ListAPIView):
    serializer_class = serializers.EnrolledCourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = User.objects.get(id=user_id)

        return models.EnrolledCourse.objects.filter(user=user)


class StudentCourseDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.EnrolledCourseSerializer
    permission_classes = [AllowAny]
    lookup_field = "enroll_id"

    def get_object(self):
        user_id = self.kwargs["user_id"]
        enroll_id = self.kwargs["enroll_id"]
        user = User.objects.get(id=user_id)

        return models.EnrolledCourse.objects.get(user=user, enroll_id=enroll_id)


class StudentCourseCompletedCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.CompletedLessonSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data["user_id"]
        course_id = request.data["course_id"]
        variant_item_id = request.data["variant_item_id"]

        user = User.objects.get(id=user_id)
        course = models.Course.objects.get(id=course_id)
        variant_item = models.VariantItem.objects.get(variant_item_id=variant_item_id)

        completed_lessons = models.CompletedLesson.objects.filter(
            user=user, course=course, variant_item=variant_item
        ).first()

        if completed_lessons:
            completed_lessons.delete()
            return Response({"message": "Course marked as not completed."})
        else:
            models.CompletedLesson.objects.create(
                user=user, course=course, variant_item=variant_item
            )
            return Response({"message": "Course marked as completed."})


class StudentNoteCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.NoteSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data["user_id"]
        enroll_id = request.data["enroll_id"]
        title = request.data["title"]
        note = request.data["note"]

        user = User.objects.get(id=user_id)

        enrolled = models.EnrolledCourse.objects.get(enroll_id=enroll_id)

        models.Note.objects.create(
            user=user, course=enrolled.course, note=note, title=title
        )

        return Response(
            {"message": "Note created successfully"}, status=status.HTTP_201_CREATED
        )


class StudentNoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.NoteSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        enroll_id = self.kwargs["enroll_id"]
        note_id = self.kwargs["note_id"]

        user = User.objects.get(id=user_id)
        enrolled = models.EnrolledCourse.objects.get(enroll_id=enroll_id)
        note = models.Note.objects.get(
            user=user, course=enrolled.course, note_id=note_id
        )

        return note


class StudentNoteListAPIView(generics.ListAPIView):
    serializer_class = serializers.NoteSerializer
    permisssion_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        enroll_id = self.kwargs["enroll_id"]

        user = User.objects.get(id=user_id)

        enrolled = models.EnrolledCourse.objects.get(enroll_id=enroll_id)

        return models.Note.objects.filter(user=user, course=enrolled.course)


class StudentRatingCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data["user_id"]
        course_id = request.data["course_id"]
        rating = request.data["rating"]
        review = request.data["review"]

        user = User.objects.get(id=user_id)
        course = models.Course.objects.get(course_id=course_id)

        models.Review.objects.create(
            user=user,
            course=course,
            review=review,
            rating=rating,
            # active=True,
        )

        return Response({"message": "Review Created successfully..."})


class StudentRatingRetrieveAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        review_id = self.kwargs["review_id"]

        user = User.objects.get(id=user_id)
        return models.Review.objects.get(id=review_id, user=user)


class StudentWishListCreateListAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.WishListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = User.objects.get(id=user_id)

        return models.Wishlist.objects.filter(user=user)

    def create(self, request, *args, **kwargs):

        user_id = request.data["user_id"]
        course_id = request.data["course_id"]

        user = User.objects.get(id=user_id)
        course = models.Course.objects.get(course_id=course_id)

        wishlist = models.Wishlist.objects.filter(user=user, course=course).first()

        if wishlist:
            wishlist.delete()
            return Response({"message": "Wishlist deleted"}, status=status.HTTP_200_OK)
        else:
            models.Wishlist.objects.create(user=user, course=course)
            return Response(
                {"message": "Wishlist Created"}, status=status.HTTP_201_CREATED
            )


class QuestionAnswerListAPIView(generics.ListAPIView):
    serializer_class = serializers.QuestionAnswerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        course = models.Course.objects.get(course_id=course_id)
        if course:
            return models.Question_Answer.objects.filter(course=course)
        return Response({"message": "Course doesn't exist."})


class QuestionAnswerCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.QuestionAnswerSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data["course_id"]
        user_id = request.data["user_id"]
        title = request.data["title"]
        message = request.data["message"]

        user = User.objects.get(id=user_id)
        course = models.Course.objects.get(course_id=course_id)

        question = models.Question_Answer.objects.create(
            course=course, user=user, title=title
        )

        models.Question_Answer_Message.objects.create(
            course=course, user=user, message=message, question=question
        )
        return Response({"message": "Conversation started successfully."})


class QuestionAnswerMessageCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.QuestionAnswerMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data["course_id"]
        question_id = request.data["question_id"]
        user_id = request.data["user_id"]
        message = request.data["message"]

        user = User.objects.get(id=user_id)
        course = models.Course.objects.get(course_id=course_id)
        question = models.Question_Answer.objects.get(question_id=question_id)
        models.Question_Answer_Message.objects.create(
            course=course, user=user, message=message, question=question
        )

        question_serializer = serializers.QuestionAnswerSerializer(question)
        return Response(
            {"message": "Message Sent", "question_serializer": question_serializer.data}
        )
