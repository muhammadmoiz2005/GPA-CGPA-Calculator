import streamlit as st
import pandas as pd
from datetime import datetime
import io
import hashlib
import json
import os
from pathlib import Path
import secrets
import string

# Page configuration
st.set_page_config(
    page_title="SMIU GPA & CGPA Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# File paths
DATA_DIR = "data"
STUDENT_GPA_FILE = f"{DATA_DIR}/student_gpa_records.json"
STUDENT_CGPA_FILE = f"{DATA_DIR}/student_cgpa_records.json"
ADMIN_CONFIG_FILE = f"{DATA_DIR}/admin_config.json"
URL_SHORTENER_FILE = f"{DATA_DIR}/url_shortener.json"

# Create data directory if it doesn't exist
Path(DATA_DIR).mkdir(exist_ok=True)

# Initialize admin configuration if not exists
def init_admin_config():
    if not os.path.exists(ADMIN_CONFIG_FILE):
        default_config = {
            "username": "admin",
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest()
        }
        with open(ADMIN_CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)

# Initialize URL shortener database
def init_url_shortener():
    if not os.path.exists(URL_SHORTENER_FILE):
        default_data = {
            "base_url": "https://smiumgpa.streamlit.app",
            "short_codes": {},
            "active_short_codes": [],
            "url_history": []
        }
        with open(URL_SHORTENER_FILE, 'w') as f:
            json.dump(default_data, f, indent=2)

# Initialize student data files
def init_student_data():
    for file_path in [STUDENT_GPA_FILE, STUDENT_CGPA_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f, indent=2)

# Load data from JSON files
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return []

# Save data to JSON files
def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generate random short code
def generate_short_code(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Initialize all files
init_admin_config()
init_url_shortener()
init_student_data()

# Load configurations
with open(ADMIN_CONFIG_FILE, 'r') as f:
    admin_config = json.load(f)

# Load URL shortener data
with open(URL_SHORTENER_FILE, 'r') as f:
    url_data = json.load(f)

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
            if student_name:  # Individual student from admin panel
                # Check if data has 'summary' key
                if 'summary' in data:
                    summary_data = data['summary']
                else:
                    # If data is from admin panel (raw record), extract necessary info
                    summary_data = {
                        'total_credit_hours': data.get('total_credit_hours', 0),
                        'total_grade_points': data.get('total_grade_points', 0),
                        'gpa': data.get('final_gpa', 0),
                        'timestamp': data.get('timestamp', '')
                    }
                    courses_data = data.get('courses', [])
                    
                    # Course details sheet
                    if courses_data:
                        courses_df = pd.DataFrame(courses_data)
                        courses_df.index = courses_df.index + 1
                        courses_df.index.name = 'Course No.'
                        courses_df.to_excel(writer, sheet_name='Course Details')
                
                # Summary sheet
                summary_df = pd.DataFrame({
                    'Metric': ['Student Name', 'Total Credit Hours', 'Total Grade Points', 'Final GPA', 'Date'],
                    'Value': [student_name, 
                             summary_data.get('total_credit_hours', 0), 
                             summary_data.get('total_grade_points', 0),
                             summary_data.get('gpa', 0),
                             summary_data.get('timestamp', '')]
                })
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
            else:  # All students
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='All GPA Records', index=False)
                
        else:  # CGPA
            if student_name:  # Individual student from admin panel
                # Check if data has 'summary' key
                if 'summary' in data:
                    summary_data = data['summary']
                else:
                    # If data is from admin panel (raw record), extract necessary info
                    summary_data = {
                        'total_credit_hours': data.get('total_credit_hours', 0),
                        'total_grade_points': data.get('total_grade_points', 0),
                        'cgpa': data.get('final_cgpa', 0),
                        'timestamp': data.get('timestamp', '')
                    }
                    semesters_data = data.get('semesters', [])
                    
                    # Semester details sheet
                    if semesters_data:
                        semesters_df = pd.DataFrame(semesters_data)
                        semesters_df.index = semesters_df.index + 1
                        semesters_df.index.name = 'Semester No.'
                        semesters_df.to_excel(writer, sheet_name='Semester Details')
                
                # Summary sheet
                summary_df = pd.DataFrame({
                    'Metric': ['Student Name', 'Total Credit Hours', 'Total Grade Points', 'Final CGPA', 'Date'],
                    'Value': [student_name,
                             summary_data.get('total_credit_hours', 0), 
                             summary_data.get('total_grade_points', 0),
                             summary_data.get('cgpa', 0),
                             summary_data.get('timestamp', '')]
                })
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            else:  # All students
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='All CGPA Records', index=False)
    
    output.seek(0)
    return output

def export_to_csv(data, calculation_type, student_name=None):
    """Export data to CSV format"""
    if calculation_type == 'GPA':
        if student_name:  # Individual student
            # Create two CSV files for individual report
            if 'summary' in data:
                summary_data = data['summary']
                courses_data = data.get('courses', [])
            else:
                summary_data = {
                    'total_credit_hours': data.get('total_credit_hours', 0),
                    'total_grade_points': data.get('total_grade_points', 0),
                    'gpa': data.get('final_gpa', 0),
                    'timestamp': data.get('timestamp', '')
                }
                courses_data = data.get('courses', [])
            
            # Create summary CSV
            summary_df = pd.DataFrame({
                'Metric': ['Student Name', 'Total Credit Hours', 'Total Grade Points', 'Final GPA', 'Date'],
                'Value': [student_name, 
                         summary_data.get('total_credit_hours', 0), 
                         summary_data.get('total_grade_points', 0),
                         summary_data.get('gpa', 0),
                         summary_data.get('timestamp', '')]
            })
            
            # Create courses CSV if exists
            courses_csv = None
            if courses_data:
                courses_df = pd.DataFrame(courses_data)
                courses_df.index = courses_df.index + 1
                courses_df.index.name = 'Course No.'
                courses_csv = courses_df.to_csv(index=True)
            
            return summary_df.to_csv(index=False), courses_csv
        else:  # All students
            df = pd.DataFrame(data)
            return df.to_csv(index=False), None
    else:  # CGPA
        if student_name:  # Individual student
            if 'summary' in data:
                summary_data = data['summary']
                semesters_data = data.get('semesters', [])
            else:
                summary_data = {
                    'total_credit_hours': data.get('total_credit_hours', 0),
                    'total_grade_points': data.get('total_grade_points', 0),
                    'cgpa': data.get('final_cgpa', 0),
                    'timestamp': data.get('timestamp', '')
                }
                semesters_data = data.get('semesters', [])
            
            # Create summary CSV
            summary_df = pd.DataFrame({
                'Metric': ['Student Name', 'Total Credit Hours', 'Total Grade Points', 'Final CGPA', 'Date'],
                'Value': [student_name,
                         summary_data.get('total_credit_hours', 0), 
                         summary_data.get('total_grade_points', 0),
                         summary_data.get('cgpa', 0),
                         summary_data.get('timestamp', '')]
            })
            
            # Create semesters CSV if exists
            semesters_csv = None
            if semesters_data:
                semesters_df = pd.DataFrame(semesters_data)
                semesters_df.index = semesters_df.index + 1
                semesters_df.index.name = 'Semester No.'
                semesters_csv = semesters_df.to_csv(index=True)
            
            return summary_df.to_csv(index=False), semesters_csv
        else:  # All students
            df = pd.DataFrame(data)
            return df.to_csv(index=False), None

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
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
    }
    .stButton>button:hover {
        background-color: #5a67d8;
    }
    .admin-panel {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
    }
    .url-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .short-url-container {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .danger-button {
        background-color: #dc3545 !important;
        color: white !important;
    }
    .danger-button:hover {
        background-color: #c82333 !important;
    }
    .warning-button {
        background-color: #ffc107 !important;
        color: #212529 !important;
    }
    .warning-button:hover {
        background-color: #e0a800 !important;
    }
    .deactivated-message {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem auto;
        max-width: 600px;
    }
    .deactivated-title {
        color: #856404;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .deactivated-text {
        color: #856404;
        font-size: 1.1rem;
    }
    .back-button {
        background-color: #6c757d !important;
        color: white !important;
        margin-top: 1rem;
    }
    .delete-confirmation {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .calculator-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    .export-option {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'show_admin_login' not in st.session_state:
    st.session_state.show_admin_login = False
if 'show_clear_history_confirm' not in st.session_state:
    st.session_state.show_clear_history_confirm = False
if 'show_delete_url_confirm' not in st.session_state:
    st.session_state.show_delete_url_confirm = False
if 'url_to_delete' not in st.session_state:
    st.session_state.url_to_delete = None

# Admin Login Function
def admin_login():
    st.title("🔐 Admin Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            with open(ADMIN_CONFIG_FILE, 'r') as f:
                current_admin_config = json.load(f)
            
            if username == current_admin_config["username"] and hash_password(password) == current_admin_config["password_hash"]:
                st.session_state.authenticated = True
                st.session_state.current_user = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    # Back button only if we came from student interface
    query_params = st.query_params
    if 'student' in query_params or 'access_code' in query_params:
        if st.button("← Back to Calculator"):
            st.session_state.show_admin_login = False
            st.rerun()

# Show deactivated URL message to students
def show_deactivated_message():
    st.markdown("""
        <div class="deactivated-message">
            <h2 class="deactivated-title">🚫 URL Deactivated</h2>
            <p class="deactivated-text">
                <strong>This URL has been deactivated by your class CR.</strong><br><br>
                Please contact your class representative for a new access URL.
            </p>
            <p style="color: #666; margin-top: 1rem;">
                If you are the admin, please login through the admin panel.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔐 Admin Login", key="admin_login_deactivated"):
        st.session_state.show_admin_login = True
        st.rerun()

# Admin Panel
def admin_panel():
    st.sidebar.title("👨‍💼 Admin Panel")
    
    # Display current admin username
    with open(ADMIN_CONFIG_FILE, 'r') as f:
        current_admin_config = json.load(f)
    
    st.sidebar.info(f"Logged in as: **{current_admin_config['username']}**")
    
    # Navigation
    menu = st.sidebar.selectbox(
        "Navigation",
        ["📊 Dashboard", "🔗 Short URL System", "🎓 Student GPA Records", 
         "📈 Student CGPA Records", "👤 Admin Account"]
    )
    
    if menu == "📊 Dashboard":
        st.title("Admin Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        # Load data for stats
        gpa_data = load_data(STUDENT_GPA_FILE)
        cgpa_data = load_data(STUDENT_CGPA_FILE)
        
        # Load URL data
        with open(URL_SHORTENER_FILE, 'r') as f:
            url_data = json.load(f)
        
        with col1:
            st.metric("Total GPA Calculations", len(gpa_data))
        with col2:
            st.metric("Total CGPA Calculations", len(cgpa_data))
        with col3:
            active_short_codes = len(url_data.get("active_short_codes", []))
            st.metric("Active Short URLs", active_short_codes)
        
        # Recent activity
        st.subheader("Recent Activity")
        
        # Combine and sort recent records
        all_records = []
        for record in gpa_data[-5:]:
            record['type'] = 'GPA'
            all_records.append(record)
        for record in cgpa_data[-5:]:
            record['type'] = 'CGPA'
            all_records.append(record)
        
        all_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        for record in all_records[:10]:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{record.get('user_name', 'Unknown')}** - {record.get('type', '')}")
            with col2:
                st.write(record.get('timestamp', ''))
            with col3:
                if record['type'] == 'GPA':
                    st.write(f"GPA: {record.get('final_gpa', 0):.2f}")
                else:
                    st.write(f"CGPA: {record.get('final_cgpa', 0):.2f}")
            st.divider()
    
    elif menu == "🔗 Short URL System":
        st.title("🔗 Short URL System")
        
        with open(URL_SHORTENER_FILE, 'r') as f:
            url_data = json.load(f)
        
        # Get current app URL
        try:
            # Try to get the actual app URL from the environment
            import urllib.request
            import json as json_module
            
            # For Streamlit Cloud, we can use the sharing URL
            # First, let's get the current URL from query params or use default
            current_url = "https://smiumgpa.streamlit.app"
            
            # Check if we're in Streamlit Cloud
            import os
            if "STREAMLIT_SHARING_URL" in os.environ:
                current_url = os.environ["STREAMLIT_SHARING_URL"]
            elif "STREAMLIT_SERVER_BASE_URL_PATH" in os.environ:
                current_url = os.environ["STREAMLIT_SERVER_BASE_URL_PATH"]
            
        except:
            current_url = "https://smiumgpa.streamlit.app"
        
        base_url = url_data.get("base_url", current_url)
        
        # Display current URLs
        st.info(f"**Current App URL:** `{current_url}`")
        st.info(f"**Stored Base URL:** `{base_url}`")
        
        # Create new short URL
        st.subheader("Create New Short URL")
        
        with st.form("create_short_url"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                custom_code = st.text_input("Custom Short Code (Optional)", 
                                          placeholder="e.g., smiu-gpa-2024")
            
            with col2:
                code_length = st.selectbox("Code Length", [6, 8, 10], index=1)
            
            if st.form_submit_button("🎯 Generate Short URL"):
                if custom_code:
                    short_code = custom_code
                else:
                    short_code = generate_short_code(code_length)
                
                # Create full URL with student parameter
                base_url_clean = base_url.rstrip('/')
                full_url = f"{base_url_clean}/?student={short_code}"
                
                # Save to database
                if "short_codes" not in url_data:
                    url_data["short_codes"] = {}
                
                url_data["short_codes"][short_code] = {
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "created_by": st.session_state.current_user,
                    "full_url": full_url,
                    "status": "active",
                    "base_url_used": base_url_clean
                }
                
                # Add to active codes
                if "active_short_codes" not in url_data:
                    url_data["active_short_codes"] = []
                
                if short_code not in url_data["active_short_codes"]:
                    url_data["active_short_codes"].append(short_code)
                
                # Add to history
                history_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "created",
                    "code": short_code,
                    "by": st.session_state.current_user,
                    "url": full_url
                }
                
                if "url_history" not in url_data:
                    url_data["url_history"] = []
                
                url_data["url_history"].append(history_entry)
                
                # Save data
                save_data(URL_SHORTENER_FILE, url_data)
                
                st.success(f"✅ Short URL created successfully!")
                
                # Display the generated URL
                st.markdown(f"""
                <div class="short-url-container">
                    <h3>🎯 Your Short URL:</h3>
                    <h4><code>{full_url}</code></h4>
                    <p>Copy and share this URL with students</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Copy button
                st.code(full_url, language="text")
        
        # Display active short URLs
        st.subheader("📋 Active Short URLs")
        
        if url_data.get("short_codes"):
            active_codes = url_data["short_codes"]
            
            display_data = []
            for code, details in active_codes.items():
                if details.get("status") == "active":
                    display_data.append({
                        'Short Code': code,
                        'URL': details.get('full_url', ''),
                        'Created At': details.get('created_at', ''),
                        'Created By': details.get('created_by', ''),
                        'Status': details.get('status', 'active')
                    })
            
            if display_data:
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # URL management
                st.subheader("🔧 Manage Short URLs")
                col1, col2 = st.columns(2)
                
                with col1:
                    codes_list = list(active_codes.keys())
                    selected_code = st.selectbox("Select Short Code to Manage", [""] + codes_list)
                    
                    if selected_code:
                        st.info(f"Selected: **{selected_code}**")
                        
                        # Show current URL
                        current_url_display = active_codes[selected_code].get('full_url', '')
                        st.code(current_url_display, language="text")
                        
                        # Copy button
                        if st.button("📋 Copy URL", key="copy_url"):
                            st.write(f"URL copied to clipboard: {current_url_display}")
                
                with col2:
                    if selected_code:
                        # Deactivate button with confirmation
                        if st.button("🚫 Deactivate Code", type="primary", key="deactivate"):
                            url_data["short_codes"][selected_code]["status"] = "inactive"
                            if selected_code in url_data.get("active_short_codes", []):
                                url_data["active_short_codes"].remove(selected_code)
                            
                            # Add to history
                            history_entry = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "action": "deactivated",
                                "code": selected_code,
                                "by": st.session_state.current_user,
                                "message": "Deactivated by class CR"
                            }
                            url_data["url_history"].append(history_entry)
                            
                            save_data(URL_SHORTENER_FILE, url_data)
                            st.success(f"✅ Code '{selected_code}' has been deactivated!")
                            st.info("Students will now see a message that the URL was deactivated by their class CR.")
                            st.rerun()
                        
                        # Regenerate button
                        if st.button("🔄 Regenerate Code", key="regenerate"):
                            new_code = generate_short_code(8)
                            old_data = url_data["short_codes"][selected_code]
                            
                            # Deactivate old
                            url_data["short_codes"][selected_code]["status"] = "inactive"
                            if selected_code in url_data.get("active_short_codes", []):
                                url_data["active_short_codes"].remove(selected_code)
                            
                            # Create new
                            base_url_used = old_data.get('base_url_used', base_url)
                            new_full_url = f"{base_url_used}/?student={new_code}"
                            url_data["short_codes"][new_code] = {
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "created_by": st.session_state.current_user,
                                "full_url": new_full_url,
                                "status": "active",
                                "base_url_used": base_url_used
                            }
                            
                            url_data["active_short_codes"].append(new_code)
                            
                            # Add to history
                            history_entry = {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "action": "regenerated",
                                "old_code": selected_code,
                                "new_code": new_code,
                                "by": st.session_state.current_user
                            }
                            url_data["url_history"].append(history_entry)
                            
                            save_data(URL_SHORTENER_FILE, url_data)
                            st.success(f"✅ New code '{new_code}' generated!")
                            st.rerun()
                        
                        # Delete button with confirmation
                        if st.button("🗑️ Delete URL", type="secondary", key="delete_url"):
                            st.session_state.show_delete_url_confirm = True
                            st.session_state.url_to_delete = selected_code
                            st.rerun()
            else:
                st.info("No active short URLs found.")
        else:
            st.info("No short URLs created yet.")
        
        # Delete URL Confirmation Dialog
        if st.session_state.get('show_delete_url_confirm', False):
            url_to_delete = st.session_state.url_to_delete
            
            st.markdown(f"""
                <div class="delete-confirmation">
                    <h3>⚠️ Confirm Deletion</h3>
                    <p>Are you sure you want to delete the URL with code: <strong>{url_to_delete}</strong>?</p>
                    <p>This action <strong>cannot be undone</strong> and will permanently remove the URL from the system.</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("✅ Yes, Delete", type="primary"):
                    # Remove from short_codes
                    if url_to_delete in url_data["short_codes"]:
                        # Add to history before deleting
                        history_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "action": "deleted",
                            "code": url_to_delete,
                            "by": st.session_state.current_user,
                            "url": url_data["short_codes"][url_to_delete].get('full_url', '')
                        }
                        url_data["url_history"].append(history_entry)
                        
                        # Delete the URL
                        del url_data["short_codes"][url_to_delete]
                    
                    # Remove from active_short_codes if present
                    if url_to_delete in url_data.get("active_short_codes", []):
                        url_data["active_short_codes"].remove(url_to_delete)
                    
                    # Save data
                    save_data(URL_SHORTENER_FILE, url_data)
                    
                    st.success(f"✅ URL '{url_to_delete}' has been deleted!")
                    st.session_state.show_delete_url_confirm = False
                    st.session_state.url_to_delete = None
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.show_delete_url_confirm = False
                    st.session_state.url_to_delete = None
                    st.rerun()
        
        # Bulk Delete URLs Section
        st.subheader("🗑️ Bulk URL Management")
        
        with st.expander("Delete Multiple URLs"):
            st.warning("⚠️ **Warning:** This will permanently delete selected URLs from the system.")
            
            if url_data.get("short_codes"):
                # Get all URLs for selection
                all_urls = list(url_data["short_codes"].keys())
                
                if all_urls:
                    # Multi-select for URLs to delete
                    urls_to_delete = st.multiselect(
                        "Select URLs to delete:",
                        all_urls,
                        help="Select multiple URLs to delete at once"
                    )
                    
                    if urls_to_delete:
                        st.warning(f"Selected {len(urls_to_delete)} URL(s) for deletion:")
                        
                        for url_code in urls_to_delete:
                            url_details = url_data["short_codes"][url_code]
                            st.write(f"- **{url_code}**: {url_details.get('full_url', '')} (Status: {url_details.get('status', 'unknown')})")
                        
                        # Confirmation for bulk delete
                        confirmation_text = st.text_input(
                            f"Type 'DELETE {len(urls_to_delete)}' to confirm:",
                            placeholder=f"Enter DELETE {len(urls_to_delete)}"
                        )
                        
                        if st.button("🗑️ Delete Selected URLs", type="secondary", key="bulk_delete"):
                            if confirmation_text == f"DELETE {len(urls_to_delete)}":
                                deleted_count = 0
                                
                                for url_code in urls_to_delete:
                                    if url_code in url_data["short_codes"]:
                                        # Add to history
                                        history_entry = {
                                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "action": "bulk_deleted",
                                            "code": url_code,
                                            "by": st.session_state.current_user
                                        }
                                        url_data["url_history"].append(history_entry)
                                        
                                        # Delete from short_codes
                                        del url_data["short_codes"][url_code]
                                        deleted_count += 1
                                    
                                    # Remove from active_short_codes if present
                                    if url_code in url_data.get("active_short_codes", []):
                                        url_data["active_short_codes"].remove(url_code)
                                
                                # Save data
                                save_data(URL_SHORTENER_FILE, url_data)
                                
                                # Add summary to history
                                summary_entry = {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "action": "bulk_delete_summary",
                                    "deleted_count": deleted_count,
                                    "by": st.session_state.current_user
                                }
                                url_data["url_history"].append(summary_entry)
                                save_data(URL_SHORTENER_FILE, url_data)
                                
                                st.success(f"✅ {deleted_count} URL(s) deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Please type 'DELETE {len(urls_to_delete)}' exactly to confirm deletion.")
                else:
                    st.info("No URLs available to delete.")
            else:
                st.info("No URLs available to delete.")
        
        # System Configuration Section
        st.subheader("⚙️ System Configuration")
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("### 🔧 Base URL Settings")
            
            with st.form("base_url_form"):
                current_base_url = st.text_input(
                    "Current Base URL", 
                    value=base_url,
                    help="This is the base URL used for generating short URLs"
                )
                
                if st.form_submit_button("🔄 Update Base URL"):
                    if current_base_url != base_url:
                        url_data["base_url"] = current_base_url
                        
                        # Update all existing active URLs with new base URL
                        if "short_codes" in url_data:
                            for code, details in url_data["short_codes"].items():
                                if details.get("status") == "active":
                                    # Extract student code from old URL
                                    old_url = details.get("full_url", "")
                                    if "student=" in old_url:
                                        student_code = old_url.split("student=")[-1]
                                        # Clean the base URL
                                        new_base_url = current_base_url.rstrip('/')
                                        new_full_url = f"{new_base_url}/?student={student_code}"
                                        url_data["short_codes"][code]["full_url"] = new_full_url
                                        url_data["short_codes"][code]["base_url_used"] = new_base_url
                        
                        # Add to history
                        history_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "action": "base_url_changed",
                            "old_base_url": base_url,
                            "new_base_url": current_base_url,
                            "by": st.session_state.current_user
                        }
                        url_data["url_history"].append(history_entry)
                        
                        save_data(URL_SHORTENER_FILE, url_data)
                        st.success(f"✅ Base URL updated to: {current_base_url}")
                        st.info("All active short URLs have been updated with the new base URL.")
                        st.rerun()
                    else:
                        st.info("Base URL is already set to this value.")
        
        with config_col2:
            st.markdown("### 🗑️ Data Management")
            
            # Delete URL History
            st.warning("**Delete URL History**")
            st.write("This will permanently delete all URL history records.")
            
            with st.form("delete_history_form"):
                confirmation = st.text_input(
                    "Type 'DELETE' to confirm",
                    placeholder="Enter DELETE to confirm",
                    help="This action cannot be undone!"
                )
                
                if st.form_submit_button("🗑️ Delete All History", type="secondary"):
                    if confirmation == "DELETE":
                        # Count records before deletion
                        history_count = len(url_data.get("url_history", []))
                        
                        # Create a history entry for the deletion
                        deletion_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "action": "history_cleared",
                            "records_deleted": history_count,
                            "by": st.session_state.current_user
                        }
                        
                        # Clear history and add deletion entry
                        url_data["url_history"] = [deletion_entry]
                        
                        save_data(URL_SHORTENER_FILE, url_data)
                        st.success(f"✅ URL history cleared! {history_count} records deleted.")
                        st.rerun()
                    else:
                        st.error("Please type 'DELETE' to confirm deletion.")
            
            # Additional cleanup options
            st.markdown("---")
            st.markdown("### 🧹 Advanced Cleanup")
            
            with st.expander("Cleanup Inactive URLs"):
                st.warning("This will permanently delete all inactive short URLs.")
                
                # Count inactive URLs
                inactive_count = 0
                if "short_codes" in url_data:
                    for code, details in url_data["short_codes"].items():
                        if details.get("status") == "inactive":
                            inactive_count += 1
                
                st.write(f"**Found {inactive_count} inactive URLs**")
                
                with st.form("cleanup_inactive_form"):
                    cleanup_confirmation = st.text_input(
                        "Type 'CLEANUP' to remove inactive URLs",
                        placeholder="Enter CLEANUP to confirm"
                    )
                    
                    if st.form_submit_button("🧹 Cleanup Inactive URLs", type="secondary"):
                        if cleanup_confirmation == "CLEANUP":
                            if inactive_count > 0:
                                # Create new dictionary with only active URLs
                                active_urls = {}
                                for code, details in url_data["short_codes"].items():
                                    if details.get("status") == "active":
                                        active_urls[code] = details
                                
                                url_data["short_codes"] = active_urls
                                
                                # Add to history
                                history_entry = {
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "action": "inactive_urls_cleaned",
                                    "inactive_urls_deleted": inactive_count,
                                    "by": st.session_state.current_user
                                }
                                url_data["url_history"].append(history_entry)
                                
                                save_data(URL_SHORTENER_FILE, url_data)
                                st.success(f"✅ Cleanup completed! {inactive_count} inactive URLs removed.")
                                st.rerun()
                            else:
                                st.info("No inactive URLs found to cleanup.")
                        else:
                            st.error("Please type 'CLEANUP' to confirm.")
        
        # URL History with Direct Delete Option
        st.subheader("📜 URL History")
        
        # Show history stats
        history_count = len(url_data.get("url_history", []))
        st.write(f"**Total History Records:** {history_count}")
        
        # Direct Delete Button for History
        if url_data.get("url_history"):
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("🗑️ Clear History", type="secondary", key="direct_delete_history"):
                    st.session_state.show_clear_history_confirm = True
            
            if st.session_state.get('show_clear_history_confirm', False):
                st.warning("Are you sure you want to clear all history? This action cannot be undone!")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, delete all history", type="primary"):
                        # Keep only the deletion entry
                        deletion_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "action": "history_cleared",
                            "records_deleted": history_count,
                            "by": st.session_state.current_user
                        }
                        url_data["url_history"] = [deletion_entry]
                        
                        save_data(URL_SHORTENER_FILE, url_data)
                        st.success(f"✅ History cleared! {history_count} records deleted.")
                        st.session_state.show_clear_history_confirm = False
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.show_clear_history_confirm = False
                        st.rerun()
        
        if url_data.get("url_history"):
            # Filter options for history
            col1, col2 = st.columns(2)
            with col1:
                filter_action = st.selectbox(
                    "Filter by Action",
                    ["All Actions", "created", "deactivated", "regenerated", 
                     "base_url_changed", "history_cleared", "inactive_urls_cleaned", "deleted", "bulk_deleted"]
                )
            
            with col2:
                filter_user = st.selectbox(
                    "Filter by User",
                    ["All Users"] + sorted(list(set([h.get("by", "Unknown") for h in url_data["url_history"]])))
                )
            
            # Apply filters
            filtered_history = url_data["url_history"]
            
            if filter_action != "All Actions":
                filtered_history = [h for h in filtered_history if h.get("action") == filter_action]
            
            if filter_user != "All Users":
                filtered_history = [h for h in filtered_history if h.get("by") == filter_user]
            
            # Sort by timestamp (newest first)
            filtered_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            if filtered_history:
                history_df = pd.DataFrame(filtered_history)
                
                # Display columns nicely
                display_cols = []
                for col in history_df.columns:
                    if col not in ['by', 'action', 'timestamp']:
                        display_cols.append(col)
                
                # Reorder columns
                history_df = history_df[['timestamp', 'action', 'by'] + display_cols]
                
                st.dataframe(history_df, use_container_width=True)
                
                # Export history option
                st.markdown("### 📥 Export History")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Export History to CSV"):
                        csv = history_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"url_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                with col2:
                    if st.button("Export History to Excel"):
                        # Create Excel file
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            history_df.to_excel(writer, sheet_name='URL History', index=False)
                        output.seek(0)
                        
                        st.download_button(
                            label="Download Excel",
                            data=output,
                            file_name=f"url_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.info("No history records found with the selected filters.")
        else:
            st.info("No URL history available.")
    
    elif menu == "🎓 Student GPA Records":
        st.title("Student GPA Records")
        
        gpa_data = load_data(STUDENT_GPA_FILE)
        
        if gpa_data:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("Search by Student Name")
            
            # Filter data
            filtered_data = gpa_data
            if search_term:
                filtered_data = [r for r in filtered_data if search_term.lower() in r.get('user_name', '').lower()]
            
            if filtered_data:
                # Create display dataframe
                display_data = []
                for record in filtered_data:
                    display_data.append({
                        'Student Name': record.get('user_name', ''),
                        'Date': record.get('timestamp', ''),
                        'Courses': len(record.get('courses', [])),
                        'Total Credits': record.get('total_credit_hours', 0),
                        'GPA': f"{record.get('final_gpa', 0):.2f}"
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Export options
                st.subheader("📥 Export Data")
                st.markdown("**Export All Records:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Download All GPA Records (Excel)"):
                        excel_file = export_to_excel(gpa_data, 'GPA')
                        st.download_button(
                            label="Click to Download Excel",
                            data=excel_file,
                            file_name=f"All_GPA_Records_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with col2:
                    if st.button("📄 Download All GPA Records (CSV)"):
                        csv_data, _ = export_to_csv(gpa_data, 'GPA')
                        st.download_button(
                            label="Click to Download CSV",
                            data=csv_data,
                            file_name=f"All_GPA_Records_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                
                # Individual student export
                st.markdown("---")
                st.markdown("**Export Individual Student Report:**")
                student_names = list(set([r.get('user_name', '') for r in filtered_data]))
                selected_student = st.selectbox("Select Student for Individual Report", [""] + student_names)
                
                if selected_student:
                    student_records = [r for r in filtered_data if r.get('user_name', '') == selected_student]
                    if student_records:
                        # Take the most recent record for the student
                        latest_record = max(student_records, key=lambda x: x.get('timestamp', ''))
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Excel Export
                            excel_file = export_to_excel(latest_record, 'GPA', selected_student)
                            st.download_button(
                                label=f"📊 Download {selected_student}'s Report (Excel)",
                                data=excel_file,
                                file_name=f"GPA_Report_{selected_student}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        with col2:
                            # CSV Export (two files: summary and courses)
                            st.markdown(f"**CSV Export for {selected_student}:**")
                            
                            # Get CSV data
                            summary_csv, courses_csv = export_to_csv(latest_record, 'GPA', selected_student)
                            
                            # Summary CSV
                            if summary_csv:
                                st.download_button(
                                    label="📄 Download Summary CSV",
                                    data=summary_csv,
                                    file_name=f"GPA_Summary_{selected_student}_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
                            
                            # Courses CSV (if available)
                            if courses_csv:
                                st.download_button(
                                    label="📄 Download Course Details CSV",
                                    data=courses_csv,
                                    file_name=f"GPA_Courses_{selected_student}_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
            else:
                st.info("No records found with the selected filters.")
        else:
            st.info("No GPA records available yet.")
    
    elif menu == "📈 Student CGPA Records":
        st.title("Student CGPA Records")
        
        cgpa_data = load_data(STUDENT_CGPA_FILE)
        
        if cgpa_data:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("Search by Student Name", key="cgpa_search")
            
            # Filter data
            filtered_data = cgpa_data
            if search_term:
                filtered_data = [r for r in filtered_data if search_term.lower() in r.get('user_name', '').lower()]
            
            if filtered_data:
                # Create display dataframe
                display_data = []
                for record in filtered_data:
                    display_data.append({
                        'Student Name': record.get('user_name', ''),
                        'Date': record.get('timestamp', ''),
                        'Semesters': len(record.get('semesters', [])),
                        'Total Credits': record.get('total_credit_hours', 0),
                        'CGPA': f"{record.get('final_cgpa', 0):.2f}"
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Export options
                st.subheader("📥 Export Data")
                st.markdown("**Export All Records:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Download All CGPA Records (Excel)"):
                        excel_file = export_to_excel(cgpa_data, 'CGPA')
                        st.download_button(
                            label="Click to Download Excel",
                            data=excel_file,
                            file_name=f"All_CGPA_Records_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                
                with col2:
                    if st.button("📄 Download All CGPA Records (CSV)"):
                        csv_data, _ = export_to_csv(cgpa_data, 'CGPA')
                        st.download_button(
                            label="Click to Download CSV",
                            data=csv_data,
                            file_name=f"All_CGPA_Records_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                
                # Individual student export
                st.markdown("---")
                st.markdown("**Export Individual Student Report:**")
                student_names = list(set([r.get('user_name', '') for r in filtered_data]))
                selected_student = st.selectbox("Select Student for Individual Report", 
                                               [""] + student_names, key="cgpa_student")
                
                if selected_student:
                    student_records = [r for r in filtered_data if r.get('user_name', '') == selected_student]
                    if student_records:
                        # Take the most recent record for the student
                        latest_record = max(student_records, key=lambda x: x.get('timestamp', ''))
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Excel Export
                            excel_file = export_to_excel(latest_record, 'CGPA', selected_student)
                            st.download_button(
                                label=f"📊 Download {selected_student}'s Report (Excel)",
                                data=excel_file,
                                file_name=f"CGPA_Report_{selected_student}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        with col2:
                            # CSV Export (two files: summary and semesters)
                            st.markdown(f"**CSV Export for {selected_student}:**")
                            
                            # Get CSV data
                            summary_csv, semesters_csv = export_to_csv(latest_record, 'CGPA', selected_student)
                            
                            # Summary CSV
                            if summary_csv:
                                st.download_button(
                                    label="📄 Download Summary CSV",
                                    data=summary_csv,
                                    file_name=f"CGPA_Summary_{selected_student}_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
                            
                            # Semesters CSV (if available)
                            if semesters_csv:
                                st.download_button(
                                    label="📄 Download Semester Details CSV",
                                    data=semesters_csv,
                                    file_name=f"CGPA_Semesters_{selected_student}_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
            else:
                st.info("No records found with the selected filters.")
        else:
            st.info("No CGPA records available yet.")
    
    elif menu == "👤 Admin Account":
        st.title("Admin Account Management")
        
        with open(ADMIN_CONFIG_FILE, 'r') as f:
            current_admin_config = json.load(f)
        
        with st.form("admin_account"):
            st.subheader("Change Username and Password")
            
            current_username = st.text_input("Current Username", value=current_admin_config["username"], disabled=True)
            new_username = st.text_input("New Username", placeholder="Enter new username")
            
            st.divider()
            
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password", help="Leave empty if you don't want to change password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔄 Update Account"):
                # Verify current password
                if hash_password(current_password) != current_admin_config["password_hash"]:
                    st.error("❌ Current password is incorrect!")
                else:
                    updated = False
                    
                    # Update username if provided
                    if new_username and new_username != current_username:
                        current_admin_config["username"] = new_username
                        updated = True
                    
                    # Update password if provided
                    if new_password:
                        if new_password != confirm_password:
                            st.error("❌ New passwords don't match!")
                        elif len(new_password) < 6:
                            st.error("❌ Password must be at least 6 characters!")
                        else:
                            current_admin_config["password_hash"] = hash_password(new_password)
                            updated = True
                    
                    if updated:
                        save_data(ADMIN_CONFIG_FILE, current_admin_config)
                        st.success("✅ Account updated successfully!")
                        st.info("Please login again with new credentials.")
                        st.session_state.authenticated = False
                        st.session_state.current_user = None
                        st.rerun()
                    else:
                        st.warning("⚠️ No changes were made.")
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", type="primary"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.show_admin_login = False
        st.rerun()

# Student GPA Calculator Interface with Short URL Access
def student_calculator_interface(short_code=None):
    st.markdown(f"""
        <div class="main-header" style="text-align: center;">
         <img src="https://www.smiu.edu.pk/themes/smiu/images/13254460_710745915734761_8157428650049174152_n.png" width="200">
            <h1>SMIU GPA & CGPA Calculator</h1>
            <p>Calculate your GPA and CGPA</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Show access code if provided
    if short_code:
        st.info(f"✅ This URL is valid.")
    
    # Tabs for student calculator
    tab1, tab2, tab3 = st.tabs(["📊 GPA Calculator", "📈 CGPA Calculator", "📋 Grading Scale"])
    
    # ============= GPA CALCULATOR =============
    with tab1:
        st.header("Semester GPA Calculator")
        
        # User name input
        st.subheader("👤 Student Information")
        user_name = st.text_input("Enter Your Name *", placeholder="e.g., M.Moiz", key='gpa_user_name')
        
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
            if not user_name:
                st.warning("⚠️ Please enter your name to continue")
            else:
                total_grade_points = 0
                total_credit_hours = 0
                course_results = []
                course_db_data = []
                
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
                        
                        course_db_data.append({
                            'course_name': course['course_name'],
                            'total_marks': float(course['total_marks']),
                            'obtained_marks': float(course['obtained_marks']),
                            'credit_hours': float(course['credit_hours']),
                            'percentage': float(percentage),
                            'grade': grade,
                            'gpa': float(gpa),
                            'grade_points': float(grade_points)
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
                    
                    # Save to JSON
                    gpa_record = {
                        'user_name': user_name,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'courses': course_db_data,
                        'final_gpa': float(final_gpa),
                        'total_credit_hours': float(total_credit_hours),
                        'total_grade_points': float(total_grade_points)
                    }
                    
                    # Load existing data and append new record
                    gpa_data = load_data(STUDENT_GPA_FILE)
                    gpa_data.append(gpa_record)
                    save_data(STUDENT_GPA_FILE, gpa_data)
                    
                    st.info("❤ Thank You! For using the SMIU Semester GPA Calculator.")
                    
                    # Export options
                    st.subheader("📥 Download Report")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Export to Excel for student
                        export_data = {
                            'courses': course_results,
                            'summary': {
                                'gpa': final_gpa,
                                'total_credit_hours': total_credit_hours,
                                'total_grade_points': total_grade_points,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        }
                        excel_file = export_to_excel(export_data, 'GPA', user_name)
                        
                        st.download_button(
                            label="📊 Download Excel Report",
                            data=excel_file,
                            file_name=f"GPA_Report_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # Export to CSV for student
                        summary_csv, courses_csv = export_to_csv(export_data, 'GPA', user_name)
                        
                        st.markdown("**CSV Reports:**")
                        
                        if summary_csv:
                            st.download_button(
                                label="📄 Download Summary CSV",
                                data=summary_csv,
                                file_name=f"GPA_Summary_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                        if courses_csv:
                            st.download_button(
                                label="📄 Download Course Details CSV",
                                data=courses_csv,
                                file_name=f"GPA_Courses_{user_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
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
                semester_gpa = st.number_input(f"Total semester Grade Points", 
                                              min_value=0.0, 
                                              value=0.0,
                                              step=0.01,
                                              key=f'sem_gpa_{i}')
            with col2:
                semester_credits = st.number_input(f"Total Semester Credit Hours", 
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
            if not user_name_cgpa:
                st.warning("⚠️ Please enter your name to continue")
            else:
                total_grade_points = 0
                total_credit_hours = 0
                semester_results = []
                semester_db_data = []
                
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
                        
                        semester_db_data.append({
                            'semester_number': i + 1,
                            'semester_gpa': float(semester['gpa']),
                            'credit_hours': float(semester['credit_hours']),
                            'grade_points': float(grade_points)
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
                    
                    # Save to JSON
                    cgpa_record = {
                        'user_name': user_name_cgpa,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'semesters': semester_db_data,
                        'final_cgpa': float(final_cgpa),
                        'total_credit_hours': float(total_credit_hours),
                        'total_grade_points': float(total_grade_points)
                    }
                    
                    # Load existing data and append new record
                    cgpa_data = load_data(STUDENT_CGPA_FILE)
                    cgpa_data.append(cgpa_record)
                    save_data(STUDENT_CGPA_FILE, cgpa_data)
                    
                    st.info("❤ Thank You! For using the SMIU CGPA Calculator.")
                    
                    # Export options
                    st.subheader("📥 Download Report")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Export to Excel for student
                        export_data = {
                            'semesters': semester_results,
                            'summary': {
                                'cgpa': final_cgpa,
                                'total_credit_hours': total_credit_hours,
                                'total_grade_points': total_grade_points,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                        }
                        excel_file = export_to_excel(export_data, 'CGPA', user_name_cgpa)
                        
                        st.download_button(
                            label="📊 Download Excel Report",
                            data=excel_file,
                            file_name=f"CGPA_Report_{user_name_cgpa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # Export to CSV for student
                        summary_csv, semesters_csv = export_to_csv(export_data, 'CGPA', user_name_cgpa)
                        
                        st.markdown("**CSV Reports:**")
                        
                        if summary_csv:
                            st.download_button(
                                label="📄 Download Summary CSV",
                                data=summary_csv,
                                file_name=f"CGPA_Summary_{user_name_cgpa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                        if semesters_csv:
                            st.download_button(
                                label="📄 Download Semester Details CSV",
                                data=semesters_csv,
                                file_name=f"CGPA_Semesters_{user_name_cgpa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
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
    st.markdown(f"""
        <div style='text-align: center; color: #666;'>
            <p>Made By Muhammad Moiz | SMIU GPA & CGPA Management System</p>
        </div>
    """, unsafe_allow_html=True)

# Handle student access
def handle_student_access(student_code):
    """Handle student access with short code"""
    # Load URL data to check if code is valid
    with open(URL_SHORTENER_FILE, 'r') as f:
        url_data = json.load(f)
    
    short_codes = url_data.get("short_codes", {})
    
    if student_code in short_codes:
        if short_codes[student_code].get("status") == "active":
            student_calculator_interface(student_code)
        else:
            show_deactivated_message()
    else:
        st.error("❌ Invalid or expired student URL!")
        st.info("Please contact admin for a valid access URL.")
        
        # Show admin login button
        if st.button("🔐 Admin Login", key="invalid_url_admin_login"):
            st.session_state.show_admin_login = True
            st.rerun()

# Main App Logic
def main():
    # Check for student code in query parameters
    query_params = st.query_params
    
    # Get student code from query params
    student_code = None
    if 'student' in query_params:
        student_code = query_params['student']
    elif 'access_code' in query_params:  # For backward compatibility
        student_code = query_params['access_code']
    
    # MAIN DECISION TREE:
    # 1. Admin authenticated hai?
    if st.session_state.authenticated:
        admin_panel()
        return
    
    # 2. Admin login dikhana hai? (either from button or direct access)
    if st.session_state.get('show_admin_login', False) or not student_code:
        admin_login()
        return
    
    # 3. Student code hai?
    if student_code:
        handle_student_access(student_code)
        return

if __name__ == "__main__":
    main()
