from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.api.filters import TitleFilter
from api_yamdb.api.permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAuthorOrHigherOrReadOnly
)
from api_yamdb.api.serializers import (
    CategorySerializer, CommentSerializer, EditSelfProfileSerializer,
    GenreSerializer, RegistrationSerializer, ReviewSerializer,
    TitleSerializer, TitleShowSerializer, TokenSerializer, UserSerializer
)
from api_yamdb.reviews.models import Category, Genre, Title, Review, User


class CategoriesViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    GenericViewSet, mixins.ListModelMixin
):
    permission_classes = (AllowAny, IsAdminOrReadOnly)
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    ordering_fields = ('name',)


class GenresViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    GenericViewSet, mixins.ListModelMixin
):
    permission_classes = (AllowAny, IsAdminOrReadOnly)
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    ordering_fields = ('name',)


class TitlesViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny, IsAdminOrReadOnly)
    queryset = (Title.objects.all()
                .annotate(rating=Avg('reviews__score')).order_by('-id'))
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_class = TitleFilter
    search_fields = ('name', 'year', 'category', 'genre')
    ordering_fields = ('name', 'year',)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return TitleSerializer
        else:
            return TitleShowSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrHigherOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrHigherOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Вью-функция для получения письма с кодом подтверждения."""
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, _ = User.objects.get_or_create(**serializer.data)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Confirmation code for registration in YaMDb',
        message=f'Your confirmation code: {confirmation_code}',
        from_email=None,
        recipient_list=[
            user.email,
        ]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Вью-функция для получения токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    if default_token_generator.check_token(
        user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет модели User."""
    http_method_names = ['delete', 'get', 'post', 'patch']
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAdmin,)
    ordering_fields = ('username',)

    @action(
        methods=[
            'get',
            'patch',
        ],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated],
        serializer_class=EditSelfProfileSerializer,
    )
    def users_own_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
