from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Student, Book, Issue, Faculty
from .serializers import StudentSerializer, BookSerializer, IssueSerializer, FacultySerializer, IssuedBooksSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token

class MyPagination(PageNumberPagination):
    page_size = 5000  # Set the number of items per page

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Generate or retrieve token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
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
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = MyPagination

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

class FacultyCreateView(generics.CreateAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    
class FacultyListView(generics.ListAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    pagination_class = MyPagination

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

class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = MyPagination

class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'book_id'

class BookDeleteView(generics.DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'book_id'

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()
        # Check if there are any issued copies of the book
        issued_copies = Issue.objects.filter(book=book, returned=False).exists()
        if issued_copies:
            return Response({"error": "Cannot delete book. There are issued copies."}, status=status.HTTP_400_BAD_REQUEST)

        # If no issued copies, delete the book and its associated copies
        book.delete()

        return Response({"message": "Book and associated copies deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class IssueBookView(generics.CreateAPIView):
    serializer_class = IssueSerializer

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        issuer_id = request.data.get('issuer_id')
        is_student = request.data.get('is_student')

        try:
            book = Book.objects.get(book_id=book_id)
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

        if is_student and issuer.books_issued.count() >= issuer.max_books_allowed:
            return Response({"error": "Issuer has already reached the maximum limit of books allowed to issue"}, status=status.HTTP_400_BAD_REQUEST)

        issue = Issue(book=book, student=issuer) if is_student else Issue(book=book, faculty=issuer)
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

class ReturnBookView(generics.UpdateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def update(self, request, *args, **kwargs):
        # Retrieve book_id, student_id, and faculty_id from the request data
        book_id = request.data.get('book_id')
        issuer_id = request.data.get('issuer_id')
        is_student = request.data.get('is_student', True)
        book = Book.objects.get(book_id=book_id)

        if is_student:
            student_id = issuer_id
            student = Student.objects.get(adm_number=student_id)
        else:
            faculty_id = issuer_id
            faculty = Faculty.objects.get(faculty_id=faculty_id)

        # Check if either student_id or faculty_id is provided
        if not (student_id or faculty_id):
            return Response({"error": "Either student_id or faculty_id must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Determine the type of issuer and retrieve the issue object accordingly
        try:
            if student_id:
                issue = Issue.objects.get(book=book, student=student, returned=False)
            else:
                issue = Issue.objects.get(book=book, faculty=faculty, returned=False)
        except (Issue.DoesNotExist, Student.DoesNotExist, Faculty.DoesNotExist):
            return Response({"error": "Issue not found for the provided book and issuer"}, status=status.HTTP_404_NOT_FOUND)

        # Calculate overdue amount if return date is in the past
        if issue.return_date and issue.return_date < timezone.now().date():
            days_overdue = (timezone.now().date() - issue.return_date).days
            overdue_fee_per_day = 5  # Adjust as needed
            issue.overdue_amount = days_overdue * overdue_fee_per_day

        # Update the instance to mark the book as returned
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
        # Filter issues where books are not returned
        return Issue.objects.filter(returned=False)

class ReturnedBooksListView(generics.ListAPIView):
    serializer_class = IssuedBooksSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        return Issue.objects.filter(returned=True)

class AllIssuesListView(generics.ListAPIView):
    serializer_class = IssuedBooksSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        return Issue.objects.all()
