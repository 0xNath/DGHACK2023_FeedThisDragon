import requests
import uuid
from time import sleep
import json
from pprint import pprint
from datetime import datetime
import os

tokenFile = open("token", "+w")
token = tokenFile.read()

sessionUUID = str(uuid.uuid4())

if token == "":
    tokenFile.write(sessionUUID)
else:
    sessionUUID = token

tokenFile.close()

session = requests.Session()

session.headers.update(
    {
        "session": sessionUUID,
        "Content-Type": "application/json",
        "Authorization": "mynotsosecrettoken",
        "Update": "true",
        "Shopuuid": "",
        "Itemuuid": "",
    }
)

currentAchievements = []
currentAchievementsName = []
hurtAcquired = False

session.cookies.update({"uuid": sessionUUID, "achievements": f"{currentAchievements}"})


def updateCookies(session, achievements):
    for achievement in achievements:
        if (
            achievement["acquired"] == True
            and achievement["slug"] not in currentAchievementsName
        ):
            currentAchievementsName.append(achievement["slug"])
            currentAchievements.append(
                {
                    "slug": achievement["slug"],
                    "name": achievement["name"],
                    "description": achievement["description"],
                    "delay": datetime.now().strftime("%s"),
                }
            )
    session.cookies.update({"achievements": f"{currentAchievements}"})


response = session.get("https://feedthisdragon4.chall.malicecyber.com/api/v1")
responseJson = response.json()

if __name__ == "__main__":
    try:
        while (
            response.status_code == 200 and int(responseJson["health"]) > 0
        ) and "all" not in currentAchievementsName:
            for item in responseJson["items"]:
                if hurtAcquired:
                    if item["type"] != "trap" and item["type"] != "fox":
                        response = session.post(
                            "https://feedthisdragon4.chall.malicecyber.com/api/v1",
                            headers={"Itemuuid": item["uuid"]},
                        )
                else:
                    if item["type"] != "fox":
                        response = session.post(
                            "https://feedthisdragon4.chall.malicecyber.com/api/v1",
                            headers={"Itemuuid": item["uuid"]},
                        )
                        if item["type"] == "trap":
                            hurtAcquired = True

            for upgrade in responseJson["upgrades"]:
                if "faster" not in currentAchievementsName:
                    if upgrade["name"] == "Greed":
                        if responseJson["coin"] >= upgrade["cost"]:
                            response = session.post(
                                "https://feedthisdragon4.chall.malicecyber.com/api/v1",
                                headers={"Shopuuid": upgrade["uuid"]},
                            )

                    if upgrade["name"] == "Feed":
                        if responseJson["coin"] >= upgrade["cost"]:
                            response = session.post(
                                "https://feedthisdragon4.chall.malicecyber.com/api/v1",
                                headers={"Shopuuid": upgrade["uuid"]},
                            )

                if upgrade["name"] == "Bag" and responseJson["bag"] < 9999:
                    if responseJson["coin"] >= upgrade["cost"]:
                        response = session.post(
                            "https://feedthisdragon4.chall.malicecyber.com/api/v1",
                            headers={"Shopuuid": upgrade["uuid"]},
                        )

            responseJson = response.json()
            updateCookies(session, responseJson["achievements"])
            os.system("clear")
            print(
                f"health : {responseJson['health']} / {responseJson['max_health']}",
                flush=False,
            )
            print(f"level : {responseJson['level']}", flush=False)
            print(
                f"coins : {responseJson['coin']} / {responseJson['bag']}",
                flush=False,
            )
            print(f"achivements : {currentAchievementsName}", flush=True)
            response = session.get(
                "https://feedthisdragon4.chall.malicecyber.com/api/v1"
            )
            responseJson = response.json()
    finally:
        pprint(responseJson)
        exit()
