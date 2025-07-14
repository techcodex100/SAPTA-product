from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from typing import Optional
from io import BytesIO
import os

app = FastAPI(title="SAPTA Certificate Generator", version="1.0.0")


class SAPTACertificateData(BaseModel):
    reference_no: Optional[str] = ""
    issued_in: Optional[str] = ""
    consigned_from: Optional[str] = ""
    consigned_to: Optional[str] = ""
    transport_route: Optional[str] = ""
    official_use: Optional[str] = ""
    tariff_item_number: Optional[str] = ""
    package_marks_numbers: Optional[str] = ""
    package_description: Optional[str] = ""
    origin_criterion: Optional[str] = ""
    gross_weight_or_quantity: Optional[str] = ""
    invoice_number_date: Optional[str] = ""
    declaration_country: Optional[str] = ""
    importing_country: Optional[str] = ""
    declaration_place_date: Optional[str] = ""
    declaration_signature: Optional[str] = ""
    certification_place_date: Optional[str] = ""
    certification_signature_stamp: Optional[str] = ""


@app.get("/")
def root():
    return {"message": "SAPTA Certificate Generator is running 🚀"}


@app.post("/generate-sapta-certificate-pdf/")
def generate_sapta_pdf(data: SAPTACertificateData):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        def draw_image(filename):
            path = os.path.join(os.path.dirname(__file__), "static", filename)
            if os.path.exists(path):
                c.drawImage(ImageReader(path), 0, 0, width=width, height=height)
            else:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(100, 800, f"⚠️ Missing background: {filename}")

        def draw_multiline(label, value, x, y, label_font="Helvetica-Bold", value_font="Helvetica", size=9.2, spacing=10):
            c.setFont(label_font, size)
            for i, line in enumerate(label.splitlines()):
                c.drawString(x, y - i * spacing, line)
            y_val_start = y - len(label.splitlines()) * spacing - 2
            c.setFont(value_font, size)
            for i, line in enumerate(value.splitlines()):
                c.drawString(x, y_val_start - i * spacing, line)

        # === Page 1 ===
        draw_image("bg.jpg")

        reference_label = "SAARC PREFERENTIAL TRADING ARRANGEMENT \n(SAPTA)\nReference No."
        draw_multiline(reference_label, data.reference_no, 300, 745)
        draw_multiline("Issued in", data.issued_in, 300, 700)

        draw_multiline("1. Goods consigned from \n(exporter's business name, address, country)", data.consigned_from, 50, 745)
        draw_multiline("2. Goods consigned to \n(consignee's name, address, country)", data.consigned_to, 50, 680)
        draw_multiline("3. Means of Transport and route \n(as far as known)", data.transport_route, 50, 600)
        draw_multiline("4. For Official use", data.official_use, 300, 600)
        draw_multiline("5. Tariff \nitem number", data.tariff_item_number, 50, 525)
        draw_multiline("6. Marks and \nnumbers of \npackages", data.package_marks_numbers, 110, 525)
        draw_multiline("7. Number and kind of \npackages:description \nof goods", data.package_description, 185, 525)
        draw_multiline("8. Origin Criterion\n(see notes \noverleaf)", data.origin_criterion, 300, 525)
        draw_multiline("9. Gross weight\nor other quantity", data.gross_weight_or_quantity, 383, 525)
        draw_multiline("10. Number and date\nof invoices", data.invoice_number_date, 465, 525)

        declaration_text = (
            f"The undersigned hereby declares that the above details \nand statements are correct; "
            f"that all the goods were \nproduced in {data.declaration_country} and that they comply with the origin \n"
            f"requirements specified for those \ngoods in SAPTA for goods exported to {data.importing_country}."
        )
        draw_multiline("11. Declaration by the exporter", declaration_text, 50, 310)
        draw_multiline("Place and date", data.declaration_place_date, 50, 140)

        cert_text = (
            "It is hereby certified on the basis \nof control carried out, "
            "that the declaration by the exporter is \ncorrect."
        )
        draw_multiline("12. Certificate", cert_text, 300, 310)
        draw_multiline("Place and date", data.certification_place_date, 300, 200)

        c.showPage()

        # === Page 2 ===
        draw_image("2.jpg")
        c.showPage()

        c.save()
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=sapta_certificate.pdf"}
        )

    except Exception as e:
        print("⚠️ PDF generation failed:", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
