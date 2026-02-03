import streamlit as st
import pandas as pd
from datetime import datetime
import io
import secrets
from urllib.parse import urlparse
import json

# Page configuration
st.set_page_config(
    page_title="SMIU GPA & CGPA Calculator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= INITIALIZE SESSION STATE =============
def initialize_session_state():
    """Initialize all session state variables"""
    default_credentials = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # Admin settings
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    if 'admin_credentials' not in st.session_state:
        st.session_state.admin_credentials = default_credentials
    if 'admin_settings' not in st.session_state:
        st.session_state.admin_settings = {
            'short_url': None,
            'base_url': "https://gpa-calculator.streamlit.app",
            'app_title': "SMIU GPA & CGPA Calculator",
            'institution_name': "Sindh Madressatul Islam University",
            'institution_logo': "https://www.smiu.edu.pk/themes/smiu/images/13254460_710745915734761_8157428650049174152_n.png"
        }
    
    # Student calculations storage
    if 'gpa_calculations' not in st.session_state:
        st.session_state.gpa_calculations = []
    if 'cgpa_calculations' not in st.session_state:
        st.session_state.cgpa_calculations = []
    
    # User interface settings
    if 'num_courses' not in st.session_state:
        st.session_state.num_courses = 1
    if 'num_semesters' not in st.session_state:
        st.session_state.num_semesters = 1

# Initialize session state
initialize_session_state()

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
    """Generate a random short URL"""
    return f"gpa-{secrets.token_hex(3)}"

def validate_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def export_to_excel(data, calculation_type, student_name=None):
    """Export data to Excel format"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Add institution header
        header_df = pd.DataFrame({
            'Institution': [st.session_state.admin_settings['institution_name']],
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

def clear_calculations():
    """Clear all calculation history"""
    st.session_state.gpa_calculations = []
    st.session_state.cgpa_calculations = []
    st.success("All calculation history cleared!")

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
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Result cards */
    .result-card {
        background: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Admin section styling */
    .admin-section {
        background: linear-gradient(120deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        background-color: #f8f9fa;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ============= HEADER =============
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div class="main-header">
        <img src="{st.session_state.admin_settings['institution_logo']}" width="150" style="margin-bottom: 1rem;">
        <h1>{st.session_state.admin_settings['app_title']}</h1>
        <p style="margin-top: 0.5rem; opacity: 0.9;">{st.session_state.admin_settings['institution_name']}</p>
    </div>
    """, unsafe_allow_html=True)

# ============= ADMIN LOGIN MODAL =============
if not st.session_state.admin_logged_in:
    # Check for admin login button in main interface
    if st.sidebar.button("🔐 Admin Login", use_container_width=True):
        # Create login form in main area
        st.markdown("---")
        st.subheader("🔐 Admin Login")
        
        login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
        with login_col2:
            admin_user = st.text_input("Username", key="admin_user_input")
            admin_pass = st.text_input("Password", type="password", key="admin_pass_input")
            
            if st.button("Login", key="admin_login_button", use_container_width=True):
                if (admin_user == st.session_state.admin_credentials['username'] and 
                    admin_pass == st.session_state.admin_credentials['password']):
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
            
            if st.button("Back to Calculator", key="back_to_calc"):
                st.rerun()

# ============= ADMIN PANEL =============
if st.session_state.admin_logged_in:
    with st.sidebar:
        st.markdown("### ⚙️ Admin Panel")
        
        # Admin Info
        with st.expander("👤 Admin Information", expanded=True):
            st.info(f"Logged in as: **{st.session_state.admin_credentials['username']}**")
            
            # Change Credentials
            st.subheader("Change Credentials")
            new_user = st.text_input("New Username", 
                                    value=st.session_state.admin_credentials['username'],
                                    key="new_username")
            new_pass = st.text_input("New Password", 
                                    type="password", 
                                    value=st.session_state.admin_credentials['password'],
                                    key="new_password")
            
            if st.button("Update Credentials", key="update_creds"):
                if new_user and new_pass:
                    st.session_state.admin_credentials['username'] = new_user
                    st.session_state.admin_credentials['password'] = new_pass
                    st.success("Credentials updated successfully!")
                else:
                    st.error("Username and password cannot be empty!")
        
        # URL Management
        with st.expander("🔗 URL Management"):
            st.subheader("Base URL Configuration")
            current_base = st.session_state.admin_settings['base_url']
            new_base = st.text_input("New Base URL", 
                                    value=current_base,
                                    placeholder="https://your-domain.streamlit.app",
                                    key="new_base_url")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Base URL", key="update_base"):
                    if validate_url(new_base):
                        st.session_state.admin_settings['base_url'] = new_base.rstrip('/')
                        st.success("Base URL updated!")
                    else:
                        st.error("Invalid URL format!")
            
            with col2:
                if st.button("Generate Short URL", key="gen_short"):
                    st.session_state.admin_settings['short_url'] = generate_short_url()
            
            if st.session_state.admin_settings['short_url']:
                st.markdown("---")
                st.subheader("Shareable URL")
                short_url = f"{st.session_state.admin_settings['base_url']}/?short={st.session_state.admin_settings['short_url']}"
                st.code(short_url, language="text")
                
                # Copy button functionality
                if st.button("📋 Copy URL", key="copy_url"):
                    st.info("URL copied to clipboard! (Simulated - in production use pyperclip)")
            
            # Quick access URLs
            st.markdown("---")
            st.subheader("Quick Access")
            regular_url = f"{st.session_state.admin_settings['base_url']}/"
            st.code(regular_url, language="text")
            st.caption("Regular access link (for admin)")
        
        # App Customization
        with st.expander("🎨 App Customization"):
            st.subheader("Appearance Settings")
            
            new_title = st.text_input("App Title", 
                                     value=st.session_state.admin_settings['app_title'],
                                     key="new_app_title")
            new_inst = st.text_input("Institution Name", 
                                    value=st.session_state.admin_settings['institution_name'],
                                    key="new_inst_name")
            new_logo = st.text_input("Logo URL", 
                                    value=st.session_state.admin_settings['institution_logo'],
                                    key="new_logo_url")
            
            if st.button("Update Appearance", key="update_appearance"):
                st.session_state.admin_settings['app_title'] = new_title
                st.session_state.admin_settings['institution_name'] = new_inst
                st.session_state.admin_settings['institution_logo'] = new_logo
                st.success("App appearance updated!")
                st.rerun()
        
        # Data Management
        with st.expander("📊 Data Management"):
            st.subheader("Calculation Statistics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("GPA Calculations", len(st.session_state.gpa_calculations))
            with col2:
                st.metric("CGPA Calculations", len(st.session_state.cgpa_calculations))
            
            st.markdown("---")
            
            # Clear Data
            if st.button("🗑️ Clear All Data", key="clear_data"):
                clear_calculations()
            
            # Export All Data
            if st.session_state.gpa_calculations or st.session_state.cgpa_calculations:
                st.markdown("---")
                st.subheader("Export All Data")
                
                export_col1, export_col2 = st.columns(2)
                with export_col1:
                    if st.session_state.gpa_calculations:
                        excel_file = export_to_excel(st.session_state.gpa_calculations, 'BULK_GPA')
                        st.download_button(
                            label="📥 All GPA Data",
                            data=excel_file,
                            file_name=f"All_GPA_Data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="dl_all_gpa"
                        )
                
                with export_col2:
                    if st.session_state.cgpa_calculations:
                        excel_file = export_to_excel(st.session_state.cgpa_calculations, 'BULK_CGPA')
                        st.download_button(
                            label="📥 All CGPA Data",
                            data=excel_file,
                            file_name=f"All_CGPA_Data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="dl_all_cgpa"
                        )
        
        # Logout Section
        st.markdown("---")
        if st.button("🚪 Logout", key="admin_logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

# ============= ACCESS CONTROL =============
# Check if short URL is required and present
short_url_enabled = st.session_state.admin_settings['short_url'] is not None
if short_url_enabled and not st.session_state.admin_logged_in:
    query_params = st.query_params
    if 'short' not in query_params or query_params['short'] != st.session_state.admin_settings['short_url']:
        st.error("""
        ## ⚠️ Access Restricted
        
        This calculator requires a special access URL provided by your institution.
        
        **Please contact your administrator for the correct link.**
        
        If you are an administrator, please login using the admin panel.
        """)
        if st.button("🔼 Back to Login", key="access_back"):
            st.rerun()
        st.stop()

# ============= MAIN CALCULATOR TABS =============
tab1, tab2, tab3 = st.tabs(["📊 GPA Calculator", "📈 CGPA Calculator", "📋 Grading Scale"])

# ============= GPA CALCULATOR TAB =============
with tab1:
    st.header("🎯 Semester GPA Calculator")
    st.markdown("Calculate your semester GPA based on course grades and credit hours")
    
    # Student Information
    with st.expander("👤 Student Information (Optional)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("Student Name", 
                                     placeholder="e.g., Muhammad Moiz",
                                     key='gpa_user_name')
        with col2:
            student_id = st.text_input("Student ID (Optional)", 
                                      placeholder="e.g., SM123456",
                                      key='gpa_student_id')
    
    st.markdown("---")
    
    # Course Configuration
    st.subheader("📚 Course Configuration")
    col1, col2 = st.columns([3, 1])
    with col1:
        num_courses = st.number_input("Number of Courses", 
                                     min_value=1, max_value=20, 
                                     value=st.session_state.num_courses,
                                     key='courses_input',
                                     help="Enter the total number of courses this semester")
    with col2:
        if st.button("🔄 Reset Courses", key="reset_courses"):
            st.session_state.num_courses = 1
            st.rerun()
    
    # Course Inputs
    courses_data = []
    
    for i in range(st.session_state.num_courses):
        st.markdown(f"### Course {i+1}")
        
        course_col1, course_col2 = st.columns([2, 3])
        with course_col1:
            course_name = st.text_input(f"Course Name", 
                                      placeholder=f"e.g., Data Structures",
                                      key=f'course_name_{i}',
                                      help="Enter the name of the course")
        
        with course_col2:
            col1, col2, col3 = st.columns(3)
            with col1:
                total_marks = st.number_input(f"Total Marks", 
                                            min_value=0.0, 
                                            value=100.0,
                                            step=1.0,
                                            key=f'total_{i}',
                                            help="Maximum possible marks")
            with col2:
                obtained_marks = st.number_input(f"Obtained Marks", 
                                               min_value=0.0, 
                                               max_value=total_marks,
                                               value=0.0,
                                               step=0.5,
                                               key=f'obtained_{i}',
                                               help="Marks you obtained")
            with col3:
                credit_hours = st.number_input(f"Credit Hours", 
                                             min_value=0.0,
                                             max_value=10.0,
                                             value=3.0,
                                             step=0.5,
                                             key=f'credit_{i}',
                                             help="Credit hours for this course")
        
        courses_data.append({
            'course_name': course_name if course_name else f"Course {i+1}",
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'credit_hours': credit_hours
        })
        
        if i < st.session_state.num_courses - 1:
            st.markdown("---")
    
    # Calculate GPA Button
    st.markdown("---")
    calc_col1, calc_col2, calc_col3 = st.columns([1, 2, 1])
    with calc_col2:
        calculate_gpa = st.button("🧮 Calculate GPA", 
                                 type="primary", 
                                 key='calc_gpa',
                                 use_container_width=True)
    
    if calculate_gpa:
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
                
                # Display success message
                st.success("### ✅ GPA Calculated Successfully!")
                
                # Course Results Table
                st.subheader("📊 Course-wise Results")
                df = pd.DataFrame(course_results)
                styled_df = df.style.set_properties(**{
                    'background-color': '#f8f9fa',
                    'border': '1px solid #dee2e6'
                })
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
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
                
                # Store calculation in session
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
                
                download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
                with download_col2:
                    st.download_button(
                        label="⬇️ Download GPA Report (Excel)",
                        data=excel_file,
                        file_name=f"GPA_Report_{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                # Success Message
                st.info("""
                ### ❤️ Thank You!
                Your GPA has been calculated successfully. 
                You can download your report above.
                """)
                
                # Update number of courses for next calculation
                st.session_state.num_courses = len(courses_data)
            else:
                st.error("❌ Total credit hours must be greater than zero!")

# ============= CGPA CALCULATOR TAB =============
with tab2:
    st.header("📈 Overall CGPA Calculator")
    st.markdown("Calculate your cumulative GPA across multiple semesters")
    
    # Student Information
    with st.expander("👤 Student Information (Optional)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            user_name_cgpa = st.text_input("Student Name", 
                                          placeholder="e.g., Muhammad Moiz",
                                          key='cgpa_user_name')
        with col2:
            student_id_cgpa = st.text_input("Student ID (Optional)", 
                                           placeholder="e.g., SM123456",
                                           key='cgpa_student_id')
    
    st.markdown("---")
    
    # Semester Configuration
    st.subheader("📅 Semester Configuration")
    col1, col2 = st.columns([3, 1])
    with col1:
        num_semesters = st.number_input("Number of Semesters", 
                                       min_value=1, max_value=12, 
                                       value=st.session_state.num_semesters,
                                       key='semesters_input',
                                       help="Enter total number of completed semesters")
    with col2:
        if st.button("🔄 Reset Semesters", key="reset_semesters"):
            st.session_state.num_semesters = 1
            st.rerun()
    
    # Semester Inputs
    semesters_data = []
    
    for i in range(st.session_state.num_semesters):
        st.markdown(f"### Semester {i+1}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            semester_gpa = st.number_input(f"Semester GPA", 
                                          min_value=0.0, 
                                          max_value=4.0,
                                          value=0.0,
                                          step=0.01,
                                          key=f'sem_gpa_{i}',
                                          help="Enter your GPA for this semester",
                                          format="%.2f")
        
        with col2:
            semester_credits = st.number_input(f"Credit Hours", 
                                              min_value=0.0,
                                              max_value=50.0,
                                              value=0.0,
                                              step=0.5,
                                              key=f'sem_credits_{i}',
                                              help="Total credit hours completed this semester")
        
        semesters_data.append({
            'gpa': semester_gpa,
            'credit_hours': semester_credits
        })
        
        if i < st.session_state.num_semesters - 1:
            st.markdown("---")
    
    # Calculate CGPA Button
    st.markdown("---")
    calc_col1, calc_col2, calc_col3 = st.columns([1, 2, 1])
    with calc_col2:
        calculate_cgpa = st.button("🧮 Calculate CGPA", 
                                  type="primary", 
                                  key='calc_cgpa',
                                  use_container_width=True)
    
    if calculate_cgpa:
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
                
                # Display success message
                st.success("### ✅ CGPA Calculated Successfully!")
                
                # Semester Results Table
                st.subheader("📊 Semester-wise Results")
                df = pd.DataFrame(semester_results)
                styled_df = df.style.set_properties(**{
                    'background-color': '#f8f9fa',
                    'border': '1px solid #dee2e6'
                })
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
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
                
                # Store calculation in session
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
                
                download_col1, download_col2, download_col3 = st.columns([1, 2, 1])
                with download_col2:
                    st.download_button(
                        label="⬇️ Download CGPA Report (Excel)",
                        data=excel_file,
                        file_name=f"CGPA_Report_{student_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                # Success Message
                st.info("""
                ### ❤️ Thank You!
                Your CGPA has been calculated successfully. 
                You can download your report above.
                """)
                
                # Update number of semesters for next calculation
                st.session_state.num_semesters = len(semesters_data)
            else:
                st.error("❌ Total credit hours must be greater than zero!")

# ============= GRADING SCALE TAB =============
with tab3:
    st.header("📋 SMIU Grading Scale")
    st.markdown("Official grading system used by Sindh Madressatul Islam University")
    
    # Grading Table
    grade_df = pd.DataFrame(GRADE_TABLE, columns=['Min %', 'Max %', 'Letter Grade', 'Grade Point'])
    grade_df['Percentage Range'] = grade_df.apply(lambda x: f"{x['Min %']}% - {x['Max %']}%", axis=1)
    
    # Display with styling
    display_df = grade_df[['Percentage Range', 'Letter Grade', 'Grade Point']]
    
    # Apply conditional formatting
    def color_grades(val):
        if val == 'A':
            return 'background-color: #28a745; color: white'
        elif val == 'B':
            return 'background-color: #17a2b8; color: white'
        elif val == 'C':
            return 'background-color: #ffc107; color: black'
        elif val == 'D':
            return 'background-color: #fd7e14; color: white'
        elif val == 'F':
            return 'background-color: #dc3545; color: white'
        return ''
    
    styled_df = display_df.style.applymap(color_grades, subset=['Letter Grade'])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Grading Information
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 GPA Calculation Formula
        
        **For Single Course:**
        ```
        Course GPA = Grade Point × Credit Hours
        ```
        
        **For Semester GPA:**
        ```
        Semester GPA = Σ(Course GPA) ÷ Σ(Credit Hours)
        ```
        
        **Example:**
        - Course 1: A (4.0) × 3 credits = 12.0
        - Course 2: B+ (3.33) × 3 credits = 9.99
        - Total Grade Points = 21.99
        - Total Credits = 6
        - **GPA = 21.99 ÷ 6 = 3.67**
        """)
    
    with col2:
        st.markdown("""
        ### 📈 CGPA Calculation Formula
        
        **For Semester CGPA Contribution:**
        ```
        Semester Points = Semester GPA × Semester Credits
        ```
        
        **For Overall CGPA:**
        ```
        Overall CGPA = Σ(Semester Points) ÷ Σ(Total Credits)
        ```
        
        **Example:**
        - Semester 1: GPA 3.5 × 15 credits = 52.5
        - Semester 2: GPA 3.8 × 18 credits = 68.4
        - Total Grade Points = 120.9
        - Total Credits = 33
        - **CGPA = 120.9 ÷ 33 = 3.66**
        """)
    
    # Additional Information
    st.markdown("---")
    st.markdown("""
    ### ℹ️ Important Notes
    
    1. **Minimum Passing Grade:** Students must obtain at least 'D' grade (50% marks) to pass a course.
    2. **Credit Hours:** Each course has specific credit hours that determine its weight in GPA calculation.
    3. **GPA Ranges:**
       - **Excellent:** 3.67 - 4.00 (A to A-)
       - **Good:** 3.00 - 3.66 (B to B+)
       - **Satisfactory:** 2.00 - 2.99 (C to B-)
       - **Passing:** 1.00 - 1.99 (D to C-)
       - **Fail:** Below 1.00 (F)
    
    4. **Incomplete Grades:** Courses with 'I' grade are not included in GPA calculation until completed.
    5. **Withdrawal:** Courses with 'W' grade do not affect GPA.
    """)

# ============= FOOTER =============
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p style='font-size: 0.9rem; margin-bottom: 0.5rem;'>
            <strong>© 2024 {institution_name} - GPA & CGPA Calculator</strong>
        </p>
        <p style='font-size: 0.8rem; margin-bottom: 0.5rem; opacity: 0.8;'>
            Developed by Muhammad Moiz | Computer Science Department
        </p>
        <p style='font-size: 0.75rem; opacity: 0.7;'>
            ⚠️ Your data is processed temporarily and not stored permanently.
            Calculations are based on SMIU's official grading policy.
        </p>
        <p style='font-size: 0.7rem; opacity: 0.6; margin-top: 1rem;'>
            Version 2.0 | Last Updated: {date}
        </p>
    </div>
    """.format(
        institution_name=st.session_state.admin_settings['institution_name'],
        date=datetime.now().strftime("%B %d, %Y")
    ), unsafe_allow_html=True)

# ============= ADMIN DOWNLOAD MODAL =============
if st.session_state.admin_logged_in:
    # Show quick download options in sidebar
    with st.sidebar:
        if st.session_state.gpa_calculations or st.session_state.cgpa_calculations:
            st.markdown("---")
            st.subheader("⚡ Quick Downloads")
            
            # Individual student downloads
            if st.session_state.gpa_calculations:
                gpa_students = list(set([calc['student_name'] for calc in st.session_state.gpa_calculations]))
                selected_gpa_student = st.selectbox("Select Student (GPA)", [""] + gpa_students, key="sidebar_gpa_select")
                
                if selected_gpa_student:
                    student_calcs = [calc for calc in st.session_state.gpa_calculations 
                                   if calc['student_name'] == selected_gpa_student]
                    if student_calcs:
                        latest_calc = student_calcs[-1]
                        excel_file = export_to_excel(latest_calc, 'GPA', selected_gpa_student)
                        st.download_button(
                            label=f"📥 {selected_gpa_student}'s GPA",
                            data=excel_file,
                            file_name=f"GPA_{selected_gpa_student.replace(' ', '_')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="sidebar_gpa_dl"
                        )
            
            if st.session_state.cgpa_calculations:
                cgpa_students = list(set([calc['student_name'] for calc in st.session_state.cgpa_calculations]))
                selected_cgpa_student = st.selectbox("Select Student (CGPA)", [""] + cgpa_students, key="sidebar_cgpa_select")
                
                if selected_cgpa_student:
                    student_calcs = [calc for calc in st.session_state.cgpa_calculations 
                                   if calc['student_name'] == selected_cgpa_student]
                    if student_calcs:
                        latest_calc = student_calcs[-1]
                        excel_file = export_to_excel(latest_calc, 'CGPA', selected_cgpa_student)
                        st.download_button(
                            label=f"📥 {selected_cgpa_student}'s CGPA",
                            data=excel_file,
                            file_name=f"CGPA_{selected_cgpa_student.replace(' ', '_')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="sidebar_cgpa_dl"
                        )
