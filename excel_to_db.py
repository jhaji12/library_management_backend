import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_backend.settings')
django.setup()

import pandas as pd
from library.models import Book

def upload_data_from_excel():
    print("Started uploading data from Excel...")
    
    # Read Excel file into a DataFrame
    df = pd.read_excel('LOFTYReport.xlsx')
    
    # Iterate over rows in the DataFrame
    for index, row in df.iterrows():
        # Check if a book with the same ISBN exists
        existing_book = Book.objects.filter(book_id=row['book_id']).first()
        
        if existing_book:
            print("existing")
            # Update the existing book record
            existing_book.book_id = row['book_id']
            existing_book.accession_date = row['accession_date']
            existing_book.title = row['title']
            existing_book.vendor = row['vendor']
            existing_book.language = row['language']
            existing_book.publication = row['publication']
            existing_book.shelf_name = row['shelf_name']
            existing_book.available_copies = row['available_copies']
            existing_book.isbn = row['isbn']
            existing_book.school_id = row['school_id']
            
            # Save the updated instance to the database
            existing_book.save()
        else:
            # Create a new instance of your Django model
            new_book = Book(
                book_id=row['book_id'],
                accession_date=row['accession_date'],
                title=row['title'],
                vendor=row['vendor'],
                language=row['language'],
                publication=row['publication'],
                shelf_name=row['shelf_name'],
                available_copies=row['available_copies'],
                isbn=row['isbn'],
                school_id=row['school_id']
            )
            
            # Save the new instance to the database
            new_book.save()
    
    print("Data upload completed.")

# Call the function to upload data from Excel
upload_data_from_excel()

