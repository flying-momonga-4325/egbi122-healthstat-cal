import pandas as pd
from pathlib import Path
from datetime import datetime


class FoodManager:
    def __init__(self, data_folder="data"):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        self.food_file = self.data_folder / "food_data.csv"
        self.cal_file = self.data_folder / "cal_rec.csv"
        if not self.food_file.exists():
            pd.DataFrame(columns=["food", "cal"]).to_csv(self.food_file, index=False)

    def get_food_list(self) -> list:
        df = pd.read_csv(self.food_file)
        return df["food"].tolist() if not df.empty else []

    def add_food(self, user: str, food_name: str) -> tuple:
        df = pd.read_csv(self.food_file)
        row = df[df["food"] == food_name]
        if row.empty:
            return False, f"❌ Food '{food_name}' not found!"
        cal = int(row.iloc[0]["cal"])
        record = pd.DataFrame(
            [{"time": datetime.now(), "name": user, "food": food_name, "cal": cal}]
        )
        if self.cal_file.exists() and self.cal_file.stat().st_size > 0:
            record.to_csv(self.cal_file, mode="a", header=False, index=False)
        else:
            record.to_csv(self.cal_file, index=False)
        return True, f"✅ Added {food_name} ({cal} cal)!"
