from import_export import resources
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

from reviews.models import (User, Category, Genre,
                            Title, GenreTitle, Review, Comment)


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
        )


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_classes = [CategoryResource]
    list_display = (
        'name',
        'slug',
    )


class GenreResource(resources.ModelResource):
    class Meta:
        model = Genre
        fields = (
            'id',
            'name',
            'slug',
        )


@admin.register(Genre)
class GenreAdmin(ImportExportModelAdmin):
    resource_classes = [GenreResource]
    list_display = (
        'name',
        'slug',
    )


class TitleResource(resources.ModelResource):
    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'category',
            'genre',
        )


@admin.register(Title)
class TitleAdmin(ImportExportModelAdmin):
    resource_classes = [TitleResource]
    # list_display = [field.name for field in Title._meta.get_fields()
    #                 if not field.many_to_many]
    list_display = []


class GenreTitleResource(resources.ModelResource):
    class Meta:
        model = GenreTitle
        fields = (
            'id',
            'title_id',
            'genre_id',
        )


@admin.register(GenreTitle)
class GenreTitleAdmin(ImportExportModelAdmin):
    resource_classes = [GenreTitleResource]
    list_display = (
        'genre_id',
        'title_id',
    )


class ReviewResource(resources.ModelResource):
    class Meta:
        model = Review
        fields = (
            'id',
            'title_id',
            'text',
            'author',
            'score',
            'pub_date',
        )


# @admin.register(Review)
# class ReviewAdmin(ImportExportModelAdmin):
#     resource_classes = [ReviewResource]
#     list_display = (
#         'id',
#         'title_id',
#         'text',
#     )


class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
        fields = (
            'id',
            'review_id',
            'text',
            'author',
            'pub_date',
        )


@admin.register(Comment)
class ReviewAdmin(ImportExportModelAdmin):
    resource_classes = [CommentResource]
    list_display = (
        'id',
        'review_id',
        'text',
    )


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'role',
            'bio',
            'first_name',
            'last_name',
        )


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_classes = [UserResource]
    list_display = (
        'id',
        'username',
        'email',
        'role',
    )
