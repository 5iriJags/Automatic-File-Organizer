#pdf_report.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path
import os  # Added for os.startfile

def generate_pdf_report(directory, changes):
    report_filename = "dry_run_report.pdf"
    report_path = Path(directory) / report_filename
    c = canvas.Canvas(str(report_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 50, "Dry Run Report - File Organizer")

    c.setFont("Helvetica", 10)
    c.drawString(100, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 100, "The following file movements will occur:")

    y_position = height - 130
    c.setFont("Helvetica", 10)
    for change in changes:
        if y_position < 50:
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica", 10)
        c.drawString(100, y_position, change)
        y_position -= 15

    c.save()
    print(f"PDF report generated: {report_path}") # Keep print for console users
    return report_path # Return the path for GUI use

def open_report(report_path):
    """Opens the report using the default system viewer."""
    try:
        if os.name == 'nt': # Windows
            os.startfile(report_path)
        elif os.uname().sysname == 'Darwin': # macOS
            os.system(f'open "{report_path}"')
        else: # Linux
            os.system(f'xdg-open "{report_path}"')
        return True
    except Exception as e:
        print(f"Error opening report: {e}")
        return False
