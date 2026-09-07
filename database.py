import sqlite3
from pathlib import Path


# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------

DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_NAME = DATABASE_DIR / "jobtrack.db"


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ---------------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------------

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            application_date TEXT NOT NULL,
            status TEXT NOT NULL,
            job_type TEXT,
            notes TEXT,
            interview_date TEXT,
            follow_up_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    # -----------------------------------------------------
    # DATABASE MIGRATION
    # -----------------------------------------------------

    cursor.execute("PRAGMA table_info(jobs)")

    existing_columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "interview_date" not in existing_columns:

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN interview_date TEXT
        """)

    if "follow_up_date" not in existing_columns:

        cursor.execute("""
            ALTER TABLE jobs
            ADD COLUMN follow_up_date TEXT
        """)

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# ADD APPLICATION
# ---------------------------------------------------------

def add_application(
    company,
    role,
    location,
    salary,
    application_date,
    status,
    job_type,
    notes,
    interview_date=None,
    follow_up_date=None
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO jobs (
            company,
            role,
            location,
            salary,
            application_date,
            status,
            job_type,
            notes,
            interview_date,
            follow_up_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company,
        role,
        location,
        salary,
        application_date,
        status,
        job_type,
        notes,
        interview_date,
        follow_up_date
    ))

    connection.commit()
    connection.close()


# ---------------------------------------------------------
# GET ALL APPLICATIONS
# ---------------------------------------------------------

def get_all_applications():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            company,
            role,
            location,
            salary,
            application_date,
            status,
            job_type,
            notes,
            interview_date,
            follow_up_date
        FROM jobs
        ORDER BY application_date DESC
    """)

    data = cursor.fetchall()

    connection.close()

    return data


# ---------------------------------------------------------
# UPDATE STATUS
# ---------------------------------------------------------

def update_status(application_id, new_status):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET status = ?
        WHERE id = ?
    """, (
        new_status,
        application_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()
    connection.close()

    return rows_updated > 0


# ---------------------------------------------------------
# UPDATE INTERVIEW DATE
# ---------------------------------------------------------

def update_interview_date(application_id, interview_date):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET interview_date = ?
        WHERE id = ?
    """, (
        interview_date,
        application_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()
    connection.close()

    return rows_updated > 0


# ---------------------------------------------------------
# UPDATE FOLLOW-UP DATE
# ---------------------------------------------------------

def update_follow_up_date(application_id, follow_up_date):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET follow_up_date = ?
        WHERE id = ?
    """, (
        follow_up_date,
        application_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()
    connection.close()

    return rows_updated > 0


# ---------------------------------------------------------
# UPDATE COMPLETE APPLICATION
# ---------------------------------------------------------

def update_application(
    application_id,
    company,
    role,
    location,
    salary,
    application_date,
    status,
    job_type,
    notes,
    interview_date=None,
    follow_up_date=None
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE jobs
        SET
            company = ?,
            role = ?,
            location = ?,
            salary = ?,
            application_date = ?,
            status = ?,
            job_type = ?,
            notes = ?,
            interview_date = ?,
            follow_up_date = ?
        WHERE id = ?
    """, (
        company,
        role,
        location,
        salary,
        application_date,
        status,
        job_type,
        notes,
        interview_date,
        follow_up_date,
        application_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()
    connection.close()

    return rows_updated > 0


# ---------------------------------------------------------
# DELETE APPLICATION
# ---------------------------------------------------------

def delete_application(application_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM jobs
        WHERE id = ?
    """, (
        application_id,
    ))

    rows_deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return rows_deleted > 0