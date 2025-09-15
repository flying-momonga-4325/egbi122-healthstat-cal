import gradio as gr
from datetime import datetime
import plotly.graph_objects as go
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes


class Seafoam(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.emerald,
        secondary_hue: colors.Color | str = colors.blue,
        neutral_hue: colors.Color | str = colors.gray,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_md,
        text_size: sizes.Size | str = sizes.text_lg,
        font: fonts.Font | str | list = (
            fonts.GoogleFont("Quicksand"),
            "ui-sans-serif",
            "sans-serif",
        ),
        font_mono: fonts.Font | str | list = (
            fonts.GoogleFont("IBM Plex Mono"),
            "ui-monospace",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )


seafoam = Seafoam()


class AppUI:
    def __init__(self, personal_manager, food_manager, chart_manager):
        self.personal_manager = personal_manager
        self.food_manager = food_manager
        self.chart_manager = chart_manager
        self.session_name = None

    @staticmethod
    def _empty_chart():
        fig = go.Figure()
        fig.update_layout(
            title="No data yet",
            xaxis_title="Date",
            yaxis_title="Calories",
            template="plotly_white",
        )
        return fig

    @staticmethod
    def _announcement(msg, success=True):
        color_bg = "#e0ffe0" if success else "#ffe4e4"
        color_text = "#006600" if success else "#b00020"
        html_content = f"""
        <div id='popup-banner' style='
            position: fixed;
            top: 20px;
            right: 20px;
            background:{color_bg};
            color:{color_text};
            padding:15px 25px;
            border-radius:8px;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
            z-index:9999;
            font-weight:bold;
        '>{msg}</div>
        """
        return gr.update(value=html_content, visible=True)

    # --- LOGIN ---
    def login_handler(self, login_name):
        self.session_name = login_name
        name_box_val = login_name
        record = self.personal_manager.load_last_entry(login_name)

        if record:
            chart = self.chart_manager.build_last_7_days_chart(login_name)
            bmi = record.get("bmi", 0)
            bmr = record.get("bmr", 0)
            tdee = record.get("tdee", 0)
            bd_parts = record.get("bd", "1:Jan:2000").split(":")
            sex_val = record.get("sex", "Male")
            height_val = record.get("height", 0)
            weight_val = record.get("weight", 0)
            height_unit = record.get("height_unit", "cm")
            weight_unit = record.get("weight_unit", "kg")
            activity_val = record.get("activity_level", "sedentary")
            reverse_map = {
                "sedentary": "ออกกำลังกายน้อยมาก หรือไม่ออกเลย",
                "light": "ออกกำลังกาย 1-3 ครั้งต่อสัปดาห์",
                "moderate": "ออกกำลังกาย 4-5 ครั้งต่อสัปดาห์",
                "active": "ออกกำลังกาย 6-7 ครั้งต่อสัปดาห์",
                "very_active": "ออกกำลังกายวันละ 2 ครั้งขึ้นไป",
            }
            activity_val = reverse_map.get(activity_val, "ออกกำลังกายน้อยมาก หรือไม่ออกเลย")
            return (
                gr.update(visible=False),
                name_box_val,
                gr.update(visible=True),
                sex_val,
                bd_parts[0],
                bd_parts[1],
                bd_parts[2],
                height_val,
                weight_val,
                height_unit,
                weight_unit,
                activity_val,
                chart,
                bmi,
                bmr,
                tdee,
                gr.update(value="", visible=False),
                gr.update(value="", visible=False),
            )
        else:
            return (
                gr.update(visible=False),
                name_box_val,
                gr.update(visible=True),
                "Male",
                "1",
                "Jan",
                str(datetime.now().year - 25),
                0,
                0,
                "cm",
                "kg",
                "ออกกำลังกายน้อยมาก หรือไม่ออกเลย",
                self._empty_chart(),
                0,
                0,
                0,
                gr.update(value="", visible=False),
                gr.update(value="", visible=False),
            )

    # --- SAVE INFO ---
    def save_info_handler(
        self,
        name,
        sex,
        bd_day,
        bd_month,
        bd_year,
        height,
        weight,
        height_unit,
        weight_unit,
        activity,
    ):
        bd = f"{bd_day}:{bd_month}:{bd_year}"
        activity_map = {
            "ออกกำลังกายน้อยมาก หรือไม่ออกเลย": "sedentary",
            "ออกกำลังกาย 1-3 ครั้งต่อสัปดาห์": "light",
            "ออกกำลังกาย 4-5 ครั้งต่อสัปดาห์": "moderate",
            "ออกกำลังกาย 6-7 ครั้งต่อสัปดาห์": "active",
            "ออกกำลังกายวันละ 2 ครั้งขึ้นไป": "very_active",
        }
        activity_key = activity_map.get(activity, "sedentary")
        bmi, bmr, tdee = self.personal_manager.save_info(
            name, sex, bd, height, weight, activity_key, height_unit, weight_unit
        )
        chart = self.chart_manager.build_last_7_days_chart(name)
        return (
            self._announcement(f"✅ Saved! BMI:{bmi}, BMR:{bmr}, TDEE:{tdee}"),
            chart,
            bmi,
            bmr,
            tdee,
        )

    # --- ADD FOOD ---
    def add_food_handler(self, name, food_name, quantity):
        msg = ""
        success = True
        for _ in range(int(quantity)):
            s, m = self.food_manager.add_food(name, food_name)
            msg += m + "<br>"
            if not s:
                success = False
        record = self.personal_manager.load_last_entry(name)
        chart = self.chart_manager.build_last_7_days_chart(name)
        bmi = record.get("bmi", 0)
        bmr = record.get("bmr", 0)
        tdee = record.get("tdee", 0)
        return (
            AppUI._announcement(msg, success),
            chart,
            bmi,
            bmr,
            tdee,
        )

    # --- LOGOUT ---
    def logout_handler(self):
        self.session_name = None
        return gr.update(visible=True), gr.update(visible=False), gr.update(value="")

    # --- UI ---
    def build_ui(self):
        with gr.Blocks(theme=seafoam) as demo:
            # LOGIN PAGE
            with gr.Group(visible=True) as login_page:
                login_name = gr.Textbox(label="Enter your name")
                login_btn = gr.Button("Login", variant="primary")

            # APP PAGE
            with gr.Group(visible=False) as app_page:
                with gr.Tabs() as tabs:
                    # MAIN TAB
                    with gr.Tab("Main"):
                        name_box = gr.Textbox(label="Full Name", interactive=False)
                        chart_plot = gr.Plot(self._empty_chart())
                        with gr.Row():
                            bmi_out = gr.Number(label="BMI", interactive=False)
                            bmr_out = gr.Number(label="BMR", interactive=False)
                            tdee_out = gr.Number(label="TDEE", interactive=False)

                        # --- Food selection ---
                        with gr.Row():
                            food_dropdown = gr.Dropdown(
                                choices=self.food_manager.get_food_list(),
                                label="Select Food",
                                scale=3,
                            )
                            food_quantity = gr.Slider(
                                minimum=1,
                                maximum=10,
                                value=1,
                                step=1,
                                label="Quantity (times to add)",
                                scale=2,
                            )
                        add_btn = gr.Button("Add Food", variant="primary")
                        popup_food = gr.HTML(value="", visible=False)

                        add_btn.click(
                            fn=self.add_food_handler,
                            inputs=[name_box, food_dropdown, food_quantity],
                            outputs=[
                                popup_food,
                                chart_plot,
                                bmi_out,
                                bmr_out,
                                tdee_out,
                            ],
                        )
                        popup_food.change(
                            fn=lambda x: gr.update(visible=False),
                            inputs=[popup_food],
                            outputs=[popup_food],
                            queue=False,
                        )

                    # PERSONAL INFO TAB
                    with gr.Tab("Personal Info"):
                        sex = gr.Dropdown(["Male", "Female", "Other"], label="Sex")
                        days = [str(i) for i in range(1, 32)]
                        months = [
                            "Jan",
                            "Feb",
                            "Mar",
                            "Apr",
                            "May",
                            "Jun",
                            "Jul",
                            "Aug",
                            "Sep",
                            "Oct",
                            "Nov",
                            "Dec",
                        ]
                        years = [
                            str(y)
                            for y in range(
                                datetime.now().year - 100, datetime.now().year + 1
                            )
                        ]
                        bd_day = gr.Dropdown(days, label="Day")
                        bd_month = gr.Dropdown(months, label="Month")
                        bd_year = gr.Dropdown(years, label="Year")

                        # Height + Unit
                        with gr.Row():
                            height = gr.Number(label="Height", scale=2)
                            height_unit = gr.Dropdown(
                                choices=["cm", "ft"], label="Unit", value="cm", scale=0
                            )

                        # Weight + Unit
                        with gr.Row():
                            weight = gr.Number(label="Weight", scale=2)
                            weight_unit = gr.Dropdown(
                                choices=["kg", "lbs"], label="Unit", value="kg", scale=0
                            )

                        activity = gr.Dropdown(
                            choices=[
                                "ออกกำลังกายน้อยมาก หรือไม่ออกเลย",
                                "ออกกำลังกาย 1-3 ครั้งต่อสัปดาห์",
                                "ออกกำลังกาย 4-5 ครั้งต่อสัปดาห์",
                                "ออกกำลังกาย 6-7 ครั้งต่อสัปดาห์",
                                "ออกกำลังกายวันละ 2 ครั้งขึ้นไป",
                            ],
                            label="Activity Level",
                        )
                        save_btn = gr.Button("💾 Save Info")
                        popup_info = gr.HTML(value="", visible=False)

                        save_btn.click(
                            fn=self.save_info_handler,
                            inputs=[
                                name_box,
                                sex,
                                bd_day,
                                bd_month,
                                bd_year,
                                height,
                                weight,
                                height_unit,
                                weight_unit,
                                activity,
                            ],
                            outputs=[
                                popup_info,
                                chart_plot,
                                bmi_out,
                                bmr_out,
                                tdee_out,
                            ],
                        )

                        logout_btn = gr.Button("🔄 Logout")
                        logout_btn.click(
                            fn=self.logout_handler,
                            outputs=[login_page, app_page, login_name],
                        )

            login_btn.click(
                fn=self.login_handler,
                inputs=[login_name],
                outputs=[
                    login_page,
                    name_box,
                    app_page,
                    sex,
                    bd_day,
                    bd_month,
                    bd_year,
                    height,
                    weight,
                    height_unit,
                    weight_unit,
                    activity,
                    chart_plot,
                    bmi_out,
                    bmr_out,
                    tdee_out,
                    gr.HTML(value="", visible=False),  # popup_food
                    gr.HTML(value="", visible=False),  # popup_info
                ],
            )
        return demo
