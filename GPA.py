import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64

# Page configuration
st.set_page_config(
    page_title="SMIU GPA & CGPA Calculator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'gpa_data' not in st.session_state:
    st.session_state.gpa_data = []
if 'cgpa_data' not in st.session_state:
    st.session_state.cgpa_data = []
if 'settings' not in st.session_state:
    st.session_state.settings = {
        "admin_username": "admin",
        "admin_password": "admin123",
        "base_url": "https://smiumoiz.streamlit.app",
        "short_url": "",
        "app_name": "SMIU GPA & CGPA Calculator"
    }

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

def export_to_excel(data, calculation_type, student_name=""):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if calculation_type == 'GPA':
            courses_df = pd.DataFrame(data['courses'])
            courses_df.index = courses_df.index + 1
            courses_df.index.name = 'Course No.'
            courses_df.to_excel(writer, sheet_name='Course Details')
            
            summary_df = pd.DataFrame({
                'Metric': ['Student Name', 'Total Credit Hours', 'Total Grade Points', 'Final GPA'],
                'Value': [student_name,
                         data['summary']['total_credit_hours'], 
                         data['summary']['total_grade_points'],
                         data['summary']['gpa']]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
        else:
            semesters_df = pd.DataFrame(data['semesters'])
            semesters_df.index = semesters_df.index + 1
            semesters_df.index.name = 'Semester No.'
            semesters_df.to_excel(writer, sheet_name='Semester Details')
            
            summary_df = pd.DataFrame({
                'Metric': ['Student Name', 'Total Credit Hours', 'Total Grade Points', 'Final CGPA'],
                'Value': [student_name,
                         data['summary']['total_credit_hours'], 
                         data['summary']['total_grade_points'],
                         data['summary']['cgpa']]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    return output

def export_all_gpa_data():
    """Export all GPA data to Excel"""
    if not st.session_state.gpa_data:
        return None
    
    output = io.BytesIO()
    all_data = []
    
    for entry in st.session_state.gpa_data:
        for course in entry['courses']:
            all_data.append({
                'Student Name': entry['student_name'],
                'Timestamp': entry['timestamp'],
                'Course Name': course['Course Name'],
                'Total Marks': course['Total Marks'],
                'Obtained Marks': course['Obtained Marks'],
                'Credit Hours': course['Credit Hours'],
                'Grade': course['Grade'],
                'GPA': course['GPA'],
                'Grade Points': course['Grade Points']
            })
    
    df = pd.DataFrame(all_data)
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All GPA Records', index=False)
        
        # Summary sheet
        summary_data = []
        for entry in st.session_state.gpa_data:
            summary_data.append({
                'Student Name': entry['student_name'],
                'Timestamp': entry['timestamp'],
                'Total Credit Hours': entry['summary']['total_credit_hours'],
                'Total Grade Points': entry['summary']['total_grade_points'],
                'GPA': entry['summary']['gpa'],
                'Number of Courses': len(entry['courses'])
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='GPA Summary', index=False)
    
    output.seek(0)
    return output

def export_all_cgpa_data():
    """Export all CGPA data to Excel"""
    if not st.session_state.cgpa_data:
        return None
    
    output = io.BytesIO()
    all_data = []
    
    for entry in st.session_state.cgpa_data:
        for semester in entry['semesters']:
            all_data.append({
                'Student Name': entry['student_name'],
                'Timestamp': entry['timestamp'],
                'Semester': semester['Semester'],
                'GPA': semester['GPA'],
                'Credit Hours': semester['Credit Hours'],
                'Grade Points': semester['Grade Points']
            })
    
    df = pd.DataFrame(all_data)
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All CGPA Records', index=False)
        
        # Summary sheet
        summary_data = []
        for entry in st.session_state.cgpa_data:
            summary_data.append({
                'Student Name': entry['student_name'],
                'Timestamp': entry['timestamp'],
                'Total Credit Hours': entry['summary']['total_credit_hours'],
                'Total Grade Points': entry['summary']['total_grade_points'],
                'CGPA': entry['summary']['cgpa'],
                'Number of Semesters': len(entry['semesters'])
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='CGPA Summary', index=False)
    
    output.seek(0)
    return output

def validate_url(url):
    """Simple URL validation"""
    if url:
        return url.startswith('http://') or url.startswith('https://')
    return True

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
    .admin-panel {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #667eea;
        margin: 1rem 0;
    }
    .login-form {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown(f"""
    <div class="main-header" style="text-align: center;">
        <img src="https://www.smiu.edu.pk/themes/smiu/images/13254460_710745915734761_8157428650049174152_n.png" width="150">
        <h1>Welcome to {st.session_state.settings['app_name']}</h1>
        <p style="font-size: 14px; margin-top: 10px;">Access URL: {st.session_state.settings['base_url']}</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar for Admin Login
with st.sidebar:
    st.markdown("### 🔐 Admin Access")
    
    if not st.session_state.admin_logged_in:
        st.markdown("---")
        admin_username = st.text_input("Username", key="admin_user")
        admin_password = st.text_input("Password", type="password", key="admin_pass")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="admin_login", use_container_width=True):
                if admin_username == st.session_state.settings['admin_username'] and admin_password == st.session_state.settings['admin_password']:
                    st.session_state.admin_logged_in = True
                    st.session_state.current_user = admin_username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")
        
        with col2:
            if st.button("Reset", key="reset_login", use_container_width=True):
                st.rerun()
    else:
        st.success(f"✅ Logged in as: {st.session_state.current_user}")
        if st.button("🚪 Logout", key="admin_logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.current_user = ""
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("GPA Records", len(st.session_state.gpa_data))
        with col2:
            st.metric("CGPA Records", len(st.session_state.cgpa_data))
        
        if st.button("🗑️ Clear All Data", key="clear_data", use_container_width=True):
            st.session_state.gpa_data = []
            st.session_state.cgpa_data = []
            st.success("✅ All data cleared successfully!")
            st.rerun()

# Create tabs
if st.session_state.admin_logged_in:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GPA Calculator", "📈 CGPA Calculator", "📋 Grading Scale", "⚙️ Admin Panel", "📥 Data Export"])
else:
    tab1, tab2, tab3 = st.tabs(["📊 GPA Calculator", "📈 CGPA Calculator", "📋 Grading Scale"])

# ============= GPA CALCULATOR =============
with tab1:
    st.header("Semester GPA Calculator")
    
    # User name input
    st.subheader("👤 Student Information")
    user_name = st.text_input("Enter Your Name *", placeholder="e.g., M.Moiz", key='gpa_user_name')
    
    if not user_name:
        st.warning("⚠️ Please enter your name to continue")
    
    st.markdown("---")
    
    # Number of courses
    num_courses = st.number_input("How many courses do you have?", 
                                  min_value=1, max_value=20, 
                                  value=3,
                                  key='courses_input')
    
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
        
        if i < num_courses - 1:
            st.markdown("---")
    
    # Calculate button
    if st.button("🧮 Calculate GPA", type="primary", key='calc_gpa'):
        if not user_name:
            st.error("❌ Please enter your name!")
            st.stop()
        
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
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary metrics
            st.subheader("📈 Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Credit Hours", f"{total_credit_hours:.2f}")
            with col2:
                st.metric("Total Grade Points", f"{total_grade_points:.2f}")
            with col3:
                st.metric("Semester GPA", f"{final_gpa:.2f}")
            
            # Save to session state
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.gpa_data.append({
                'student_name': user_name,
                'timestamp': timestamp,
                'courses': course_results,
                'summary': {
                    'gpa': final_gpa,
                    'total_credit_hours': total_credit_hours,
                    'total_grade_points': total_grade_points
                }
            })
            
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
            excel_file = export_to_excel(export_data, 'GPA', user_name)
            
            st.download_button(
                label="📥 Download Your GPA Report",
                data=excel_file,
                file_name=f"GPA_Report_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("❌ Please enter valid credit hours!")

# ============= CGPA CALCULATOR =============
with tab2:
    st.header("Overall CGPA Calculator")
    
    # User name input
    st.subheader("👤 Student Information")
    user_name_cgpa = st.text_input("Enter Your Name *", placeholder="e.g., M.Moiz", key='cgpa_user_name')
    
    if not user_name_cgpa:
        st.warning("⚠️ Please enter your name to continue")
    
    st.markdown("---")
    
    # Number of semesters
    num_semesters = st.number_input("How many semesters do you want to calculate?", 
                                    min_value=1, max_value=8, 
                                    value=1,
                                    key='semesters_input')
    
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
        
        if i < num_semesters - 1:
            st.markdown("---")
    
    # Calculate button
    if st.button("🧮 Calculate CGPA", type="primary", key='calc_cgpa'):
        if not user_name_cgpa:
            st.error("❌ Please enter your name!")
            st.stop()
        
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
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary metrics
            st.subheader("📈 Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Credit Hours", f"{total_credit_hours:.2f}")
            with col2:
                st.metric("Total Grade Points", f"{total_grade_points:.2f}")
            with col3:
                st.metric("Overall CGPA", f"{final_cgpa:.2f}")
            
            # Save to session state
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.cgpa_data.append({
                'student_name': user_name_cgpa,
                'timestamp': timestamp,
                'semesters': semester_results,
                'summary': {
                    'cgpa': final_cgpa,
                    'total_credit_hours': total_credit_hours,
                    'total_grade_points': total_grade_points
                }
            })
            
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
            excel_file = export_to_excel(export_data, 'CGPA', user_name_cgpa)
            
            st.download_button(
                label="📥 Download Your CGPA Report",
                data=excel_file,
                file_name=f"CGPA_Report_{user_name_cgpa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
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

# ============= ADMIN PANEL =============
if st.session_state.admin_logged_in:
    with tab4:
        st.header("⚙️ Admin Panel")
        
        # Account Settings
        st.subheader("🔐 Account Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("New Username", value=st.session_state.settings['admin_username'])
        with col2:
            new_password = st.text_input("New Password", type="password", value=st.session_state.settings['admin_password'])
        
        if st.button("💾 Update Credentials", key="update_creds", use_container_width=True):
            if new_username and new_password:
                st.session_state.settings['admin_username'] = new_username
                st.session_state.settings['admin_password'] = new_password
                st.success("✅ Credentials updated successfully!")
            else:
                st.error("❌ Username and password cannot be empty!")
        
        st.markdown("---")
        
        # Application Settings
        st.subheader("🌐 Application Settings")
        app_name = st.text_input("Application Name", value=st.session_state.settings['app_name'])
        base_url = st.text_input("Base URL", value=st.session_state.settings['base_url'])
        short_url = st.text_input("Short URL (Optional)", value=st.session_state.settings['short_url'])
        
        if st.button("🌐 Update URLs", key="update_urls", use_container_width=True):
            if validate_url(base_url):
                st.session_state.settings['base_url'] = base_url
                st.session_state.settings['app_name'] = app_name
                st.session_state.settings['short_url'] = short_url
                st.success("✅ URLs updated successfully!")
                st.rerun()
            else:
                st.error("❌ Please enter a valid URL starting with http:// or https://")
        
        st.markdown("---")
        
        # Data Summary
        st.subheader("📊 Data Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**GPA Records:** {len(st.session_state.gpa_data)} students")
            if st.session_state.gpa_data:
                gpa_df = pd.DataFrame([{
                    'Student': entry['student_name'],
                    'Time': entry['timestamp'],
                    'GPA': entry['summary']['gpa']
                } for entry in st.session_state.gpa_data])
                st.dataframe(gpa_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No GPA records yet")
        
        with col2:
            st.info(f"**CGPA Records:** {len(st.session_state.cgpa_data)} students")
            if st.session_state.cgpa_data:
                cgpa_df = pd.DataFrame([{
                    'Student': entry['student_name'],
                    'Time': entry['timestamp'],
                    'CGPA': entry['summary']['cgpa']
                } for entry in st.session_state.cgpa_data])
                st.dataframe(cgpa_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No CGPA records yet")

# ============= DATA EXPORT =============
if st.session_state.admin_logged_in:
    with tab5:
        st.header("📥 Data Export")
        
        # Individual Student Export
        st.subheader("👤 Individual Student Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### GPA Records")
            if st.session_state.gpa_data:
                gpa_students = list(set([entry['student_name'] for entry in st.session_state.gpa_data]))
                selected_gpa_student = st.selectbox("Select Student for GPA Export", gpa_students)
                
                if selected_gpa_student:
                    selected_gpa_record = next((record for record in st.session_state.gpa_data 
                                               if record['student_name'] == selected_gpa_student), None)
                    
                    if selected_gpa_record:
                        excel_file = export_to_excel({
                            'courses': selected_gpa_record['courses'],
                            'summary': selected_gpa_record['summary']
                        }, 'GPA', selected_gpa_student)
                        
                        st.download_button(
                            label=f"📥 Download {selected_gpa_student}'s GPA Report",
                            data=excel_file,
                            file_name=f"GPA_Report_{selected_gpa_student}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
            else:
                st.info("No GPA records available")
        
        with col2:
            st.markdown("##### CGPA Records")
            if st.session_state.cgpa_data:
                cgpa_students = list(set([entry['student_name'] for entry in st.session_state.cgpa_data]))
                selected_cgpa_student = st.selectbox("Select Student for CGPA Export", cgpa_students)
                
                if selected_cgpa_student:
                    selected_cgpa_record = next((record for record in st.session_state.cgpa_data 
                                                 if record['student_name'] == selected_cgpa_student), None)
                    
                    if selected_cgpa_record:
                        excel_file = export_to_excel({
                            'semesters': selected_cgpa_record['semesters'],
                            'summary': selected_cgpa_record['summary']
                        }, 'CGPA', selected_cgpa_student)
                        
                        st.download_button(
                            label=f"📥 Download {selected_cgpa_student}'s CGPA Report",
                            data=excel_file,
                            file_name=f"CGPA_Report_{selected_cgpa_student}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
            else:
                st.info("No CGPA records available")
        
        st.markdown("---")
        
        # Bulk Export
        st.subheader("📦 Bulk Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.gpa_data:
                excel_file = export_all_gpa_data()
                if excel_file:
                    st.download_button(
                        label="📥 Export All GPA Records",
                        data=excel_file,
                        file_name=f"All_GPA_Records_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                st.info(f"Total GPA Records: {len(st.session_state.gpa_data)} students")
            else:
                st.warning("No GPA records to export")
        
        with col2:
            if st.session_state.cgpa_data:
                excel_file = export_all_cgpa_data()
                if excel_file:
                    st.download_button(
                        label="📥 Export All CGPA Records",
                        data=excel_file,
                        file_name=f"All_CGPA_Records_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                st.info(f"Total CGPA Records: {len(st.session_state.cgpa_data)} students")
            else:
                st.warning("No CGPA records to export")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Made By Muhammad Moiz | SMIU GPA & CGPA Calculator</strong></p>
        <p style='font-size: 14px;'>Your data is processed temporarily and not stored permanently.</p>
        <p style='font-size: 12px; color: #888;'>© 2024 Sindh Madressatul Islam University</p>
    </div>
""", unsafe_allow_html=True)
