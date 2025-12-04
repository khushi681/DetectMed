import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_daily_report(rows):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    today = date.today().strftime("%Y-%m-%d")
    filename = f"reports/daily_report_{today}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    x, y = 50, height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, f"DetectMed – Daily Report ({today})")
    y -= 40

    # summary
    total = len(rows)
    expired = sum(1 for r in rows if r[4] == "Expired")
    valid = sum(1 for r in rows if r[4] == "Valid")

    c.setFont("Helvetica", 12)
    c.drawString(x, y, f"Total Scans: {total}")
    y -= 20
    c.drawString(x, y, f"Valid: {valid}   Expired: {expired}")
    y -= 30

    # table header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "ID")
    c.drawString(x+40, y, "File")
    c.drawString(x+190, y, "Expiry")
    c.drawString(x+310, y, "Damage")
    c.drawString(x+420, y, "Timestamp")
    y -= 20

    c.line(x, y, width - 50, y)
    y -= 20

    # rows
    c.setFont("Helvetica", 10)
    for r in rows:
        if y < 60:
            c.showPage()
            y = height - 60

        c.drawString(x, y, str(r[0]))
        c.drawString(x+40, y, r[1][:18])
        c.drawString(x+190, y, r[4])
        c.drawString(x+310, y, r[6])
        c.drawString(x+420, y, r[7][:19])
        y -= 16

    c.save()
    return filename


def generate_weekly_report(rows):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    today = date.today().strftime("%Y-%m-%d")
    filename = f"reports/weekly_report_{today}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    x, y = 50, height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, f"DetectMed – Weekly Report (Last 7 Days)")
    y -= 40

    total = len(rows)
    expired = sum(1 for r in rows if r[4] == "Expired")
    valid = sum(1 for r in rows if r[4] == "Valid")

    c.setFont("Helvetica", 12)
    c.drawString(x, y, f"Total Scans: {total}")
    y -= 20
    c.drawString(x, y, f"Valid: {valid}   Expired: {expired}")
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "ID")
    c.drawString(x+40, y, "File")
    c.drawString(x+190, y, "Expiry")
    c.drawString(x+310, y, "Damage")
    c.drawString(x+420, y, "Timestamp")
    y -= 20

    c.line(x, y, width - 50, y)
    y -= 20

    c.setFont("Helvetica", 10)
    for r in rows:
        if y < 60:
            c.showPage()
            y = height - 60

        c.drawString(x, y, str(r[0]))
        c.drawString(x+40, y, r[1][:18])
        c.drawString(x+190, y, r[4])
        c.drawString(x+310, y, r[6])
        c.drawString(x+420, y, r[7][:19])
        y -= 16

    c.save()
    return filename

