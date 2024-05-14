
from django.contrib import admin
from django.urls import path
from library.views import UserLoginView, UserLogoutView, StudentDetailView, StudentCreateView, StudentListView, StudentDeleteView, StudentUpdateView, BookDetailView, BookCreateView, BookListView, BookDeleteView, IssueBookView, ReturnBookView, IssuedBooksListView, ReturnedBooksListView, FacultyListView, FacultyCreateView, FacultyDeleteView, FacultyDetailView, AllIssuesListView, BookUpdateView
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Library Management System'
admin.site.site_title = 'Library Management System'
admin.site.index_title = 'Mountassisi School'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('books/', BookListView.as_view()),
    path('books/add/', BookCreateView.as_view()),
    path('books/<str:book_id>/', BookDetailView.as_view()),
    path('books/<str:book_id>/edit/', BookUpdateView.as_view(), name='book-edit'),
    path('books/<str:book_id>/delete/', BookDeleteView.as_view()),
    path('students/', StudentListView.as_view()),
    path('students/add/', StudentCreateView.as_view()),
    path('students/<str:adm_number>/', StudentDetailView.as_view()),
    path('students/<str:adm_number>/edit/', StudentUpdateView.as_view(), ),
    path('students/<str:adm_number>/delete/', StudentDeleteView.as_view()),
    path('faculty/', FacultyListView.as_view()),
    path('faculty/add/', FacultyCreateView.as_view()),
    path('issue/', IssuedBooksListView.as_view()),
    path('issue/add/', IssueBookView.as_view()),
    path('return/add/', ReturnBookView.as_view()),
    path('return/', ReturnedBooksListView.as_view()),
    path('issues/all/', AllIssuesListView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

