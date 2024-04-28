"""
URL configuration for library_management_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from library.views import UserLoginView, UserLogoutView, StudentDetailView, StudentCreateView, StudentListView, StudentDeleteView, BookDetailView, BookCreateView, BookListView, BookDeleteView, IssueBookView, ReturnBookView, IssuedBooksListView, ReturnedBooksListView, FacultyListView, FacultyCreateView, FacultyDeleteView, FacultyDetailView, AllIssuesListView

'''
Books API:
GET /api/books/: Get a list of all books.
POST /api/books/: Add a new book.
GET /api/books/<book_id>/: Get details of a specific book.
PUT /api/books/<book_id>/: Update details of a specific book.
DELETE /api/books/<book_id>/: Delete a specific book.
Students API:
GET /api/students/: Get a list of all students.
POST /api/students/: Add a new student.
GET /api/students/<student_id>/: Get details of a specific student.
PUT /api/students/<student_id>/: Update details of a specific student.
DELETE /api/students/<student_id>/: Delete a specific student.
Issues API:
GET /api/issues/: Get a list of all issued books.
POST /api/issues/: Issue a book to a student.
GET /api/issues/<issue_id>/: Get details of a specific issue.
PUT /api/issues/<issue_id>/: Update details of a specific issue (e.g., return a book).
DELETE /api/issues/<issue_id>/: Delete a specific issue.
'''

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('books/', BookListView.as_view()),
    path('books/add/', BookCreateView.as_view()),
    path('books/<str:book_id>/', BookDetailView.as_view()),
    path('books/<str:book_id>/delete/', BookDeleteView.as_view()),
    path('students/', StudentListView.as_view()),
    path('students/add/', StudentCreateView.as_view()),
    path('students/<str:adm_number>/', StudentDetailView.as_view()),
    path('students/<str:adm_number>/delete/', StudentDeleteView.as_view()),
    path('faculty/', FacultyListView.as_view()),
    path('faculty/add/', FacultyCreateView.as_view()),
    path('issue/', IssuedBooksListView.as_view()),
    path('issue/add/', IssueBookView.as_view()),
    path('return/add/', ReturnBookView.as_view()),
    path('return/', ReturnedBooksListView.as_view()),
    path('issues/all/', AllIssuesListView.as_view()),
]
