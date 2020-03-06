import os
from psycopg2 import connect


res2 = [['tqk#9714', 'Tqk'],
 ['ひろきん#3653', 'GOI'],
 ['Nerve#8156', 'nrvft'],
 ['ねしゃ～#8529', 'nesya'],
 ['Ko#9356', 'keiouok'],
 ['NOSS#9904', 'NOSS'],
 ['shun0923#8647', 'shun0923'],
 ['かるだの#1084', 'karudano'],
 ['Kodaman', '#1261'],
 ['Kodaman#1261', 'KoD'],
 ['maguro#6630', 'Altale'],
 ['31536000#9725', 'cirno3153'],
 ['Thistle#8983', 'Thistle'],
 ['prime#2302', 'primenumber']]

with connect(os.environ['DATABASE_URL']) as conn:
    with conn.cursor() as cur:
        for [disc,atc] in res2:
            cur.execute("INSERT INTO profile (discord_name, atcoder_name, color) "
                        "VALUES (%s, %s, '')", (disc,atc))
        print("operation successfull")
