# app.py
from flask import Flask, render_template, request, send_from_directory, send_file
from utils.ocr_utils import extract_text_from_image
from utils.date_parser import parse_expiry_date
from utils.damage_detection import detect_damage
from utils.report_genearator import generate_daily_report, generate_weekly_report

import os, base64
from datetime import datetime, date
import database   # loads db = Database()

app = Flask(__name__)

# ---------------- FOLDERS ----------------
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# ---------------- INIT DB ----------------
database.db.init_db()


# ---------------- STATIC SERVE ----------------
@app.route('/processed/<path:filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)


# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html')


# ---------------- COMMON PROCESSING PIPELINE ----------------
def _process_common(filepath, original_filename):

    extracted_text = extract_text_from_image(filepath)
    expiry_status, expiry_date = parse_expiry_date(extracted_text)
    damage_status, processed_filename = detect_damage(filepath)

    database.db.save_scan(
        original_filename,
        processed_filename,
        str(extracted_text),
        expiry_status,
        expiry_date,
        damage_status
    )

    return extracted_text, expiry_status, expiry_date, damage_status, processed_filename


# ---------------- PROCESS FILE UPLOAD ----------------
@app.route('/process', methods=['POST'])
def process():
    file = request.files.get('file')
    if not file or file.filename == "":
        return "No file uploaded", 400

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(save_path)

    extracted, status, date_val, damage, processed = _process_common(save_path, file.filename)

    return render_template(
        "result.html",
        extracted_text=extracted,
        expiry_status=status,
        expiry_date=date_val,
        damage_status=damage,
        processed_image=processed
    )


# ---------------- PROCESS CAMERA CAPTURE ----------------
@app.route('/capture', methods=['POST'])
def capture():
    img_data = request.form.get('imageData')
    if not img_data:
        return "No image data", 400

    img_data = img_data.split(",")[1]

    filename = f"captured_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(img_data))

    extracted, status, date_val, damage, processed = _process_common(filepath, filename)

    return render_template(
        "result.html",
        extracted_text=extracted,
        expiry_status=status,
        expiry_date=date_val,
        damage_status=damage,
        processed_image=processed
    )


# ---------------- HISTORY PAGE ----------------
@app.route('/history')
def history():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 8, type=int)

    rows, total = database.db.get_scans_page(page, per_page)
    total_pages = (total + per_page - 1) // per_page

    scans = [{
        "id": r[0],
        "filename": r[1],
        "processed_filename": r[2],
        "extracted_text": r[3],
        "expiry_status": r[4],
        "expiry_date": r[5],
        "damage_status": r[6],
        "timestamp": r[7]
    } for r in rows]

    return render_template("history.html",
                           scans=scans,
                           total=total,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages)


# ---------------- DAILY REPORT ----------------
@app.route('/daily_report')
def daily_report():
    today_str = date.today().isoformat()
    rows, total = database.db.get_scans_by_date(today_str)

    if total == 0:
        return "No scans found for today's report."

    pdf_path = generate_daily_report(rows)
    return send_file(pdf_path, as_attachment=True)


# ---------------- WEEKLY REPORT PAGE ----------------
@app.route('/weekly-report')
def weekly_report():
    rows = database.db.get_scans_last_7_days()

    chart_labels = [r[0] for r in rows]
    chart_data = [int(r[1]) for r in rows]   # FIXED HERE

    total_scans = sum(chart_data)
    valid_count = database.db.count_expiry_status("Valid")
    expired_count = database.db.count_expiry_status("Expired")

    return render_template(
        "weekly_report.html",
        chart_labels=chart_labels,
        chart_data=chart_data,
        total_scans=total_scans,
        valid_count=valid_count,
        expired_count=expired_count
    )


# ---------------- WEEKLY PDF DOWNLOAD ----------------
@app.route('/weekly_report_pdf')
def weekly_report_pdf():
    rows = database.db.get_scans_last_7_days()

    # Convert weekly rows into full scan rows:
    full_rows = database.db.get_scans_last_7_days_full()

    if not full_rows:
        return "No weekly data available."

    pdf_path = generate_weekly_report(full_rows)
    return send_file(pdf_path, as_attachment=True)



if __name__ == "__main__":
    app.run(debug=True)
