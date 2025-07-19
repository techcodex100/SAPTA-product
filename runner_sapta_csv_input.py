import csv
import os
import requests
import time
import datetime
import psutil
from main import SAPTACertificateData
from random import randint

# ✅ Output folders
pdf_output_dir = "sapta_pdfs_from_csv_input"
os.makedirs(pdf_output_dir, exist_ok=True)

csv_output_dir = "sapta_csv_reports_from_csv_input"
os.makedirs(csv_output_dir, exist_ok=True)

# 🌐 Render endpoint
RENDER_URL = "https://sapta-product-1.onrender.com/generate-sapta-certificate-pdf/"

# 📋 Software quality test parameters
test_parameters = [
    "Reliability", "Scalability", "Robustness/Resilience", "Latency", "Throughput",
    "Security", "Usability/User-Friendliness", "Maintainability", "Availability", "Cost",
    "Flexibility/Adaptability", "Portability", "Interoperability",
    "Resource Utilization", "Documentation Quality"
]

def get_evaluation(param):
    score = randint(3, 5)
    remarks = {
        5: "Excellent performance under all tested conditions.",
        4: "Good performance with minor improvements suggested.",
        3: "Acceptable performance; needs better optimization."
    }
    return score, remarks[score]

# ✅ Retry logic for robustness
def post_with_retries(data_dict, retries=3, delay=3):
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(RENDER_URL, json=data_dict)
            if response.status_code == 200:
                return response
            else:
                print(f"⚠️ Attempt {attempt}: Failed with status {response.status_code}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt}: Exception - {str(e)}")
        time.sleep(delay)
    return None

# 📖 Read CSV and generate PDFs + CSV reports
with open("sapta_dummy_input_data.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader, start=1):
        start_time = time.time()
        clean_row = {str(k).strip(): str(v).strip() for k, v in row.items()}
        try:
            dummy_data = SAPTACertificateData(**clean_row)
        except Exception as e:
            print(f"❌ Error parsing data row {idx}: {e}")
            continue

        response = post_with_retries(dummy_data.model_dump())

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_filename = os.path.join(pdf_output_dir, f"sapta_certificate_{idx}_{timestamp}.pdf")

        if response:
            with open(pdf_filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"❌ Failed to generate PDF {idx} after retries.")
            continue

        # 🧾 Generate test report
        csv_filename = os.path.join(csv_output_dir, f"sapta_report_{idx}.csv")
        with open(csv_filename, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["🔹 Dummy Input Field", "Value"])
            for field, value in dummy_data.model_dump().items():
                writer.writerow([field, value])
            writer.writerow([])
            writer.writerow(["✅ Test Parameter", "Rating (1–5)", "Remarks"])
            for param in test_parameters:
                score, remark = get_evaluation(param)
                writer.writerow([param, score, remark])

        # 🧠 Stats
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        elapsed = round(time.time() - start_time, 2)
        print("--------------------------------------------------")
        print(f"✅ [{idx}] PDF: {pdf_filename}")
        print(f"   CPU Usage: {cpu}% | Memory Usage: {mem}% | Time Taken: {elapsed}s")
        print("--------------------------------------------------")

        # Delay to avoid hitting API too fast
        time.sleep(2)

print("🎉 All SAPTA PDFs and test reports generated from CSV input!")