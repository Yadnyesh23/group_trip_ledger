from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.reports import ReportResponseSchema


def generate_trip_report_pdf(report: ReportResponseSchema) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="GroupTrip Ledger - Trip Report",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )

    story = []

    # Report heading
    story.append(
        Paragraph("GroupTrip Ledger", styles["ReportTitle"])
    )
    story.append(
        Paragraph("Trip Financial Report", styles["Heading2"])
    )
    story.append(
        Paragraph(
            f"Generated on: {date.today().isoformat()}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 8 * mm))

    # 1. Trip members
    story.append(
        Paragraph("Trip Members", styles["Heading2"])
    )

    member_rows = [["Member Name", "Status", "Joined"]]

    for member in report.members.members:
        member_rows.append([
            member.user_name,
            str(member.status),
            str(member.joined_at),
        ])

    story.append(_make_table(member_rows))
    story.append(Spacer(1, 6 * mm))

    # 2. Expenses and allocations
    story.append(
        Paragraph("Expenses and Allocations", styles["Heading2"])
    )

    for expense in report.expenses.expenses:
        story.append(
            Paragraph(
                f"{expense.name} - INR {expense.amount:.2f}",
                styles["Heading3"],
            )
        )

        split_type = getattr(
            expense.split_type,
            "value",
            expense.split_type,
        )

        story.append(
            Paragraph(
                f"Paid by: {expense.paid_by_name} | "
                f"Date: {expense.expense_date} | "
                f"Split: {split_type}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 2 * mm))

        allocation_rows = [
            ["Member Name", "Allocated Amount (INR)"]
        ]

        for allocation in expense.allocations:
            allocation_rows.append([
                allocation.member_name,
                f"{allocation.amount:.2f}",
            ])

        story.append(_make_table(allocation_rows))
        story.append(Spacer(1, 4 * mm))

    story.append(Spacer(1, 3 * mm))

    # 3. Trip balances
    story.append(
        Paragraph("Trip Balances", styles["Heading2"])
    )

    balance_rows = [
        ["Member Name", "Net Balance (INR)"]
    ]

    for balance in report.balances.balances:
        balance_rows.append([
            balance.member_name,
            f"{balance.balance:.2f}",
        ])

    story.append(_make_table(balance_rows))
    story.append(Spacer(1, 6 * mm))

    # 4. Suggested settlements
    story.append(
        Paragraph("Suggested Settlements", styles["Heading2"])
    )

    settlement_rows = [
        ["Payer", "Payee", "Amount (INR)"]
    ]

    for settlement in report.settlements.settlements:
        settlement_rows.append([
            settlement.payer_name,
            settlement.payee_name,
            f"{settlement.amount:.2f}",
        ])

    if len(settlement_rows) == 1:
        story.append(
            Paragraph(
                "No settlements are currently required.",
                styles["Normal"],
            )
        )
    else:
        story.append(_make_table(settlement_rows))

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def _make_table(rows):
    if len(rows[0]) == 2:
        col_widths = [85 * mm, 75 * mm]
    else:
        col_widths = [55 * mm, 55 * mm, 55 * mm]

    table = Table(
        rows,
        repeatRows=1,
        colWidths=col_widths,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#26364A"),
            ),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.lightgrey,
            ),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    return table