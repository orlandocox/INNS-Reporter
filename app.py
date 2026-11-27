import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date

st.set_page_config(
    page_title="United Utilities INNS Portal",
    layout="wide"
)

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

try:
    reports = pd.read_csv("data/inns_reports.csv")
except:
    reports = pd.DataFrame(
        columns=[
            "Species",
            "Catchment",
            "Site",
            "Latitude",
            "Longitude",
            "Status",
            "Date",
            "Risk Score"
        ]
    )

try:
    treatments = pd.read_csv("data/treatments.csv")
except:
    treatments = pd.DataFrame(
        columns=[
            "Species",
            "Site",
            "Method",
            "Area",
            "Cost",
            "Date",
            "Follow Up"
        ]
    )

try:
    compliance = pd.read_csv("data/compliance.csv")
except:
    compliance = pd.DataFrame(
        columns=[
            "Asset",
            "Operative",
            "Compliant",
            "Date"
        ]
    )

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------

st.sidebar.title("INNS Portal")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Interactive Map",
        "New Report",
        "Treatment Log",
        "Check Clean Dry",
        "AMP9 Planning"
    ]
)

# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------

if page == "Dashboard":

    st.title("United Utilities INNS Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    active_sites = len(reports)

    species_count = (
        reports["Species"].nunique()
        if len(reports) > 0
        else 0
    )

    treatment_count = len(treatments)

    compliance_rate = 0

    if len(compliance) > 0:
        compliance_rate = round(
            (
                compliance["Compliant"].astype(str)
                .str.lower()
                .eq("yes")
                .mean()
            )
            * 100,
            1,
        )

    col1.metric("Active Sites", active_sites)
    col2.metric("Species Recorded", species_count)
    col3.metric("Treatments Logged", treatment_count)
    col4.metric("Compliance %", compliance_rate)

    st.subheader("Species Breakdown")

    if len(reports) > 0:
        species_summary = (
            reports["Species"]
            .value_counts()
            .reset_index()
        )

        species_summary.columns = [
            "Species",
            "Records"
        ]

        st.bar_chart(
            species_summary.set_index("Species")
        )

# ------------------------------------------------
# MAP
# ------------------------------------------------

elif page == "Interactive Map":

    st.title("INNS Mapping")

    species_filter = st.selectbox(
        "Filter Species",
        ["All"] + sorted(reports["Species"].unique().tolist())
        if len(reports) > 0
        else ["All"]
    )

    display_data = reports.copy()

    if (
        species_filter != "All"
        and len(display_data) > 0
    ):
        display_data = display_data[
            display_data["Species"]
            == species_filter
        ]

    m = folium.Map(
        location=[54.6, -2.8],
        zoom_start=7
    )

    for _, row in display_data.iterrows():

        colour = "red"

        if row["Status"] == "Under Treatment":
            colour = "orange"

        elif row["Status"] == "Eradicated":
            colour = "green"

        elif row["Status"] == "Monitoring":
            colour = "blue"

        popup = f"""
        <b>{row['Species']}</b><br>
        Site: {row['Site']}<br>
        Status: {row['Status']}<br>
        Risk Score: {row['Risk Score']}
        """

        folium.Marker(
            location=[
                row["Latitude"],
                row["Longitude"]
            ],
            popup=popup,
            icon=folium.Icon(
                color=colour
            )
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=650
    )

# ------------------------------------------------
# NEW REPORT
# ------------------------------------------------

elif page == "New Report":

    st.title("Create New INNS Report")

    with st.form("report_form"):

        species = st.text_input("Species")

        catchment = st.text_input(
            "Catchment"
        )

        site = st.text_input("Site")

        latitude = st.number_input(
            "Latitude",
            value=54.5
        )

        longitude = st.number_input(
            "Longitude",
            value=-2.5
        )

        status = st.selectbox(
            "Status",
            [
                "Active",
                "Under Treatment",
                "Monitoring",
                "Eradicated"
            ]
        )

        risk_score = st.slider(
            "Risk Score",
            0,
            100,
            50
        )

        submit = st.form_submit_button(
            "Save Report"
        )

        if submit:

            new_record = pd.DataFrame(
                [{
                    "Species": species,
                    "Catchment": catchment,
                    "Site": site,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Status": status,
                    "Date": date.today(),
                    "Risk Score": risk_score
                }]
            )

            reports = pd.concat(
                [
                    reports,
                    new_record
                ]
            )

            reports.to_csv(
                "data/inns_reports.csv",
                index=False
            )

            st.success("Report saved")

# ------------------------------------------------
# TREATMENTS
# ------------------------------------------------

elif page == "Treatment Log":

    st.title("Treatment Logging")

    with st.form("treatment_form"):

        species = st.text_input(
            "Species"
        )

        site = st.text_input("Site")

        method = st.selectbox(
            "Method",
            [
                "Hand Pull",
                "Spray",
                "Cut",
                "Mechanical",
                "Other"
            ]
        )

        area = st.number_input(
            "Area Treated (ha)",
            0.0
        )

        cost = st.number_input(
            "Cost (£)",
            0
        )

        follow_up = st.date_input(
            "Follow Up Date"
        )

        submitted = (
            st.form_submit_button(
                "Log Treatment"
            )
        )

        if submitted:

            new_treatment = pd.DataFrame(
                [{
                    "Species": species,
                    "Site": site,
                    "Method": method,
                    "Area": area,
                    "Cost": cost,
                    "Date": date.today(),
                    "Follow Up": follow_up
                }]
            )

            treatments = pd.concat(
                [
                    treatments,
                    new_treatment
                ]
            )

            treatments.to_csv(
                "data/treatments.csv",
                index=False
            )

            st.success(
                "Treatment recorded"
            )

    st.subheader(
        "Treatment History"
    )

    st.dataframe(
        treatments,
        use_container_width=True
    )

# ------------------------------------------------
# BIOSECURITY
# ------------------------------------------------

elif page == "Check Clean Dry":

    st.title(
        "Check Clean Dry Compliance"
    )

    with st.form(
        "compliance_form"
    ):

        asset = st.text_input(
            "Asset / Reservoir"
        )

        operative = st.text_input(
            "Operative"
        )

        compliant = st.selectbox(
            "Biosecurity Completed?",
            [
                "Yes",
                "No"
            ]
        )

        submitted = (
            st.form_submit_button(
                "Save Entry"
            )
        )

        if submitted:

            new_record = pd.DataFrame(
                [{
                    "Asset": asset,
                    "Operative": operative,
                    "Compliant": compliant,
                    "Date": date.today()
                }]
            )

            compliance = pd.concat(
                [
                    compliance,
                    new_record
                ]
            )

            compliance.to_csv(
                "data/compliance.csv",
                index=False
            )

            st.success(
                "Compliance saved"
            )

    st.dataframe(
        compliance,
        use_container_width=True
    )

# ------------------------------------------------
# AMP9
# ------------------------------------------------

elif page == "AMP9 Planning":

    st.title(
        "AMP9 Investment Planner"
    )

    annual_budget = st.slider(
        "Annual Investment (£)",
        1000,
        500000,
        50000
    )

    estimated_reduction = min(
        round(
            annual_budget / 1000
            * 1.2,
            1
        ),
        100
    )

    st.metric(
        "Estimated Risk Reduction (%)",
        estimated_reduction
    )

    st.info(
        "Demo prediction model. In Databricks this could use actual treatment costs, species spread, asset criticality and catchment risk."
    )
