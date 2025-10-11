# 📁 File Management System (FMS)

### 🏗 Overview

The **File Management System (FMS)** is a powerful web-based solution developed using **Python (Django Framework)** for organizing and managing large volumes of physical and digital files. It is designed for government offices, corporations, and organizations that need to efficiently **store, locate, and access documents** with enhanced security and easy retrieval.

This system digitizes the manual file management process — allowing users to store all client-related documents, track where each file is located (drawer, compartment, etc.), generate secure PDF files, and quickly retrieve client data using **QR codes**.

---

## 🚀 Key Features

### 🔹 File Management

* Store complete file details including client name, file number, department, division, and physical location (drawer and compartment).
* Upload and manage digital versions of documents (PDFs, DOCX, Images, etc.).
* Automatically generate unique file numbers and document titles.

### 🔹 PDF Management & Security

* Merge multiple documents (PDF, Word, Images, etc.) into one secured PDF.
* Automatically generate **password-protected PDF files** for every client.
* Prevents unauthorized access — files can only be opened using their assigned password.
* Download single, multiple, or all files at once — even as **ZIP files with password protection**.

### 🔹 QR Code System

* Each client record is assigned a **unique QR code**.
* Scanning the QR code instantly displays the client’s details and uploaded PDF.
* Option to generate **multiple QR codes at once** or only for selected clients.
* Automatically generates a professional **QR code PDF report** for all or selected clients.

### 🔹 Advanced Document Operations

* **Merge and Unmerge** documents dynamically.
* Replace individual files within a merged document without reuploading everything.
* View and manage document metadata such as file type, page count, and creation date.
* Export documents with metadata into ZIP archives for backups.

### 🔹 Smart Search and Filtering

* Search files by client name, file number, survey number, village, district, taluka, etc.
* Filter data by date range, division, and other parameters.
* View detailed statistics and recent records on the **Dashboard**.

### 🔹 User Management

* Role-based access for admin and division-level users.
* Admins can view and manage all divisions.
* Regular users can only view and manage files within their assigned division.

### 🔹 Clean & Modern UI

* Intuitive dashboard with summary cards and analytics.
* Responsive, simple, and minimal interface for smooth navigation.
* Fully optimized layout for both desktop and tablet screens.

---

## 🧱 System Architecture

* **Frontend:** HTML, CSS, JavaScript, Bootstrap
* **Backend:** Python, Django Framework
* **Database:** SQLite / MYSQL
* **Libraries Used:**

  * `PyPDF2` – PDF read, write, merge, encryption
  * `reportlab` – PDF and QR code generation
  * `pdf2docx` – File format conversions
  * `Pillow` – Image handling
  * `qrcode` – QR code creation
  * `zipfile` – File compression
  * `json` – Metadata management

---

## ⚙️ Core Functional Flow

1. **File Creation:**
   User adds a new client record with full details → system auto-generates file number & password.

2. **Document Upload:**
   User uploads single or multiple files → system merges them into one encrypted PDF.

3. **QR Code Generation:**
   Each client gets a QR code → scanning it shows client details and allows PDF download.

4. **Document Access:**
   PDF download requires the assigned password → ensures document security.

5. **Unmerge or Replace:**
   Users can unmerge PDF files or replace a specific document without affecting the rest.

6. **Download Options:**

   * Single client file
   * Multiple client files
   * All files together as password-protected ZIP

---

## 📊 Dashboard Insights

* **Total Files Count**
* **Files with Documents / Without Documents**
* **Recent File Registrations (7 Days)**
* **Division-Wise File Distribution Chart**

---

## 🔒 Security Highlights

* Every PDF file is **encrypted with a unique password**.
* Even downloaded ZIP archives require the same password to extract files.
* Passwords are generated automatically and stored securely in the database.

---

## 🖨 QR Code Example Workflow

* Click “Generate QR Code” → system generates QR for each client.
* Download all QR codes in a printable PDF.
* Each QR code shows client data like:

  * Name
  * File No
  * Division
  * Ward, Drawer, Compartment
  * PDF Password

---

## 💡 Future Enhancements

* Add document expiry tracking and automatic alerts.
* Introduce digital signature and approval workflow.
* Enable bulk import/export via Excel.
* Add cloud integration (Google Drive / AWS S3).
* Implement API for third-party integration.

---

## 🧑‍💻 Developer Information

**Developed By:** [Adarsh Madankar](https://github.com/adarshmadankar45)
**Role:** Python / Django Backend Developer
**Experience:** 1.6+ Years in Django, REST APIs, and MySQL
**Portfolio:** [adarshmadankar45.github.io/portfolio](https://adarshmadankar45.github.io/portfolio/)

---

## ⚠️ Disclaimer

> **Do not use or redistribute this project without permission.**
> If you are interested in using or customizing this project for your organization, please contact:

📩 **Adarsh Madankar**
📞 *Available for freelance & project collaborations*
🔗 GitHub: [adarshmadankar45](https://github.com/adarshmadankar45)

