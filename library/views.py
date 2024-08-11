from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Student, Book, Issue, Faculty, School
from .serializers import StudentSerializer, BookSerializer, IssueSerializer, FacultySerializer, IssuedBooksSerializer, UserRegistrationSerializer
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.db.models import Q
from datetime import date, timedelta

class MyPagination(PageNumberPagination):
    page_size = 5000  # Set the number of items per page

def get_school_level(request):
    """
    Utility function to retrieve school level from request headers.
    """
    school_level = request.headers.get('School-Level')
    if not school_level:
        raise ValueError("School level not provided in headers")
    return school_level

class UserSignupView(APIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            school_level = user.school.id  # Assuming User model has a foreign key to School
            return Response({"token": token.key, "school_level": school_level}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    
class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
class StudentListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        try:
            school_level = get_school_level(self.request)
            return Student.objects.filter(school__id=school_level)
        except ValueError as e:
            return Student.objects.none()

class StudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'adm_number'

class StudentDeleteView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'adm_number'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Student deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'adm_number'

class FacultyCreateView(generics.CreateAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    
class FacultyListView(generics.ListAPIView):
    serializer_class = FacultySerializer
    pagination_class = MyPagination

    def get_queryset(self):
        school_level = self.request.headers.get('School-Level')
        if school_level:
            # Fetch all the issued books
            queryset = Faculty.objects.filter(school__id=school_level)

            # Trigger save method to update overdue amounts
            with transaction.atomic():
                for issue in queryset:
                    issue.save()

        return queryset

class FacultyDetailView(generics.RetrieveAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    lookup_field = 'faculty_id'

class FacultyDeleteView(generics.DestroyAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    lookup_field = 'faculty_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Faculty deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class FacultyUpdateView(generics.UpdateAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    lookup_field = "faculty_id"

class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        try:
            school_level = get_school_level(self.request)
            return Book.objects.filter(school__id=school_level)
        except ValueError as e:
            return Book.objects.none()

class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'book_id'

class BookUpdateView(generics.UpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'book_id'
    
class BookDeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'book_id'

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        issued_copies = Issue.objects.filter(book=book, returned=False).exists()
        if issued_copies:
            return Response({"error": "Cannot delete book. There are issued copies."}, status=status.HTTP_400_BAD_REQUEST)

        book.delete()
        return Response({"message": "Book and associated copies deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class IssueBookView(generics.CreateAPIView):
    serializer_class = IssueSerializer

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        issuer_id = request.data.get('issuer_id')
        is_student = request.data.get('is_student')
        days = int(request.data.get('days', 0))  # Ensure days is an integer
        overdue_fee_per_day = float(request.data.get('fine', 0))  # Ensure fine is a float
        school_id = request.data.get('school')

        try:
            book = Book.objects.get(book_id=book_id)
            school = School.objects.get(id=school_id)
            if is_student:
                issuer = Student.objects.get(adm_number=issuer_id)
            else:
                issuer = Faculty.objects.get(faculty_id=issuer_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except (Student.DoesNotExist, Faculty.DoesNotExist):
            if is_student:
                return Response({"error": f"Student with admission number {issuer_id} not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": f"Faculty with ID {issuer_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        if self.is_book_already_issued(book, issuer, is_student):
            return Response({"error": "The book is already issued to the issuer"}, status=status.HTTP_400_BAD_REQUEST)

        if book.available_copies <= 0:
            return Response({"error": "No available copies of the book"}, status=status.HTTP_400_BAD_REQUEST)
        
        issuer_issues_count = self.get_issuer_issues_count(issuer_id, is_student)
        if issuer_issues_count >= (issuer.max_books_allowed if is_student else issuer.max_books_allowed):
            return Response({"error": "Issuer has already reached the maximum limit of books allowed to issue"}, status=status.HTTP_400_BAD_REQUEST)

        return_date = date.today() + timedelta(days=days)
        overdue_amount = days * overdue_fee_per_day  # Calculate overdue amount

        issue = Issue(
            book=book,
            student=issuer if is_student else None,
            faculty=issuer if not is_student else None,
            school=school,
            days=days,
            overdue_fee_per_day=overdue_fee_per_day,
            overdue_amount=overdue_amount,  # Set the calculated overdue amount
            return_date=return_date
        )
        issue.save()

        book.available_copies -= 1
        book.save()

        serializer = self.get_serializer(issue)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def is_book_already_issued(self, book, issuer, is_student):
        if is_student:
            return Issue.objects.filter(book=book, student=issuer, returned=False).exists()
        else:
            return Issue.objects.filter(book=book, faculty=issuer, returned=False).exists()
    
    def get_issuer_issues_count(self, issuer_id, is_student):
        if is_student:
            return Issue.objects.filter(student__adm_number=issuer_id, returned=False).count()
        else:
            return Issue.objects.filter(faculty__faculty_id=issuer_id, returned=False).count()

class ReturnBookView(generics.UpdateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def update(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        school_id = request.data.get('school')
        issuer_id = request.data.get('issuer_id')
        is_student = request.data.get('is_student', True)
        book = Book.objects.get(book_id=book_id)
        school = School.objects.get(id=school_id)

        if is_student:
            student_id = issuer_id
            student = Student.objects.get(adm_number=student_id)
        else:
            faculty_id = issuer_id
            faculty = Faculty.objects.get(faculty_id=faculty_id)

        if not (student_id or faculty_id):
            return Response({"error": "Either student_id or faculty_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if student_id:
                issue = Issue.objects.get(book=book, student=student, school=school, returned=False)
            else:
                issue = Issue.objects.get(book=book, faculty=faculty, school=school, returned=False)
        except (Issue.DoesNotExist, Student.DoesNotExist, Faculty.DoesNotExist):
            return Response({"error": "Issue not found for the provided book and issuer"}, status=status.HTTP_404_NOT_FOUND)

        issue.returned = True
        issue.save()

        # Increment the available_copies of the associated book
        book = issue.book
        book.available_copies += 1
        book.save()

        return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)

class IssuedBooksListView(generics.ListAPIView):
    serializer_class = IssuedBooksSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        school_level = self.request.headers.get('School-Level')
        queryset = Issue.objects.filter(returned=False)

        if school_level:
            queryset = queryset.filter(
                Q(student__school__id=school_level) |
                Q(faculty__school__id=school_level)
            )
        
        # Calculate overdue amount for each issue
        current_date = date.today()
        for issue in queryset:
            issue.overdue_amount = issue.calculate_overdue_amount(current_date)

        return queryset

class ReturnedBooksListView(generics.ListAPIView):
    serializer_class = IssuedBooksSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        school_level = self.request.headers.get('School-Level')
        if school_level:
            return Issue.objects.filter(returned=True).filter(Q(student__school__id=school_level) |
                Q(faculty__school__id=school_level))
        return Issue.objects.filter(returned=True)

class AllIssuesListView(generics.ListAPIView):
    serializer_class = IssuedBooksSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        school_level = self.request.headers.get('School-Level')
        if school_level:
            return Issue.objects.filter(Q(student__school__id=school_level) |
                Q(faculty__school__id=school_level))
        return Issue.objects.all()
