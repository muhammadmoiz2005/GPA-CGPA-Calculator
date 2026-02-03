import streamlit as st
import pandas as pd
from datetime import datetime
import io
import secrets

# Page configuration
st.set_page_config(
    page_title="SMIU GPA Calculator",
    page_icon="🎓",
    layout="wide"
)

# ============= INITIALIZE SESSION STATE =============
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
    
if 'admin_username' not in st.session_state:
    st.session_state.admin_username = "admin"
    
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"
    
if 'short_url_code' not in st.session_state:
    st.session_state.short_url_code = None
    
if 'gpa_calculations' not in st.session_state:
    st.session_state.gpa_calculations = []
    
if 'cgpa_calculations' not in st.session_state:
    st.session_state.cgpa_calculations = []
    
if 'num_courses' not in st.session_state:
    st.session_state.num_courses = 1
    
if 'num_semesters' not in st.session_state:
    st.session_state.num_semesters = 1
    
if 'app_settings' not in st.session_state:
    st.session_state.app_settings = {
        'app_title': "SMIU GPA & CGPA Calculator",
        'institution_name': "Sindh Madressatul Islam University",
        'institution_logo': "https://www.smiu.edu.pk/themes/smiu/images/13254460_710745915734761_8157428650049174152_n.png",
        'base_url': "http://localhost:8501"
    }

# ============= GRADING SYSTEM =============
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
    """Get grade and GPA based on percentage"""
    for min_score, max_score, grade, gpa in GRADE_TABLE:
        if min_score <= percentage <= max_score:
            return grade, gpa
    return 'F', 0.00

# ============= UTILITY FUNCTIONS =============
def generate_short_url():
    """Generate a random short URL code"""
    return f"gpa-{secrets.token_hex(4)}"

def export_to_excel(data, calculation_type, student_name=None):
    """Export data to Excel format"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Add institution header
        header_df = pd.DataFrame({
            'Institution': [st.session_state.app_settings['institution_name']],
            'Report Type': [calculation_type],
            'Generated On': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        header_df.to_excel(writer, sheet_name='Report Info', index=False)
        
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
                student_name = student_data['student_name']
                for course in student_data['courses']:
                    all_data.append({
                        'Student Name': student_name,
                        'Timestamp': student_data['timestamp'],
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
                student_name = student_data['student_name']
                for semester in student_data['semesters']:
                    all_data.append({
                        'Student Name': student_name,
                        'Timestamp': student_data['timestamp'],
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

# ============= CUSTOM CSS =============
st.markdown("""
    <style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(90deg, #1a2980 0%, #26d0ce 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
    }
    
    /* Admin section styling */
    .admin-section {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    
    /* URL box styling */
    .url-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 2px dashed #667eea;
        font-family: monospace;
        margin: 1rem 0;
        word-break: break-all;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ============= SIDEBAR - ADMIN PANEL =============
with st.sidebar:
    st.markdown("## 🔐 Admin Panel")
    
    # Admin Login/Logout Section
    if not st.session_state.admin_logged_in:
        st.markdown("### Admin Login")
        
        admin_user = st.text_input("Username", key="admin_user")
        admin_pass = st.text_input("Password", type="password", key="admin_pass")
        
        if st.button("Login", key="login_btn", use_container_width=True):
            if admin_user == st.session_state.admin_username and admin_pass == st.session_state.admin_password:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid credentials!")
    else:
        st.success(f"✅ Logged in as **{st.session_state.admin_username}**")
        
        # Admin Functions
        st.markdown("---")
        st.markdown("### ⚙️ Admin Functions")
        
        # Change Credentials
        with st.expander("🔑 Change Credentials"):
            new_user = st.text_input("New Username", value=st.session_state.admin_username, key="new_user")
            new_pass = st.text_input("New Password", type="password", value=st.session_state.admin_password, key="new_pass")
            
            if st.button("Update Credentials", key="update_creds"):
                if new_user and new_pass:
                    st.session_state.admin_username = new_user
                    st.session_state.admin_password = new_pass
                    st.success("✅ Credentials updated!")
                else:
                    st.error("❌ Both fields are required!")
        
        # Short URL Management
        with st.expander("🔗 Short URL"):
            if st.session_state.short_url_code:
                full_url = f"{st.session_state.app_settings['base_url']}/?short={st.session_state.short_url_code}"
                st.success("✅ Short URL is ACTIVE")
                st.markdown(f'<div class="url-box">{full_url}</div>', unsafe_allow_html=True)
                st.caption("Share this URL with students")
                
                if st.button("Disable Short URL", key="disable_url"):
                    st.session_state.short_url_code = None
                    st.rerun()
            else:
                st.warning("⚠️ Short URL is DISABLED")
                if st.button("Generate Short URL", key="gen_url"):
                    st.session_state.short_url_code = generate_short_url()
                    st.rerun()
        
        # Data Management
        with st.expander("📊 Data Management"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("GPA Calculations", len(st.session_state.gpa_calculations))
            with col2:
                st.metric("CGPA Calculations", len(st.session_state.cgpa_calculations))
            
            if st.session_state.gpa_calculations:
                excel_file = export_to_excel(st.session_state.gpa_calculations, 'BULK_GPA')
                st.download_button(
                    label="📥 Download All GPA Data",
                    data=excel_file,
                    file_name=f"All_GPA_Data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_all_gpa"
                )
            
            if st.session_state.cgpa_calculations:
                excel_file = export_to_excel(st.session_state.cgpa_calculations, 'BULK_CGPA')
                st.download_button(
                    label="📥 Download All CGPA Data",
                    data=excel_file,
                    file_name=f"All_CGPA_Data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_all_cgpa"
                )
            
            if st.button("🗑️ Clear All Data", key="clear_data"):
                st.session_state.gpa_calculations = []
                st.session_state.cgpa_calculations = []
                st.success("✅ All data cleared!")
        
        # App Settings
        with st.expander("🎨 App Settings"):
            new_title = st.text_input("App Title", value=st.session_state.app_settings['app_title'], key="new_title")
            new_inst = st.text_input("Institution Name", value=st.session_state.app_settings['institution_name'], key="new_inst")
            new_base = st.text_input("Base URL", value=st.session_state.app_settings['base_url'], key="new_base")
            
            if st.button("Save Settings", key="save_settings"):
                st.session_state.app_settings['app_title'] = new_title
                st.session_state.app_settings['institution_name'] = new_inst
                st.session_state.app_settings['base_url'] = new_base
                st.success("✅ Settings saved!")
                st.rerun()
        
        # Logout Button
        st.markdown("---")
        if st.button("🚪 Logout", type="primary", key="logout_btn", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

# ============= ACCESS CONTROL =============
# Get query parameters
query_params = st.experimental_get_query_params()
has_valid_short_url = False

# Check if short URL is provided and valid
if 'short' in query_params:
    if st.session_state.short_url_code and query_params['short'][0] == st.session_state.short_url_code:
        has_valid_short_url = True

# Check access
access_granted = False

if st.session_state.admin_logged_in:
    # Admin always has access
    access_granted = True
elif st.session_state.short_url_code is None:
    # No short URL required, public access
    access_granted = True
elif has_valid_short_url:
    # Valid short URL provided
    access_granted = True
else:
    # No access
    access_granted = False
    st.error("""
    ## ⚠️ Access Restricted
    
    This calculator requires a special access URL provided by your institution.
    
    **Please contact your administrator for the correct link.**
    
    If you are an administrator, please login using the sidebar.
    """)
    st.stop()

# ============= MAIN APPLICATION =============
if access_granted:
    # Show access notification
    if has_valid_short_url:
        st.info("✅ Access granted via short URL")
    
    # Display Header
    st.markdown(f"""
    <div class="main-header">
        <img src="{st.session_state.app_settings['institution_logo']}" width="150" style="margin-bottom: 1rem;">
        <h1>{st.session_state.app_settings['app_title']}</h1>
        <p style="margin-top: 0.5rem; opacity: 0.9;">{st.session_state.app_settings['institution_name']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Calculator Tabs
    tab1, tab2, tab3 = st.tabs(["📊 GPA Calculator", "📈 CGPA Calculator", "📋 Grading Scale"])
    
    # ============= GPA CALCULATOR =============
    with tab1:
        st.header("🎯 Semester GPA Calculator")
        
        # Student Information
        with st.expander("👤 Student Information (Optional)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Student Name", placeholder="e.g., Muhammad Moiz", key='gpa_user_name')
            with col2:
                student_id = st.text_input("Student ID", placeholder="e.g., SM123456", key='gpa_student_id')
        
        st.markdown("---")
        
        # Course Configuration
        st.subheader("📚 Course Configuration")
        col1, col2 = st.columns([3, 1])
        with col1:
            num_courses = st.number_input("Number of Courses", min_value=1, max_value=20, 
                                         value=st.session_state.num_courses, key='courses_input')
        with col2:
            if st.button("🔄 Reset", key="reset_courses"):
                st.session_state.num_courses = 1
                st.rerun()
        
        # Course Inputs
        courses_data = []
        
        for i in range(st.session_state.num_courses):
            st.markdown(f"### Course {i+1}")
            
            course_col1, course_col2 = st.columns([2, 3])
            with course_col1:
                course_name = st.text_input(f"Course Name", placeholder=f"e.g., Data Structures", 
                                           key=f'course_name_{i}')
            
            with course_col2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_marks = st.number_input(f"Total Marks", min_value=0.0, value=100.0,
                                                 step=1.0, key=f'total_{i}')
                with col2:
                    obtained_marks = st.number_input(f"Obtained Marks", min_value=0.0, value=0.0,
                                                    step=0.5, key=f'obtained_{i}')
                with col3:
                    credit_hours = st.number_input(f"Credit Hours", min_value=0.0, value=3.0,
                                                  step=0.5, key=f'credit_{i}')
            
            courses_data.append({
                'course_name': course_name if course_name else f"Course {i+1}",
                'total_marks': total_marks,
                'obtained_marks': obtained_marks,
                'credit_hours': credit_hours
            })
            
            if i < st.session_state.num_courses - 1:
                st.markdown("---")
        
        # Calculate Button
        st.markdown("---")
        if st.button("🧮 Calculate GPA", type="primary", key='calc_gpa', use_container_width=True):
            # Validate inputs
            valid_inputs = True
            for i, course in enumerate(courses_data):
                if course['credit_hours'] <= 0:
                    st.error(f"❌ Course {i+1}: Credit hours must be greater than 0")
                    valid_inputs = False
                if course['total_marks'] <= 0:
                    st.error(f"❌ Course {i+1}: Total marks must be greater than 0")
                    valid_inputs = False
            
            if valid_inputs:
                total_grade_points = 0
                total_credit_hours = 0
                course_results = []
                
                # Calculate for each course
                for i, course in enumerate(courses_data):
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
                        'GPA': f"{gpa:.2f}",
                        'Grade Points': f"{grade_points:.2f}"
                    })
                
                if total_credit_hours > 0:
                    final_gpa = total_grade_points / total_credit_hours
                    
                    # Display results
                    st.success("### ✅ GPA Calculated Successfully!")
                    
                    # Course Results Table
                    st.subheader("📊 Course-wise Results")
                    df = pd.DataFrame(course_results)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Summary Metrics
                    st.subheader("📈 Semester Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>Total Credit Hours</h4>
                                <h2>{total_credit_hours:.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>Total Grade Points</h4>
                                <h2>{total_grade_points:.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        gpa_color = "#28a745" if final_gpa >= 3.0 else "#ffc107" if final_gpa >= 2.0 else "#dc3545"
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>Semester GPA</h4>
                                <h2 style="color: {gpa_color}">{final_gpa:.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Store calculation
                    student_name = user_name if user_name else f"Student_{len(st.session_state.gpa_calculations)+1}"
                    
                    calculation_data = {
                        'student_name': student_name,
                        'student_id': student_id,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'courses': course_results,
                        'summary': {
                            'gpa': final_gpa,
                            'total_credit_hours': total_credit_hours,
                            'total_grade_points': total_grade_points
                        }
                    }
                    
                    st.session_state.gpa_calculations.append(calculation_data)
                    
                    # Download Section
                    st.markdown("---")
                    st.subheader("📥 Download Results")
                    
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
                        label="⬇️ Download GPA Report",
                        data=excel_file,
                        file_name=f"GPA_Report_{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    # Success Message
                    st.info("### ❤️ Thank You! Your GPA has been calculated successfully.")
                    
                    # Update course count
                    st.session_state.num_courses = len(courses_data)
                else:
                    st.error("❌ Total credit hours must be greater than zero!")
    
    # ============= CGPA CALCULATOR =============
    with tab2:
        st.header("📈 Overall CGPA Calculator")
        
        # Student Information
        with st.expander("👤 Student Information (Optional)", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                user_name_cgpa = st.text_input("Student Name", placeholder="e.g., Muhammad Moiz", 
                                              key='cgpa_user_name')
            with col2:
                student_id_cgpa = st.text_input("Student ID", placeholder="e.g., SM123456", 
                                               key='cgpa_student_id')
        
        st.markdown("---")
        
        # Semester Configuration
        st.subheader("📅 Semester Configuration")
        col1, col2 = st.columns([3, 1])
        with col1:
            num_semesters = st.number_input("Number of Semesters", min_value=1, max_value=12,
                                           value=st.session_state.num_semesters, key='semesters_input')
        with col2:
            if st.button("🔄 Reset", key="reset_semesters"):
                st.session_state.num_semesters = 1
                st.rerun()
        
        # Semester Inputs
        semesters_data = []
        
        for i in range(st.session_state.num_semesters):
            st.markdown(f"### Semester {i+1}")
            
            col1, col2 = st.columns(2)
            with col1:
                semester_gpa = st.number_input(f"Semester GPA", min_value=0.0, max_value=4.0,
                                              value=0.0, step=0.01, key=f'sem_gpa_{i}', format="%.2f")
            with col2:
                semester_credits = st.number_input(f"Credit Hours", min_value=0.0, max_value=50.0,
                                                  value=0.0, step=0.5, key=f'sem_credits_{i}')
            
            semesters_data.append({
                'gpa': semester_gpa,
                'credit_hours': semester_credits
            })
            
            if i < st.session_state.num_semesters - 1:
                st.markdown("---")
        
        # Calculate Button
        st.markdown("---")
        if st.button("🧮 Calculate CGPA", type="primary", key='calc_cgpa', use_container_width=True):
            # Validate inputs
            valid_inputs = True
            for i, semester in enumerate(semesters_data):
                if semester['credit_hours'] < 0:
                    st.error(f"❌ Semester {i+1}: Credit hours cannot be negative")
                    valid_inputs = False
            
            if valid_inputs:
                total_grade_points = 0
                total_credit_hours = 0
                semester_results = []
                
                # Calculate for each semester
                for i, semester in enumerate(semesters_data):
                    if semester['credit_hours'] > 0:
                        grade_points = semester['gpa'] * semester['credit_hours']
                        total_grade_points += grade_points
                        total_credit_hours += semester['credit_hours']
                        
                        semester_results.append({
                            'Semester': f"Semester {i+1}",
                            'GPA': f"{semester['gpa']:.2f}",
                            'Credit Hours': f"{semester['credit_hours']:.2f}",
                            'Grade Points': f"{grade_points:.2f}"
                        })
                
                if total_credit_hours > 0:
                    final_cgpa = total_grade_points / total_credit_hours
                    
                    # Display results
                    st.success("### ✅ CGPA Calculated Successfully!")
                    
                    # Semester Results Table
                    st.subheader("📊 Semester-wise Results")
                    df = pd.DataFrame(semester_results)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Summary Metrics
                    st.subheader("📈 Academic Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>Total Credit Hours</h4>
                                <h2>{total_credit_hours:.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>Total Grade Points</h4>
                                <h2>{total_grade_points:.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        cgpa_color = "#28a745" if final_cgpa >= 3.0 else "#ffc107" if final_cgpa >= 2.0 else "#dc3545"
                        st.markdown(f"""
                            <div class="metric-card">
                                <h4>Overall CGPA</h4>
                                <h2 style="color: {cgpa_color}">{final_cgpa:.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Store calculation
                    student_name = user_name_cgpa if user_name_cgpa else f"Student_{len(st.session_state.cgpa_calculations)+1}"
                    
                    calculation_data = {
                        'student_name': student_name,
                        'student_id': student_id_cgpa,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'semesters': semester_results,
                        'summary': {
                            'cgpa': final_cgpa,
                            'total_credit_hours': total_credit_hours,
                            'total_grade_points': total_grade_points
                        }
                    }
                    
                    st.session_state.cgpa_calculations.append(calculation_data)
                    
                    # Download Section
                    st.markdown("---")
                    st.subheader("📥 Download Results")
                    
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
                        label="⬇️ Download CGPA Report",
                        data=excel_file,
                        file_name=f"CGPA_Report_{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                    # Success Message
                    st.info("### ❤️ Thank You! Your CGPA has been calculated successfully.")
                    
                    # Update semester count
                    st.session_state.num_semesters = len(semesters_data)
                else:
                    st.error("❌ Total credit hours must be greater than zero!")
    
    # ============= GRADING SCALE TAB =============
    with tab3:
        st.header("📋 SMIU Grading Scale")
        
        # Grading Table
        grade_df = pd.DataFrame(GRADE_TABLE, columns=['Min %', 'Max %', 'Letter Grade', 'Grade Point'])
        grade_df['Percentage Range'] = grade_df.apply(lambda x: f"{x['Min %']}% - {x['Max %']}%", axis=1)
        
        display_df = grade_df[['Percentage Range', 'Letter Grade', 'Grade Point']]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Calculation Formulas
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 GPA Calculation
            **For a course:**
            ```
            Course GPA = Grade Point × Credit Hours
            ```
            
            **For semester:**
            ```
            Semester GPA = Σ(Course GPA) ÷ Σ(Credit Hours)
            ```
            """)
        
        with col2:
            st.markdown("""
            ### 📈 CGPA Calculation
            **For semester:**
            ```
            Semester Points = Semester GPA × Semester Credits
            ```
            
            **Overall:**
            ```
            Overall CGPA = Σ(Semester Points) ÷ Σ(Total Credits)
            ```
            """)
        
        # Notes
        st.markdown("---")
        st.markdown("""
        ### ℹ️ Important Notes
        1. Minimum passing grade is 'D' (50% marks)
        2. Credit hours determine course weight in GPA
        3. Incomplete ('I') and Withdrawal ('W') grades don't affect GPA
        4. Calculations follow SMIU's official grading policy
        """)
    
    # ============= FOOTER =============
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p style='font-size: 0.9rem; margin-bottom: 0.5rem;'>
            <strong>© 2024 {st.session_state.app_settings['institution_name']} - GPA & CGPA Calculator</strong>
        </p>
        <p style='font-size: 0.8rem; margin-bottom: 0.5rem; opacity: 0.8;'>
            Developed by Muhammad Moiz | Computer Science Department
        </p>
        <p style='font-size: 0.75rem; opacity: 0.7;'>
            ⚠️ Your data is processed temporarily and not stored permanently.
            Calculations are based on SMIU's official grading policy.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============= DEBUG INFO (Visible only to admin) =============
if st.session_state.admin_logged_in:
    with st.sidebar:
        st.markdown("---")
        with st.expander("🔧 Debug Info"):
            st.write("**Session State:**")
            st.json({
                'admin_logged_in': st.session_state.admin_logged_in,
                'short_url_code': st.session_state.short_url_code,
                'gpa_count': len(st.session_state.gpa_calculations),
                'cgpa_count': len(st.session_state.cgpa_calculations)
            })
            
            # Test URL generator
            if st.session_state.short_url_code:
                test_url = f"{st.session_state.app_settings['base_url']}/?short={st.session_state.short_url_code}"
                st.code(test_url, language="text")
                st.caption("Test this URL in a new tab")
