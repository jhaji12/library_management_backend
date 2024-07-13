import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_backend.settings')
django.setup()

import pandas as pd
from library.models import Student

def upload_data_from_csv():
    print("started")
    # Read Excel file into a DataFrame
    df = pd.read_csv('student_updated.csv')

    # Iterate over rows in the DataFrame
    for index, row in df.iterrows():
        # Create a new instance of your Django model
        my_model_instance = Student(name=row['name'], adm_number=row['adm_number'], school_class=row['school_class'], max_books_allowed=row['max_books_allowed'], school_id=row['school_id'])

        # Save the instance to the database
        my_model_instance.save()
    print("doneeee")


upload_data_from_csv()
