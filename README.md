# 💼 JobTrack — Job Application Tracking & Analytics System

JobTrack is a Python-based web application designed to help job seekers manage, track, and analyze their job applications from a single dashboard.

The application allows users to record job applications, monitor application status, manage interview and follow-up dates, maintain notes, and visualize their job-search progress through interactive analytics.

---

## 🚀 Features

### 📊 Dashboard

* View total number of job applications
* Track interviews
* View selection/success rate
* View interview conversion
* Monitor upcoming interviews
* Track pending and overdue follow-ups
* Visualize application status

### ➕ Add Applications

Users can add job application details including:

* Company name
* Job role
* Location
* Salary
* Application date
* Application status
* Job type
* Interview date
* Follow-up date
* Notes

### 📋 Application Management

* View all applications
* Search applications by company or role
* Filter applications by status
* Update application status
* Edit application information
* Delete applications
* Export application data to CSV

### 🔎 Application Details

View detailed information about an individual application, including:

* Company
* Job role
* Location
* Salary
* Job type
* Application date
* Current status
* Interview date
* Follow-up date
* Notes

### 📈 Analytics

JobTrack provides interactive analytics using charts:

* Applications by status
* Applications by company
* Applications by job type
* Applications over time
* Interview conversion
* Selection rate
* Overall application summary

---

## 🛠️ Technologies Used

| Technology | Purpose                        |
| ---------- | ------------------------------ |
| Python     | Application development        |
| Streamlit  | Web application interface      |
| SQLite     | Database management            |
| Pandas     | Data processing and analysis   |
| Plotly     | Interactive data visualization |

---

## 📁 Project Structure

```text
JobTrack/
│
├── app.py                 # Main Streamlit application
├── database.py            # SQLite database operations
├── utils.py               # Data processing and utility functions
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Files excluded from Git
│
└── data/
    └── jobtrack.db        # SQLite database
```

> The `venv/` virtual environment is used locally for development and is excluded from Git using `.gitignore`.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

### 2. Navigate to the project

```bash
cd JobTrack
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the Streamlit application using:

```bash
streamlit run app.py
```

The application will open in your browser.

If it does not open automatically, Streamlit will display a local URL in the terminal.

---

## 🗄️ Database

JobTrack uses **SQLite** for data storage.

The database is automatically initialized when the application starts.

Database location:

```text
data/jobtrack.db
```

The application automatically creates the required database table and handles the required database columns.

---

## 🔄 Application Workflow

```text
Add Job Application
        │
        ▼
Track Application Status
        │
        ├── Applied
        ├── Screening
        ├── Interview
        ├── Selected
        └── Rejected
        │
        ▼
Manage Interview & Follow-up Dates
        │
        ▼
View Application Details
        │
        ▼
Analyze Job Search Performance
```

---

## 📊 Analytics Workflow

JobTrack converts stored application data into useful insights.

```text
SQLite Database
       │
       ▼
    Pandas
       │
       ▼
 Data Processing
       │
       ▼
    Plotly
       │
       ▼
Interactive Analytics
```

---

## 🎯 Project Objectives

The main objectives of JobTrack are:

1. Centralize job application information.
2. Reduce the need for manual spreadsheets.
3. Track application progress.
4. Manage interview and follow-up dates.
5. Provide useful job-search analytics.
6. Improve organization during the job-search process.

---

## 🔐 Data & Security

JobTrack currently uses a local SQLite database for development and personal use.

No external authentication or cloud database is required to run the application.

For production deployment, authentication and a managed database can be added.

---

## 🔮 Future Enhancements

Possible future improvements include:

* Application priority levels
* Job posting URL tracking
* Resume and cover-letter tracking
* Email reminders
* User authentication
* PostgreSQL database support
* Cloud deployment
* Mobile-friendly interface
* Advanced analytics
* Automated notifications

---

## 💡 Learning Outcomes

This project demonstrates practical experience with:

* Python application development
* Streamlit application development
* CRUD operations
* SQLite database integration
* Pandas data processing
* Interactive data visualization
* Form handling
* Search and filtering
* Data export
* Application state management
* Error-resistant date and data handling

---

## 👨‍💻 Project Type

**Python Portfolio Project**

**Domain:** Job Search / Productivity / Data Analytics

**Application:** Job Application Tracking & Analytics System

---

## 📌 How to Use

1. Open the application.
2. Go to **Add Application**.
3. Enter the job application information.
4. Save the application.
5. Track its status from **Applications**.
6. Add interview and follow-up dates when required.
7. Use **Application Details** to view complete information.
8. Use **Dashboard** and **Analytics** to monitor your job-search progress.
9. Export your applications as CSV when required.

---

## ⭐ Author

**JobTrack — Job Application Tracking & Analytics System**

Built as a Python portfolio project to demonstrate practical Python, database, data-processing, and visualization skills.
