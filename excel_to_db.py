import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_backend.settings')
django.setup()

import pandas as pd
from library.models import Book

def upload_data_from_excel():
    print("started")
    # Read Excel file into a DataFrame
    df = pd.read_excel('LOFTYReport.xlsx')

    # Iterate over rows in the DataFrame
    for index, row in df.iterrows():
        # Create a new instance of your Django model
        my_model_instance = Book(book_id=row['book_id'], accession_date=row['accession_date'], title=row['title'], vendor=row['vendor'], language=row['language'], publication=row['publication'], shelf_name=row['shelf_name'], available_copies=row['available_copies'])

        # Save the instance to the database
        my_model_instance.save()
    print("doneeee")


upload_data_from_excel()
