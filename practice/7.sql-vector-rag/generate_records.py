import psycopg2
from faker import Faker
import random

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

# Initialize Faker for generating random data
fake = Faker()

conn = psycopg2.connect(**conn_params)
cur = conn.cursor()

# Generate and insert 100 sample records
for _ in range(100):
    name = fake.name()
    age = random.randint(1, 101)
    gender = random.choice(['Male', 'Female', 'Other'])
    medical_history = fake.text(max_nb_chars=200)
    
    insert_query = """
    INSERT INTO patients (name, age, gender, medical_history)
    VALUES (%s, %s, %s, %s);
    """
    cur.execute(insert_query, (name, age, gender, medical_history))

patient_ids = list(range(1, 101))  # Assuming patient IDs from 1 to 100

# Visits table
visit_ids = []
for _ in range(100):
    patient_id = random.choice(patient_ids)
    visit_date = fake.date_between(start_date='-2y', end_date='today')
    symptoms = fake.text(max_nb_chars=200)
    diagnosis = fake.text(max_nb_chars=200)
    treatment_plan = fake.text(max_nb_chars=200)
    
    cur.execute("""
        INSERT INTO visits (patient_id, visit_date, symptoms, diagnosis, treatment_plan)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING visit_id;
    """, (patient_id, visit_date, symptoms, diagnosis, treatment_plan))
    
    visit_id = cur.fetchone()[0]
    visit_ids.append(visit_id)

# Lab results table
for _ in range(100):
    visit_id = random.choice(visit_ids)
    test_name = fake.word()
    test_result = fake.text(max_nb_chars=200)
    result_date = fake.date_between(start_date='-2y', end_date='today')
    
    cur.execute("""
        INSERT INTO lab_results (visit_id, test_name, test_result, result_date)
        VALUES (%s, %s, %s, %s);
    """, (visit_id, test_name, test_result, result_date))

# Medications table
for _ in range(100):
    patient_id = random.choice(patient_ids)
    medication_name = fake.word()
    dosage = fake.word()
    start_date = fake.date_between(start_date='-2y', end_date='-1y')
    end_date = fake.date_between(start_date='-1y', end_date='today')
    
    cur.execute("""
        INSERT INTO medications (patient_id, medication_name, dosage, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s);
    """, (patient_id, medication_name, dosage, start_date, end_date))

# Treatments table
for _ in range(100):
    visit_id = random.choice(visit_ids)
    treatment_name = fake.word()
    description = fake.text(max_nb_chars=200)
    treatment_date = fake.date_between(start_date='-2y', end_date='today')
    
    cur.execute("""
        INSERT INTO treatments (visit_id, treatment_name, description, treatment_date)
        VALUES (%s, %s, %s, %s);
    """, (visit_id, treatment_name, description, treatment_date))

# Appointments table
for _ in range(100):
    patient_id = random.choice(patient_ids)
    appointment_date = fake.date_between(start_date='today', end_date='+1y')
    doctor_name = fake.name()
    notes = fake.text(max_nb_chars=200)
    
    cur.execute("""
        INSERT INTO appointments (patient_id, appointment_date, doctor_name, notes)
        VALUES (%s, %s, %s, %s);
    """, (patient_id, appointment_date, doctor_name, notes))

# Doctors table
doctor_ids = []
for _ in range(50):  # Assuming you want 50 doctors
    name = fake.name()
    specialty = fake.word()
    contact_info = fake.phone_number()
    
    cur.execute("""
        INSERT INTO doctors (name, specialty, contact_info)
        VALUES (%s, %s, %s)
        RETURNING doctor_id;
    """, (name, specialty, contact_info))
    
    doctor_id = cur.fetchone()[0]
    doctor_ids.append(doctor_id)

# Patient_doctor table
unique_combinations = set()
while len(unique_combinations) < 100:
    patient_id = random.choice(patient_ids)
    doctor_id = random.choice(doctor_ids)
    combination = (patient_id, doctor_id)
    
    if combination not in unique_combinations:
        unique_combinations.add(combination)
        cur.execute("""
            INSERT INTO patient_doctor (patient_id, doctor_id)
            VALUES (%s, %s);
        """, (patient_id, doctor_id))

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print("100 sample records inserted into the patients table successfully.")
