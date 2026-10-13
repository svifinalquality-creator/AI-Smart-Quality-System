

import streamlit as st
import pandas as pd
from openai import OpenAI
from pathlib import Path

st.set_page_config(
    page_title="AI Smart Quality System",
    page_icon="🔧",
    layout="wide"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    page_title="AI Smart Quality System",
    page_icon="🔧",
    layout="wide"
)
from pathlib import Path

with st.sidebar:
    st.title("🔧 Quality System")
    st.divider()

    menu = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📊 Quality Analysis",
            "🤖 AI Quality Analysis",
            "🔧 Rework Analysis",
            "📄 Reports"
        ]
    )

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
# Google Sheet connection
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZnae3JXIjgSJU1-y2O0JNAunb6kwvYVfxdRiW9bDyWI_C4Zh5qnCaXYAJxZcEUD9i2VEknx2dould/pub?output=csv"

# Read data from Google Sheet
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip().str.upper()
st.subheader("📋 Live Google Sheet Data")

st.dataframe(df, use_container_width=True)

if menu == "🏠 Dashboard":
    st.title("🔧 AI Smart Quality Management System")
    st.write("Welcome to the Smart Quality Dashboard")
    
st.divider()

st.subheader("📊 Quality Overview")

col1, col2, col3, col4 = st.columns(4)

total_parts = df["INVORD PART COUNT"].sum()
rejected_parts = df["REJECTED QUANTITY"].sum()

rejection_rate = (rejected_parts / total_parts * 100) if total_parts > 0 else 0

problem_col = next(
    (col for col in df.columns if "PROBLEM" in col),
    None
)

if problem_col and not df[problem_col].dropna().empty:
    top_defect = df[problem_col].value_counts().idxmax()
else:
    top_defect = "None"
col1.metric("Total Parts", f"{total_parts:,.0f}")
col2.metric("Rejected Parts", f"{rejected_parts:,.0f}")
col3.metric("Rejection Rate", f"{rejection_rate:.2f}%")
col4.metric("Top Defect", top_defect)

st.divider()

st.subheader("📋 Rejection Data")

# Show rejected parts
rejected_data = df[df["REJECTED QUANTITY"] > 0]

if not rejected_data.empty:
    st.dataframe(rejected_data, use_container_width=True)
else:
    st.info("No rejected parts found.")
    st.divider()

st.subheader("📊 Defect Analysis")

if problem_col:
    defect_data = (
        rejected_data.groupby(problem_col)["REJECTED QUANTITY"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(defect_data)
else:
    st.warning("Problem description column not found.")
    
    st.divider()

st.subheader("🏭 Supplier-wise Rejection")

supplier_col = next(
    (col for col in df.columns if "SUPPLIER" in col),
    None
)

if supplier_col:
    supplier_data = (
        rejected_data.groupby(supplier_col)["REJECTED QUANTITY"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(supplier_data)
else:
    st.warning("Supplier column not found.")
    
    st.divider()

st.subheader("📅 Date-wise Rejection Trend")

date_col = next(
    (col for col in df.columns if col == "DATE"),
    None
)

if date_col:
    date_data = df.copy()
    date_data[date_col] = pd.to_datetime(
        date_data[date_col],
        dayfirst=True,
        errors="coerce"
    )

    date_data = (
        date_data.dropna(subset=[date_col])
        .groupby(date_col)["REJECTED QUANTITY"]
        .sum()
        .sort_index()
    )

    st.line_chart(date_data)
else:
    st.warning("Date column not found.")
    
    st.divider()

st.subheader("🔧 Rework Analysis")

rework_col = next(
    (col for col in df.columns if "REWORK" in col),
    None
)

if rework_col:
    rework_data = pd.to_numeric(
        df[rework_col], errors="coerce"
    ).fillna(0)

    total_rework = rework_data.sum()

    st.metric("Total Rework Quantity", f"{total_rework:,.0f}")

    rework_by_date = (
        pd.DataFrame({
            "DATE": pd.to_datetime(df["DATE"], dayfirst=True, errors="coerce"),
            "REWORK": rework_data
        })
        .dropna(subset=["DATE"])
        .groupby("DATE")["REWORK"]
        .sum()
        .sort_index()
    )

    st.line_chart(rework_by_date)

else:
    st.warning("Rework column not found.")
    
    st.divider()

st.divider()

st.subheader("🤖 AI Quality Analysis")

# Convert quantities to numbers
rejected_data["REJECTED QUANTITY"] = pd.to_numeric(
    rejected_data["REJECTED QUANTITY"], errors="coerce"
).fillna(0)

top_defect_row = (
    rejected_data.groupby(problem_col)["REJECTED QUANTITY"]
    .sum()
    .sort_values(ascending=False)
)


st.divider()
st.subheader("🤖 AI Quality Analysis")

if st.button("Run AI Analysis"):

  defect_summary = (
    rejected_data.groupby(problem_col)["REJECTED QUANTITY"]
    .sum()
    .sort_values(ascending=False)
)
defect_summary = (
    rejected_data.groupby(problem_col)["REJECTED QUANTITY"]
    .sum()
    .sort_values(ascending=False)
)

part_summary = (
    rejected_data.groupby("PART NUMBER")["REJECTED QUANTITY"]
    .sum()
    .sort_values(ascending=False)
)
top_defect = defect_summary.index[0] if not defect_summary.empty else "No defect data"
top_defect_quantity = defect_summary.iloc[0] if not defect_summary.empty else 0

quality_summary = f"""
Total Parts: {total_parts}
Rejected Parts: {rejected_parts}
Rejection Rate: {rejection_rate:.2f}%
Top Defect: {top_defect}
Top Defect Rejection Quantity: {top_defect_quantity}
Total Rework Quantity: {total_rework}

Defect-wise Rejection Quantity:
{defect_summary.to_string()}
"""
response = client.responses.create(
    model="gpt-5.6-luna",
input=[
    {
        "role": "user",
"content": f"""You are a manufacturing quality engineer.

Analyze the following quality data:

{quality_summary}
Provide:

1. Top quality issue
2. Defect-wise rejection quantity
3. Possible root causes
4. 5 Why Analysis
5. Immediate containment action
6. Corrective action
7. Preventive action
8. Risk level
9. What should be verified on the shop floor
10. Recommended next action

For the 5 Why Analysis:
- Start from the actual defect.
- Ask why step by step.
- Do not assume a confirmed root cause.
- Clearly mark unverified causes as hypotheses.
- Stop when the available data is insufficient.

Do not invent facts.
Clearly label root causes as hypotheses unless confirmed by the provided data.
"""
                }
            ]
        )

st.write(response.output_text)

pdf_file = "AI_Smart_Quality_Complete_Report.pdf"

pdf_data = df.copy()

pdf_data["REJECTED QUANTITY"] = pd.to_numeric(
    pdf_data["REJECTED QUANTITY"],
    errors="coerce"
).fillna(0)

pdf_data = pdf_data[pdf_data["REJECTED QUANTITY"] > 0].copy()

pdf_data["DATE"] = pd.to_datetime(
    pdf_data["DATE"],
    dayfirst=True,
    errors="coerce"
)

pdf_data = pdf_data.dropna(subset=["DATE"])

part_name_col = next(
    (col for col in pdf_data.columns if "PART NAME" in col),
    None
)

part_number_col = next(
    (col for col in pdf_data.columns if "PART NUMBER" in col),
    None
)

problem_col = next(
    (col for col in pdf_data.columns if "PROBLEM" in col),
    None
)

pdf_data["DATE"] = pdf_data["DATE"].dt.strftime("%d-%m-%Y")

table_data = [
    ["Date", "Part Name", "Part Number", "Defect", "Rejection Qty"]
]

for _, row in pdf_data.iterrows():
    table_data.append([
        str(row["DATE"]),
        str(row[part_name_col]) if part_name_col else "",
        str(row[part_number_col]) if part_number_col else "",
        str(row[problem_col]) if problem_col else "",
        str(int(row["REJECTED QUANTITY"]))
    ])

doc = SimpleDocTemplate(
    pdf_file,
    pagesize=landscape(A4),
    rightMargin=20,
    leftMargin=20,
    topMargin=20,
    bottomMargin=20
)

styles = getSampleStyleSheet()

story = []

story.append(
    Paragraph(
        "AI Smart Quality Management System",
        styles["Title"]
    )
)

story.append(Spacer(1, 10))

story.append(
    Paragraph(
        "Date-wise Quality Rejection Report",
        styles["Heading2"]
    )
)

story.append(Spacer(1, 10))

table = Table(
    table_data,
    repeatRows=1,
    colWidths=[75, 180, 110, 180, 85]
)

table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (4, 1), (4, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [colors.white, colors.lightgrey]
        )
    ])
)

story.append(table)

story.append(PageBreak())

story.append(
    Paragraph(
        "AI Quality Analysis",
        styles["Heading1"]
    )
)

story.append(Spacer(1, 10))

report_text = response["message"]["content"]

for line in report_text.split("\n"):
    line = line.strip()

    if line:
        safe_line = (
            line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        story.append(
            Paragraph(
                safe_line,
                styles["BodyText"]
            )
        )

        story.append(Spacer(1, 6))

doc.build(story)

with open(pdf_file, "rb") as file:
    st.download_button(
        "📄 Download Complete Quality Report",
        file,
        file_name="AI_Smart_Quality_Complete_Report.pdf",
        mime="application/pdf"
    )
