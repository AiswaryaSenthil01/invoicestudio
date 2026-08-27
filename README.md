# Namura Invoice Studio - Desktop Invoice Management System

A professional, modern desktop Invoice Management System built for small businesses using Python, CustomTkinter, SQLite, ReportLab, python-docx, Pillow, and PyMuPDF.

---

## 🌟 Key Features

1. **Executive Dashboard**:
   - High-level business metrics: Total Revenue Billed, Total Invoices Generated, Paid Invoices & Amount, Pending / Unpaid Invoices.
   - Quick action shortcuts to create invoices, add customers, catalog products, and view history.
   - Recent invoice activity table with instant click-to-preview.

2. **Structured Invoice Creation**:
   - Auto-generated sequential invoice numbers (`INV-001`, `INV-002`, customizable prefix and padding).
   - Pre-filled company GSTIN, PAN, address, phone, email, and state code.
   - Customer picker with auto-fill for Billed To & Shipped To addresses.
   - Quick-insert product catalog selector.
   - Interactive line items table with real-time automatic calculation of Subtotal, CGST, SGST, IGST, Total Tax, and Grand Total.
   - Automatic currency-to-words conversion in the Indian numbering system (Lakhs, Crores, Rupees, Paise).
   - Intra-state (CGST + SGST) vs Inter-state (IGST) tax modes.

3. **Live High-Resolution PDF Preview**:
   - Built-in real-time preview powered by vector rasterization via PyMuPDF.
   - Faithfully replicates the exact reference GST Tax Invoice format before final confirmation.

4. **Multi-Format Export & System Printing**:
   - **PDF Generation**: Crisp, print-ready A4 vector PDF matching the reference GST Tax Invoice layout.
   - **Word Export**: Optional `.docx` export using `python-docx` mirroring the table structure.
   - **System Printing**: One-click print sending the invoice directly to the default printer / print dialog.
   - **Organized Storage**: Automatic directory hierarchy (`Invoices/<Year>/<Month>/<INV_NO>.pdf`).

5. **Invoice History & Management**:
   - Search by Invoice Number, Customer Name, P.O. Number, or Vehicle Number.
   - Filter by Payment Status (All, Paid, Unpaid, Pending) and sort by date or amount.
   - Context actions: View PDF, Edit Invoice, Duplicate/Clone Invoice, Export Word, Toggle Status, Delete.

6. **Customer & Product Catalog Management**:
   - Save customer profiles with GSTIN, PAN, address, contact numbers, and shipping details.
   - Manage standard product/service catalog with default rates, HSN codes, and tax rates.

7. **Company & Numbering Settings**:
   - Custom business profile details, GSTIN, PAN, bank accounts, and declaration footer.
   - Customizable invoice numbering formats and sequence counters.

8. **Theme Support**:
   - Executive dark theme and clean light theme with instant toggle.

---

## 🚀 How to Run

### 1. Requirements
Ensure Python 3.10+ is installed along with the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python main.py
```

### 3. Run Automated Tests
```bash
# Run unit & logic test suite
python tests/test_core.py

# Run GUI smoke test
python tests/test_gui.py

# Run full end-to-end workflow test
python tests/test_e2e.py
```

---

## 📂 Project Architecture

```
invoice_manager/
│
├── main.py                        # Application entry point
├── requirements.txt               # Dependencies list
├── README.md                      # Documentation
│
├── src/
│   ├── config.py                  # Theme, colors, paths, constants
│   ├── database/                  # SQLite persistence layer
│   │   ├── db_manager.py          # Database connection context manager & schema
│   │   ├── invoice_repository.py  # Invoices & line items CRUD & analytics
│   │   ├── customer_repository.py # Customer CRUD & search
│   │   ├── product_repository.py  # Products/Services CRUD & search
│   │   └── settings_repository.py # Company profile & numbering sequence
│   │
│   ├── utils/                     # Business logic utilities
│   │   ├── calculations.py        # Tax, subtotal, grand total & currency formatting
│   │   ├── number_to_words.py     # Indian numbering system amount-to-words
│   │   ├── validators.py          # Form field validation (GSTIN, PAN, dates, items)
│   │   └── file_utils.py          # Auto directory organizer (Invoices/YYYY/Month/)
│   │
│   ├── services/                  # Output engines
│   │   ├── pdf_generator.py       # ReportLab PDF engine matching reference GST invoice
│   │   ├── docx_generator.py      # python-docx Word exporter
│   │   ├── preview_service.py     # PyMuPDF real-time high-DPI page renderer
│   │   └── print_service.py       # System print integration & file launcher
│   │
│   └── gui/                       # CustomTkinter GUI Layer
│       ├── app.py                 # Main Window & Sidebar Navigation
│       ├── components/            # StatCard, SearchBar, ModalDialogs
│       └── views/                 # Dashboard, NewInvoice, History, Customers, Products, Settings
│
├── Invoices/                      # Automatically organized generated PDF & DOCX files
└── tests/                         # Test suites (test_core.py, test_gui.py, test_e2e.py)
```
