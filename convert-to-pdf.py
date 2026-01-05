#!/usr/bin/env python3
"""
Simple Script to Convert Text to PDF
Run: python convert_to_pdf.py
"""

import os
import subprocess
import sys

# Install required package if not present
try:
    from fpdf import FPDF
except ImportError:
    print("Installing fpdf2...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
    from fpdf import FPDF

# PDF content data
documents = {
    "Student_Handbook_2025-2026": """STUDENT HANDBOOK 2025-2026

═══════════════════════════════════════════════════════════════

1. ACADEMIC REGULATIONS

COURSE REQUIREMENTS:
• Minimum 12 credit hours per semester
• Maximum 20 credit hours per semester
• Minimum CGPA required to continue: 2.0
• Academic probation if CGPA < 2.0 for consecutive semesters

ATTENDANCE POLICY:
• Minimum attendance: 75% of classes
• Medical certificate for absences > 3 days
• <75% attendance = cannot sit for exams

GRADING SYSTEM:
• A: 90-100 (4.0 GPA)
• B+: 80-89 (3.5 GPA)
• B: 70-79 (3.0 GPA)
• C+: 60-69 (2.5 GPA)
• C: 50-59 (2.0 GPA)
• D: 40-49 (1.0 GPA)
• F: Below 40 (0.0 GPA)

SUPPLEMENTARY EXAMINATIONS:
• Students scoring below 40 are eligible
• Schedule: July (after summer break)
• Only ONE supplementary per subject
• Fee: ₹500 per subject

2. FEE STRUCTURE 2025-2026

TUITION FEES:
• Per semester: ₹50,000
• Annual: ₹1,00,000
• Deadline: First week of semester

ADDITIONAL FEES:
• Library: ₹2,000/semester
• Sports: ₹1,500/semester
• Lab (Engineering): ₹3,000/semester
• Exam: ₹1,000/semester
• Technology: ₹2,500/semester

HOSTEL FEES (OPTIONAL):
• Accommodation: ₹25,000/semester
• Meal plan: ₹15,000/semester
• Utilities: ₹1,000/month

3. EXAMINATION SCHEDULE

FINAL EXAMS (January 2026):
• Period: January 20 - February 10, 2026
• Time: 2:00 PM - 5:00 PM
• Admit card required

MIDTERM EXAMS (October 2025):
• Period: October 15 - November 5, 2025
• Time: 2:00 PM - 3:30 PM (1.5 hours)
• Marks: 50 (MCQ/Short Answer)
• Weightage: 30% of final grade

EXAM RULES:
• Negative marking: -0.25 per wrong MCQ
• Only blue/black pens allowed
• Mobile phones prohibited
• Malpractice = Exam cancellation
• Late arrival (>30 min) = No entry

4. CAMPUS FACILITIES

LIBRARY:
• Hours: 8 AM-8 PM (Mon-Fri), 10 AM-6 PM (Sat-Sun)
• Max books: 5 per student
• Borrowing: 14 days
• Late fee: ₹10/day
• Digital access: 24/7

COMPUTER LABS:
• Lab A: 50 computers (Programming)
• Lab B: 30 computers (Data Analysis)
• Lab C: 40 computers (Open access)
• Hours: 8 AM - 7 PM
• WiFi: 100 Mbps

SPORTS FACILITIES:
• Basketball courts
• Tennis courts (2)
• Olympic swimming pool
• Gym with modern equipment
• Yoga studio
• Hours: 6 AM - 9 PM

5. HOSTEL INFORMATION

CAPACITY:
• Girls Hostel: 200 rooms
• Boys Hostel: 250 rooms

AMENITIES:
• Air-conditioned rooms
• Wi-Fi in every room
• Common TV room
• Laundry service (2x/week)
• 24/7 security & CCTV

HOSTEL RULES:
• Gate closure: 10:00 PM
• Guests: Max 1/month (3 hours)
• Ragging: Strictly prohibited
• Noise restriction: After 9 PM
• Inspection: Every Friday 2 PM

CONTACT:
• Girls Warden: Dr. Priya Sharma (9876543210)
• Boys Warden: Mr. Rajesh Kumar (9876543211)
• Office hours: 10 AM - 5 PM

6. DISCIPLINARY CODE

ACADEMIC MISCONDUCT:
• Cheating: Exam cancellation + 1 semester suspension
• Plagiarism: Re-submission + grade penalty
• Unauthorized collaboration: 50% deduction
• Unfair means: Up to expulsion

CONDUCT VIOLATIONS:
• Ragging: Zero tolerance + rustication
• Harassment: Immediate suspension + legal action
• Violence: Expulsion
• Drug use: Expulsion

GRIEVANCE REDRESSAL:
• Submit within 5 days
• Review within 10 days
• Appeal within 7 days
• Online portal available

═══════════════════════════════════════════════════════════════

IMPORTANT CONTACTS:
Principal: principal@campus.edu (Ext: 101)
Registrar: registrar@campus.edu (Ext: 102)
Finance: finance@campus.edu (Ext: 103)
Academic Advisor: advising@campus.edu
Student Services: studentservices@campus.edu

Last Updated: December 2025""",
    
    "Data_Science_Course_Syllabus": """COURSE SYLLABUS: DATA SCIENCE 101

═══════════════════════════════════════════════════════════════

COURSE INFORMATION:
Course Code: DS-101
Semester: Spring 2026
Credits: 4
Instructor: Dr. Arun Patel
Office Hours: Mon & Wed, 3:00 PM - 5:00 PM (Room 305)
Email: arun.patel@campus.edu

COURSE OVERVIEW:
This course introduces fundamental concepts of data science including 
data collection, cleaning, analysis, and visualization.

COURSE OBJECTIVES:
1. Understand the data science pipeline
2. Master Python libraries: NumPy, Pandas, Matplotlib
3. Perform exploratory data analysis (EDA)
4. Build basic machine learning models
5. Communicate findings through visualizations

PREREQUISITES:
• Computer Science Fundamentals (CS-101)
• Basic mathematics (Statistics preferred)

COURSE MATERIALS:
• Textbook: "Python for Data Analysis" by Wes McKinney (2nd Ed)
• Software: Python 3.9+, Jupyter Notebook, Anaconda
• All tools are free and open-source

GRADING BREAKDOWN:
• Attendance: 5%
• Class Participation: 10%
• Assignments (5 × 5%): 25%
• Midterm Project: 20%
• Final Project: 40%

GRADING SCALE:
• A: 90-100
• B: 80-89
• C: 70-79
• D: 60-69
• F: Below 60

COURSE SCHEDULE:

WEEKS 1-2: Introduction to Data Science
• What is Data Science?
• Data Science Workflow
• Python Basics (Variables, Data Types)
• Tools Setup

WEEKS 3-4: Data Handling with Pandas
• DataFrames and Series
• Reading CSV and Excel files
• Data Cleaning (Missing Values)
• Data Transformation

WEEKS 5-6: Data Visualization
• Matplotlib Basics
• Creating Plots (Line, Bar, Scatter)
• Seaborn for Advanced Visualization
• Creating Dashboards

WEEKS 7-8: Exploratory Data Analysis
• Statistical Summary
• Correlation Analysis
• Distribution Analysis
• Outlier Detection

WEEK 9: Midterm Project
• Analyze provided dataset
• Create comprehensive report
• Present findings (5 minutes)

WEEKS 10-11: Machine Learning Basics
• Supervised Learning Overview
• Linear Regression
• Logistic Regression
• Model Evaluation Metrics

WEEKS 12-13: Advanced Topics
• Decision Trees and Random Forests
• Unsupervised Learning (K-Means)
• Cross-Validation Techniques
• Hyperparameter Tuning

WEEKS 14-15: Final Project Work
• Individual/Team Project
• Consultations with Instructor
• Final Presentation Rehearsal

WEEK 16: Final Presentations & Exam Week

ASSIGNMENT DEADLINES:
• Assignment 1: January 30, 2026 (11:59 PM)
• Assignment 2: February 13, 2026 (11:59 PM)
• Assignment 3: February 27, 2026 (11:59 PM)
• Midterm Project: March 13, 2026 (11:59 PM)
• Assignment 4: April 10, 2026 (11:59 PM)
• Assignment 5: April 24, 2026 (11:59 PM)
• Final Project: May 10, 2026 (11:59 PM)

COURSE POLICIES:

ATTENDANCE:
• Mandatory for all lectures and labs
• >3 absences without certificate = grade penalty
• >15 min late = marked absent

ACADEMIC INTEGRITY:
• All work must be original
• Citing sources is mandatory
• Plagiarism = course failure
• Cheating = course cancellation

LATE SUBMISSION:
• After deadline: -10% per day
• Maximum 3 days late (no credit after)

LAB REQUIREMENTS:
• Every Friday, 2:00 PM - 4:00 PM (Room 402)
• Attendance mandatory
• Laptop with Python required

FINAL EXAM:
• Date: May 15, 2026
• Time: 2:00 PM - 5:00 PM
• Format: 2-hour exam + 1-hour project
• Coverage: All topics Weeks 1-16
• 1 page handwritten notes allowed

RECOMMENDED RESOURCES:
• Kaggle.com (Datasets)
• DataCamp (Interactive Learning)
• GitHub (Code Repository)
• Stack Overflow (Q&A)
• Medium (Blog Articles)

CONTACT AND SUPPORT:
Email: arun.patel@campus.edu
Course Forum: Available on Canvas
Emergency Contact: 9876543220

Last Updated: December 2025""",

    "Exam_Guidelines_Schedule": """EXAMINATION GUIDELINES & SCHEDULE 2025-2026

═══════════════════════════════════════════════════════════════

SEMESTER EXAMINATION TIMETABLE

ODD SEMESTER (JANUARY 2026) - FINAL EXAMS
Exam Period: January 20 - February 10, 2026

DATE     | TIME     | COURSE  | COURSE TITLE            | VENUE
─────────────────────────────────────────────────────────────
Jan 20   | 2:00 PM  | CS-101  | Computer Fundamentals  | Hall A
Jan 21   | 2:00 PM  | MATH-101| Calculus I             | Hall B
Jan 22   | 2:00 PM  | ENG-101 | English Communication  | Hall C
Jan 23   | 2:00 PM  | PHYS-101| Physics I              | Hall A
Jan 26   | 2:00 PM  | DS-101  | Data Science           | Hall B
Jan 27   | 2:00 PM  | WEB-101 | Web Development        | Hall C
Jan 28   | 2:00 PM  | DB-101  | Database Design        | Hall A
Jan 29   | 2:00 PM  | AI-101  | Introduction to AI     | Hall B
Jan 30   | 2:00 PM  | CHEM-101| Chemistry              | Hall C
Feb 2    | 2:00 PM  | STAT-101| Statistics             | Hall A
Feb 3    | 2:00 PM  | ECO-101 | Economics              | Hall B
Feb 4    | 2:00 PM  | PSYCH-101| Psychology            | Hall C

EVEN SEMESTER (MAY 2026) - FINAL EXAMS
Exam Period: May 15 - June 5, 2026
(Schedule to be released in April 2026)

MIDTERM EXAMINATION SCHEDULE (October 2025)
Exam Period: October 15 - November 5, 2025
• Timing: 2:00 PM - 3:30 PM (1.5 hours)
• Format: 50 marks MCQ/Short Answer
• Weightage: 30% of final grade

EXAMINATION RULES AND PROCEDURES

BEFORE THE EXAMINATION:

Admit Card:
✓ Issued 7 days before exam
✓ Available on student portal
✓ Must carry to exam hall
✓ Duplicate available at ₹100

Seat Allocation:
✓ Displayed 3 days before exam
✓ Roll number wise arrangement
✓ Alphabetical order

Preparation:
✓ Only textbooks and official notes
✓ No advance help from instructors
✓ Contact academic office for clarifications

DURING THE EXAMINATION:

Entry Requirements:
✓ Arrive 15 minutes before start
✓ Gate closure strictly at exam time
✓ Valid photo ID + Admit card required
✓ Mobile phones strictly prohibited

Exam Duration:
✓ Final: 3 hours
✓ Midterm: 1.5 hours
✓ Question paper: 5 minutes after start
✓ Warning bell: 15 minutes before end

Conduct During Exam:
✓ Silence must be maintained
✓ No communication with students
✓ Raise hand for assistance
✓ Only blue/black ballpoint pens
✓ Rough work on answer sheet only

Malpractice:
✓ Cheating: Answer sheet confiscated
✓ Exam canceled: Course marked 'F'
✓ Disciplinary action: Up to suspension
✓ Serious cases: Referred to Dean

AFTER THE EXAMINATION:

Answer Sheet:
✓ Return to invigilator before leaving
✓ Don't fold or damage
✓ Keep copy of exam slip

Result Declaration:
✓ Within 2 weeks after exam
✓ Available on student portal
✓ SMS notification
✓ Email notification

Re-evaluation:
✓ Request within 5 days
✓ Fee: ₹500 per subject
✓ Evaluated by different examiner
✓ Final result is binding
✓ No appeal after re-eval

EXAMINATION CENTERS:

MAIN CAMPUS (City Center):
• Address: 123 University Road, Downtown
• Exam Halls: A, B, C, D (Capacity: 100 each)
• Parking: Available (₹50/day)
• Contact: 9876543200

NORTH CAMPUS:
• Address: 456 Tech Park, North Zone
• Exam Halls: E, F (Capacity: 80 each)
• Parking: Free
• Contact: 9876543201

SOUTH CAMPUS:
• Address: 789 Innovation Hub, South Zone
• Exam Halls: G, H (Capacity: 60 each)
• Parking: Limited
• Contact: 9876543202

SPECIAL CIRCUMSTANCES:

MEDICAL LEAVE DURING EXAMS:
✓ Medical certificate required
✓ Submit within 24 hours
✓ Alternative exam date scheduled
✓ Must appear within same year

GRIEVANCE/DISPUTE:
✓ File complaint within 3 days
✓ Investigation period: 10 days
✓ Appeal process available

SUPPLEMENTARY EXAMS:
✓ Eligible: Scored below 40
✓ Schedule: July 2026
✓ Fee: ₹500 per subject
✓ Only ONE per subject

IMPORTANT CONTACTS:

Academic Affairs: 9876543100
Examination Cell: 9876543101
Student Services: 9876543102
Medical Center: 9876543103

Email:
academic@campus.edu
exams@campus.edu
studentservices@campus.edu
medical@campus.edu

FREQUENTLY ASKED QUESTIONS:

Q: Can I request a different exam time?
A: No, exam times are fixed unless medical grounds.

Q: What if I miss an exam due to illness?
A: Submit medical certificate within 24 hours.

Q: Is there a penalty for being late?
A: Yes, cannot enter after gate closure.

Q: Can I use calculator in exams?
A: Only non-programmable calculator allowed.

Q: How many times can I attempt supplementary?
A: Only one per subject.

Q: When can I get my answer sheet?
A: After results, available for 3 months in office.

═══════════════════════════════════════════════════════════════

Document Version: 2.1
Last Updated: December 2025
Next Review: August 2026"""
}

def create_pdfs():
    """Create PDF files from content"""
    print("Creating PDF files...")
    print("=" * 70)
    
    for filename, content in documents.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Add content
        for line in content.split('\n'):
            if len(line) == 0:
                pdf.ln(5)
            else:
                # Handle long lines
                pdf.multi_cell(0, 5, line)
        
        pdf_filename = f"{filename}.pdf"
        pdf.output(pdf_filename)
        
        file_size = os.path.getsize(pdf_filename)
        print(f"✅ Created: {pdf_filename} ({file_size/1024:.1f} KB)")
    
    print("=" * 70)
    print("🎉 All PDF files ready in current directory!")
    print("📂 Files created:")
    for filename in documents.keys():
        print(f"   - {filename}.pdf")

if __name__ == "__main__":
    create_pdfs()
