🌿 DetectMed — AI Medicine Expiry & Damage Scanner

DetectMed is an AI-powered system that helps users scan medicine strips, detect expiry dates, identify damaged packaging, and generate daily & weekly PDF reports.
Built with OpenCV, Flask, OCR, and Chart.js, this app ensures safe medicine usage through smart automation.

🚀 Features
🔍 1. OCR-Based Medicine Text Extraction

Extracts text from medicine strips

Identifies expiry dates dynamically

Handles noisy, complex images

🧪 2. Smart Expiry Date Detection

Labels: VALID, EXPIRED, EXPIRING SOON, UNKNOWN

Auto-parsed from OCR output

Multiple date formats supported

📦 3. Packaging Damage Detection

Uses OpenCV edge detection

Detects inconsistencies in medicine packaging

Saves processed images

📸 4. Image Upload + Camera Capture

Upload from device

Capture using live webcam

Both support full pipeline

📊 5. Weekly Activity Dashboard

Graph of scans (last 7 days) using Chart.js

Shows valid/expired counts

Shows total scans

📄 6. Downloadable PDF Reports

Daily report (detailed table of all scans today)

Weekly report (last 7 days summary + scan details)

📚 7. Scan History

Paginated table

Stores extracted text, expiry, damage status, timestamp

View processed image any time

🧩 Tech Stack
Component	Technology
Backend	Flask (Python)
Database	SQLite
OCR	Tesseract via pytesseract
Image Processing	OpenCV
Frontend	HTML, Tailwind, Flowbite
Charts	Chart.js
PDF Reports	ReportLab
Camera	JavaScript getUserMedia
📁 Folder Structure
DetectMed/
│── app.py
│── database.py
│── requirements.txt
│── README.md
│── scans.db
│
├── uploads/
│    └── (saved original images)
│
├── processed/
│    └── (OpenCV processed images)
│
├── reports/
│    └── daily_report_YYYY-MM-DD.pdf
│    └── weekly_report_YYYY-MM-DD.pdf
│
├── templates/
│    │── base.html
│    │── index.html
│    │── result.html
│    │── history.html
│    │── weekly_report.html
│
├── static/
│    ├── css/
│    ├── js/
│    └── images/
│
└── utils/
     │── ocr_utils.py
     │── date_parser.py
     │── damage_detection.py
     │── report_generator.py

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/YOUR_USERNAME/DetectMed.git
cd DetectMed

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Install Tesseract OCR

Download from:
🔗 https://github.com/UB-Mannheim/tesseract/wiki

Add tesseract.exe path in environment variables or inside your script:

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

5️⃣ Run the App
python app.py


Go to:
👉 http://127.0.0.1:5000/

🧪 How It Works
1. User uploads/captures medicine image

→ Saved in uploads/

2. OCR extracts text

→ Passed to expiry parser

3. Expiry date parsed & validated

If date < today → Expired

If date ~ soon → Expiring Soon

If no date → Unknown

4. Damage detection applied

→ Processed image saved in processed/

5. Result page displays:

Extracted text

Expiry status

Packaging condition

Before/After processed image

6. Database logs entry

→ View it anytime in History page

📥 PDF Reports
🗓 Daily Report

Route:

/daily_report


Contains:

Summary stats

Full table of today’s scans

Expiry & damage info

📅 Weekly Report

Route:

/weekly-report


Download PDF:

/weekly_report_pdf


Includes:

7-day scan chart

Valid/expired summary

Full scan details

📸 Screenshots (Add yours here)

You can include images like:

/static/images/homepage.png
/static/images/result_page.png
/static/images/weekly_chart.png


Example:

![Homepage](static/images/homepage.png)

🛡 License — MIT

This project is licensed under the MIT License, meaning:

✔ You keep full credit
✔ Anyone can use or modify your code
✔ No one can hold you liable for anything

See LICENSE file for details.

🌟 Contributing

Pull requests are welcome!
Submit issues for bugs, ideas, or improvements.

💬 Author

Khushi Jha
DetectMed — AI Medicine Safety Tool

