import pandas as pd
from pathlib import Path
from datetime import datetime
from modules.calculators.health_calculators import BMI, BMR, TDEE


class PersonalManager:
    def __init__(self, data_folder="data"):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        self.file = self.data_folder / "personal_info.csv"

    def load_last_entry(self, user="default") -> dict:
        if self.file.exists() and self.file.stat().st_size > 0:
            df = pd.read_csv(self.file)
            user_df = df[df["name"] == user] if "name" in df.columns else df
            if not user_df.empty:
                return user_df.iloc[-1].to_dict()
        return {}

    def save_info(
        self,
        user: str,
        sex: str,
        bd: str,
        height: float,
        weight: float,
        activity_level: str,
    ) -> tuple:
        height = float(height) if height else 0
        weight = float(weight) if weight else 0

        bmi = BMI.calculate(weight, height)
        bmr = BMR.calculate(weight, height, bd, sex) if height > 0 else 0
        tdee = TDEE.calculate(bmr, activity_level) if bmr > 0 else 0

        record = pd.DataFrame(
            [
                {
                    "time": datetime.now(),
                    "name": user,
                    "sex": sex,
                    "bd": bd,
                    "height": height,
                    "weight": weight,
                    "bmi": bmi,
                    "bmr": bmr,
                    "tdee": tdee,
                    "activity_level": activity_level,
                }
            ]
        )

        if self.file.exists() and self.file.stat().st_size > 0:
            record.to_csv(self.file, mode="a", header=False, index=False)
        else:
            record.to_csv(self.file, index=False)

        return bmi, bmr, tdee
