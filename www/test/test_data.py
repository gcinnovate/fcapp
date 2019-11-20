# import sys
import simplejson
import psycopg2
import psycopg2.extras
import random

config = {
    "db_name": "fctemba",
    "db_host": "localhost",
    "db_port": "5432",
    "db_user": "postgres",
    "db_passwd": "postgres"
}

conn = psycopg2.connect(
    "dbname=" + config["db_name"] + " host= " + config["db_host"] + " port=" + config["db_port"] +
    " user=" + config["db_user"] + " password=" + config["db_passwd"])

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

data = [
    ["Mayuge", "Baitambogwe", "Butte", "Bute B", "Bute HC II", "aPXQhyTI3oq"],
    ["Mayuge", "Kigandalo", "", "Kioga", "Kyoga HC II", "qIZ5LRWbGhE"],
    ["Mayuge", "Bukabooli", "Buyugu", "Busitema", "Buyugu HC II", "OPOuhWyA5PX"],
    ["Mayuge", "Mayuge Town Council", "Kyebando Ward", "St. Mulumba", "Mayuge HC III", "qkq6TBG0tnA"],
    ["Mayuge", "Mpungwe", "Muggi", "Muggi", "Muggi HC II", "ac4kdbslWxB"],
    ["Mayuge", "Kityerera", "Kityerera", "Bugadde B", "Kityerera HC IV", "W65MlPtBlmF"],
    ["Zombo", "Akaa", "Ayaka", "Akaa", "Amwonyo HC II", "V3MblSOicMQ"],
    ["Zombo", "Paidha Town Council", "Dwonga Ward", "Thungu", "Paidha HC III", "P1F2OCX6d3t"],
    ["Zombo", "Zeu", "Lorr Central", "Anyu", "Zeu HC III", "Wk8yKMCUZOk"],
    ["Zombo", "Paidha", "Otheko", "Jupaneka", "Paidha HC III", "P1F2OCX6d3t"],
    ["Zombo", "Alangi", "Angar", "Lunguru", "Alangi HC III", "apEUhKfLxjY"],
    ["Nebbi", "Parombo", "Parwo", "Jupanguma", "Parombo HC III", "xYbII9uvF5o"],
    ["Nebbi", "Atego", "Pamora Upper", "Ayombira", "Paminya HC III", "t8rivYmnWIo"],
    ["Nebbi", "Kucwiny", "Mvura", "Orango", "Kucwiny HC III", "a6UyqE2Tgjx"],
    ["Nebbi", "Nebbi", "Forest Ward", "Oryang", "Nebbi Hospital", "iEdI13kUo0h"],
    ["Nebbi", "Erussi", "Pachaka", "Oriwo Acwera II", "Jupanziri HC III", "T2ENFWE19Bu"]
]

INDICATORS = [
    "male_1_5_yrs", "female_1_5_yrs", "male_10_14_yrs", "male_15_19_yrs",
    "male_20_24_yrs", "male_25_49_yrs", "male_1_11_month", "male_lt_1_month", "female_10_14_yrs",
    "female_15_19_yrs", "female_20_24_yrs", "female_25_49_yrs", "female_1_11_month", "female_lt_1_month"
]

# cur.execute("SELECT id, name FROM fcapp_locations WHERE level = 2")
# res = cur.fetchall()

for d in data:
    cur.execute("SELECT id FROM fcapp_locations WHERE name = %s AND level = 2", [d[0]])
    district_id = cur.fetchone()['id']
    hh_number = '{0:03d}'.format(random.choice(range(1, 100)))

    values = {'hh_number': hh_number}
    for i in INDICATORS:
        values[i] = random.choice(range(0, 50))
    print(values)
    cur.execute(
        "INSERT INTO fcapp_flow_data(district, facility, facilityuid, subcounty, village, "
        "report_type, month, year, quarter, values) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        [
            district_id, d[4], d[5], d[1], d[3], 'gis', '2019-11', '2019', '2019Q4',
            psycopg2.extras.Json(values, dumps=simplejson.dumps)
        ])
    conn.commit()

conn.close()
