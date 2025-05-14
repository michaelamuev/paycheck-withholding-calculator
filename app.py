import random
import streamlit as st
from decimal import Decimal, getcontext, ROUND_HALF_UP
from states import get_calculator, STATE_CALCULATORS
import time
from datetime import datetime
import json
import os
import hashlib
import uuid
import re

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="2024 Withholding (Pub 15-T)",
    page_icon="💸",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        /* Main container styling */
        .main {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Header styling */
        h1 {
            color: #1E88E5;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.5rem !important;
            text-align: center;
            padding: 1rem;
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Tip of the day styling */
        .stInfo {
            background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%) !important;
            padding: 1rem !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* Warning/disclaimer styling */
        .stWarning {
            background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%) !important;
            padding: 1rem !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #F5F5F5 0%, #E0E0E0 100%);
            padding: 2rem 1rem;
        }
        
        /* Input fields styling */
        .stTextInput > div > div {
            background: white;
            border-radius: 8px;
            border: 2px solid #E0E0E0;
            padding: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div:focus-within {
            border-color: #1E88E5;
            box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #1E88E5 0%, #1976D2 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Metric containers styling */
        [data-testid="stMetricValue"] {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: #1E88E5;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 100%);
            border-radius: 8px;
            padding: 1rem !important;
            font-weight: 600;
        }
        
        /* Select box styling */
        .stSelectbox > div > div {
            background: white;
            border-radius: 8px;
            border: 2px solid #E0E0E0;
        }
        
        /* Radio buttons styling */
        .stRadio > div {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Checkbox styling */
        .stCheckbox > div > label > div {
            background: white;
            padding: 0.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

IRS_TRIVIA = [
    "Did you know? The new 2024 W-4 no longer uses withholding allowances — you enter dollar amounts instead.",
    "Tip: If you have more than one job, checking Step 2 can prevent underwithholding later in the year.",
    "Fun fact: Publication 15-T was first introduced in 2005, but percentage-method tables go back much further!",
    "Remember: Your standard deduction (for 2024) is $14,600 if single, $29,200 if married filing jointly.",
    "Heads up: Any extra withholding you enter in Step 4(c) applies every pay period, so small amounts add up fast.",
    "IRS trivia: Form W-4P is for pensions and annuities, not your regular paycheck — don't mix them up!",
]

# ─── ANALYTICS SETUP ─────────────────────────────────────────────────────────────
# Google Analytics 4 Measurement ID
GA_TRACKING_ID = "G-68KQ82NWCK"  # User's GA4 tracking ID

# Admin password hash - Replace with your own hashed password
ADMIN_PASSWORD_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"  # Password: admin123

def display_analytics_dashboard():
    """Display enhanced analytics dashboard"""
    st.markdown("### Analytics Dashboard")
    
    # Display current session stats
    st.subheader("Current Session")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Page Views", st.session_state.page_views)
    with col2:
        st.metric("Session Duration", f"{(time.time() - st.session_state.session_start) / 60:.1f} min")
    with col3:
        st.metric("Features Used", len(st.session_state.features_used))
        
    # Show features used
    if st.session_state.features_used:
        st.markdown("**Features Used This Session:**")
        for feature in sorted(st.session_state.features_used):
            st.markdown(f"- {feature}")
    
    # Enhanced Traffic Analysis
    st.subheader("Traffic Analysis")
    try:
        analytics_file = ".private/analytics_data.json"
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r') as f:
                analytics_data = json.load(f)
            
            # Group by session_id for more accurate metrics
            sessions = {}
            for entry in analytics_data:
                # Handle legacy entries without session_id
                session_id = entry.get('session_id', entry.get('timestamp', 'unknown'))
                
                # Skip entries without required fields
                if not all(key in entry for key in ['timestamp', 'utm_source']):
                    continue
                    
                if session_id not in sessions:
                    sessions[session_id] = entry
                elif entry.get('session_duration', 0) > sessions[session_id].get('session_duration', 0):
                    # Keep the entry with the longest duration for each session
                    sessions[session_id] = entry
            
            # Use session data for metrics
            session_data = list(sessions.values())
            
            if not session_data:
                st.info("No analytics data available yet.")
                return
            
            # Aggregate metrics
            total_sessions = len(sessions)
            total_pageviews = sum(entry.get('total_session_pageviews', 1) for entry in session_data)
            unique_features = set()
            feature_counts = {}
            utm_sources = {}
            utm_mediums = {}
            utm_campaigns = {}
            
            for entry in session_data:
                # UTM tracking (with defaults)
                source = entry.get('utm_source', 'direct')
                medium = entry.get('utm_medium', 'none')
                campaign = entry.get('utm_campaign', 'none')
                
                utm_sources[source] = utm_sources.get(source, 0) + 1
                utm_mediums[medium] = utm_mediums.get(medium, 0) + 1
                utm_campaigns[campaign] = utm_campaigns.get(campaign, 0) + 1
                
                # Feature tracking
                for feature in entry.get('features_used', []):
                    unique_features.add(feature)
                    feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
            # Display overall stats
            st.markdown("#### Overall Statistics")
            stats_cols = st.columns(4)
            with stats_cols[0]:
                st.metric("Total Sessions", total_sessions)
            with stats_cols[1]:
                st.metric("Total Pageviews", total_pageviews)
            with stats_cols[2]:
                st.metric("Unique Features Used", len(unique_features))
            with stats_cols[3]:
                # Calculate average session duration with error handling
                valid_durations = [float(entry.get('session_duration', 0)) for entry in session_data if entry.get('session_duration', 0) > 0]
                if valid_durations:
                    avg_session = sum(valid_durations) / len(valid_durations)
                    st.metric("Avg Session Duration", f"{avg_session/60:.1f} min")
                else:
                    st.metric("Avg Session Duration", "N/A")
            
            # Display feature popularity
            if feature_counts:
                st.markdown("#### Most Popular Features")
                for feature, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True):
                    st.text(f"{feature}: {count} uses")
            
            # Traffic sources in columns
            st.markdown("#### Traffic Sources")
            source_cols = st.columns(3)
            with source_cols[0]:
                st.markdown("**Top Sources**")
                for source, count in sorted(utm_sources.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.text(f"{source}: {count} sessions")
            with source_cols[1]:
                st.markdown("**Top Mediums**")
                for medium, count in sorted(utm_mediums.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.text(f"{medium}: {count} sessions")
            with source_cols[2]:
                st.markdown("**Top Campaigns**")
                for campaign, count in sorted(utm_campaigns.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.text(f"{campaign}: {count} sessions")
            
            # Show raw data option
            if st.checkbox("Show Raw Analytics Data"):
                st.json(session_data)  # Show deduplicated session data instead of raw data
                
    except Exception as e:
        st.error(f"Error loading analytics data: {str(e)}")
        st.exception(e)  # This will show the full traceback in development

def init_analytics():
    """Initialize analytics with improved visitor tracking"""
    if 'visitor_id' not in st.session_state:
        st.session_state.visitor_id = str(uuid.uuid4())
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'session_start' not in st.session_state:
        st.session_state.session_start = time.time()
    if 'page_views' not in st.session_state:
        st.session_state.page_views = 0
    if 'features_used' not in st.session_state:
        st.session_state.features_used = set()
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = time.time()
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

def verify_admin_password(password):
    """Verify admin password using secure hash"""
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH

def track_pageview(utm_params=None):
    """Track pageviews with UTM parameters and deduplication"""
    current_time = time.time()
    if current_time - getattr(st.session_state, 'last_track_time', 0) < 1:
        return
        
    st.session_state.last_track_time = current_time
    st.session_state.page_views += 1
    
    analytics_data = {
        'timestamp': datetime.now().isoformat(),
        'visitor_id': st.session_state.visitor_id,
        'session_id': st.session_state.session_id,
        'session_duration': current_time - st.session_state.session_start,
        'page_views': st.session_state.page_views,
        'features_used': list(st.session_state.features_used),
        'utm_source': utm_params.get('source', 'direct') if utm_params else 'direct',
        'utm_medium': utm_params.get('medium', 'none') if utm_params else 'none',
        'utm_campaign': utm_params.get('campaign', 'none') if utm_params else 'none'
    }
    
    if st.session_state.is_admin:
        save_analytics_data(analytics_data)

def track_feature_usage(feature_name: str):
    """Track feature usage with timestamps"""
    if feature_name not in st.session_state.features_used:
        st.session_state.features_used.add(feature_name)
        st.session_state.last_activity = time.time()
        track_pageview()  # Update analytics on new feature use

def save_analytics_data(data):
    """Save analytics data with deduplication"""
    try:
        analytics_file = ".private/analytics_data.json"
        os.makedirs(os.path.dirname(analytics_file), exist_ok=True)
        
        existing_data = []
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r') as f:
                existing_data = json.load(f)
        
        # Deduplicate based on session_id and timestamp
        if not any(
            entry.get('session_id') == data['session_id'] and
            entry.get('timestamp') == data['timestamp']
            for entry in existing_data
        ):
            existing_data.append(data)
            with open(analytics_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving analytics data: {str(e)}")

# Initialize analytics
init_analytics()

# Track pageview on app load
track_pageview()

# ─── Google Analytics 4 Tracking Code ─────────────────────────────────────────────
ga_script = f"""
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TRACKING_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_TRACKING_ID}');
</script>
"""

# Display tip of the day
tip = random.choice(IRS_TRIVIA)
st.info(f"💡 **Tip of the Day:** {tip}")

# Inject GA4 tracking code
st.markdown(ga_script, unsafe_allow_html=True)

# ─── Precision ─────────────────────────────────────────────────────────────────
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

# ─── CONSTANTS ─────────────────────────────────────────────────────────────────
STANDARD_DEDUCTION = {
    "single": Decimal("14600"),
    "married": Decimal("29200"),
    "head": Decimal("21900"),
}
FICA_CAP        = Decimal("168600")
SOCIAL_RATE     = Decimal("0.062")
MEDICARE_RATE   = Decimal("0.0145")
PERIODS = {
    "weekly":      Decimal("52"),
    "biweekly":    Decimal("26"),
    "semimonthly": Decimal("24"),
    "monthly":     Decimal("12"),
}

# Multiple Jobs Tax Brackets (annual ranges)
MULTIPLE_JOBS_RANGES = {
    "single": [
        {"range": (0, 14200), "adjustment": Decimal("0")},
        {"range": (14200, 34000), "adjustment": Decimal("1020")},
        {"range": (34000, 100000), "adjustment": Decimal("2040")},
        {"range": (100000, 200000), "adjustment": Decimal("3060")},
        {"range": (200000, float('inf')), "adjustment": Decimal("4080")}
    ],
    "married": [
        {"range": (0, 17000), "adjustment": Decimal("0")},
        {"range": (17000, 45000), "adjustment": Decimal("2040")},
        {"range": (45000, 120000), "adjustment": Decimal("4080")},
        {"range": (120000, 240000), "adjustment": Decimal("6120")},
        {"range": (240000, float('inf')), "adjustment": Decimal("8160")}
    ],
    "head": [
        {"range": (0, 14200), "adjustment": Decimal("0")},
        {"range": (14200, 34000), "adjustment": Decimal("1020")},
        {"range": (34000, 100000), "adjustment": Decimal("2040")},
        {"range": (100000, 200000), "adjustment": Decimal("3060")},
        {"range": (200000, float('inf')), "adjustment": Decimal("4080")}
    ]
}

def get_multiple_jobs_adjustment(annual_income: Decimal, filing_status: str) -> Decimal:
    """Calculate the multiple jobs adjustment based on IRS tables."""
    for bracket in MULTIPLE_JOBS_RANGES[filing_status]:
        if bracket["range"][0] <= float(annual_income) < bracket["range"][1]:
            return bracket["adjustment"]
    return Decimal("0")

# ─── PERCENTAGE-METHOD TABLES (Pub 15-T §1) ─────────────────────────────────────
PERCENTAGE_METHOD_TABLES = {
    "weekly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("76"),   "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("291"),  "base": Decimal("21.50"),  "rate": Decimal("0.12")},
            {"min": Decimal("933"),  "base": Decimal("104.26"), "rate": Decimal("0.22")},
            {"min": Decimal("1822"), "base": Decimal("326.26"), "rate": Decimal("0.24")},
            {"min": Decimal("3692"), "base": Decimal("788.50"), "rate": Decimal("0.32")},
            {"min": Decimal("4600"), "base": Decimal("1086.90"),"rate": Decimal("0.35")},
            {"min": Decimal("11950"),"base": Decimal("3700.27"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("230"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("711"),  "base": Decimal("48.10"),  "rate": Decimal("0.12")},
            {"min": Decimal("1691"), "base": Decimal("165.98"), "rate": Decimal("0.22")},
            {"min": Decimal("3185"), "base": Decimal("488.38"), "rate": Decimal("0.24")},
            {"min": Decimal("5159"), "base": Decimal("955.10"), "rate": Decimal("0.32")},
            {"min": Decimal("6479"), "base": Decimal("1356.54"),"rate": Decimal("0.35")},
            {"min": Decimal("16942"),"base": Decimal("4627.58"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("145"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("457"),  "base": Decimal("31.20"),  "rate": Decimal("0.12")},
            {"min": Decimal("1034"), "base": Decimal("102.54"), "rate": Decimal("0.22")},
            {"min": Decimal("1611"), "base": Decimal("228.58"), "rate": Decimal("0.24")},
            {"min": Decimal("3117"), "base": Decimal("604.90"), "rate": Decimal("0.32")},
            {"min": Decimal("3933"), "base": Decimal("865.62"), "rate": Decimal("0.35")},
            {"min": Decimal("10225"),"base": Decimal("2950.56"),"rate": Decimal("0.37")},
        ],
    },
    "biweekly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("153"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("583"),  "base": Decimal("43"),    "rate": Decimal("0.12")},
            {"min": Decimal("1866"), "base": Decimal("208.52"),"rate": Decimal("0.22")},
            {"min": Decimal("3644"), "base": Decimal("652.52"),"rate": Decimal("0.24")},
            {"min": Decimal("7385"), "base": Decimal("1577.00"),"rate": Decimal("0.32")},
            {"min": Decimal("9200"), "base": Decimal("2173.80"),"rate": Decimal("0.35")},
            {"min": Decimal("23900"),"base": Decimal("7400.70"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("460"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("1423"), "base": Decimal("96.10"), "rate": Decimal("0.12")},
            {"min": Decimal("3382"), "base": Decimal("331.96"),"rate": Decimal("0.22")},
            {"min": Decimal("6370"), "base": Decimal("976.76"),"rate": Decimal("0.24")},
            {"min": Decimal("10318"),"base": Decimal("1910.20"),"rate": Decimal("0.32")},
            {"min": Decimal("12958"),"base": Decimal("2714.14"),"rate": Decimal("0.35")},
            {"min": Decimal("33884"),"base": Decimal("9255.38"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("289"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("913"),  "base": Decimal("62.50"), "rate": Decimal("0.12")},
            {"min": Decimal("2067"), "base": Decimal("205.20"),"rate": Decimal("0.22")},
            {"min": Decimal("3222"), "base": Decimal("457.16"),"rate": Decimal("0.24")},
            {"min": Decimal("6234"), "base": Decimal("1209.40"),"rate": Decimal("0.32")},
            {"min": Decimal("7866"), "base": Decimal("1731.24"),"rate": Decimal("0.35")},
            {"min": Decimal("20450"),"base": Decimal("5901.12"),"rate": Decimal("0.37")},
        ],
    },
    "semimonthly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("166"),  "base": Decimal("0"),     "rate": Decimal("0.10")},
            {"min": Decimal("632"),  "base": Decimal("46.60"), "rate": Decimal("0.12")},
            {"min": Decimal("2022"), "base": Decimal("224.72"),"rate": Decimal("0.22")},
            {"min": Decimal("3953"), "base": Decimal("703.20"),"rate": Decimal("0.24")},
            {"min": Decimal("8015"), "base": Decimal("1697.84"),"rate": Decimal("0.32")},
            {"min": Decimal("9983"), "base": Decimal("2338.72"),"rate": Decimal("0.35")},
            {"min": Decimal("25900"),"base": Decimal("7963.20"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("500"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("1543"), "base": Decimal("104.20"), "rate": Decimal("0.12")},
            {"min": Decimal("3662"), "base": Decimal("359.28"), "rate": Decimal("0.22")},
            {"min": Decimal("6890"), "base": Decimal("1056.88"),"rate": Decimal("0.24")},
            {"min": Decimal("11100"),"base": Decimal("2066.40"),"rate": Decimal("0.32")},
            {"min": Decimal("13908"),"base": Decimal("2935.36"),"rate": Decimal("0.35")},
            {"min": Decimal("36358"),"base": Decimal("10005.84"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),    "rate": Decimal("0.10")},
            {"min": Decimal("314"),  "base": Decimal("0"),    "rate": Decimal("0.10")},
            {"min": Decimal("995"),  "base": Decimal("68.60"),"rate": Decimal("0.12")},
            {"min": Decimal("2248"), "base": Decimal("225.60"),"rate": Decimal("0.22")},
            {"min": Decimal("3500"), "base": Decimal("502.48"),"rate": Decimal("0.24")},
            {"min": Decimal("6781"), "base": Decimal("1329.20"),"rate": Decimal("0.32")},
            {"min": Decimal("8550"), "base": Decimal("1900.36"),"rate": Decimal("0.35")},
            {"min": Decimal("22215"),"base": Decimal("6472.84"),"rate": Decimal("0.37")},
        ],
    },
    "monthly": {
        "single": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("333"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("1250"), "base": Decimal("90.40"),  "rate": Decimal("0.12")},
            {"min": Decimal("4043"), "base": Decimal("450.48"), "rate": Decimal("0.22")},
            {"min": Decimal("7900"), "base": Decimal("1405.44"),"rate": Decimal("0.24")},
            {"min": Decimal("16031"),"base": Decimal("3395.68"),"rate": Decimal("0.32")},
            {"min": Decimal("19967"),"base": Decimal("4677.84"),"rate": Decimal("0.35")},
            {"min": Decimal("51800"),"base": Decimal("15921.84"),"rate": Decimal("0.37")},
        ],
        "married": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("1000"), "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("3087"), "base": Decimal("208.40"), "rate": Decimal("0.12")},
            {"min": Decimal("7325"), "base": Decimal("718.56"), "rate": Decimal("0.22")},
            {"min": Decimal("13781"),"base": Decimal("2113.76"),"rate": Decimal("0.24")},
            {"min": Decimal("22200"),"base": Decimal("4132.80"),"rate": Decimal("0.32")},
            {"min": Decimal("27817"),"base": Decimal("5870.72"),"rate": Decimal("0.35")},
            {"min": Decimal("72717"),"base": Decimal("19650.72"),"rate": Decimal("0.37")},
        ],
        "head": [
            {"min": Decimal("0"),    "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("628"),  "base": Decimal("0"),      "rate": Decimal("0.10")},
            {"min": Decimal("2000"), "base": Decimal("138.20"), "rate": Decimal("0.12")},
            {"min": Decimal("4525"), "base": Decimal("451.40"), "rate": Decimal("0.22")},
            {"min": Decimal("7034"), "base": Decimal("1004.96"),"rate": Decimal("0.24")},
            {"min": Decimal("13562"),"base": Decimal("2658.40"),"rate": Decimal("0.32")},
            {"min": Decimal("17098"),"base": Decimal("3800.72"),"rate": Decimal("0.35")},
            {"min": Decimal("44433"),"base": Decimal("12945.68"),"rate": Decimal("0.37")},
        ],
    },
}

# ─── ANNUAL IRS 1040 BRACKETS (Pub 1040) ────────────────────────────────────────
IRS_1040_BRACKETS = {
    "single": [
        {"min": Decimal("0"),      "base": Decimal("0"),      "rate": Decimal("0.10")},
        {"min": Decimal("11600"),  "base": Decimal("1160"),   "rate": Decimal("0.12")},
        {"min": Decimal("47150"),  "base": Decimal("5426"),   "rate": Decimal("0.22")},
        {"min": Decimal("100525"), "base": Decimal("17206"),  "rate": Decimal("0.24")},
        {"min": Decimal("191950"), "base": Decimal("39146"),  "rate": Decimal("0.32")},
        {"min": Decimal("243725"), "base": Decimal("55682"),  "rate": Decimal("0.35")},
        {"min": Decimal("609350"), "base": Decimal("183647"), "rate": Decimal("0.37")},
    ],
    "married": [
        {"min": Decimal("0"),      "base": Decimal("0"),      "rate": Decimal("0.10")},
        {"min": Decimal("23200"),  "base": Decimal("2320"),   "rate": Decimal("0.12")},
        {"min": Decimal("94300"),  "base": Decimal("8620"),   "rate": Decimal("0.22")},
        {"min": Decimal("201050"), "base": Decimal("29366"),  "rate": Decimal("0.24")},
        {"min": Decimal("383900"), "base": Decimal("74766"),  "rate": Decimal("0.32")},
        {"min": Decimal("487450"), "base": Decimal("105654"), "rate": Decimal("0.35")},
        {"min": Decimal("731200"), "base": Decimal("196669"), "rate": Decimal("0.37")},
    ],
    "head": [
        {"min": Decimal("0"),      "base": Decimal("0"),      "rate": Decimal("0.10")},
        {"min": Decimal("16550"),  "base": Decimal("1655"),   "rate": Decimal("0.12")},
        {"min": Decimal("63100"),  "base": Decimal("7206"),   "rate": Decimal("0.22")},
        {"min": Decimal("100500"), "base": Decimal("15498"),  "rate": Decimal("0.24")},
        {"min": Decimal("191950"), "base": Decimal("37236"),  "rate": Decimal("0.32")},
        {"min": Decimal("243700"), "base": Decimal("53772"),  "rate": Decimal("0.35")},
        {"min": Decimal("609350"), "base": Decimal("183074"), "rate": Decimal("0.37")},
    ],
}

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def round_to_penny(amount: Decimal) -> Decimal:
    """Round to nearest penny using IRS rounding rules."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def find_bracket(table, status, amt):
    """Find the appropriate tax bracket with improved precision."""
    if amt < Decimal("0"):
        raise ValueError("Taxable amount cannot be negative")
        
    for row in reversed(table[status]):
        if amt >= row["min"]:
            return row
    return table[status][0]

def calculate_periodic_pct_tax(status, taxable, period):
    """Calculate periodic percentage tax with enhanced precision."""
    if taxable < Decimal("0"):
        raise ValueError("Taxable amount cannot be negative")
        
    # Round the taxable amount first (IRS Pub 15-T requirement)
    taxable = round_to_penny(taxable)
    
    row = find_bracket(PERCENTAGE_METHOD_TABLES[period], status, taxable)
    # Calculate tax using IRS method
    excess = round_to_penny(taxable - row["min"])
    tax = row["base"] + (excess * row["rate"])
    return round_to_penny(tax)

def calculate_annual_pct_tax(status, taxable):
    """Calculate annual percentage tax with enhanced precision."""
    if taxable < Decimal("0"):
        raise ValueError("Taxable amount cannot be negative")
        
    row = find_bracket(IRS_1040_BRACKETS, status, taxable)
    tax = row["base"] + (taxable - row["min"]) * row["rate"]
    return round_to_penny(tax)

@st.cache_data
def calculate_fed(
    gross: Decimal, status: str, multi: bool, dep_credit: Decimal,
    oth: Decimal, ded: Decimal, extra: Decimal,
    period: str, annual: bool, other_job_amount: Decimal = Decimal("0")
) -> Decimal:
    """Calculate federal withholding with improved multiple jobs handling."""
    try:
        # Input validation
        if gross < Decimal("0"):
            raise ValueError("Gross pay cannot be negative")
        if dep_credit < Decimal("0"):
            raise ValueError("Dependent credits cannot be negative")
        if oth < Decimal("0"):
            raise ValueError("Other income cannot be negative")
        if ded < Decimal("0"):
            raise ValueError("Deductions cannot be negative")
        if extra < Decimal("0"):
            raise ValueError("Extra withholding cannot be negative")
            
        p = PERIODS[period]
        
        # For periodic calculations, work with the periodic amount directly
        if not annual:
            base = gross
            other_periodic = oth / p
            ded_periodic = ded / p
            annual_gross = gross * p
        else:
            base = gross / p
            other_periodic = oth / p
            ded_periodic = ded / p
            annual_gross = gross
            
        # Enhanced multiple jobs adjustment
        if multi:
            # Calculate adjustment based on annual income
            if other_job_amount > Decimal("0"):
                # For two jobs, use the higher paying job's adjustment
                higher_income = max(annual_gross, other_job_amount)
                adjustment = get_multiple_jobs_adjustment(higher_income, status)
            else:
                # For three or more jobs, use this job's adjustment
                adjustment = get_multiple_jobs_adjustment(annual_gross, status)
            
            # Apply adjustment to periodic amount
            base += adjustment / p
            
        # Calculate periodic taxable income
        standard_ded_periodic = STANDARD_DEDUCTION[status] / p
        taxable = max(
            base + other_periodic - standard_ded_periodic - ded_periodic,
            Decimal("0")
        )
        
        # Calculate periodic tax
        fed = calculate_periodic_pct_tax(status, taxable, period)
        
        # Apply dependent credit (periodic)
        credit_periodic = dep_credit / p
        fed = max(fed - credit_periodic, Decimal("0"))
        
        # Add extra withholding
        fed += extra
        
        # Convert to annual if needed
        if annual:
            fed *= p
            
        return round_to_penny(fed)
        
    except Exception as e:
        st.error(f"Error calculating federal tax: {str(e)}")
        return Decimal("0")

def calculate_ss(gross: Decimal, period: str, annual: bool) -> Decimal:
    p = PERIODS[period]
    base = gross if annual else gross * p
    ss_ann = min(base, FICA_CAP) * SOCIAL_RATE
    return (ss_ann if annual else ss_ann / p).quantize(Decimal("0.01"), ROUND_HALF_UP)

def calculate_mi(gross: Decimal, period: str, annual: bool) -> Decimal:
    p = PERIODS[period]
    base = gross if annual else gross * p
    mi_ann = base * MEDICARE_RATE
    return (mi_ann if annual else mi_ann / p).quantize(Decimal("0.01"), ROUND_HALF_UP)

# ─── SIDEBAR UI ────────────────────────────────────────────────────────────────
st.sidebar.title("Inputs")
mode = st.sidebar.radio("Mode", ["Single Paycheck", "Full Year"])
annual = mode == "Full Year"

def format_currency_input(label: str, min_value: float = 0.0, value: float = 0.0, step: float = 0.01, help: str = None, use_sidebar: bool = False) -> float:
    """Custom currency input that enforces 2 decimal places and adds commas."""
    # Format the default value with commas and 2 decimal places
    formatted_value = f"{value:,.2f}"
    
    # Choose between sidebar and main area
    input_container = st.sidebar if use_sidebar else st
    
    # Create text input for currency
    input_value = input_container.text_input(
        label,
        value=formatted_value,
        help=help,
        key=f"currency_input_{label}"
    )
    
    try:
        # Remove commas and validate input
        cleaned_value = input_value.replace(",", "")
        # Ensure only 2 decimal places
        if "." in cleaned_value:
            dollars, cents = cleaned_value.split(".")
            if len(cents) > 2:
                cents = cents[:2]
            cleaned_value = f"{dollars}.{cents}"
        
        # Convert to float and validate range
        result = float(cleaned_value)
        if result < min_value:
            input_container.error(f"Value cannot be less than {min_value:,.2f}")
            return min_value
        return result
    except ValueError:
        input_container.error("Please enter a valid number")
        return value

if annual:
    gross_val = format_currency_input(
        "Annual Gross Salary ($)",
        min_value=0.0,
        value=60000.00,
        help="Enter your annual gross salary",
        use_sidebar=True
    )
else:
    gross_val = format_currency_input(
        "Gross Amount per Paycheck ($)",
        min_value=0.0,
        value=1000.00,
        help="Enter your gross pay per paycheck",
        use_sidebar=True
    )

# Remove the try/except block since number_input handles validation
if gross_val < 0:
    st.sidebar.error("Gross amount cannot be negative")
    gross_val = 0

period = st.sidebar.selectbox("Pay Frequency", ["weekly","biweekly","semimonthly","monthly"])

# Enhanced Multiple Jobs Section
st.sidebar.subheader("Step 2: Multiple Jobs / Spouse Works")
multi = st.sidebar.checkbox("Check if any of these apply:")
if multi:
    st.sidebar.markdown("""
        📋 **Multiple Jobs Worksheet**
        - You have more than one job at the same time
        - You're married filing jointly and your spouse also works
    """)
    
    job_count = st.sidebar.radio(
        "Select your situation:",
        ["Two jobs total", "Three or more jobs total"]
    )
    
    if job_count == "Two jobs total":
        st.sidebar.markdown("For most accurate withholding with two jobs:")
        other_job_amount = format_currency_input(
            "Annual salary of other job ($)",
            min_value=0.0,
            value=0.00,
            help="Enter the annual salary of the other job",
            use_sidebar=True
        )
    else:  # Three or more jobs
        st.sidebar.markdown("""
            For three or more jobs:
            - Higher withholding amounts will be applied
            - Consider using the IRS Tax Withholding Estimator for more accuracy
        """)

# New dependent credit section
st.sidebar.subheader("Step 3: Dependent Credits")
st.sidebar.markdown("""
    Enter total dependent credits:
    - $2,000 per qualifying child under 17
    - $1,500 per dependent 17 and older
""")
dep_credit = format_currency_input(
    "Total Dependent Credits ($)",
    min_value=0.0,
    value=0.00,
    help="Enter total dependent credits",
    use_sidebar=True
)

# Update other inputs to use the same format
oth = format_currency_input("Step 4(a): Other income ($)", 
    min_value=0.0, value=0.0, step=100.0, use_sidebar=True)
ded = format_currency_input("Step 4(b): Deductions over standard ($)", 
    min_value=0.0, value=0.0, step=100.0, use_sidebar=True)
extra = format_currency_input("Step 4(c): Extra withholding per period ($)", 
    min_value=0.0, value=0.0, step=5.0, use_sidebar=True)

# Filing status must match lowercase keys:
filing = st.sidebar.selectbox("Filing Status (Step 1c)", ["single","married","head"])

# State Tax Section
st.sidebar.markdown("---")
st.sidebar.subheader("State Tax")

# State selection
selected_state = st.sidebar.selectbox(
    "Select State",
    ["None"] + sorted(STATE_CALCULATORS.keys()),
    format_func=lambda x: "No state tax" if x == "None" else f"{get_calculator(x).state_name} ({x})"
)

state_inputs = {}
if selected_state != "None":
    calculator = get_calculator(selected_state)
    
    # Get and render state-specific UI components
    ui_components = calculator.get_ui_components()
    if "render" in ui_components:
        state_inputs = ui_components["render"](st.sidebar)
else:
    calculator = None

# ─── MAIN AREA ────────────────────────────────────────────────────────────────
st.title("2024 Paycheck Tax Withholding Calculator")
st.markdown("This uses IRS Publication 15-T percentage and annual 1040 tables for federal withholding, plus optional NY state withholding.")

st.warning("""
⚠️ **Disclaimer**: 
- This calculator provides estimates based on IRS Publication 15-T procedures
- Results are approximations and should not be used for official tax filing purposes
- For accurate tax advice, please consult a qualified tax professional
- Actual withholding may vary based on specific employer policies and circumstances
""")

if st.sidebar.button("Calculate"):
    if gross_val > 250_000:
        st.error("who we lying to 👀")
        st.stop()
        
    # Track calculator usage
    track_feature_usage('calculator_used')  # Track basic calculator usage
    if multi:
        track_feature_usage('multiple_jobs')
    if dep_credit > 0:
        track_feature_usage('dependent_credits')
    if selected_state != "None":
        track_feature_usage(f'state_tax_{selected_state}')
        
    # Convert float values to Decimal for calculations
    gross = Decimal(str(gross_val))
    dep_credit_dec = Decimal(str(dep_credit))
    other_job = Decimal(str(other_job_amount)) if multi and job_count == "Two jobs total" else Decimal("0")
    oth_dec = Decimal(str(oth))
    ded_dec = Decimal(str(ded))
    extra_dec = Decimal(str(extra))
    
    # Calculate taxes
    fed = calculate_fed(gross, filing, multi, dep_credit_dec, oth_dec, ded_dec, extra_dec, period, annual, other_job)
    ss  = calculate_ss(gross, period, annual)
    mi  = calculate_mi(gross, period, annual)
    if annual:
        net = gross - fed - ss - mi
        per_pay = gross / PERIODS[period]
    else:
        per_pay = gross
        net = per_pay - fed - ss - mi

    cols = st.columns(4)
    cols[0].metric("Federal Tax",     f"${fed:,.2f}")
    cols[1].metric("Social Security", f"${ss:,.2f}")
    cols[2].metric("Medicare",        f"${mi:,.2f}")
    cols[3].metric("Net Pay",         f"${net:,.2f}")

    # State Tax Calculation
    if calculator is not None:
        annual_income = Decimal(str(gross if annual else gross * PERIODS[period]))
        
        # Calculate state taxes using the modular calculator
        result = calculator.calculate(
            income=annual_income,
            pay_period=period,
            is_annual=annual,
            **state_inputs
        )
        
        # Display State Tax Information
        st.markdown(f"### {calculator.state_name} Tax Breakdown")
        
        # Create columns based on whether there are local taxes
        num_cols = 4 if result.local_taxes else 3
        state_cols = st.columns(num_cols)
        
        # State Tax
        with state_cols[0]:
            st.metric(
                f"{calculator.state_code} State Tax",
                f"${result.state_tax:,.2f}",
                help=f"{calculator.state_name} state withholding tax per pay period"
            )
            
        # Local Taxes (if any)
        col_index = 1
        total_tax = result.state_tax
        for locality, amount in result.local_taxes.items():
            with state_cols[col_index]:
                st.metric(
                    f"{locality.upper()} Tax",
                    f"${amount:,.2f}",
                    help=f"{locality} local tax per pay period"
                )
                total_tax += amount
                col_index += 1
                
        # Effective Rate
        with state_cols[-2]:
            st.metric(
                "Effective Rate",
                f"{float(result.effective_rate)*100:.2f}%",
                help="Total effective tax rate (state + local)"
            )
            
        # Total State Tax
        with state_cols[-1]:
            st.metric(
                "Total State Tax",
                f"${total_tax:,.2f}",
                help=f"Total {calculator.state_name} taxes per pay period"
            )
            
        # Show annual equivalent if in single paycheck mode
        if not annual:
            annual_state = total_tax * PERIODS[period]
            st.markdown("#### Annual Equivalent")
            st.markdown(f"**Total {calculator.state_name} Tax: ${annual_state:,.2f}**")
            
        # Show any warnings or errors
        if result.warnings:
            for warning in result.warnings:
                st.warning(f"⚠️ {warning}")
                
        if result.errors:
            for error in result.errors:
                st.error(f"❗ {error}")
            
        # Add explanatory notes
        with st.expander(f"ℹ️ About {calculator.state_name} Tax Calculations"):
            st.markdown(f"""
                **Calculation Details:**
                - Filing Status: {state_inputs.get('filing_status', 'Single')}
                - Deductions: {', '.join(f'{k}: ${v:,.2f}' for k,v in result.deductions.items())}
                - Credits: {', '.join(f'{k}: ${v:,.2f}' for k,v in result.credits.items()) if result.credits else 'None applied'}
                
                **Notes:**
                - These calculations are estimates based on 2024 tax tables
                - Actual withholding may vary based on your specific situation
                - Consult a tax professional for personalized advice
            """)

# ─── Feedback Section ─────────────────────────────────────────────────────────
with st.expander("💬 Have feedback or suggestions?"):
    name = st.text_input(
        "Your name (optional)",
        placeholder="If you'd like to be credited…"
    )
    feedback = st.text_area(
        "Leave any comments, tweaks, or general feedback here:",
        placeholder="Type away…",
        height=100,
    )
    if st.button("Submit Feedback"):
        if not feedback.strip():
            st.warning("Oops—you didn't write anything!")
        else:
            # Acknowledge
            st.success("Thanks for your feedback! 🙏")
            st.balloons()
            # Save to your server for review
            with open("user_feedback.log", "a") as f:
                who = name.strip() or "Anonymous"
                f.write(f"{who}: {feedback.replace(chr(10), ' ')}\n---\n")

# ─── Admin: View All Feedback ─────────────────────────────────────────────────
if st.sidebar.checkbox("🔒 Show Feedback Log (admin)"):
    try:
        with open("user_feedback.log", "r") as f:
            log = f.read().strip()
        if log:
            st.text_area("User Feedback Log", log, height=300)
        else:
            st.info("No feedback yet.")
    except FileNotFoundError:
        st.warning("No feedback log found.")

# ─── Admin Analytics Dashboard ─────────────────────────────────────────────────
st.markdown("---")
with st.expander("🔒 Analytics Dashboard (Admin Only)", expanded=False):
    if not st.session_state.is_admin:
        admin_password = st.text_input("Enter admin password", type="password")
        if st.button("Login"):
            if verify_admin_password(admin_password):
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("Invalid password")
    else:
        display_analytics_dashboard()
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

# ─── Snake Game Section ─────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🐍 Take a Break: Play Snake!", expanded=False):
    st.markdown("""
        ### Snake Game
        Use arrow keys to control the snake:
        - ⬆️ Move Up
        - ⬇️ Move Down
        - ⬅️ Move Left
        - ➡️ Move Right
        
        Click 'Start New Game' to begin!
        
        *Note: If the game doesn't load properly, try refreshing the page.*
    """)
    try:
        from snake_game import snake_game
        snake_game()
    except Exception as e:
        st.error("Unable to load the snake game. Please refresh the page.")
        st.warning(f"Error details: {str(e)}")









