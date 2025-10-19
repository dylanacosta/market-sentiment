import os
import pandas as pd
from datetime import datetime

def save_to_csv(data, filename: str, folder="share/outputs"):
    os.makedirs(folder, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(folder, f"{filename}_{date_str}.csv")

    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)

    print(f"💾 Saved {len(df)} posts to {filepath}")
    return filepath
