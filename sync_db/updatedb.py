import psycopg2
from psycopg2.extras import Json
import os
import dotenv

dotenv.load_dotenv()
local_db = os.getenv("LOCAL_DB")
render_db = os.getenv("RENDER_DB")

local_conn = psycopg2.connect(local_db)
render_conn = psycopg2.connect(render_db)

lcur = local_conn.cursor()
rcur = render_conn.cursor()

# get newest row in render
rcur.execute("SELECT MAX(draw_date) FROM daily_results")
last_date = rcur.fetchone()[0]

# fetch new rows from local
lcur.execute(
    "SELECT draw_date, numbers FROM daily_results WHERE draw_date > %s", (last_date,)
)

rows = lcur.fetchall()


for row in rows:
    rcur.execute(
        "INSERT INTO daily_results (draw_date, numbers) VALUES (%s,%s)",
        (row[0], Json(row[1])),
    )

render_conn.commit()

print("Synced", len(rows), "rows")
