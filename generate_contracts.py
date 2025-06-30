from fpdf import FPDF
import os
import random
import uuid
from datetime import date, timedelta

# Sample legal clauses mapped to their classification categories
sample_clauses = {
    "Obligation": "The service provider shall deliver weekly progress reports to the client.",
    "Penalty": "Failure to meet deadlines shall incur a penalty of Rs. 5,000 per delayed week.",
    "Liability": "The liability of the service provider is limited to the total contract value.",
    "Duration": "This agreement shall remain in effect for a period of 12 months from the start date.",
    "Payment Clause": "An upfront payment of 40% shall be made, with the balance upon completion.",
    "Risky": "In case of disputes, either party may terminate the contract without prior notice.",
    "Neutral": "The contract shall be governed by the laws of the Republic of India."
}

def generate_sample_contract(output_path="sample_contract.pdf", contract_type="service", party_a="Company A", party_b="Client B", start_date=None, end_date=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    if not start_date:
        start_date = date.today().isoformat()
    if not end_date:
        end_date = (date.today().replace(year=date.today().year + 1)).isoformat()

    title_map = {
        "service": "Service Agreement",
        "rental": "Rental Agreement",
        "nda": "Non-Disclosure Agreement (NDA)"
    }
    title = title_map.get(contract_type.lower(), "General Contract")

    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=title, ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"This {title} is made on {start_date} between {party_a} and {party_b}.")
    pdf.multi_cell(0, 10, f"Contract Period: From {start_date} to {end_date}.")
    pdf.ln(5)

    # Inject at least 5 different clauses
    clause_keys = random.sample(list(sample_clauses.keys()), 5)
    for key in clause_keys:
        pdf.multi_cell(0, 10, f"{sample_clauses[key]}")
        pdf.ln(2)

    pdf.ln(10)
    pdf.cell(0, 10, f"Signed by {party_a} and {party_b}", ln=True)
    pdf.cell(0, 10, f"Date: {start_date}", ln=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    pdf.output(output_path)
    return output_path

def generate_random_contract(output_dir="contracts/"):
    contract_types = ["service", "rental", "nda"]
    company_names = ["Acme Corp", "Globex Pvt Ltd", "Initech Solutions", "Cyberdyne Systems", "Hooli India"]
    client_names = ["John Doe", "Rita Sharma", "Rajesh Kumar", "Fatima Khan", "Michael Fernandes"]

    contract_type = random.choice(contract_types)
    party_a = random.choice(company_names)
    party_b = random.choice(client_names)

    start_date = date.today() - timedelta(days=random.randint(0, 30))
    end_date = start_date + timedelta(days=random.randint(180, 540))

    filename = f"{contract_type}_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join(output_dir, filename)

    return generate_sample_contract(
        output_path=output_path,
        contract_type=contract_type,
        party_a=party_a,
        party_b=party_b,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )

# Generate 5 contracts
for _ in range(5):
    path = generate_random_contract()
    print(f"Generated: {path}")
