from fpdf import FPDF

def generate_pdf(report_text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    for line in report_text.split("\n"):
        pdf.multi_cell(0, 8, line)

    pdf.output(filename)
