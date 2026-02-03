import streamlit as st
import pandas as pd
from datetime import datetime
import io
import secrets
import hashlib
from urllib.parse import urlparse

# Page configuration
st.set_page_config(
    page_title="SMIU GPA & CGPA Calculator",
    page_icon="🎓",
    layout="wide"
)

# Session state initialization
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'admin_credentials' not in st.session_state:
    st.session_state.admin_credentials = {'username': 'admin', 'password': 'admin123'}
if 'short_url' not in st.session_state:
    st.session_state.short_url = None
if 'base_url' not in st.session_state:
    st.session_state.base_url = "https://gpa-calculator.streamlit.app"
if 'gpa_calculations' not in st.session_state:
    st.session_state.gpa_calculations = []
if 'cgpa_calculations' not in st.session_state:
    st.session_state.cgpa_calculations = []

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

def export_to_excel(data, calculation_type, student_name=None):
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
            
        elif calculation_type == 'CGPA':
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
        
        elif calculation_type == 'BULK_GPA':
            # Create consolidated report
            all_data = []
            for student_data in data:
                for course in student_data['courses']:
                    all_data.append({
                        'Student Name': student_data['student_name'],
                        'Course Name': course['Course Name'],
                        'Total Marks': course['Total Marks'],
                        'Obtained Marks': course['Obtained Marks'],
                        'Percentage': course['Percentage'],
                        'Credit Hours': course['Credit Hours'],
                        'Grade': course['Grade'],
                        'GPA': course['GPA'],
                        'Grade Points': course['Grade Points']
                    })
            
            if all_data:
                bulk_df = pd.DataFrame(all_data)
                bulk_df.to_excel(writer, sheet_name='All GPA Records', index=False)
        
        elif calculation_type == 'BULK_CGPA':
            # Create consolidated report
            all_data = []
            for student_data in data:
                for semester in student_data['semesters']:
                    all_data.append({
                        'Student Name': student_data['student_name'],
                        'Semester': semester['Semester'],
                        'GPA': semester['GPA'],
                        'Credit Hours': semester['Credit Hours'],
                        'Grade Points': semester['Grade Points']
                    })
            
            if all_data:
                bulk_df = pd.DataFrame(all_data)
                bulk_df.to_excel(writer, sheet_name='All CGPA Records', index=False)
    
    output.seek(0)
    return output

def generate_short_url():
    """Generate a random short URL"""
    return f"gpa-{secrets.token_hex(3)}"

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
        background-color: #667eea;
        color: white;
        font-weight: bold;
    }
    .admin-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header" style="text-align: center;">
        <img src="https://www.smiu.edu.pk/themes/smiu/images/13254460_710745915734761_8157428650049174152_n.png" width="200">
        <h1>Welcome to SMIU GPA & CGPA Calculator</h1>
    </div>
""", unsafe_allow_html=True)

# ============= ADMIN LOGIN =============
if not st.session_state.admin_logged_in:
    st.sidebar.header("🔐 Admin Login")
    admin_user = st.sidebar.text_input("Username", key="admin_user")
    admin_pass = st.sidebar.text_input("Password", type="password", key="admin_pass")
    
    if st.sidebar.button("Login", key="admin_login"):
        if (admin_user == st.session_state.admin_credentials['username'] and 
            admin_pass == st.session_state.admin_credentials['password']):
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials!")

# ============= ADMIN PANEL =============
if st.session_state.admin_logged_in:
    with st.sidebar:
        st.header("⚙️ Admin Panel")
        
        # Change credentials
        with st.expander("Change Admin Credentials"):
            new_user = st.text_input("New Username", value=st.session_state.admin_credentials['username'])
            new_pass = st.text_input("New Password", type="password", value=st.session_state.admin_credentials['password'])
            if st.button("Update Credentials"):
                st.session_state.admin_credentials['username'] = new_user
                st.session_state.admin_credentials['password'] = new_pass
                st.success("Credentials updated successfully!")
        
        # URL Management
        with st.expander("URL Management"):
            st.write("Current Base URL:")
            st.code(st.session_state.base_url)
            
            new_base = st.text_input("New Base URL", value=st.session_state.base_url)
            if st.button("Update Base URL"):
                # Validate URL
                try:
                    result = urlparse(new_base)
                    if all([result.scheme, result.netloc]):
                        st.session_state.base_url = new_base.rstrip('/')
                        st.success("Base URL updated!")
                    else:
                        st.error("Invalid URL format")
                except:
                    st.error("Invalid URL")
            
            if st.button("Generate Short URL"):
                st.session_state.short_url = generate_short_url()
            
            if st.session_state.short_url:
                st.write("Short URL:")
                full_url = f"{st.session_state.base_url}/?short={st.session_state.short_url}"
                st.code(full_url)
                st.info("Share this URL with students")
        
        # Download Options
        with st.expander("Download Data"):
            col1, col2 = st.columns(2)
            with col1:
                # Individual GPA Downloads
                if st.session_state.gpa_calculations:
                    student_names = list(set([calc['student_name'] for calc in st.session_state.gpa_calculations]))
                    selected_student = st.selectbox("Select Student (GPA)", [""] + student_names)
                    
                    if selected_student:
                        student_calcs = [calc for calc in st.session_state.gpa_calculations 
                                       if calc['student_name'] == selected_student]
                        if student_calcs:
                            latest_calc = student_calcs[-1]
                            excel_file = export_to_excel(latest_calc, 'GPA', selected_student)
                            st.download_button(
                                label=f"📥 {selected_student}'s GPA",
                                data=excel_file,
                                file_name=f"GPA_{selected_student}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
            
            with col2:
                # Individual CGPA Downloads
                if st.session_state.cgpa_calculations:
                    student_names = list(set([calc['student_name'] for calc in st.session_state.cgpa_calculations]))
                    selected_student = st.selectbox("Select Student (CGPA)", [""] + student_names)
                    
                    if selected_student:
                        student_calcs = [calc for calc in st.session_state.cgpa_calculations 
                                       if calc['student_name'] == selected_student]
                        if student_calcs:
                            latest_calc = student_calcs[-1]
                            excel_file = export_to_excel(latest_calc, 'CGPA', selected_student)
                            st.download_button(
                                label=f"📥 {selected_student}'s CGPA",
                                data=excel_file,
                                file_name=f"CGPA_{selected_student}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
            
            # Bulk Downloads
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state.gpa_calculations:
                    excel_file = export_to_excel(st.session_state.gpa_calculations, 'BULK_GPA')
                    st.download_button(
                        label="📥 All GPA Records",
                        data=excel_file,
                        file_name=f"All_GPA_Records_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                if st.session_state.cgpa_calculations:
                    excel_file = export_to_excel(st.session_state.cgpa_calculations, 'BULK_CGPA')
                    st.download_button(
                        label="📥 All CGPA Records",
                        data=excel_file,
                        file_name=f"All_CGPA_Records_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

# ============= MAIN CALCULATOR TABS =============
if st.session_state.admin_logged_in or not st.session_state.short_url:
    tab1, tab2, tab3 = st.tabs(["📊 GPA Calculator", "📈 CGPA Calculator", "📋 Grading Scale"])
    
    # ============= GPA CALCULATOR =============
    with tab1:
        st.header("Semester GPA Calculator")
        
        # User name input
        st.subheader("👤 Student Information")
        user_name = st.text_input("Enter Your Name", placeholder="e.g., M.Moiz", key='gpa_user_name')
        
        st.markdown("---")
        
        # Initialize session state for courses
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
            
            course_name = st.text_input(f"Course Name", 
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
                st.success(f"✅ GPA Calculated Successfully!")
                
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
                
                # Store in session (temporary storage)
                if user_name:
                    student_name = user_name
                else:
                    student_name = f"Student_{len(st.session_state.gpa_calculations)+1}"
                
                calculation_data = {
                    'student_name': student_name,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'courses': course_results,
                    'summary': {
                        'gpa': final_gpa,
                        'total_credit_hours': total_credit_hours,
                        'total_grade_points': total_grade_points
                    }
                }
                
                st.session_state.gpa_calculations.append(calculation_data)
                
                st.info("❤ Thank You! For using the SMIU Semester GPA Calculator.")
                
                # Export to Excel for student
                export_data = {
                    'courses': course_results,
                    'summary': {
                        'gpa': final_gpa,
                        'total_credit_hours': total_credit_hours,
                        'total_grade_points': total_grade_points
                    }
                }
                excel_file = export_to_excel(export_data, 'GPA', student_name)
                
                st.download_button(
                    label="📥 Download My GPA Report",
                    data=excel_file,
                    file_name=f"GPA_Report_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("❌ Please enter valid credit hours!")
    
    # ============= CGPA CALCULATOR =============
    with tab2:
        st.header("Overall CGPA Calculator")
        
        # User name input
        st.subheader("👤 Student Information")
        user_name_cgpa = st.text_input("Enter Your Name", placeholder="e.g., M.Moiz", key='cgpa_user_name')
        
        st.markdown("---")
        
        # Initialize session state for semesters
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
                st.success(f"✅ CGPA Calculated Successfully!")
                
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
                
                # Store in session (temporary storage)
                if user_name_cgpa:
                    student_name = user_name_cgpa
                else:
                    student_name = f"Student_{len(st.session_state.cgpa_calculations)+1}"
                
                calculation_data = {
                    'student_name': student_name,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'semesters': semester_results,
                    'summary': {
                        'cgpa': final_cgpa,
                        'total_credit_hours': total_credit_hours,
                        'total_grade_points': total_grade_points
                    }
                }
                
                st.session_state.cgpa_calculations.append(calculation_data)
                
                st.info("❤ Thank You! For using the SMIU CGPA Calculator.")
                
                # Export to Excel for student
                export_data = {
                    'semesters': semester_results,
                    'summary': {
                        'cgpa': final_cgpa,
                        'total_credit_hours': total_credit_hours,
                        'total_grade_points': total_grade_points
                    }
                }
                excel_file = export_to_excel(export_data, 'CGPA', student_name)
                
                st.download_button(
                    label="📥 Download My CGPA Report",
                    data=excel_file,
                    file_name=f"CGPA_Report_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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

# ============= ACCESS DENIED =============
elif st.session_state.short_url:
    # Check for short URL in query parameters
    query_params = st.query_params
    if 'short' not in query_params or query_params['short'] != st.session_state.short_url:
        st.error("""
        ⚠️ Access Denied
        
        This calculator requires a special access URL. 
        Please contact your administrator for the correct link.
        """)
        st.stop()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Made By Muhammad Moiz | SMIU GPA & CGPA Calculator</p>
        <p>Your data is processed temporarily and not stored permanently.</p>
    </div>
""", unsafe_allow_html=True)
