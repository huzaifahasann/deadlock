"""
NagrikResolve - Citizen Complaint Management System
A Streamlit application for registering and tracking citizen complaints.
Built for a hackathon - 150 minutes total development time.

Features:
- Citizen complaint registration
- Complaint categories
- Description and filing date
- Photo upload
- SQLite database
- Automatic days-waited calculation
- Illustrative escalation authority suggestions (clearly labeled as illustrative)
- Editable complaint letter
- Editable RTI draft
- Downloadable TXT documents
- Complaint status timeline
- Clearly labelled sample data
"""

import streamlit as st
import sqlite3
import os
from datetime import datetime, date
from pathlib import Path
import base64

# ============================================
# CONFIGURATION & CONSTANTS
# ============================================

DB_PATH = "complaints.db"
UPLOAD_DIR = "uploads"

# Complaint categories
CATEGORIES = [
    "Road & Infrastructure",
    "Water Supply",
    "Electricity",
    "Sanitation & Waste",
    "Public Health",
    "Traffic & Transport",
    "Building & Construction",
    "Environment & Pollution",
    "Other"
]

# Status options
STATUSES = [
    "Submitted",
    "Under Review",
    "In Progress",
    "Resolved",
    "Closed"
]

# Illustrative escalation authorities (clearly labeled as sample/illustrative)
ESCALATION_AUTHORITIES = {
    "Road & Infrastructure": [
        ("Municipal Corporation - Roads Department", "Illustrative: Local ward office"),
        ("Public Works Department (PWD)", "Illustrative: District level"),
        ("National Highways Authority (NHAI)", "Illustrative: For national highways")
    ],
    "Water Supply": [
        ("Municipal Corporation - Water Department", "Illustrative: Local ward office"),
        ("Jal Board / Water Supply Board", "Illustrative: City/State level"),
        ("District Collector Office", "Illustrative: For escalation")
    ],
    "Electricity": [
        ("Electricity Distribution Company", "Illustrative: Local circle office"),
        ("State Electricity Regulatory Commission", "Illustrative: For tariff/quality issues"),
        ("Consumer Grievance Redressal Forum", "Illustrative: For consumer disputes")
    ],
    "Sanitation & Waste": [
        ("Municipal Corporation - Sanitation Dept", "Illustrative: Local ward office"),
        ("District Health Office", "Illustrative: For public health concerns"),
        ("State Pollution Control Board", "Illustrative: For environmental violations")
    ],
    "Public Health": [
        ("Primary Health Centre / CHC", "Illustrative: Local health facility"),
        ("District Medical Officer", "Illustrative: District level"),
        ("State Health Department", "Illustrative: State level escalation")
    ],
    "Traffic & Transport": [
        ("Traffic Police Department", "Illustrative: Local traffic division"),
        ("Regional Transport Office (RTO)", "Illustrative: For vehicle/license issues"),
        ("Municipal Corporation - Transport Dept", "Illustrative: For public transport")
    ],
    "Building & Construction": [
        ("Municipal Corporation - Building Dept", "Illustrative: Local ward office"),
        ("Town Planning Department", "Illustrative: For planning violations"),
        ("Development Authority", "Illustrative: For unauthorized construction")
    ],
    "Environment & Pollution": [
        ("State Pollution Control Board", "Illustrative: Regional office"),
        ("National Green Tribunal (NGT)", "Illustrative: For environmental cases"),
        ("District Collector Office", "Illustrative: For immediate action")
    ],
    "Other": [
        ("Municipal Corporation - General", "Illustrative: Local ward office"),
        ("District Collector / DM Office", "Illustrative: District level"),
        ("State Public Grievance Portal", "Illustrative: Online portal")
    ]
}

# ============================================
# DATABASE SETUP
# ============================================

def init_db():
    """Initialize SQLite database with complaints table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_name TEXT NOT NULL,
            citizen_phone TEXT,
            citizen_email TEXT,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            filing_date DATE NOT NULL,
            photo_path TEXT,
            status TEXT DEFAULT 'Submitted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def insert_sample_data():
    """Insert clearly labeled sample data if database is empty."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_complaints = [
            ("SAMPLE - Rajesh Kumar", "9876543210", "rajesh.sample@email.com",
             "Road & Infrastructure",
             "SAMPLE DATA: Large pothole on Main Street near bus stop causing accidents. "
             "Reported multiple times but no action taken. Water accumulates during rain.",
             "2024-10-15", None, "Under Review"),
            ("SAMPLE - Priya Sharma", "9876543211", "priya.sample@email.com",
             "Water Supply",
             "SAMPLE DATA: No water supply in Sector 7 for 5 days. Tanker not arriving on schedule. "
             "Residents forced to buy water at high prices.",
             "2024-10-20", None, "In Progress"),
            ("SAMPLE - Amit Patel", "9876543212", "amit.sample@email.com",
             "Sanitation & Waste",
             "SAMPLE DATA: Garbage not collected for 2 weeks in Block C. Overflowing bins, "
             "stray animals, foul smell. Health hazard for children and elderly.",
             "2024-10-25", None, "Submitted"),
            ("SAMPLE - Sunita Devi", "9876543213", "sunita.sample@email.com",
             "Electricity",
             "SAMPLE DATA: Frequent power cuts (6-8 hours daily) in Village Rampur. "
             "Transformer damaged since last storm. No response from electricity board.",
             "2024-10-28", None, "Under Review"),
            ("SAMPLE - Mohan Lal", "9876543214", "mohan.sample@email.com",
             "Public Health",
             "SAMPLE DATA: Dengue cases rising in Colony XYZ. No fogging done. "
             "Standing water in vacant plots. Request urgent vector control.",
             "2024-11-01", None, "Submitted"),
        ]
        cursor.executemany("""
            INSERT INTO complaints (citizen_name, citizen_phone, citizen_email, category,
                                   description, filing_date, photo_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_complaints)
        conn.commit()
    conn.close()


def get_all_complaints():
    """Fetch all complaints from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints ORDER BY filing_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_complaint_by_id(complaint_id):
    """Fetch a single complaint by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def add_complaint(citizen_name, citizen_phone, citizen_email, category,
                  description, filing_date, photo_path):
    """Add a new complaint to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (citizen_name, citizen_phone, citizen_email, category,
                               description, filing_date, photo_path, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Submitted')
    """, (citizen_name, citizen_phone, citizen_email, category,
          description, filing_date, photo_path))
    conn.commit()
    complaint_id = cursor.lastrowid
    conn.close()
    return complaint_id


def update_complaint_status(complaint_id, new_status):
    """Update complaint status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE complaints SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, complaint_id))
    conn.commit()
    conn.close()


# ============================================
# UTILITY FUNCTIONS
# ============================================

def calculate_days_waited(filing_date_str):
    """Calculate days waited from filing date to today."""
    try:
        filing_date = datetime.strptime(filing_date_str, "%Y-%m-%d").date()
        today = date.today()
        delta = today - filing_date
        return delta.days
    except:
        return 0


def save_uploaded_photo(uploaded_file, complaint_id):
    """Save uploaded photo to uploads directory."""
    if uploaded_file is None:
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_ext = Path(uploaded_file.name).suffix
    filename = f"complaint_{complaint_id}{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return filepath


def generate_complaint_letter(complaint):
    """Generate editable complaint letter."""
    days_waited = calculate_days_waited(complaint['filing_date'])
    authorities = ESCALATION_AUTHORITIES.get(complaint['category'], ESCALATION_AUTHORITIES['Other'])

    letter = f"""COMPLAINT LETTER
{'='*60}

Date: {datetime.now().strftime('%d %B %Y')}

To,
{authorities[0][0]}
{authorities[0][1]}

Subject: Complaint regarding {complaint['category']} - Reference No: {complaint['id']}

Respected Sir/Madam,

I, {complaint['citizen_name']}, resident of [Your Address], wish to bring to your
kind attention the following issue:

COMPLAINT DETAILS:
------------------
Category: {complaint['category']}
Description: {complaint['description']}
Date of Filing: {complaint['filing_date']}
Days Waited: {days_waited} days
Current Status: {complaint['status']}

This matter has been pending for {days_waited} days since my initial complaint
was filed on {complaint['filing_date']}. Despite repeated follow-ups, no
satisfactory action has been taken.

I request you to kindly look into this matter urgently and take appropriate
action to resolve the issue at the earliest.

CONTACT DETAILS:
----------------
Name: {complaint['citizen_name']}
Phone: {complaint['citizen_phone'] or 'Not provided'}
Email: {complaint['citizen_email'] or 'Not provided'}

Yours faithfully,

{complaint['citizen_name']}
Date: {datetime.now().strftime('%d %B %Y')}

---
NOTE: This is an auto-generated draft. Please review and edit before submission.
Escalation authorities listed are ILLUSTRATIVE ONLY - verify actual jurisdiction
before submitting to any authority.
"""
    return letter


def generate_rti_draft(complaint):
    """Generate editable RTI application draft."""
    days_waited = calculate_days_waited(complaint['filing_date'])

    rti = f"""RTI APPLICATION (Right to Information Act, 2005)
{'='*60}

Date: {datetime.now().strftime('%d %B %Y')}

To,
The Public Information Officer (PIO)
[Relevant Department - Verify jurisdiction before submitting]

Subject: Application under Section 6(1) of RTI Act, 2005 for information
         regarding Complaint Reference No: {complaint['id']}

Respected Sir/Madam,

I, {complaint['citizen_name']}, hereby request the following information under
the Right to Information Act, 2005:

INFORMATION REQUESTED:
----------------------
1. Status and action taken on my complaint dated {complaint['filing_date']}
   regarding {complaint['category']} (Reference No: {complaint['id']}).

2. Details of officers responsible for handling this complaint and their
   designated timelines for resolution.

3. Copy of all correspondence, notes, and orders related to this complaint.

4. Reason for delay in resolution (complaint pending for {days_waited} days).

5. Expected date of resolution as per citizen charter / service level agreement.

6. Details of any disciplinary action initiated against officers for delay.

APPLICANT DETAILS:
------------------
Name: {complaint['citizen_name']}
Address: [Your Complete Address]
Phone: {complaint['citizen_phone'] or 'Not provided'}
Email: {complaint['citizen_email'] or 'Not provided'}

I am a citizen of India. I am enclosing the application fee of Rs. 10
(via Indian Postal Order / Court Fee Stamp / Online payment - as applicable).

Please provide the information within 30 days as mandated under Section 7(1)
of the RTI Act, 2005.

Yours faithfully,

{complaint['citizen_name']}
Date: {datetime.now().strftime('%d %B %Y')}

---
NOTE: This is an auto-generated draft. Please verify the correct PIO/Department
before submission. Fees and process may vary by state/department.
"""
    return rti


def create_download_link(text_content, filename, label):
    """Create a download link for text content."""
    b64 = base64.b64encode(text_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{label}</a>'
    return href


# ============================================
# STREAMLIT APP
# ============================================

def main():
    st.set_page_config(
        page_title="NagrikResolve - Citizen Complaint System",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize database
    init_db()
    insert_sample_data()

    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
        .sample-badge {
            background: #fef3c7;
            color: #92400e;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .illustrative-badge {
            background: #fce7f3;
            color: #be185d;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .status-submitted { background: #dbeafe; color: #1e40af; }
        .status-review { background: #fef3c7; color: #92400e; }
        .status-progress { background: #e0e7ff; color: #3730a3; }
        .status-resolved { background: #dcfce7; color: #166534; }
        .status-closed { background: #f3f4f6; color: #374151; }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0;">📋 NagrikResolve</h1>
            <p style="margin: 0.5rem 0 0 0;">Citizen Complaint Registration & Tracking System</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; opacity: 0.9;">
                Built for Hackathon | All escalation authorities are ILLUSTRATIVE ONLY
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "📝 Register Complaint",
        "📋 View Complaints",
        "📊 Dashboard",
        "ℹ️ About"
    ])

    if page == "📝 Register Complaint":
        register_complaint_page()
    elif page == "📋 View Complaints":
        view_complaints_page()
    elif page == "📊 Dashboard":
        dashboard_page()
    elif page == "ℹ️ About":
        about_page()


def register_complaint_page():
    st.header("📝 Register New Complaint")
    st.markdown("*All fields marked with * are required*")

    with st.form("complaint_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            citizen_name = st.text_input("Citizen Name *", placeholder="Enter your full name")
            citizen_phone = st.text_input("Phone Number", placeholder="+91-XXXXXXXXXX")
            citizen_email = st.text_input("Email Address", placeholder="email@example.com")

        with col2:
            category = st.selectbox("Complaint Category *", CATEGORIES)
            filing_date = st.date_input("Filing Date *", value=date.today(), max_value=date.today())

        description = st.text_area(
            "Complaint Description *",
            placeholder="Describe the issue in detail...",
            height=150
        )

        photo = st.file_uploader(
            "Upload Photo (Optional)",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a photo of the issue (max 10MB)"
        )

        submitted = st.form_submit_button("Submit Complaint", type="primary", use_container_width=True)

        if submitted:
            if not citizen_name or not category or not description:
                st.error("Please fill all required fields (marked with *)")
            else:
                # Save photo first to get complaint_id
                # We need to insert first, then save photo with the ID
                photo_path = None
                complaint_id = add_complaint(
                    citizen_name, citizen_phone, citizen_email,
                    category, description, filing_date.strftime("%Y-%m-%d"), photo_path
                )

                # Now save photo with the complaint_id
                if photo:
                    photo_path = save_uploaded_photo(photo, complaint_id)
                    # Update database with photo path
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE complaints SET photo_path = ? WHERE id = ?",
                                 (photo_path, complaint_id))
                    conn.commit()
                    conn.close()

                st.success(f"✅ Complaint registered successfully! Reference ID: **#{complaint_id}**")
                st.balloons()

                # Show next steps
                st.info("""
                **Next Steps:**
                1. Save your Reference ID: `#{0}`
                2. Go to "View Complaints" to track status
                3. Generate complaint letter or RTI draft from the complaint details
                """.format(complaint_id))


def view_complaints_page():
    st.header("📋 All Complaints")

    complaints = get_all_complaints()

    if not complaints:
        st.info("No complaints registered yet. Go to 'Register Complaint' to add one.")
        return

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All"] + STATUSES)
    with col3:
        show_samples_only = st.checkbox("Show only SAMPLE data", value=False)

    # Apply filters
    filtered = complaints
    if filter_category != "All":
        filtered = [c for c in filtered if c['category'] == filter_category]
    if filter_status != "All":
        filtered = [c for c in filtered if c['status'] == filter_status]
    if show_samples_only:
        filtered = [c for c in filtered if c['citizen_name'].startswith("SAMPLE")]

    st.markdown(f"**Showing {len(filtered)} of {len(complaints)} complaints**")

    # Display complaints
    for complaint in filtered:
        days_waited = calculate_days_waited(complaint['filing_date'])
        is_sample = complaint['citizen_name'].startswith("SAMPLE")

        with st.expander(
            f"#{complaint['id']} | {complaint['category']} | {complaint['status']} | "
            f"{complaint['filing_date']} ({days_waited} days) "
            f"{'🏷️ SAMPLE' if is_sample else ''}",
            expanded=False
        ):
            # Complaint details
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Citizen:** {complaint['citizen_name']}")
                if is_sample:
                    st.markdown('<span class="sample-badge">SAMPLE DATA</span>', unsafe_allow_html=True)
                st.markdown(f"**Phone:** {complaint['citizen_phone'] or 'Not provided'}")
                st.markdown(f"**Email:** {complaint['citizen_email'] or 'Not provided'}")
                st.markdown(f"**Category:** {complaint['category']}")
                st.markdown(f"**Filing Date:** {complaint['filing_date']}")
                st.markdown(f"**Days Waited:** **{days_waited} days**")
                st.markdown(f"**Description:** {complaint['description']}")

                if complaint['photo_path'] and os.path.exists(complaint['photo_path']):
                    st.image(complaint['photo_path'], caption="Uploaded Photo", width=300)

            with col2:
                # Status badge
                status_class = {
                    "Submitted": "status-submitted",
                    "Under Review": "status-review",
                    "In Progress": "status-progress",
                    "Resolved": "status-resolved",
                    "Closed": "status-closed"
                }.get(complaint['status'], "status-submitted")

                st.markdown(f"""
                    <div style="text-align: center; padding: 1rem;">
                        <span class="status-badge {status_class}">{complaint['status']}</span>
                    </div>
                """, unsafe_allow_html=True)

                # Status update
                new_status = st.selectbox(
                    "Update Status",
                    STATUSES,
                    index=STATUSES.index(complaint['status']),
                    key=f"status_{complaint['id']}"
                )
                if st.button("Update", key=f"update_{complaint['id']}"):
                    update_complaint_status(complaint['id'], new_status)
                    st.success(f"Status updated to {new_status}")
                    st.rerun()

                st.markdown("---")

                # Download buttons
                letter = generate_complaint_letter(complaint)
                rti = generate_rti_draft(complaint)

                st.markdown(create_download_link(
                    letter, f"complaint_letter_{complaint['id']}.txt",
                    "📄 Download Complaint Letter"
                ), unsafe_allow_html=True)

                st.markdown(create_download_link(
                    rti, f"rti_draft_{complaint['id']}.txt",
                    "📋 Download RTI Draft"
                ), unsafe_allow_html=True)

                # Editable previews
                with st.expander("✏️ Edit Complaint Letter"):
                    edited_letter = st.text_area("Edit letter", letter, height=300, key=f"letter_{complaint['id']}")
                    st.markdown(create_download_link(
                        edited_letter, f"complaint_letter_{complaint['id']}_edited.txt",
                        "💾 Download Edited Letter"
                    ), unsafe_allow_html=True)

                with st.expander("✏️ Edit RTI Draft"):
                    edited_rti = st.text_area("Edit RTI", rti, height=300, key=f"rti_{complaint['id']}")
                    st.markdown(create_download_link(
                        edited_rti, f"rti_draft_{complaint['id']}_edited.txt",
                        "💾 Download Edited RTI"
                    ), unsafe_allow_html=True)

            # Timeline
            st.markdown("### 📅 Status Timeline")
            timeline_events = [
                {"date": complaint['filing_date'], "event": "Complaint Submitted", "status": "Submitted"},
            ]
            if complaint['status'] != "Submitted":
                timeline_events.append({"date": complaint.get('updated_at', complaint['filing_date'])[:10] if complaint['updated_at'] else complaint['filing_date'],
                                       "event": f"Status: {complaint['status']}", "status": complaint['status']})

            for i, event in enumerate(timeline_events):
                col_a, col_b = st.columns([1, 4])
                with col_a:
                    st.markdown(f"**{event['date']}**")
                with col_b:
                    st.markdown(f"{event['event']}")
                if i < len(timeline_events) - 1:
                    st.markdown("<div style='border-left: 2px solid #3b82f6; height: 20px; margin-left: 10px;'></div>", unsafe_allow_html=True)

            # Illustrative escalation authorities
            st.markdown("### ⚠️ Illustrative Escalation Authorities")
            st.markdown('<span class="illustrative-badge">ILLUSTRATIVE ONLY - Verify actual jurisdiction</span>', unsafe_allow_html=True)
            authorities = ESCALATION_AUTHORITIES.get(complaint['category'], ESCALATION_AUTHORITIES['Other'])
            for auth, note in authorities:
                st.markdown(f"- **{auth}** — *{note}*")


def dashboard_page():
    st.header("📊 Dashboard")

    complaints = get_all_complaints()

    if not complaints:
        st.info("No data available. Register complaints to see dashboard.")
        return

    # Metrics
    total = len(complaints)
    sample_count = len([c for c in complaints if c['citizen_name'].startswith("SAMPLE")])
    real_count = total - sample_count
    avg_days = sum(calculate_days_waited(c['filing_date']) for c in complaints) / total if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Complaints", total)
    with col2:
        st.metric("Sample Data", sample_count)
    with col3:
        st.metric("Real Complaints", real_count)
    with col4:
        st.metric("Avg Days Waiting", f"{avg_days:.1f}")

    # Category distribution
    st.subheader("Complaints by Category")
    cat_counts = {}
    for c in complaints:
        cat_counts[c['category']] = cat_counts.get(c['category'], 0) + 1

    cat_cols = st.columns(len(cat_counts) if cat_counts else 1)
    for i, (cat, count) in enumerate(sorted(cat_counts.items(), key=lambda x: -x[1])):
        with cat_cols[i % len(cat_cols)]:
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0;">{cat}</h4>
                    <h2 style="margin: 0.5rem 0; color: #3b82f6;">{count}</h2>
                </div>
            """, unsafe_allow_html=True)

    # Status distribution
    st.subheader("Complaints by Status")
    status_counts = {}
    for c in complaints:
        status_counts[c['status']] = status_counts.get(c['status'], 0) + 1

    status_cols = st.columns(len(status_counts) if status_counts else 1)
    status_colors = {
        "Submitted": "#3b82f6", "Under Review": "#f59e0b",
        "In Progress": "#6366f1", "Resolved": "#22c55e", "Closed": "#9ca3af"
    }
    for i, (status, count) in enumerate(sorted(status_counts.items(), key=lambda x: -x[1])):
        with status_cols[i % len(status_cols)]:
            color = status_colors.get(status, "#3b82f6")
            st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0; color: {color};">{status}</h4>
                    <h2 style="margin: 0.5rem 0;">{count}</h2>
                </div>
            """, unsafe_allow_html=True)

    # Longest waiting
    st.subheader("⏳ Longest Waiting Complaints")
    sorted_complaints = sorted(complaints, key=lambda c: calculate_days_waited(c['filing_date']), reverse=True)
    for c in sorted_complaints[:5]:
        days = calculate_days_waited(c['filing_date'])
        is_sample = " 🏷️ SAMPLE" if c['citizen_name'].startswith("SAMPLE") else ""
        st.markdown(f"- **#{c['id']}** | {c['category']} | {c['status']} | **{days} days**{is_sample}")


def about_page():
    st.header("ℹ️ About NagrikResolve")

    st.markdown("""
    ### Project Overview
    **NagrikResolve** is a citizen complaint management system built for a hackathon.
    It allows citizens to register complaints, track their status, and generate
    official documents for escalation.

    ### Features Implemented
    - ✅ Citizen complaint registration with categories
    - ✅ Description and filing date tracking
    - ✅ Photo upload support
    - ✅ SQLite database for persistence
    - ✅ Automatic days-waited calculation
    - ✅ **Illustrative** escalation authority suggestions (clearly labeled)
    - ✅ Editable complaint letter generation
    - ✅ Editable RTI (Right to Information) draft generation
    - ✅ Downloadable TXT documents
    - ✅ Complaint status timeline
    - ✅ Clearly labelled sample data

    ### Important Disclaimers
    ⚠️ **All escalation authorities listed are ILLUSTRATIVE ONLY** - They are sample
    suggestions for demonstration purposes. Citizens must verify the actual
    jurisdictional authority for their specific location and issue before submitting
    any official correspondence.

    📋 **Sample Data** - The system includes clearly labelled sample complaints
    (prefixed with "SAMPLE -") for demonstration. These are not real complaints.

    🏛️ **No Real Submissions** - This application does not submit complaints to any
    real government systems. It generates draft documents for citizens to review,
    edit, and submit through appropriate official channels.

    ### Technical Stack
    - **Frontend:** Streamlit
    - **Database:** SQLite
    - **Language:** Python 3.9+
    - **Dependencies:** streamlit only (minimal requirements)

    ### Hackathon Info
    - **Development Time:** 150 minutes total
    - **Single File:** All logic in `app.py`
    - **No Paid APIs:** Completely free and open source

    ---
    *Built with ❤️ for the hackathon*
    """)


if __name__ == "__main__":
    main()


