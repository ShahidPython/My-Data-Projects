import requests

def convert_currency(from_currency, to_currency, amount):
    url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Error: Failed to retrieve data from API.")
        return
    
    data = response.json()
    
    if "rates" not in data or to_currency not in data["rates"]:
        print("⚠️ API response received but currency data is missing. Check currency codes.")
        return

    converted_amount = data["rates"][to_currency]
    rate = converted_amount / amount  # Calculate the exchange rate
    
    print(f"\n✅ Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
    print(f"💰 {amount} {from_currency} = {converted_amount:.2f} {to_currency}\n")

print("💱 Currency Converter (Real-Time)\n")

from_curr = input("Enter FROM currency (e.g., USD): ").upper()
to_curr = input("Enter TO currency (e.g., EUR): ").upper()

try:
    amount = float(input("Enter amount to convert: "))
    convert_currency(from_curr, to_curr, amount)
except ValueError:
    print("❌ Error: Please enter a valid number for the amount.")