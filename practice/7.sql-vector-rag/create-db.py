import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
load_dotenv()
import os

# Define connection parameters
conn_params = {
    'dbname': os.environ.get('DATABASE') ,
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('PASSWORD'),
    'host': os.environ.get('HOST'),
    'port': os.environ.get('PORT')
}

# Define the SQL statements for table creation
create_table_queries = [
    """
    CREATE TABLE patients (
        patient_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INT,
        gender VARCHAR(10),
        medical_history TEXT
    );
    """,
    """
    CREATE TABLE visits (
        visit_id SERIAL PRIMARY KEY,
        patient_id INT REFERENCES patients(patient_id),
        visit_date DATE,
        symptoms TEXT,
        diagnosis TEXT,
        treatment_plan TEXT
    );
    """,
    """
    CREATE TABLE lab_results (
        lab_result_id SERIAL PRIMARY KEY,
        visit_id INT REFERENCES visits(visit_id),
        test_name VARCHAR(100),
        test_result TEXT,
        result_date DATE
    );
    """,
    """
    CREATE TABLE medications (
        medication_id SERIAL PRIMARY KEY,
        patient_id INT REFERENCES patients(patient_id),
        medication_name VARCHAR(100),
        dosage VARCHAR(50),
        start_date DATE,
        end_date DATE
    );
    """,
    """
    CREATE TABLE treatments (
        treatment_id SERIAL PRIMARY KEY,
        visit_id INT REFERENCES visits(visit_id),
        treatment_name VARCHAR(100),
        description TEXT,
        treatment_date DATE
    );
    """,
    """
    CREATE TABLE appointments (
        appointment_id SERIAL PRIMARY KEY,
        patient_id INT REFERENCES patients(patient_id),
        appointment_date DATE,
        doctor_name VARCHAR(100),
        notes TEXT
    );
    """,
    """
    CREATE TABLE doctors (
        doctor_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        specialty VARCHAR(100),
        contact_info VARCHAR(100)
    );
    """,
    """
    CREATE TABLE patient_doctor (
        patient_id INT REFERENCES patients(patient_id),
        doctor_id INT REFERENCES doctors(doctor_id),
        PRIMARY KEY (patient_id, doctor_id)
    );
    """
]

# Connect to the PostgreSQL database
conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

# Execute the table creation queries
try:
    for query in create_table_queries:
        cur.execute(query)
    conn.commit()
    print("Tables created successfully")
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
