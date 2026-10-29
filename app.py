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
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f3ff 0%, #f0f7ff 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #211c45, #44358a);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
h1, h2, h3 {
    color: #30245f;
}
div.stButton > button {
    background: linear-gradient(90deg, #6558d3, #8878ee);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1rem;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #4839ad;
    color: white;
    border: 1px solid #b8adff;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e4defa;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 3px 12px #30245f12;
}
div[data-testid="stForm"] {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e4defa;
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
