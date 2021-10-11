# uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
from typing import Optional

from interface.dashbot_interface import *

app = FastAPI()
dashbot = Interface(DashBot)

app.mount("/src", StaticFiles(directory="./interface/src"), name="src")

@app.get("/preprocess_data/{dataset_name}")
async def preprocess_data(dataset_name : str):
    return dashbot.do_preprocess_data(dataset_name)

@app.get("/set_diversity_to_{boolean}_with_start_{start_generation}")
async def set_diversity(boolean : bool, start_generation : bool):
    return dashbot.set_diversity(boolean, start_generation)

@app.get("/start_dashboard_generation")
def start_dashboard_generation():
    dashbot.initialize_dashboard_generation()
    dashbot.generate_new_panel()
    return dashbot.show_to_U()

@app.get("/process_user_answer")
async def process_user_answer(user_feedback : bool, refinement_info : str):
    dashbot.translate_user_feedback(user_feedback, refinement_info)
    dashbot.update_system()
    dashbot.find_next_suggestion()
    return dashbot.show_to_U()
