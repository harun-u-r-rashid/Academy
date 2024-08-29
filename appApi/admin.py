from django.contrib import admin
from . import models


class CategoryAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug': ('title',)}
        list_display = ['title', 'slug']

class CourseAdmin(admin.ModelAdmin):
        prepopulated_fields = {'slug': ('title',)}
        list_display = ['title', 'slug']


admin.site.register(models.Teacher)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Variant)
admin.site.register(models.VariantItem)

admin.site.register(models.Question_Answer)
admin.site.register(models.Question_Answer_Message)
admin.site.register(models.Cart)
admin.site.register(models.CartOrder)
admin.site.register(models.CartOrderItem)
admin.site.register(models.Coupon)
admin.site.register(models.Certification)

admin.site.register(models.CompletedLesson)
admin.site.register(models.EnrolledCourse)
admin.site.register(models.Note)

admin.site.register(models.Review)

admin.site.register(models.Notification)

admin.site.register(models.Wishlist)

admin.site.register(models.Country)


