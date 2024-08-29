from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
from moviepy.editor import VideoFileClip
import math
from appAuth.models import User, Profile
from .constants import (
    LANGUAGE,
    LEVEL,
    TEACHER_STATUS,
    PLATFORM_STATUS,
    PAYMENT_STATUS,
    RATING,
    NOTIFICATION_TYPE,
)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to="teacher", blank=True, null=True)
    full_name = models.CharField(max_length=100)
    bio = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.full_name

    def students(self):
            return CartOrderItem.objects.filter(teacher=self)

    def courses(self):
            return Course.objects.filter(teacher=self)

    def review(self):
            return Course.objects.filter(teacher=self).count()


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to="category", blank=True, null=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Category"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def course_count(self):
            return Course.objects.filter(category=self).count()

    def save(self, *arg, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Category, self).save(*arg, **kwargs)


class Course(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    file = models.FileField(upload_to="course", blank=True, null=True)
    image = models.FileField(upload_to="course", blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    language = models.CharField(max_length=100, choices=LANGUAGE, default="ENGLISH")
    level = models.CharField(max_length=100, choices=LEVEL, default="BEGGINER")
    platform_status = models.CharField(
        max_length=100, choices=PLATFORM_STATUS, default="PUBLISHED"
    )
    teacher_course_status = models.CharField(max_length=100, default="PUBLISHED")
    featured = models.BooleanField(default=False)
    course_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )
    slug = models.SlugField(unique=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def save(self, *arg, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Course, self).save(*arg, **kwargs)  


    def students(self):
        return EnrolledCourse.objects.filter(course=self)


    def curriculam(self):
        return Variant.objects.filter(course=self)
    

    def lectures(self):
        return VariantItem.objects.filter(variant__course=self)

       
    def average_rating(self):
        average_rating = Review.objects.filter(course=self).aggregate(
            avg_rating=models.Avg("rating")
        )
        return average_rating["avg_rating"]

    def rating_count(self):
        return Review.objects.filter(course=self).count()

    def reviews(self):
        return Review.objects.filter(course=self, active=True)


class Variant(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    varient_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def variant_items(self):
        return VariantItem.objects.filter(variant=self)


class VariantItem(models.Model):
    variant = models.ForeignKey(
        Variant, on_delete=models.CASCADE, related_name="variant_items"
    )
    title = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="varient_item", blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    content_duration = models.CharField(max_length=100, blank=True, null=True)
    preview = models.BooleanField(default=False)
    variant_item_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )

    def __str__(self):
        return f"{self.variant.title}-{self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file:
            clip = VideoFileClip(self.file.path)
            duration_seconds = clip.duration
            minutes, remainder = divmod(duration_seconds, 60)
            minutes = math.floor(minutes)
            seconds = math.floor(remainder)

            duration_text = f"{minutes}m {seconds}s"
            self.content_duration = duration_text
            super().save(update_fields=["content_duration"])

            # TODO
            # What is moviepy
            # need to install moviepy


class Question_Answer(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    question_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}-{self.course.title}"

    class Meta:
        ordering = ["-date"]

    def messages(self):
        return Question_Answer_Message.objects.filter(question=self)

    def profile(self):
        return Profile.objects.get(user=self.user)


class Question_Answer_Message(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.ForeignKey(Question_Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    question_ans_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}-{self.course.title}"

    class Meta:
        ordering = ["date"]

    def profile(self):
        return Profile.objects.get(user=self.user)


class Cart(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    country = models.CharField(max_length=100, blank=True, null=True)
    cart_id = ShortUUIDField(
        length=6, max_length=20, alphabet="1234567890"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title


class CartOrder(models.Model):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ManyToManyField(Teacher, blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    coupons = models.ManyToManyField("appApi.Coupon", blank=True)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="PROCESSING")
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    stripe_session_id = models.CharField(max_length=1000, null=True, blank=True)
    order_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date"]

    def order_items(self):
        return CartOrderItem.objects.filter(order=self)

    def __str__(self):
        return self.order_id


class CartOrderItem(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    order = models.ForeignKey(
        CartOrder, on_delete=models.CASCADE, related_name="orderitem"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="order_item"
    ) 
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    coupons = models.ManyToManyField("appApi.Coupon", blank=True)
    applied_coupon = models.BooleanField(default=False)
    order_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date"]

    def order_id(self):
        return f"Order ID : {self.order_id}"

    def payment_status(self):
        return f"{self.payment_status}"

    def __str__(self):
        return f"{self.order_id}"


class Coupon(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, blank=True, null=True
    )
    used_by = models.ManyToManyField(User, blank=True)
    code = models.CharField(max_length=50)
    discount = models.IntegerField(default=1)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code


class Certification(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    certification_id = ShortUUIDField(
        unique=True, max_length=20, length=6, alphabet="1234567890"
    )

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title


class CompletedLesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    variant_item = models.ForeignKey(VariantItem, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title


class EnrolledCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    order_item = models.ForeignKey(CartOrderItem, on_delete=models.CASCADE)
    enroll_id = ShortUUIDField(unique=True, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title

    def lectures(self):
        return VariantItem.objects.filter(variant__course=self.course)

    def completed_lesson(self):
        return CompletedLesson.objects.filter(course=self.course, user=self.user)

    def curriculam(self):
        return Variant.objects.filter(course=self.course)

    def note(self):
        return Note.objects.filter(course=self.course, user=self.user)

    def question_answer(self):
        return Question_Answer.objects.filter(course=self.course)

    def review(self):
        return Review.objects.filter(course=self.course, user=self.user)


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField()
    note_id = ShortUUIDField(
        unique=True, length=6, max_length=20, alphabet="1234567890"
    )
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    reply = models.CharField(null=True, blank=True, max_length=1000)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title

    def get_profile(self):
        return Profile.objects.filter(user=self.user)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, blank=True, null=True
    )
    order = models.ForeignKey(
        CartOrder, on_delete=models.SET_NULL, blank=True, null=True
    )

    order_item = models.ForeignKey(
        CartOrderItem, on_delete=models.SET_NULL, blank=True, null=True
    )

    review = models.ForeignKey(Review, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=100, choices=NOTIFICATION_TYPE)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.type


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.course.title


class Country(models.Model):
    name = models.CharField(max_length=100)
    tax_rate = models.IntegerField(default=5)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

