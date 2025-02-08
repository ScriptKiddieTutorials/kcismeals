"""KCIS Automated Meal Reserve System

Author: Jeff Wu
Version: 1.0
"""

import logging
from datetime import datetime
from requests import Session
from bs4 import BeautifulSoup
from utils import *


# Student system credentials
ACCOUNT = ""
PASSWORD = ""

MEAL_URL = "https://pos.kcis.ntpc.edu.tw"
ORDER_URL = "https://pos.kcis.ntpc.edu.tw/OrderApply.aspx"

logging.basicConfig(
    filename="mealreserve.log",
    filemode="a",
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


def login_meal(session, acc, pwd):
    """Login to meal system"""
    login_res = post(session, MEAL_URL, acc=acc, pwd=pwd, sub="登入/Login")
    if "Login" in login_res.text:
        logging.error("Login failed: Invalid credentials")
        raise ValueError("Login failed. Please check your credentials.")

    logging.info("Logged in successfully")
    return login_res


def _reserve_meal(session, catalog, day: int, key: str):
    """Reserve meal on {day} based on {key}"""
    for title in catalog.find_all("h3"):
        date = list(title.stripped_strings)[0][:10]
        logging.debug(f"Date: {date}")

        if day == datetime.strptime(date, "%Y/%m/%d").isoweekday():
            logging.debug(f"Date {date} matches day {day}")

            reserve_res = session.get(MEAL_URL + "/Order.aspx", params={"DT": date})
            soup = BeautifulSoup(reserve_res.text, "html.parser")
            subcatalog = soup.find("div", class_="col-md-8 col-md-push-4")

            for dish in subcatalog.find_all("h3"):
                dish_name = list(dish.stripped_strings)[1]
                logging.debug(f"Dish: {dish_name}")
                if key in dish_name:
                    logging.info(f"Matching dish found: {dish_name}")
                    uid = int(dish.find_next("img")["src"].split("=")[-1])
                    final_res = session.get(ORDER_URL, params={"UID": uid})
                    return final_res

    return None


def reserve_meals(acc, pwd, meals):
    """Wrapper function to reserve multiple meals"""
    s = Session()
    login_res = login_meal(s, acc, pwd)
    soup = BeautifulSoup(login_res.text, "html.parser")
    catalog = soup.find("div", class_="col-md-8 col-md-push-4")

    res_list = []

    for day, key in meals:
        res = _reserve_meal(s, catalog, day, key)

        if res is None:
            logging.error(f"Could not find meal on day {day} with keyword '{key}'")
        elif not res.ok:
            logging.error(
                f"Failed to reserve meal. Status code: {res.status_code}. Response: {res.text}."
            )
        elif not "更新餐點成功" in res.text:
            logging.warning("Did not receive confirmation message")
        else:
            logging.info("Meal reserved successfully")

        res_list.append(res)

    return res_list


def main():
    print("KCIS Lunch Reservation System".upper())
    acc = input("Enter ID: ")
    pwd = input("Enter password: ")

    meals = []
    while True:
        day = input("Enter day of the week (1-5): ")
        dish_name = input("Enter dish name in Chinese (partial is enough): ")
        meals.append((day, dish_name))
        while True:
            choice = input("Add more dishes? (Y/N): ").upper()[:1]
            if choice in "YN":
                break

        if choice == "N":
            break

    input("Press [ENTER] to begin meal reservation: ")
    print("OK")
    reserve_meals(acc or ACCOUNT, pwd or PASSWORD, meals)


if __name__ == "__main__":
    main()
