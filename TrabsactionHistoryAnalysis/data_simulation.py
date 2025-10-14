# data_simulation.py
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import uuid
import os

fake = Faker()

def generate_transaction_data(num_months=12, transaction_density=2.5):
    """
    Generates a highly realistic and dense transactional dataset.
    'transaction_density' controls the average number of small, daily transactions.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_months * 30)
    
    transactions = []
    current_balance = 7500.0

    # --- Business Patterns ---
    base_monthly_income = 8000
    income_growth_rate = 1.02
    
    fixed_expenses = {
        "Rent": {"amount": -2000, "day": 1},
        "Salaries": {"amount": -3500, "day": 28},
        "Adobe Creative Cloud": {"amount": -80, "day": 15},
        "Google Workspace": {"amount": -50, "day": 15},
        "QuickBooks": {"amount": -30, "day": 15},
        "UTILITIES BILL": {"amount": -150, "day": 20}
    }

    # High-frequency, low-value "noise" transactions
    daily_noise_categories = {
        "Meals & Entertainment": {"merchant": "Various Cafes/Restaurants", "range": (-60, -5)},
        "Office Supplies": {"merchant": "Amazon Business", "range": (-100, -10)},
        "Local Travel": {"merchant": "Uber/Lyft", "range": (-40, -8)},
        "Bank Fees": {"merchant": "Bank Service Charge", "range": (-25, -5)}
    }

    # --- Generate Transactions Day by Day for 12 months ---
    total_days = (end_date - start_date).days
    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)

        # --- High-Frequency "Noise" Transactions ---
        if random.random() < transaction_density / 2: # Chance to have multiple small transactions a day
            num_noise_transactions = np.random.poisson(transaction_density)
            for _ in range(num_noise_transactions):
                category = random.choice(list(daily_noise_categories.keys()))
                details = daily_noise_categories[category]
                amount = random.uniform(details["range"][0], details["range"][1])
                current_balance += amount
                transactions.append({
                    "transaction_id": str(uuid.uuid4()), "timestamp": current_date, "description": f"{details['merchant']}",
                    "amount": round(amount, 2), "currency": "GBP", "balance": round(current_balance, 2),
                    "merchant_name": details['merchant'].split(" ")[0], "category": category
                })

        # --- Low-Frequency, High-Value Events (Monthly) ---
        # Fixed Expenses
        for desc, details in fixed_expenses.items():
            if current_date.day == details['day']:
                amount = details['amount']
                current_balance += amount
                category = "Software Subscriptions" if " " in desc else desc
                if desc == "UTILITIES BILL": category = "Utilities"
                transactions.append({
                    "transaction_id": str(uuid.uuid4()), "timestamp": current_date, "description": desc,
                    "amount": round(amount, 2), "currency": "GBP", "balance": round(current_balance, 2),
                    "merchant_name": desc.split(" ")[0].replace("BILL", "Co"), "category": category
                })

        # Income (Client Payments)
        if current_date.day in [10, 25]: # Bi-monthly income pattern
            month_index = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month
            monthly_income = base_monthly_income * (income_growth_rate ** month_index)
            if current_date.month in [10, 11, 12]: monthly_income *= 1.2 # Q4 boost
            if current_date.month in [1, 2, 3]: monthly_income *= 0.85 # Q1 dip
            
            amount = monthly_income / 2 # Split income into two payments
            current_balance += amount
            transactions.append({
                "transaction_id": str(uuid.uuid4()), "timestamp": current_date, "description": f"Payment from {fake.company()}",
                "amount": round(amount, 2), "currency": "GBP", "balance": round(current_balance, 2),
                "merchant_name": fake.company(), "category": "Client Payments"
            })
            
        # Mid-Frequency Events (Marketing, larger travel, etc.)
        if current_date.day == 5: # Monthly marketing spend
            marketing_spend = -random.uniform(500, 1500)
            if current_date.month in [10, 11, 12]: marketing_spend *= 1.5
            current_balance += marketing_spend
            transactions.append({
                "transaction_id": str(uuid.uuid4()), "timestamp": current_date, "description": "GOOGLE ADS GBR*",
                "amount": round(marketing_spend, 2), "currency": "GBP", "balance": round(current_balance, 2),
                "merchant_name": "Google", "category": "Marketing Spend"
            })
        
        if current_date.day == 22 and random.random() > 0.5: # Sporadic larger travel
            travel_spend = -random.uniform(200, 800)
            current_balance += travel_spend
            transactions.append({
                "transaction_id": str(uuid.uuid4()), "timestamp": current_date, "description": f"Trainline {fake.city()}",
                "amount": round(travel_spend, 2), "currency": "GBP", "balance": round(current_balance, 2),
                "merchant_name": "Trainline", "category": "Travel"
            })

    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp').reset_index(drop=True)

    # Introduce a "near-miss" cash flow pressure point
    if len(df) > 50:
        low_point_idx = random.randint(30, len(df) - 20)
        df.loc[low_point_idx, 'balance'] = random.uniform(50, 200)
        for i in range(low_point_idx + 1, len(df)):
            df.loc[i, 'balance'] = df.loc[i-1, 'balance'] + df.loc[i, 'amount']
    
    return df

if __name__ == '__main__':
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # transaction_density controls the average number of small transactions per day.
    # A value of 2.5 will generate a few thousand transactions over a year.
    applicant_data = generate_transaction_data(transaction_density=2.5)
    
    output_path = "data/artisan_digital_transactions.csv"
    applicant_data.to_csv(output_path, index=False)
    
    print(f"\nGenerated {len(applicant_data)} transactions.")
    print(f"Data saved successfully to '{output_path}'")