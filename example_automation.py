import pandas as pd

data = {
    "Client": ["Client A", "Client B", "Client C"],
    "Debt": [5000, 12000, 8000],
    "Days_Past_Due": [15, 75, 32]
}

df = pd.DataFrame(data)

high_risk = df[df["Days_Past_Due"] > 30]

print("High Risk Clients:")
print(high_risk)