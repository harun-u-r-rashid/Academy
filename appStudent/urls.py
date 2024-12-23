
from django.urls import path
from . import views



urlpatterns = [
    # =====appApi students urls starts from here=======#
    path("summary/<user_id>/", views.StudentSummaryAPIView.as_view()),
    path("course_list/<user_id>/", views.StudentCourseListAPIView.as_view()),
    path(
        "course_details/<user_id>/<enroll_id>/",
        views.StudentCourseDetailsAPIView.as_view(),
    ),
    path(
        "course_completed/", views.StudentCourseCompletedCreateAPIView.as_view()
    ),
    path("note_create/", views.StudentNoteCreateAPIView.as_view()),
    path(
        "note_list/<user_id>/<enroll_id>/",
        views.StudentNoteListAPIView.as_view(),
    ),
    path(
        "note_details/<user_id>/<enroll_id>/<note_id>/",
        views.StudentNoteDetailAPIView.as_view(),
    ),
    path("review/", views.StudentRatingCreateAPIView.as_view()),
    path(
        "review_details/<user_id>/<review_id>/",
        views.StudentRatingRetrieveAPIView.as_view(),
    ),
    path(
        "wishlist/<user_id>/", views.StudentWishListCreateListAPIView.as_view()
    ),
    path(
        "question_list/<course_id>/", views.QuestionAnswerListAPIView.as_view()
    ),
    path("question_create/", views.QuestionAnswerCreateAPIView.as_view()),
    path(
        "question_answer_create/", views.QuestionAnswerMessageCreateAPIView.as_view()
    ),
]
