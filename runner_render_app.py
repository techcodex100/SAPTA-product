import os
import time
import datetime
import requests
import psutil
from faker import Faker
from main import SAPTACertificateData

fake = Faker()

pdf_output_dir = "rendered_sapta_pdfs_final"
csv_output_dir = "rendered_sapta_csv_reports_final"
os.makedirs(pdf_output_dir, exist_ok=True)
os.makedirs(csv_output_dir, exist_ok=True)

RENDER_URL = "https://sapta-product-1.onrender.com/generate-sapta-certificate-pdf/"

MAX_RETRIES = 5
DELAY_BETWEEN_REQUESTS = 2  # in seconds

def generate_dummy_data():
    return SAPTACertificateData(
        reference_no=f"SAPTA-REF-{fake.random_number(digits=4)}",
        issued_in=fake.city(),
        consigned_from=fake.company() + "\n" + fake.address(),
        consigned_to=fake.company() + "\n" + fake.address(),
        transport_route="Sea via " + fake.city(),
        official_use="Verified by Commerce Dept.",
        tariff_item_number=str(fake.random_number(digits=4)),
        package_marks_numbers="PKG-" + str(fake.random_number(digits=3)),
        package_description=fake.text(max_nb_chars=40),
        origin_criterion="Rule " + fake.random_element(elements=("A", "B", "C")),
        gross_weight_or_quantity=f"{fake.random_int(min=100, max=1500)} kg",
        invoice_number_date=f"INV-{fake.random_number(digits=5)} dated {fake.date()}",
        declaration_country="India",
        importing_country=fake.country(),
        declaration_place_date=fake.city() + ", " + fake.date(),
        declaration_signature=fake.name(),
        certification_place_date=fake.city() + ", " + fake.date(),
        certification_signature_stamp=fake.name()
    )

for i in range(1, 51):
    dummy_data = generate_dummy_data()
    start_time = time.time()

    # 🔁 Retry loop
    for attempt in range(1, MAX_RETRIES + 1):
        response = requests.post(RENDER_URL, json=dummy_data.model_dump())
        if response.status_code == 200:
            break
        else:
            print(f"⚠️ Attempt {attempt}: Failed to generate PDF {i} (Status: {response.status_code})")
            time.sleep(3)

    if response.status_code != 200:
        print(f"❌ Skipped PDF {i} after {MAX_RETRIES} retries.")
        continue

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = os.path.join(pdf_output_dir, f"sapta_certificate_{i}_{timestamp}.pdf")

    with open(pdf_filename, "wb") as pdf_file:
        pdf_file.write(response.content)

    # ✅ Show stats
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    elapsed = round(time.time() - start_time, 2)

    print(f"✅ [{i}/50] PDF Generated: {pdf_filename}")
    print(f"   CPU Usage: {cpu}% | Memory: {mem}% | Time: {elapsed}s")
    print("-" * 50)

    time.sleep(DELAY_BETWEEN_REQUESTS)

print("🎉 All 50 PDFs attempted with retry and delay logic.")
