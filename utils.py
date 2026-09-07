import pandas as pd


# ---------------------------------------------------------
# CONVERT DATABASE DATA TO DATAFRAME
# ---------------------------------------------------------

def applications_to_dataframe(data):

    columns = [
        "ID",
        "Company",
        "Role",
        "Location",
        "Salary",
        "Application Date",
        "Status",
        "Job Type",
        "Notes",
        "Interview Date",
        "Follow-up Date"
    ]

    return pd.DataFrame(
        data,
        columns=columns
    )


# ---------------------------------------------------------
# CALCULATE SUCCESS RATE
# ---------------------------------------------------------

def calculate_success_rate(df):

    if df.empty:
        return 0

    selected = len(
        df[df["Status"] == "Selected"]
    )

    total = len(df)

    return (selected / total) * 100