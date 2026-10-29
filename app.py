import streamlit as st
import pandas as pd
import joblib
from database import get_connection

st.set_page_config(
    page_title="Smart Complaint AI",
    page_icon="📩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the trained ML model
@st.cache_resource
def load_model():
    return joblib.load("complaint_model.joblib")
def load_metrics():
    try:
        return joblib.load("model_metrics.joblib")
    except FileNotFoundError:
        return None

model = load_model()

DEPARTMENTS = [
    "Account & Login",
    "Banking & Payments",
    "Billing & Refunds",
    "Customer Service",
    "Delivery & Logistics",
    "Fraud & Security",
    "Internet & Telecom",
    "Order & Booking",
    "Product Quality & Returns",
    "Technical Support"
]

STATUSES = ["Pending", "In Progress", "Resolved"]

# Custom CSS

# Custom CSS
st.markdown("""
<style>

/* =========================
   MAIN APPLICATION
   ========================= */
.stApp {
    background: linear-gradient(135deg, #f5f3ff 0%, #eef5ff 100%);
    color: #27304f;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Main headings */
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #30245f !important;
}

/* Main content text */
[data-testid="stAppViewContainer"] .main p,
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main
[data-testid="stMarkdownContainer"] {
    color: #374151;
}

/* =========================
   SIDEBAR
   ========================= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #211c45 0%, #44358a 100%);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* Sidebar navigation */
[data-testid="stSidebar"] [role="radiogroup"] label {
    color: #ffffff !important;
    background: transparent;
    border-radius: 8px;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #ffffff1a;
}

/* =========================
   BUTTONS
   ========================= */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(90deg, #5b4bce, #7968ed) !important;
    color: #ffffff !important;
    border: 1px solid #5b4bce !important;
    border-radius: 10px !important;
    padding: 0.55rem 1rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
}

.stButton > button p,
.stFormSubmitButton > button p {
    color: #ffffff !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #4333a5 !important;
    border-color: #4333a5 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px #30245f30;
}

.stButton > button:focus,
.stFormSubmitButton > button:focus {
    outline: 2px solid #a99cff !important;
    outline-offset: 2px;
}

/* =========================
   INPUTS AND DROPDOWNS
   ========================= */
.stTextInput input,
.stTextArea textarea,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    background-color: #ffffff !important;
    color: #27304f !important;
    border-color: #c9c4e8 !important;
    border-radius: 8px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #7b8194 !important;
}

[data-baseweb="select"] *,
[data-baseweb="popover"] * {
    color: #27304f;
}

[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stCheckbox"] label {
    color: #30245f !important;
}

/* =========================
   METRIC CARDS
   ========================= */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e4defa;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 3px 12px #30245f12;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #625b85 !important;
}

[data-testid="stMetricValue"] {
    color: #30245f !important;
}

/* =========================
   FORMS AND EXPANDERS
   ========================= */
[data-testid="stForm"] {
    background: #ffffff;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e4defa;
}

[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e4defa;
    border-radius: 10px;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #30245f !important;
}

/* =========================
   ALERTS AND MESSAGES
   ========================= */
[data-testid="stAlert"] {
    border-radius: 10px;
}

[data-testid="stAlert"] p {
    color: #27304f !important;
}

/* =========================
   TABLES AND DATAFRAMES
   ========================= */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #e4defa;
    border-radius: 10px;
    overflow: hidden;
}

/* =========================
   DIVIDERS AND CAPTIONS
   ========================= */
hr {
    border-color: #d9d2f0 !important;
}

.stCaption,
[data-testid="stCaptionContainer"] p {
    color: #625b85 !important;
}

/* Keep sidebar captions white */
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #ffffff !important;
}

/* =========================
   CHECKBOXES
   ========================= */
[data-testid="stCheckbox"] label p {
    color: #374151 !important;
}

/* ===== FIX MANAGE COMPLAINTS COLORS ===== */

/* Department and status dropdowns */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #30245f !important;
    border: 1px solid #c9c4e8 !important;
    border-radius: 8px !important;
}

/* Selected dropdown text and arrow */
[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] input {
    color: #30245f !important;
}

/* Dropdown options menu */
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background-color: #ffffff !important;
}

[role="option"] {
    background-color: #ffffff !important;
    color: #30245f !important;
}

[role="option"]:hover {
    background-color: #eee9ff !important;
    color: #30245f !important;
}

/* Data table background and text */
[data-testid="stDataFrame"] {
    background-color: #ffffff !important;
    border: 1px solid #ddd6f3 !important;
    border-radius: 10px !important;
}

/* White background for table cells */
[data-testid="stDataFrame"] iframe {
    background-color: #ffffff !important;
}

/* Search input */
[data-testid="stTextInput"] input {
    background-color: #ffffff !important;
    color: #30245f !important;
    border: 1px solid #c9c4e8 !important;
}

/* Labels and result count */
[data-testid="stAppViewContainer"] .main label,
[data-testid="stAppViewContainer"] .main p {
    color: #30245f !important;
}

/* Complaint edit form and text area */
[data-testid="stTextArea"] textarea {
    background-color: #ffffff !important;
    color: #30245f !important;
    border: 1px solid #c9c4e8 !important;
}

</style>
""", unsafe_allow_html=True)


def fetch_complaints():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT complaint_id, complaint_text,
                   predicted_department, created_at,
                   status
            FROM public.complaints
            ORDER BY complaint_id DESC
        """)
        rows = cursor.fetchall()
        return pd.DataFrame(
            rows,
            columns=[
                "ID", "Complaint", "Department",
                "Created At", "Status"
            ]
        )
    finally:
        cursor.close()
        connection.close()


def update_complaint(complaint_id, text, department, status):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE public.complaints
            SET complaint_text = %s,
                predicted_department = %s,
                status = %s
            WHERE complaint_id = %s
        """, (text, department, status, complaint_id))
        connection.commit()
    finally:
        cursor.close()
        connection.close()




def delete_complaint(complaint_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "DELETE FROM public.complaints WHERE complaint_id = %s",
            (complaint_id,)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()


# Sidebar navigation
st.sidebar.title("📩 Complaint AI")
st.sidebar.caption("Smart Complaint Management")
page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Classify Complaint",
        "Manage Complaints",
        "ML Performance"
    ]
)
st.sidebar.divider()
st.sidebar.caption("Powered by TF-IDF + Logistic Regression")



# DASHBOARD
if page == "Dashboard":
    st.title("📊 Complaint Dashboard")
    st.write(
        "Monitor complaint status, department distribution "
        "and customer complaint trends."
    )

    try:
        df = fetch_complaints()

        if df.empty:
            st.info(
                "No complaints yet. Submit a complaint to see "
                "dashboard statistics."
            )
        else:
            total = len(df)
            pending = int((df["Status"] == "Pending").sum())
            progress = int((df["Status"] == "In Progress").sum())
            resolved = int((df["Status"] == "Resolved").sum())

            # Summary statistics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Complaints", total)
            c2.metric("Pending", pending)
            c3.metric("In Progress", progress)
            c4.metric("Resolved", resolved)

            st.divider()

            # Department-wise statistics
            st.subheader("📊 Department-wise Analysis")

            dept_stats = (
                df["Department"]
                .value_counts()
                .rename_axis("Department")
                .reset_index(name="Complaint Count")
            )

            dept_stats["Percentage (%)"] = (
                dept_stats["Complaint Count"] / total * 100
            ).round(2)

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Complaints by Department**")
                st.bar_chart(
                    dept_stats.set_index("Department")[
                        "Complaint Count"
                    ]
                )

            with col2:
                st.write("**Department Complaint Distribution (%)**")
                st.bar_chart(
                    dept_stats.set_index("Department")[
                        "Percentage (%)"
                    ]
                )

            st.write("**Department Statistical Summary**")
            st.dataframe(
                dept_stats,
                use_container_width=True,
                hide_index=True
            )

            # Status analysis
            st.subheader("📌 Complaint Status Analysis")

            status_stats = pd.DataFrame({
                "Status": ["Pending", "In Progress", "Resolved"],
                "Count": [pending, progress, resolved]
            })

            status_stats["Percentage (%)"] = (
                status_stats["Count"] / total * 100
            ).round(2)

            col3, col4 = st.columns(2)

            with col3:
                st.bar_chart(
                    status_stats.set_index("Status")["Count"]
                )

            with col4:
                st.dataframe(
                    status_stats,
                    use_container_width=True,
                    hide_index=True
                )

            # Recent complaints
            st.subheader("🕒 Recent Complaints")
            st.dataframe(
                df.head(10),
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        st.error(f"Database error: {e}")

# CLASSIFY COMPLAINT
elif page == "Classify Complaint":
    st.title("🤖 Complaint Classification")
    st.write("Enter a complaint and let the ML model recommend a department.")

    with st.form("complaint_form"):
        complaint = st.text_area(
            "Complaint description",
            placeholder="Example: My internet connection is not working...",
            height=150
        )
        predict_button = st.form_submit_button("🔍 Predict Department")

    if predict_button:
        if len(complaint.strip()) < 5:
            st.warning("Please enter a meaningful complaint.")
        else:
            prediction = model.predict([complaint.strip()])[0]
            st.session_state["current_complaint"] = complaint.strip()
            st.session_state["current_prediction"] = prediction

    if st.session_state.get("current_prediction"):
        prediction = st.session_state["current_prediction"]
        st.success(f"Recommended Department: **{prediction}**")

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba([
                st.session_state["current_complaint"]
            ])[0]
            confidence = max(probabilities) * 100
            st.metric("Model confidence estimate", f"{confidence:.1f}%")
            st.caption("Confidence is an estimate, not a guarantee of correctness.")

        if st.button("💾 Submit Complaint to Supabase"):
            connection = None
            cursor = None
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO public.complaints
                        (complaint_text, predicted_department, status)
                    VALUES (%s, %s, %s)
                """, (
                    st.session_state["current_complaint"],
                    prediction,
                    "Pending"
                ))
                connection.commit()
                st.success("Complaint saved successfully!")
                st.session_state.pop("current_complaint", None)
                st.session_state.pop("current_prediction", None)
            except Exception as e:
                st.error(f"Could not save complaint: {e}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()


# MANAGE COMPLAINTS
elif page == "Manage Complaints":
    st.title("🗂️ Manage Complaints")

    try:
        df = fetch_complaints()

        if df.empty:
            st.info("No complaints to manage yet.")
        else:
            search = st.text_input("🔎 Search complaint text")
            dept_filter = st.selectbox(
                "Filter by department",
                ["All"] + sorted(df["Department"].dropna().unique().tolist())
            )
            status_filter = st.selectbox(
                "Filter by status",
                ["All"] + STATUSES
            )

            filtered = df.copy()

            if search.strip():
                filtered = filtered[
                    filtered["Complaint"].str.contains(
                        search.strip(), case=False, na=False
                    )
                ]
            if dept_filter != "All":
                filtered = filtered[filtered["Department"] == dept_filter]
            if status_filter != "All":
                filtered = filtered[filtered["Status"] == status_filter]

            st.write(f"**{len(filtered)} complaint(s) found**")
            st.dataframe(filtered, use_container_width=True)

            ids = filtered["ID"].tolist()

            if ids:
                selected_id = st.selectbox("Select complaint ID", ids)
                selected = filtered[filtered["ID"] == selected_id].iloc[0]

                with st.expander("✏️ Edit selected complaint"):
                    with st.form("edit_form"):
                        edit_text = st.text_area(
                            "Complaint text", value=selected["Complaint"]
                        )
                        edit_department = st.selectbox(
                            "Department",
                            DEPARTMENTS,
                            index=(
                                DEPARTMENTS.index(selected["Department"])
                                if selected["Department"] in DEPARTMENTS
                                else 0
                            )
                        )
                        edit_status = st.selectbox(
                            "Status",
                            STATUSES,
                            index=(
                                STATUSES.index(selected["Status"])
                                if selected["Status"] in STATUSES
                                else 0
                            )
                        )
                        save_edit = st.form_submit_button("💾 Save Changes")

                    if save_edit:
                        if not edit_text.strip():
                            st.warning("Complaint text cannot be empty.")
                        else:
                            try:
                                update_complaint(
                                    int(selected_id),
                                    edit_text.strip(),
                                    edit_department,
                                    edit_status
                                )
                                st.success("Complaint updated.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Update failed: {e}")

                with st.expander("🗑️ Delete selected complaint"):
                    st.warning("Deletion is permanent.")
                    confirm_delete = st.checkbox(
                        f"Confirm deletion of complaint ID {selected_id}"
                    )
                    if st.button("Delete Complaint"):
                        if confirm_delete:
                            try:
                                delete_complaint(int(selected_id))
                                st.success("Complaint deleted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Delete failed: {e}")
                        else:
                            st.warning("Tick the confirmation box first.")

    except Exception as e:
        st.error(f"Database error: {e}")



# ML PERFORMANCE
elif page == "ML Performance":
    st.title("🧠 Machine Learning Performance")

    st.write(
        "TF-IDF converts complaint text into numerical features, "
        "and Logistic Regression predicts the recommended department."
    )

    metrics = load_metrics()

    if metrics is not None:
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Training Examples",
            metrics["total_complaints"]
        )

        col2.metric(
            "Test Accuracy",
            f'{metrics["accuracy"]:.2f}%'
        )

        col3.metric(
            "Test Examples",
            metrics["test_examples"]
        )

        st.info(
            "Accuracy is measured on a held-out test set. "
            "Your current dataset is small, so this result "
            "does not guarantee real-world performance."
        )

    else:
        st.warning(
            "Model metrics are not available. "
            "Run py train_model.py to generate them."
        )

    st.subheader("Departments Supported")
    st.write(", ".join(DEPARTMENTS))

    st.subheader("How the ML Workflow Works")

    st.markdown("""
    1. The customer enters a complaint.
    2. TF-IDF converts the complaint text into numerical features.
    3. Logistic Regression predicts the most likely department.
    4. The application displays the recommended department.
    5. The complaint and prediction are stored in Supabase PostgreSQL.
    """)

    st.subheader("Model Information")
    st.write("Text representation: TF-IDF")
    st.write("Classification algorithm: Logistic Regression")
