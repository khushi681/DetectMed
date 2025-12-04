# DetectMed – Medicine Expiry & Damage Detector

DetectMed is an AI-assisted Flask web application that:
- Extracts expiry dates from medicine strips using OCR  
- Detects expiry status (Valid / Expired / Expiring Soon / Unknown)  
- Detects packaging damage using image processing  
- Saves scan history into a database  
- Generates Daily & Weekly PDF Reports  
- Shows scan analytics with charts  

---

## 🚀 Features

### 🔍 OCR-Based Expiry Detection
- Reads printed expiry dates from medicine packets using Tesseract OCR  
- Auto-parses multiple date formats  

### 📦 Damage Detection
- Uses OpenCV edge detection to analyze broken / tampered packaging  

### 🧠 Smart Expiry Classification
- Valid  
- Expired  
- Expiring Soon  
- Unknown (low confidence)  

### 📊 History & Analytics Dashboard
- View previous scans  
- Pagination support  
- Graph of last 7 days  

### 📝 PDF Report Generation
- **Daily PDF**
- **Weekly PDF**

Both include:
- Summary  
- Statistics  
- Full table of scans  

---

## 🗂 Project Structure

