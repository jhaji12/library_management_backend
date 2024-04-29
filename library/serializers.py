from rest_framework import serializers
from .models import Student, Book, Issue, Faculty
       
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = "__all__"

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

class IssueSerializer(serializers.ModelSerializer):
    book_id = serializers.CharField(max_length=100)
    student_id = serializers.CharField(max_length=100, required=False)
    faculty_id = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Issue
        exclude = ['return_date']

    def create(self, validated_data):
        book_id = validated_data.pop('book_id')
        if student_id:
            issuer_type = "student"
        else:
            issuer_type = "faculty"

        # Retrieve the Book object using the provided ID
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book does not exist")

        # Determine if the issuer is a student or a faculty member
        if issuer_type == 'student':
            student_id = validated_data.pop('student_id', None)
            if not student_id:
                raise serializers.ValidationError("Student ID is required")
            try:
                student = Student.objects.get(pk=student_id)
            except Student.DoesNotExist:
                raise serializers.ValidationError("Student does not exist")

            # Create the Issue object with the retrieved Book and Student objects
            issue = Issue.objects.create(book=book, student=student, **validated_data)
        elif issuer_type == 'faculty':
            faculty_id = validated_data.pop('faculty_id', None)
            if not faculty_id:
                raise serializers.ValidationError("Faculty ID is required")
            try:
                faculty = Faculty.objects.get(pk=faculty_id)
            except Faculty.DoesNotExist:
                raise serializers.ValidationError("Faculty does not exist")

            # Create the Issue object with the retrieved Book and Faculty objects
            issue = Issue.objects.create(book=book, faculty=faculty, **validated_data)

        return issue

class IssuedBooksSerializer(serializers.ModelSerializer):
    # Define fields to be returned
    title = serializers.ReadOnlyField(source='book.title')
    book_id = serializers.ReadOnlyField(source='book.book_id')
    student_name = serializers.ReadOnlyField(source='student.name')
    adm_number = serializers.ReadOnlyField(source='student.adm_number')
    faculty_name = serializers.ReadOnlyField(source='faculty.name')
    faculty_id = serializers.ReadOnlyField(source='faculty.faculty_id')
    overdue_amount = serializers.ReadOnlyField()
    return_date = serializers.ReadOnlyField()
    # returned = serializers.ReadOnlyField()

    class Meta:
        model = Issue
        fields = ['title', 'book_id', 'student_name', 'adm_number', 'faculty_name', 'faculty_id','overdue_amount', 'return_date']
