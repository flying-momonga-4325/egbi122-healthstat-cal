from datetime import datetime


class BMI:
    @staticmethod
    def calculate(weight: float, height: float) -> float:
        return round(weight / ((height / 100) ** 2), 2) if height > 0 else 0.0


class BMR:
    @staticmethod
    def calculate(weight: float, height: float, bd: str, sex: str) -> float:
        birth_year = int(bd.split(":")[2])
        age = datetime.now().year - birth_year
        sex = sex.lower()
        if sex == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif sex == "female":
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        elif sex == "other":
            bmr = 10 * weight + 6.25 * height - 5 * age - 78
        else:
            raise ValueError("Sex must be 'male' or 'female'")
        return round(bmr, 2)


class TDEE:
    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }

    @classmethod
    def calculate(cls, bmr: float, activity_level: str) -> float:
        if activity_level not in cls.activity_factors:
            raise ValueError(
                "Activity level must be one of: 'sedentary', 'light', 'moderate', 'active', 'very_active'"
            )
        return round(bmr * cls.activity_factors[activity_level], 2)
