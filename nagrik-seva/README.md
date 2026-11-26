# NagrikResolve 📋

**Citizen Complaint Registration & Tracking System**

Built for a hackathon in 150 minutes. A Streamlit application for citizens to register complaints, track status, and generate official documents.

## Features

- ✅ **Citizen Complaint Registration** - Name, phone, email, category, description, filing date
- ✅ **Complaint Categories** - 9 predefined categories (Roads, Water, Electricity, Sanitation, Health, Traffic, Building, Environment, Other)
- ✅ **Photo Upload** - Optional photo evidence
- ✅ **SQLite Database** - Lightweight, file-based persistence
- ✅ **Automatic Days-Waited Calculation** - Tracks how long each complaint has been pending
- ✅ **Illustrative Escalation Authorities** - Sample authority suggestions (clearly labeled as illustrative)
- ✅ **Editable Complaint Letter** - Auto-generated, editable, downloadable as TXT
- ✅ **Editable RTI Draft** - Right to Information application draft, editable, downloadable as TXT
- ✅ **Complaint Status Timeline** - Visual timeline of status changes
- ✅ **Sample Data** - Clearly labelled demo complaints for testing
- ✅ **Dashboard** - Statistics and metrics overview

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone or navigate to project
cd nagrik-resolve

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
nagrik-resolve/
├── app.py              # Main application (single file)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
├── complaints.db       # SQLite database (created on first run)
└── uploads/            # Uploaded photos (created on first upload)
```

## Usage

### 1. Register Complaint
- Fill in citizen details (name required, phone/email optional)
- Select category from dropdown
- Enter description and filing date
- Optionally upload a photo
- Submit to get a Reference ID

### 2. View Complaints
- See all complaints in expandable cards
- Filter by category, status, or show only sample data
- Update complaint status
- View/uploaded photos
- Generate and download complaint letters
- Generate and download RTI drafts
- View status timeline
- See illustrative escalation authorities

### 3. Dashboard
- View total complaints, sample vs real counts
- Average days waiting metric
- Category distribution
- Status distribution
- Top 5 longest-waiting complaints

## Important Notes

### ⚠️ Illustrative Authorities Only
All escalation authorities shown are **ILLUSTRATIVE SAMPLES ONLY**. They are labeled with "Illustrative:" prefix. Citizens must verify the actual jurisdictional authority for their specific location and issue before submitting any official correspondence.

### 🏷️ Sample Data
The system includes 5 sample complaints (prefixed with "SAMPLE -") for demonstration. These are clearly marked with a yellow "SAMPLE DATA" badge.

### 🚫 No Real Submissions
This application does **not** submit complaints to any real government systems. It generates draft documents for citizens to review, edit, and submit through appropriate official channels.

## Technology Stack

- **Frontend:** Streamlit
- **Database:** SQLite (built into Python)
- **Language:** Python 3.9+
- **Dependencies:** Minimal - only `streamlit`

## Hackathon Constraints Met

- ✅ 150 minutes total development time
- ✅ Single `app.py` file
- ✅ No paid APIs
- ✅ No real government submissions
- ✅ Clearly labeled illustrative escalation rules
- ✅ Simple Python code
- ✅ All required features implemented

## License

MIT License - Built for hackathon demonstration purposes.