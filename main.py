from fastapi import FastAPI
import random
import psycopg2
from collections import Counter
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def model(times, num, top_k, occ):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT numbers FROM daily_results ORDER BY draw_date")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    history = [row[0] for row in rows]

    plot_data = [n for sublist in history for n in sublist]

    counter = Counter(plot_data)

    # last_seen = {n: None for n in range(1, max_number + 1)}

    # for day_index, daily_numbers in enumerate(history):
    #     for number in daily_numbers:
    #         last_seen[number] = day_index

    numbers = []

    for number, count in counter.items():
        if count >= occ:
            numbers.append(number)

    ans = []

    for _ in range(times):
        ans = random.sample(numbers, min(top_k, len(numbers)))

    ans.sort()
    return ans, max(counter.values()), counter[num]


@app.get("/")
def home():
    return {"message": "Lottery Prediction API Running"}


@app.get("/predict")
def predict(times: int = 50, num: int = 4019, top_k: int = 8, occ: int = 6):

    result, highest, times = model(times, num, top_k=top_k, occ=occ)

    return {
        "input_number": num,
        "times": times,
        "highest": highest,
        "prediction": result,
        "params": "times,num,top_k,occ",
    }
