
import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

from database import (
    initialize_database,
    add_application,
    get_all_applications,
    update_status,
    delete_application,
    update_application
)

from utils import (
    applications_to_dataframe,
    calculate_success_rate
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="JobTrack",
    page_icon="💼",
    layout="wide"
)


import streamlit.components.v1 as components


# =========================================================
# ANIMATED PARTICLE-NETWORK 3D BACKGROUND (canvas + JS)
# =========================================================
# Injected once into the parent document so it renders full-page,
# behind all Streamlit content, and keeps animating continuously.

components.html(
    """
    <script>
    (function() {
        const doc = window.parent.document;

        // Avoid injecting more than once on Streamlit re-runs
        if (doc.getElementById('jt-particle-bg')) { return; }

        const canvas = doc.createElement('canvas');
        canvas.id = 'jt-particle-bg';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '-1';
        canvas.style.pointerEvents = 'none';
        doc.body.prepend(canvas);

        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = doc.documentElement.clientWidth;
            canvas.height = doc.documentElement.clientHeight;
        }
        resize();
        window.parent.addEventListener('resize', resize);

        const colors = ['#22d3ee', '#ec4899', '#a78bfa', '#38bdf8', '#34d399'];
        const COUNT = 85;
        const particles = [];
        for (let i = 0; i < COUNT; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                z: Math.random() * 1 + 0.3,          // depth factor -> size/speed/parallax
                vx: (Math.random() - 0.5) * 0.35,
                vy: (Math.random() - 0.5) * 0.35,
                color: colors[Math.floor(Math.random() * colors.length)]
            });
        }

        let mouseX = canvas.width / 2;
        let mouseY = canvas.height / 2;
        doc.addEventListener('mousemove', function(e) {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // deep space gradient base
            const grad = ctx.createRadialGradient(
                canvas.width / 2, canvas.height / 2, 0,
                canvas.width / 2, canvas.height / 2, canvas.width * 0.75
            );
            grad.addColorStop(0, '#101528');
            grad.addColorStop(1, '#04050c');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // gentle parallax offset based on mouse (3D depth illusion)
            const parX = (mouseX - canvas.width / 2) * 0.01;
            const parY = (mouseY - canvas.height / 2) * 0.01;

            // update + draw connecting lines
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

                for (let j = i + 1; j < particles.length; j++) {
                    const q = particles[j];
                    const dx = p.x - q.x, dy = p.y - q.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 130) {
                        ctx.strokeStyle = 'rgba(140, 180, 255,' + ((1 - dist / 130) * 0.22) + ')';
                        ctx.lineWidth = 0.6;
                        ctx.beginPath();
                        ctx.moveTo(p.x + parX * p.z, p.y + parY * p.z);
                        ctx.lineTo(q.x + parX * q.z, q.y + parY * q.z);
                        ctx.stroke();
                    }
                }
            }

            // draw glowing particles (depth-scaled)
            for (const p of particles) {
                const drawX = p.x + parX * p.z;
                const drawY = p.y + parY * p.z;
                const radius = 1 + p.z * 2;
                ctx.beginPath();
                ctx.arc(drawX, drawY, radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.shadowBlur = 10 * p.z;
                ctx.shadowColor = p.color;
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            requestAnimationFrame(animate);
        }
        animate();
    })();
    </script>
    """,
    height=0,
)


# =========================================================
# NEON GLASS UI STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* App shell transparent so the canvas behind shows through */
    .stApp {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 1;
    }

    /* ---------- Sidebar: dark glass panel ---------- */
    [data-testid="stSidebar"] {
        background: rgba(10, 13, 28, 0.75);
        backdrop-filter: blur(18px);
        border-right: 1px solid rgba(34, 211, 238, 0.25);
    }

    [data-testid="stSidebar"] * {
        color: #eef2ff !important;
    }

    /* ---------- Neon glass content cards with real 3D tilt on hover ---------- */
    div[data-testid="stVerticalBlock"] > div:has(> div.element-container) {
        background: rgba(255, 255, 255, 0.045);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(34, 211, 238, 0.22);
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
        transition: transform 0.4s ease, box-shadow 0.4s ease, border-color 0.4s ease;
        transform-style: preserve-3d;
        perspective: 800px;
    }

    div[data-testid="stVerticalBlock"] > div:has(> div.element-container):hover {
        transform: translateY(-6px) rotateX(3deg) rotateY(-2deg);
        box-shadow:
            0 20px 45px rgba(34, 211, 238, 0.25),
            0 0 25px rgba(236, 72, 153, 0.18);
        border-color: rgba(236, 72, 153, 0.4);
    }

    /* ---------- Typography ---------- */
    .stApp, .stApp p, .stApp label, .stApp span {
        color: #e6e9fb;
    }

    .stApp h1, .stApp h2, .stApp h3 {
        background: linear-gradient(90deg, #22d3ee, #a78bfa, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 14px rgba(34, 211, 238, 0.45));
        font-weight: 800;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 0 0 14px rgba(34, 211, 238, 0.7);
    }

    [data-testid="stMetricLabel"] {
        color: #a5b4fc !important;
    }

    /* ---------- Buttons: neon gradient with glow ---------- */
    .stButton > button {
        background: linear-gradient(135deg, #22d3ee 0%, #a78bfa 50%, #ec4899 100%);
        background-size: 200% 200%;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        transition: transform 0.25s ease, box-shadow 0.25s ease, background-position 0.6s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 24px rgba(34, 211, 238, 0.4);
        background-position: 100% 50%;
    }

    /* ---------- Inputs: subtle glass ---------- */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(34, 211, 238, 0.25) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* ---------- Radio nav glow on selection ---------- */
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        color: #22d3ee !important;
        text-shadow: 0 0 8px rgba(34, 211, 238, 0.8);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_database()


# =========================================================
# LOAD APPLICATION DATA
# =========================================================

data = get_all_applications()

df = applications_to_dataframe(data)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("💼 JobTrack")

st.sidebar.markdown(
    "### Job Application Tracker"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Application",
        "Applications",
        "Application Details",
        "Analytics"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("📊 JobTrack Dashboard")

    st.markdown(
        "Track your job applications, interviews and follow-ups."
    )

    # -----------------------------------------------------
    # KPI CALCULATIONS
    # -----------------------------------------------------

    total_applications = len(df)

    interviews = len(
        df[df["Status"] == "Interview"]
    )

    selected = len(
        df[df["Status"] == "Selected"]
    )

    rejected = len(
        df[df["Status"] == "Rejected"]
    )

    success_rate = calculate_success_rate(df)

    interview_conversion = (
        (interviews + selected)
        / total_applications
        * 100
        if total_applications > 0
        else 0
    )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Applications",
            total_applications
        )

    with col2:
        st.metric(
            "Interviews",
            interviews
        )

    with col3:
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%"
        )

    with col4:
        st.metric(
            "Interview Conversion",
            f"{interview_conversion:.1f}%"
        )

    st.divider()

    # =====================================================
    # INTERVIEWS & FOLLOW-UPS
    # =====================================================

    st.subheader(
        "📅 Upcoming Interviews & Follow-ups"
    )

    if df.empty:

        st.info(
            "No applications available yet. "
            "Add your first application to start tracking."
        )

    else:

        df["Interview Date Parsed"] = pd.to_datetime(
            df["Interview Date"],
            errors="coerce"
        )

        df["Follow-up Date Parsed"] = pd.to_datetime(
            df["Follow-up Date"],
            errors="coerce"
        )

        today = date.today()

        # -------------------------------------------------
        # UPCOMING INTERVIEWS
        # -------------------------------------------------

        upcoming_interviews = df[
            df["Interview Date Parsed"].notna()
            &
            (
                df["Interview Date Parsed"]
                >= pd.Timestamp(today)
            )
        ].sort_values(
            "Interview Date Parsed"
        )

        # -------------------------------------------------
        # FOLLOW-UPS DUE
        # -------------------------------------------------

        followups_due = df[
            df["Follow-up Date Parsed"].notna()
            &
            (
                df["Follow-up Date Parsed"]
                <= pd.Timestamp(today)
            )
        ].sort_values(
            "Follow-up Date Parsed"
        )

        # -------------------------------------------------
        # FUTURE FOLLOW-UPS
        # -------------------------------------------------

        future_followups = df[
            df["Follow-up Date Parsed"].notna()
            &
            (
                df["Follow-up Date Parsed"]
                > pd.Timestamp(today)
            )
        ].sort_values(
            "Follow-up Date Parsed"
        )

        reminder_col1, reminder_col2 = st.columns(2)

        # =================================================
        # UPCOMING INTERVIEWS
        # =================================================

        with reminder_col1:

            st.markdown(
                "### 🎯 Upcoming Interviews"
            )

            if upcoming_interviews.empty:

                st.info(
                    "No upcoming interviews."
                )

            else:

                for _, row in upcoming_interviews.iterrows():

                    interview_date = (
                        row["Interview Date Parsed"].date()
                    )

                    days_left = (
                        interview_date - today
                    ).days

                    if days_left == 0:

                        message = "🔴 Today"

                    elif days_left == 1:

                        message = "🟠 Tomorrow"

                    else:

                        message = (
                            f"🟢 In {days_left} days"
                        )

                    st.write(
                        f"**{row['Company']}** — "
                        f"{row['Role']}"
                    )

                    st.write(
                        f"📅 "
                        f"{interview_date.strftime('%d-%m-%Y')} "
                        f"| {message}"
                    )

                    st.divider()

        # =================================================
        # FOLLOW-UPS
        # =================================================

        with reminder_col2:

            st.markdown(
                "### 🔔 Follow-ups"
            )

            if followups_due.empty:

                st.success(
                    "No follow-ups due today or overdue."
                )

            else:

                for _, row in followups_due.iterrows():

                    followup_date = (
                        row["Follow-up Date Parsed"].date()
                    )

                    days_overdue = (
                        today - followup_date
                    ).days

                    if days_overdue == 0:

                        message = "🔴 Due Today"

                    else:

                        message = (
                            f"🔴 {days_overdue} "
                            f"days overdue"
                        )

                    st.write(
                        f"**{row['Company']}** — "
                        f"{row['Role']}"
                    )

                    st.write(
                        f"📅 "
                        f"{followup_date.strftime('%d-%m-%Y')} "
                        f"| {message}"
                    )

                    st.divider()

            if not future_followups.empty:

                st.markdown(
                    "#### 📌 Future Follow-ups"
                )

                for _, row in future_followups.iterrows():

                    followup_date = (
                        row["Follow-up Date Parsed"].date()
                    )

                    days_left = (
                        followup_date - today
                    ).days

                    st.write(
                        f"**{row['Company']}** — "
                        f"{followup_date.strftime('%d-%m-%Y')} "
                        f"({days_left} days)"
                    )

    st.divider()

    # =====================================================
    # STATUS CHART
    # =====================================================

    if not df.empty:

        st.subheader(
            "📌 Application Status Overview"
        )

        status_counts = (
            df["Status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = [
            "Status",
            "Count"
        ]

        fig = px.bar(
            status_counts,
            x="Status",
            y="Count",
            text="Count",
            title="Applications by Status"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


# =========================================================
# ADD APPLICATION
# =========================================================

elif page == "Add Application":

    st.title("➕ Add Job Application")

    with st.form(
        "add_application_form",
        clear_on_submit=True
    ):

        company = st.text_input(
            "Company Name *"
        )

        role = st.text_input(
            "Job Role *"
        )

        col1, col2 = st.columns(2)

        with col1:

            location = st.text_input(
                "Location"
            )

        with col2:

            salary = st.text_input(
                "Salary"
            )

        col3, col4 = st.columns(2)

        with col3:

            application_date = st.date_input(
                "Application Date",
                value=date.today()
            )

        with col4:

            status = st.selectbox(
                "Status",
                [
                    "Applied",
                    "Screening",
                    "Interview",
                    "Selected",
                    "Rejected"
                ]
            )

        job_type = st.selectbox(
            "Job Type",
            [
                "Full-time",
                "Part-time",
                "Internship",
                "Contract"
            ]
        )

        # -------------------------------------------------
        # INTERVIEW DATE
        # -------------------------------------------------

        st.subheader(
            "📅 Interview & Follow-up"
        )

        interview_enabled = st.checkbox(
            "Add Interview Date"
        )

        interview_date = None

        if interview_enabled:

            interview_date = st.date_input(
                "Interview Date",
                value=date.today()
            )

        # -------------------------------------------------
        # FOLLOW-UP DATE
        # -------------------------------------------------

        followup_enabled = st.checkbox(
            "Add Follow-up Date"
        )

        follow_up_date = None

        if followup_enabled:

            follow_up_date = st.date_input(
                "Follow-up Date",
                value=date.today()
            )

        notes = st.text_area(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Add Application"
        )

        if submitted:

            if not company.strip():

                st.error(
                    "Please enter the company name."
                )

            elif not role.strip():

                st.error(
                    "Please enter the job role."
                )

            else:

                interview_date_string = (
                    interview_date.isoformat()
                    if interview_date
                    else None
                )

                follow_up_date_string = (
                    follow_up_date.isoformat()
                    if follow_up_date
                    else None
                )

                add_application(
                    company.strip(),
                    role.strip(),
                    location.strip(),
                    salary.strip(),
                    application_date.isoformat(),
                    status,
                    job_type,
                    notes.strip(),
                    interview_date_string,
                    follow_up_date_string
                )

                st.success(
                    "Application added successfully! 🎉"
                )

                st.rerun()


# =========================================================
# APPLICATIONS
# =========================================================

elif page == "Applications":

    st.title("📋 Applications")

    if df.empty:

        st.info(
            "No applications found."
        )

    else:

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        search = st.text_input(
            "🔍 Search by company or role"
        )

        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        status_filter = st.selectbox(
            "Filter by Status",
            [
                "All",
                "Applied",
                "Screening",
                "Interview",
                "Selected",
                "Rejected"
            ]
        )

        filtered_df = df.copy()

        if search:

            search_lower = search.lower()

            filtered_df = filtered_df[
                filtered_df["Company"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
                |
                filtered_df["Role"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
            ]

        if status_filter != "All":

            filtered_df = filtered_df[
                filtered_df["Status"]
                == status_filter
            ]

        # -------------------------------------------------
        # DISPLAY TABLE
        # -------------------------------------------------

        display_columns = [
            "ID",
            "Company",
            "Role",
            "Location",
            "Salary",
            "Application Date",
            "Status",
            "Job Type",
            "Interview Date",
            "Follow-up Date",
            "Notes"
        ]

        st.dataframe(
            filtered_df[display_columns],
            width="stretch",
            hide_index=True
        )

        st.divider()

        # =================================================
        # UPDATE STATUS
        # =================================================

        st.subheader(
            "🔄 Update Application Status"
        )

        application_ids = filtered_df["ID"].tolist()

        if application_ids:

            selected_id = st.selectbox(
                "Select Application ID",
                application_ids
            )

            selected_row = filtered_df[
                filtered_df["ID"] == selected_id
            ].iloc[0]

            status_options = [
                "Applied",
                "Screening",
                "Interview",
                "Selected",
                "Rejected"
            ]

            new_status = st.selectbox(
                "New Status",
                status_options,
                index=status_options.index(
                    selected_row["Status"]
                )
            )

            if st.button(
                "Update Status"
            ):

                if update_status(
                    selected_id,
                    new_status
                ):

                    st.success(
                        "Status updated successfully!"
                    )

                    st.rerun()

        st.divider()

        # =================================================
        # EDIT APPLICATION
        # =================================================

        st.subheader(
            "✏️ Edit Application"
        )

        edit_id = st.selectbox(
            "Select Application to Edit",
            application_ids,
            key="edit_application"
        )

        edit_row = filtered_df[
            filtered_df["ID"] == edit_id
        ].iloc[0]

        with st.form(
            "edit_application_form"
        ):

            edit_company = st.text_input(
                "Company Name",
                value=str(edit_row["Company"])
            )

            edit_role = st.text_input(
                "Job Role",
                value=str(edit_row["Role"])
            )

            edit_location = st.text_input(
                "Location",
                value=(
                    ""
                    if pd.isna(edit_row["Location"])
                    else str(edit_row["Location"])
                )
            )

            edit_salary = st.text_input(
                "Salary",
                value=(
                    ""
                    if pd.isna(edit_row["Salary"])
                    else str(edit_row["Salary"])
                )
            )

            # -------------------------------------------------
            # APPLICATION DATE
            # -------------------------------------------------

            application_value = edit_row[
                "Application Date"
            ]

            try:

                if (
                    pd.isna(application_value)
                    or str(application_value).strip()
                    in ["", "None", "nan"]
                ):

                    current_application_date = date.today()

                else:

                    current_application_date = (
                        pd.to_datetime(
                            application_value
                        ).date()
                    )

            except (
                ValueError,
                TypeError,
                AttributeError
            ):

                current_application_date = date.today()

            edit_application_date = st.date_input(
                "Application Date",
                value=current_application_date,
                key=f"edit_application_date_{edit_id}"
            )

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            status_options = [
                "Applied",
                "Screening",
                "Interview",
                "Selected",
                "Rejected"
            ]

            current_status = (
                edit_row["Status"]
                if edit_row["Status"]
                in status_options
                else "Applied"
            )

            edit_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(
                    current_status
                ),
                key=f"edit_status_{edit_id}"
            )

            # -------------------------------------------------
            # JOB TYPE
            # -------------------------------------------------

            job_type_options = [
                "Full-time",
                "Part-time",
                "Internship",
                "Contract"
            ]

            current_job_type = (
                edit_row["Job Type"]
                if edit_row["Job Type"]
                in job_type_options
                else "Full-time"
            )

            edit_job_type = st.selectbox(
                "Job Type",
                job_type_options,
                index=job_type_options.index(
                    current_job_type
                ),
                key=f"edit_job_type_{edit_id}"
            )

            # -------------------------------------------------
            # INTERVIEW DATE
            # -------------------------------------------------

            interview_value = edit_row[
                "Interview Date"
            ]

            has_interview_date = not (
                pd.isna(interview_value)
                or str(interview_value).strip()
                in ["", "None", "nan"]
            )

            edit_interview_enabled = st.checkbox(
                "Has Interview Date",
                value=has_interview_date,
                key=f"edit_interview_enabled_{edit_id}"
            )

            edit_interview_date = None

            if edit_interview_enabled:

                if has_interview_date:

                    try:

                        current_interview_date = (
                            pd.to_datetime(
                                interview_value
                            ).date()
                        )

                    except (
                        ValueError,
                        TypeError,
                        AttributeError
                    ):

                        current_interview_date = date.today()

                else:

                    current_interview_date = date.today()

                edit_interview_date = st.date_input(
                    "Interview Date",
                    value=current_interview_date,
                    key=f"edit_interview_date_{edit_id}"
                )

            # -------------------------------------------------
            # FOLLOW-UP DATE
            # -------------------------------------------------

            followup_value = edit_row[
                "Follow-up Date"
            ]

            has_followup_date = not (
                pd.isna(followup_value)
                or str(followup_value).strip()
                in ["", "None", "nan"]
            )

            edit_followup_enabled = st.checkbox(
                "Has Follow-up Date",
                value=has_followup_date,
                key=f"edit_followup_enabled_{edit_id}"
            )

            edit_follow_up_date = None

            if edit_followup_enabled:

                if has_followup_date:

                    try:

                        current_followup_date = (
                            pd.to_datetime(
                                followup_value
                            ).date()
                        )

                    except (
                        ValueError,
                        TypeError,
                        AttributeError
                    ):

                        current_followup_date = date.today()

                else:

                    current_followup_date = date.today()

                edit_follow_up_date = st.date_input(
                    "Follow-up Date",
                    value=current_followup_date,
                    key=f"edit_followup_date_{edit_id}"
                )

            # -------------------------------------------------
            # NOTES
            # -------------------------------------------------

            edit_notes = st.text_area(
                "Notes",
                value=(
                    ""
                    if pd.isna(edit_row["Notes"])
                    else str(edit_row["Notes"])
                ),
                key=f"edit_notes_{edit_id}"
            )

            save_changes = st.form_submit_button(
                "💾 Save Changes"
            )

            if save_changes:

                if not edit_company.strip():

                    st.error(
                        "Company name cannot be empty."
                    )

                elif not edit_role.strip():

                    st.error(
                        "Job role cannot be empty."
                    )

                else:

                    interview_string = (
                        edit_interview_date.isoformat()
                        if edit_interview_date
                        else None
                    )

                    followup_string = (
                        edit_follow_up_date.isoformat()
                        if edit_follow_up_date
                        else None
                    )

                    update_application(
                        edit_id,
                        edit_company.strip(),
                        edit_role.strip(),
                        edit_location.strip(),
                        edit_salary.strip(),
                        edit_application_date.isoformat(),
                        edit_status,
                        edit_job_type,
                        edit_notes.strip(),
                        interview_string,
                        followup_string
                    )

                    st.success(
                        "Application updated successfully! ✅"
                    )

                    st.rerun()

        st.divider()

        # =================================================
        # DELETE APPLICATION
        # =================================================

        st.subheader(
            "🗑️ Delete Application"
        )

        delete_id = st.selectbox(
            "Select Application to Delete",
            application_ids,
            key="delete_application"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this application.",
            key="confirm_delete"
        )

        if st.button(
            "Delete Application",
            type="primary"
        ):

            if not confirm_delete:

                st.warning(
                    "Please confirm deletion first."
                )

            else:

                if delete_application(
                    delete_id
                ):

                    st.success(
                        "Application deleted successfully."
                    )

                    st.rerun()

        st.divider()

        # =================================================
        # CSV EXPORT
        # =================================================

        st.subheader(
            "📥 Export Applications"
        )

        csv_data = filtered_df[
            display_columns
        ].to_csv(
            index=False
        )

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="jobtrack_applications.csv",
            mime="text/csv",
            width="stretch"
        )


# =========================================================
# APPLICATION DETAILS
# =========================================================

elif page == "Application Details":

    st.title("🔎 Application Details")

    if df.empty:

        st.info(
            "No applications available. "
            "Add an application first."
        )

    else:

        # -------------------------------------------------
        # SELECT APPLICATION
        # -------------------------------------------------

        application_ids = df["ID"].tolist()

        selected_id = st.selectbox(
            "Select Application",
            application_ids,
            format_func=lambda x: (
                f"#{x} - "
                f"{df.loc[df['ID'] == x, 'Company'].iloc[0]} - "
                f"{df.loc[df['ID'] == x, 'Role'].iloc[0]}"
            )
        )

        selected_application = df[
            df["ID"] == selected_id
        ].iloc[0]

        st.divider()

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        st.subheader(
            f"💼 {selected_application['Company']}"
        )

        st.write(
            f"### {selected_application['Role']}"
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        status = selected_application["Status"]

        if status == "Selected":

            st.success(
                "🎉 SELECTED"
            )

        elif status == "Interview":

            st.info(
                "🎯 INTERVIEW"
            )

        elif status == "Rejected":

            st.error(
                "❌ REJECTED"
            )

        elif status == "Screening":

            st.warning(
                "🔍 SCREENING"
            )

        else:

            st.write(
                "📨 APPLIED"
            )

        st.divider()

        # -------------------------------------------------
        # JOB INFORMATION
        # -------------------------------------------------

        st.subheader(
            "📋 Job Information"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("**🏢 Company**")

            st.write(
                selected_application["Company"]
            )

            st.markdown("**📍 Location**")

            location_value = (
                selected_application["Location"]
            )

            st.write(
                "Not specified"
                if pd.isna(location_value)
                or str(location_value).strip() == ""
                else str(location_value)
            )

        with col2:

            st.markdown("**💼 Job Role**")

            st.write(
                selected_application["Role"]
            )

            st.markdown("**💰 Salary**")

            salary_value = (
                selected_application["Salary"]
            )

            st.write(
                "Not specified"
                if pd.isna(salary_value)
                or str(salary_value).strip() == ""
                else str(salary_value)
            )

        with col3:

            st.markdown("**📝 Job Type**")

            st.write(
                selected_application["Job Type"]
            )

            st.markdown("**📅 Applied Date**")

            application_date = (
                selected_application[
                    "Application Date"
                ]
            )

            if (
                pd.isna(application_date)
                or str(application_date).strip()
                in ["", "None", "nan"]
            ):

                st.write(
                    "Not specified"
                )

            else:

                try:

                    formatted_application_date = (
                        pd.to_datetime(
                            application_date
                        ).strftime(
                            "%d-%m-%Y"
                        )
                    )

                    st.write(
                        formatted_application_date
                    )

                except Exception:

                    st.write(
                        str(application_date)
                    )

        st.divider()

        # -------------------------------------------------
        # INTERVIEW & FOLLOW-UP
        # -------------------------------------------------

        st.subheader(
            "📅 Interview & Follow-up"
        )

        interview_date = selected_application[
            "Interview Date"
        ]

        followup_date = selected_application[
            "Follow-up Date"
        ]

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                "### 🎯 Interview Date"
            )

            if (
                pd.isna(interview_date)
                or str(interview_date).strip()
                in ["", "None", "nan"]
            ):

                st.info(
                    "No interview date scheduled."
                )

            else:

                try:

                    interview_formatted = (
                        pd.to_datetime(
                            interview_date
                        ).strftime(
                            "%d-%m-%Y"
                        )
                    )

                    st.success(
                        f"📅 {interview_formatted}"
                    )

                except Exception:

                    st.write(
                        str(interview_date)
                    )

        with col2:

            st.markdown(
                "### 🔔 Follow-up Date"
            )

            if (
                pd.isna(followup_date)
                or str(followup_date).strip()
                in ["", "None", "nan"]
            ):

                st.info(
                    "No follow-up date scheduled."
                )

            else:

                try:

                    followup_formatted = (
                        pd.to_datetime(
                            followup_date
                        ).strftime(
                            "%d-%m-%Y"
                        )
                    )

                    st.success(
                        f"📅 {followup_formatted}"
                    )

                except Exception:

                    st.write(
                        str(followup_date)
                    )

        st.divider()

        # -------------------------------------------------
        # NOTES
        # -------------------------------------------------

        st.subheader(
            "📝 Notes"
        )

        notes = selected_application[
            "Notes"
        ]

        if (
            pd.isna(notes)
            or str(notes).strip() == ""
        ):

            st.info(
                "No notes added for this application."
            )

        else:

            st.text_area(
                "Application Notes",
                value=str(notes),
                height=150,
                disabled=True
            )

        st.divider()

        # -------------------------------------------------
        # QUICK STATUS UPDATE
        # -------------------------------------------------

        st.subheader(
            "🔄 Quick Status Update"
        )

        status_options = [
            "Applied",
            "Screening",
            "Interview",
            "Selected",
            "Rejected"
        ]

        current_status = (
            selected_application["Status"]
        )

        if current_status not in status_options:

            current_status = "Applied"

        new_status = st.selectbox(
            "Change Status",
            status_options,
            index=status_options.index(
                current_status
            ),
            key=f"details_status_{selected_id}"
        )

        if st.button(
            "Update Status",
            key=f"details_update_status_{selected_id}"
        ):

            if update_status(
                selected_id,
                new_status
            ):

                st.success(
                    "Status updated successfully! ✅"
                )

                st.rerun()

        st.divider()

        # -------------------------------------------------
        # APPLICATION SUMMARY
        # -------------------------------------------------

        st.subheader(
            "📊 Application Summary"
        )

        summary_col1, summary_col2, summary_col3 = (
            st.columns(3)
        )

        with summary_col1:

            st.metric(
                "Application ID",
                selected_application["ID"]
            )

        with summary_col2:

            st.metric(
                "Current Status",
                selected_application["Status"]
            )

        with summary_col3:

            if (
                not pd.isna(interview_date)
                and str(interview_date).strip()
                not in ["", "None", "nan"]
            ):

                st.metric(
                    "Interview",
                    "Scheduled"
                )

            else:

                st.metric(
                    "Interview",
                    "Not Scheduled"
                )


# =========================================================
# ANALYTICS
# =========================================================

elif page == "Analytics":

    st.title("📈 Job Application Analytics")

    if df.empty:

        st.info(
            "Add applications to see analytics."
        )

    else:

        analytics_df = df.copy()

        analytics_df["Application Date"] = pd.to_datetime(
            analytics_df["Application Date"],
            errors="coerce"
        )

        # =================================================
        # STATUS ANALYSIS
        # =================================================

        st.subheader(
            "📊 Applications by Status"
        )

        status_counts = (
            analytics_df["Status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = [
            "Status",
            "Count"
        ]

        fig_status = px.bar(
            status_counts,
            x="Status",
            y="Count",
            text="Count",
            title="Application Status"
        )

        st.plotly_chart(
            fig_status,
            width="stretch"
        )

        # =================================================
        # COMPANY ANALYSIS
        # =================================================

        st.subheader(
            "🏢 Applications by Company"
        )

        company_counts = (
            analytics_df["Company"]
            .value_counts()
            .reset_index()
        )

        company_counts.columns = [
            "Company",
            "Applications"
        ]

        fig_company = px.bar(
            company_counts,
            x="Company",
            y="Applications",
            text="Applications",
            title="Applications by Company"
        )

        st.plotly_chart(
            fig_company,
            width="stretch"
        )

        # =================================================
        # JOB TYPE
        # =================================================

        st.subheader(
            "💼 Applications by Job Type"
        )

        job_type_counts = (
            analytics_df["Job Type"]
            .value_counts()
            .reset_index()
        )

        job_type_counts.columns = [
            "Job Type",
            "Count"
        ]

        fig_job_type = px.pie(
            job_type_counts,
            names="Job Type",
            values="Count",
            hole=0.4,
            title="Job Type Distribution"
        )

        st.plotly_chart(
            fig_job_type,
            width="stretch"
        )

        # =================================================
        # APPLICATIONS OVER TIME
        # =================================================

        st.subheader(
            "📅 Applications Over Time"
        )

        applications_over_time = (
            analytics_df
            .dropna(
                subset=["Application Date"]
            )
            .groupby(
                "Application Date"
            )
            .size()
            .reset_index(
                name="Applications"
            )
            .sort_values(
                "Application Date"
            )
        )

        if not applications_over_time.empty:

            fig_time = px.line(
                applications_over_time,
                x="Application Date",
                y="Applications",
                markers=True,
                title="Application Trend"
            )

            st.plotly_chart(
                fig_time,
                width="stretch"
            )

        # =================================================
        # INTERVIEW PERFORMANCE
        # =================================================

        st.subheader(
            "🎯 Interview Performance"
        )

        total = len(
            analytics_df
        )

        interview_count = len(
            analytics_df[
                analytics_df["Status"]
                == "Interview"
            ]
        )

        selected_count = len(
            analytics_df[
                analytics_df["Status"]
                == "Selected"
            ]
        )

        interview_or_selected = (
            interview_count
            + selected_count
        )

        interview_percentage = (
            interview_or_selected
            / total
            * 100
            if total > 0
            else 0
        )

        selection_percentage = (
            selected_count
            / total
            * 100
            if total > 0
            else 0
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Interview / Selected",
                interview_or_selected
            )

        with col2:

            st.metric(
                "Interview Conversion",
                f"{interview_percentage:.1f}%"
            )

        with col3:

            st.metric(
                "Selection Rate",
                f"{selection_percentage:.1f}%"
            )

        # =================================================
        # ANALYTICS SUMMARY
        # =================================================

        st.subheader(
            "📋 Analytics Summary"
        )

        summary_data = {
            "Metric": [
                "Total Applications",
                "Applied",
                "Screening",
                "Interviews",
                "Selected",
                "Rejected",
                "Success Rate"
            ],
            "Value": [
                total,
                len(
                    analytics_df[
                        analytics_df["Status"]
                        == "Applied"
                    ]
                ),
                len(
                    analytics_df[
                        analytics_df["Status"]
                        == "Screening"
                    ]
                ),
                interview_count,
                selected_count,
                len(
                    analytics_df[
                        analytics_df["Status"]
                        == "Rejected"
                    ]
                ),
                f"{calculate_success_rate(analytics_df):.1f}%"
            ]
        }

        summary_df = pd.DataFrame(
            summary_data
        )

        st.dataframe(
            summary_df,
            width="stretch",
            hide_index=True
        )
