from modules.managers.personal_manager import PersonalManager
from modules.managers.food_manager import FoodManager
from modules.managers.chart_manager import ChartManager
from modules.ui import AppUI

# Initialize managers
personal_manager = PersonalManager()
food_manager = FoodManager()
chart_manager = ChartManager()

# Initialize UI
app_ui = AppUI(personal_manager, food_manager, chart_manager)

# Build and launch Gradio interface
demo = app_ui.build_ui()
if __name__ == "__main__":
    demo.launch()
