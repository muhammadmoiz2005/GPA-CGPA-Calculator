import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
import base64

# Page configuration
st.set_page_config(
    page_title="GPA & CGPA Calculator",
    page_icon="🎓",
    layout="wide"
)

# SQL file path
SQL_FILE = 'gpa_database.sql'

# Initialize SQL file with table creation
def init_sql_file():
    if not os.path.exists(SQL_FILE):
        with open(SQL_FILE, 'w', encoding='utf-8') as f:
            f.write("""-- GPA & CGPA Calculator Database
-- Created: {}

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

-- Table: gpa_records
CREATE TABLE IF NOT EXISTS gpa_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    course_name TEXT NOT NULL,
    total_marks REAL NOT NULL,
    obtained_marks REAL NOT NULL,
    credit_hours REAL NOT NULL,
    percentage REAL NOT NULL,
    grade TEXT NOT NULL,
    gpa REAL NOT NULL,
    grade_points REAL NOT NULL
);

-- Table: cgpa_records
CREATE TABLE IF NOT EXISTS cgpa_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    semester_number INTEGER NOT NULL,
    semester_gpa REAL NOT NULL,
    credit_hours REAL NOT NULL,
    grade_points REAL NOT NULL
);

-- Table: calculation_summary
CREATE TABLE IF NOT EXISTS calculation_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    calculation_type TEXT NOT NULL,
    final_result REAL NOT NULL,
    total_credit_hours REAL NOT NULL,
    total_grade_points REAL NOT NULL
);

-- ========================================
-- DATA ENTRIES START BELOW
-- ========================================

""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

# Initialize SQL file
init_sql_file()

# Grading table
GRADE_TABLE = [
    (91, 100, 'A', 4.00),
    (80, 90, 'A-', 3.66),
    (75, 79, 'B+', 3.33),
    (71, 74, 'B', 3.00),
    (68, 70, 'B-', 2.66),
    (64, 67, 'C+', 2.33),
    (61, 63, 'C', 2.00),
    (58, 60, 'C-', 1.66),
    (54, 57, 'D+', 1.33),
    (50, 53, 'D', 1.00),
    (0, 49, 'F', 0.00)
]

def get_grade_info(percentage):
    for min_score, max_score, grade, gpa in GRADE_TABLE:
        if min_score <= percentage <= max_score:
            return grade, gpa
    return 'F', 0.00

def save_gpa_to_sql(user_name, courses_data, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(SQL_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n-- GPA Calculation Entry: {timestamp}\n")
        f.write(f"-- User: {user_name}\n")
        f.write(f"-- ==========================================\n\n")
        
        # Save user
        sql = f"""INSERT INTO users (name, timestamp)
VALUES ('{user_name}', '{timestamp}');

"""
        f.write(sql)
        
        # Save individual courses
        for i, course in enumerate(courses_data, 1):
            sql = f"""INSERT INTO gpa_records (user_name, timestamp, course_name, total_marks, obtained_marks, credit_hours, percentage, grade, gpa, grade_points)
VALUES ('{user_name}', '{timestamp}', '{course['course_name']}', {course['total_marks']}, {course['obtained_marks']}, {course['credit_hours']}, {course['percentage']}, '{course['grade']}', {course['gpa']}, {course['grade_points']});
"""
            f.write(sql)
        
        # Save summary
        sql = f"""
INSERT INTO calculation_summary (user_name, timestamp, calculation_type, final_result, total_credit_hours, total_grade_points)
VALUES ('{user_name}', '{timestamp}', 'GPA', {summary['gpa']}, {summary['total_credit_hours']}, {summary['total_grade_points']});

"""
        f.write(sql)

def save_cgpa_to_sql(user_name, semesters_data, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(SQL_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n-- CGPA Calculation Entry: {timestamp}\n")
        f.write(f"-- User: {user_name}\n")
        f.write(f"-- ==========================================\n\n")
        
        # Save user
        sql = f"""INSERT INTO users (name, timestamp)
VALUES ('{user_name}', '{timestamp}');

"""
        f.write(sql)
        
        # Save individual semesters
        for i, semester in enumerate(semesters_data, 1):
            sql = f"""INSERT INTO cgpa_records (user_name, timestamp, semester_number, semester_gpa, credit_hours, grade_points)
VALUES ('{user_name}', '{timestamp}', {i}, {semester['gpa']}, {semester['credit_hours']}, {semester['grade_points']});
"""
            f.write(sql)
        
        # Save summary
        sql = f"""
INSERT INTO calculation_summary (user_name, timestamp, calculation_type, final_result, total_credit_hours, total_grade_points)
VALUES ('{user_name}', '{timestamp}', 'CGPA', {summary['cgpa']}, {summary['total_credit_hours']}, {summary['total_grade_points']});

"""
        f.write(sql)

def export_to_excel(data, calculation_type):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if calculation_type == 'GPA':
            # Course details sheet
            courses_df = pd.DataFrame(data['courses'])
            courses_df.index = courses_df.index + 1
            courses_df.index.name = 'Course No.'
            courses_df.to_excel(writer, sheet_name='Course Details')
            
            # Summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Credit Hours', 'Total Grade Points', 'Final GPA'],
                'Value': [data['summary']['total_credit_hours'], 
                         data['summary']['total_grade_points'],
                         data['summary']['gpa']]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
        else:  # CGPA
            # Semester details sheet
            semesters_df = pd.DataFrame(data['semesters'])
            semesters_df.index = semesters_df.index + 1
            semesters_df.index.name = 'Semester No.'
            semesters_df.to_excel(writer, sheet_name='Semester Details')
            
            # Summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Credit Hours', 'Total Grade Points', 'Final CGPA'],
                'Value': [data['summary']['total_credit_hours'], 
                         data['summary']['total_grade_points'],
                         data['summary']['cgpa']]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    return output

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .result-card {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header" style="text-align: center;">
        <img src="https://www.smiu.edu.pk/themes/smiu/images/13254460_710745915734761_8157428650049174152_n.png" width="200">
        <h1>Welcome to SMIU GPA & CGPA Calculator</h1>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 GPA Calculator", "📈 CGPA Calculator", "📋 Grading Scale"])

# ============= GPA CALCULATOR =============
with tab1:
    st.header("Semester GPA Calculator")
    
    # User name input
    st.subheader("👤 Student Information")
    user_name = st.text_input("Enter Your Name *", placeholder="e.g., M.Moiz", key='gpa_user_name')
    
    # if not user_name:
    #     st.warning("⚠️ Please enter your name to continue")
    #     st.stop()
    
    st.markdown("---")
    
    # Initialize session state
    if 'num_courses' not in st.session_state:
        st.session_state.num_courses = 1
    
    # Number of courses
    col1, col2 = st.columns([3, 1])
    with col1:
        num_courses = st.number_input("How many courses do you have?", 
                                      min_value=1, max_value=20, 
                                      value=st.session_state.num_courses,
                                      key='courses_input')
        st.session_state.num_courses = num_courses
    
    # Course inputs
    courses_data = []
    
    for i in range(num_courses):
        st.subheader(f"📚 Course {i+1}")
        
        # Course name input
        course_name = st.text_input(f"Course Name *", 
                                    placeholder="e.g., Data Structures",
                                    key=f'course_name_{i}')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_marks = st.number_input(f"Total Marks", 
                                         min_value=0.0, 
                                         value=100.0,
                                         key=f'total_{i}')
        with col2:
            obtained_marks = st.number_input(f"Obtained Marks", 
                                            min_value=0.0, 
                                            max_value=total_marks,
                                            value=0.0,
                                            key=f'obtained_{i}')
        with col3:
            credit_hours = st.number_input(f"Credit Hours", 
                                          min_value=0.0,
                                          value=3.0,
                                          key=f'credit_{i}')
        
        courses_data.append({
            'course_name': course_name if course_name else f"Course {i+1}",
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'credit_hours': credit_hours
        })
        
        st.markdown("---")
    
    # Calculate button
    if st.button("🧮 Calculate GPA", type="primary", key='calc_gpa'):
        total_grade_points = 0
        total_credit_hours = 0
        course_results = []
        
        for i, course in enumerate(courses_data):
            if course['total_marks'] > 0 and course['credit_hours'] > 0:
                percentage = (course['obtained_marks'] / course['total_marks']) * 100
                grade, gpa = get_grade_info(percentage)
                grade_points = gpa * course['credit_hours']
                
                total_grade_points += grade_points
                total_credit_hours += course['credit_hours']
                
                course_results.append({
                    'Course Name': course['course_name'],
                    'Total Marks': course['total_marks'],
                    'Obtained Marks': course['obtained_marks'],
                    'Percentage': f"{percentage:.2f}%",
                    'Credit Hours': course['credit_hours'],
                    'Grade': grade,
                    'GPA': gpa,
                    'Grade Points': f"{grade_points:.2f}"
                })
        
        if total_credit_hours > 0:
            final_gpa = total_grade_points / total_credit_hours
            
            # Display results
            st.success(f"✅ GPA Calculated Successfully for {user_name}!")
            
            # Results table
            st.subheader("📊 Course-wise Results")
            df = pd.DataFrame(course_results)
            st.dataframe(df, use_container_width=True)
            
            # Summary metrics
            st.subheader("📈 Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Total Credit Hours</h3>
                        <h2>{total_credit_hours:.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Total Grade Points</h3>
                        <h2>{total_grade_points:.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Semester GPA</h3>
                        <h2>{final_gpa:.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            # Save to database
            courses_db_data = []
            for course in course_results:
                courses_db_data.append({
                    'course_name': course['Course Name'],
                    'total_marks': float(course['Total Marks']),
                    'obtained_marks': float(course['Obtained Marks']),
                    'credit_hours': float(course['Credit Hours']),
                    'percentage': float(course['Percentage'].strip('%')),
                    'grade': course['Grade'],
                    'gpa': float(course['GPA']),
                    'grade_points': float(course['Grade Points'])
                })
            
            summary = {
                'gpa': final_gpa,
                'total_credit_hours': total_credit_hours,
                'total_grade_points': total_grade_points
            }
            
            save_gpa_to_sql(user_name, courses_db_data, summary)
            st.info("❤ Thank You! For using the SMIU Semester GPA Calculator.")
            
            # Export to Excel
            export_data = {
                'courses': course_results,
                'summary': summary
            }
            excel_file = export_to_excel(export_data, 'GPA')
            
            st.download_button(
                label="📥 Download Semester GPA Report",
                data=excel_file,
                file_name=f"GPA_Report_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("❌ Please enter valid credit hours!")

# ============= CGPA CALCULATOR =============
with tab2:
    st.header("Overall CGPA Calculator")
    
    # User name input
    st.subheader("👤 Student Information")
    user_name_cgpa = st.text_input("Enter Your Name *", placeholder="e.g., M.Moiz", key='cgpa_user_name')
    
    st.markdown("---")
    
    # Initialize session state
    if 'num_semesters' not in st.session_state:
        st.session_state.num_semesters = 1
    
    # Number of semesters
    col1, col2 = st.columns([3, 1])
    with col1:
        num_semesters = st.number_input("How many semesters do you want to calculate?", 
                                        min_value=1, max_value=8, 
                                        value=st.session_state.num_semesters,
                                        key='semesters_input')
        st.session_state.num_semesters = num_semesters
    
    # Semester inputs
    semesters_data = []
    
    for i in range(num_semesters):
        st.subheader(f"Semester {i+1}")
        col1, col2 = st.columns(2)
        
        with col1:
            semester_gpa = st.number_input(f"GPA", 
                                          min_value=0.0, 
                                          max_value=4.0,
                                          value=0.0,
                                          step=0.01,
                                          key=f'sem_gpa_{i}')
        with col2:
            semester_credits = st.number_input(f"Credit Hours", 
                                              min_value=0.0,
                                              value=0.0,
                                              key=f'sem_credits_{i}')
        
        semesters_data.append({
            'gpa': semester_gpa,
            'credit_hours': semester_credits
        })
        
        st.markdown("---")
    
    # Calculate button
    if st.button("🧮 Calculate CGPA", type="primary", key='calc_cgpa'):
        total_grade_points = 0
        total_credit_hours = 0
        semester_results = []
        
        for i, semester in enumerate(semesters_data):
            if semester['credit_hours'] > 0:
                grade_points = semester['gpa'] * semester['credit_hours']
                
                total_grade_points += grade_points
                total_credit_hours += semester['credit_hours']
                
                semester_results.append({
                    'Semester': f"Semester {i+1}",
                    'GPA': f"{semester['gpa']:.2f}",
                    'Credit Hours': semester['credit_hours'],
                    'Grade Points': f"{grade_points:.2f}"
                })
        
        if total_credit_hours > 0:
            final_cgpa = total_grade_points / total_credit_hours
            
            # Display results
            st.success(f"✅ CGPA Calculated Successfully for {user_name_cgpa}!")
            
            # Results table
            st.subheader("📊 Semester-wise Results")
            df = pd.DataFrame(semester_results)
            st.dataframe(df, use_container_width=True)
            
            # Summary metrics
            st.subheader("📈 Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Total Credit Hours</h3>
                        <h2>{total_credit_hours:.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Total Grade Points</h3>
                        <h2>{total_grade_points:.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <h3>Overall CGPA</h3>
                        <h2>{final_cgpa:.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            # Save to database
            semesters_db_data = []
            for semester in semester_results:
                semesters_db_data.append({
                    'gpa': float(semester['GPA']),
                    'credit_hours': float(semester['Credit Hours']),
                    'grade_points': float(semester['Grade Points'])
                })
            
            summary = {
                'cgpa': final_cgpa,
                'total_credit_hours': total_credit_hours,
                'total_grade_points': total_grade_points
            }
            
            save_cgpa_to_sql(user_name_cgpa, semesters_db_data, summary)
            st.info("❤ Thank You! For using the SMIU CGPA Calculator.")
            
            # Export to Excel
            export_data = {
                'semesters': semester_results,
                'summary': summary
            }
            excel_file = export_to_excel(export_data, 'CGPA')
            
            st.download_button(
                label="📥 Download CGPA Report",
                data=excel_file,
                file_name=f"CGPA_Report_{user_name_cgpa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("❌ Please enter valid credit hours!")

# ============= GRADING SCALE =============
with tab3:
    st.header("📋 Grading Scale Reference")
    
    grade_df = pd.DataFrame(GRADE_TABLE, columns=['Min %', 'Max %', 'Letter Grade', 'Grade Point'])
    grade_df['Percentage Range'] = grade_df.apply(lambda x: f"{x['Min %']}% - {x['Max %']}%", axis=1)
    
    display_df = grade_df[['Percentage Range', 'Letter Grade', 'Grade Point']]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.info("""
    **Note:** 
    - GPA = Sum of (Grade Points × Credit Hours) / Total Credit Hours
    - CGPA = Sum of (Semester GPA × Semester Credit Hours) / Total Credit Hours
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Made By Muhammad Moiz | SMIU GPA & CGPA Calculator</p>
        <p>If you add your name, the Excel file will be generated with your name.</p>
    </div>
""", unsafe_allow_html=True)






