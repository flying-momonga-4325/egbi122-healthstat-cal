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
                record = user_df.iloc[-1].to_dict()

                # Convert height/weight to preferred unit for display
                height_unit = record.get("height_unit", "cm")
                weight_unit = record.get("weight_unit", "kg")
                height = record.get("height", 0)
                weight = record.get("weight", 0)

                if height_unit == "ft":
                    record["height"] = round(height / 30.48, 2)
                if weight_unit == "lbs":
                    record["weight"] = round(weight * 2.20462, 2)

                record["height_unit"] = height_unit
                record["weight_unit"] = weight_unit
                return record
        return {}

    def save_info(
        self,
        user: str,
        sex: str,
        bd: str,
        height: float,
        weight: float,
        activity_level: str,
        height_unit="cm",
        weight_unit="kg",
    ) -> tuple:
        # Convert input to cm/kg for storage
        if height_unit == "ft":
            height = float(height) * 30.48
        else:
            height = float(height)

        if weight_unit == "lbs":
            weight = float(weight) / 2.20462
        else:
            weight = float(weight)

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
                    "height_unit": height_unit,
                    "weight_unit": weight_unit,
                }
            ]
        )

        if self.file.exists() and self.file.stat().st_size > 0:
            record.to_csv(self.file, mode="a", header=False, index=False)
        else:
            record.to_csv(self.file, index=False)

        return bmi, bmr, tdee
