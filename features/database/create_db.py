# standardized Python DBI API used to integrate the SQLite database
import sqlite3

# pass/create a db
#conn = sqlite3.connect(':memory:') # for a temporary db
conn = sqlite3.connect('parking_space_management')

#Create a cursor
c = conn.cursor()

# Drop table if it exists
c.execute("DROP TABLE IF EXISTS prices")

# Create a table
c.execute("""CREATE TABLE prices(
          id INTEGER PRIMARY KEY,
          address TEXT,
          ev_charging INTEGER,
          hourly_pricing REAL,
          max_daily_price REAL,
          price_1h REAL,
          price_2h REAL,
          price_3h REAL,
          price_4h REAL,
          price_5h REAL,
          price_6h REAL,
          price_7h REAL
          )
          """)


ids = [(49249524, "Königswall 1, 44137 Dortmund", 0, 1.50, 18.00, 1.50, 3.00, 5.00, 6.00, 8.00, 9.00, 11.00),
       (553319, "Dr.-Safiye-Ali-Str. 13, 44147 Dortmund", 1, 0.50, 6.00, 0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50), 
       (553286, "Am Gottesacker 10, 44143 Dortmund", 0, 0.50, 6.00, 0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50), 
       (553258, "Joseph-Scherer-Straße, 44139 Dortmund", 0, 0.50, 6.00, 0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50), 
       (553203, "Derner Str. 206, 44339 Dortmund", 0, 0.50, 6.00, 0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50), 
       (107394, "Amalienstraße 10, 44137 Dortmund", 1, 2.50, 0.00, 2.50, 5.00, 7.50, 10.00, 12.50, 15.00, 16.00), 
       (107380, "Kuhstraße 12, 44137 Dortmund", 1, 2.00, 0.00, 2.00, 3.80, 5.00, 6.50, 8.00, 9.50, 11.00), # bei Veranstaltungen
       (103824, "Kuckelke 3, 44135 Dortmund", 1, 2.50, 16.00, 2.50, 5.00, 7.50, 10.00, 12.50, 15.00, 16.00),
       (101099, "Hohe Str. 33, 44139 Dortmund", 0, 2.00, 12.00, 2.00, 4.00, 5.00, 6.00, 7.00, 8.00, 9.00),
       (101095, "Steinstrasse 44, 44147 Dortmund", 0, 3.00, 0.00, 3.00, 3.00, 3.00, 3.00, 6.00, 6.00, 6.00),
       (101092, "Königswall 15, 44137 Dortmund", 0, 1.50, 13.00, 1.50, 3.00, 5.00, 6.00, 8.00, 9.00, 11.00),
       (101090, "Leopoldstraße 50, 44147 Dortmund", 0, 2.50, 8.00, 2.50, 2.50, 3.50, 4.50, 5.50, 8.00, 8.00),
       (101088, "Brinkhoffstraße 30, 44137 Dortmund", 0, 2.00, 18.00, 2.00, 4.00, 6.00, 8.00, 10.00, 12.00, 14.00),
       (101075, "Schmiedingstraße 25, 44137 Dortmund", 1, 2.00, 14.00, 2.00, 3.80, 5.00, 6.50, 8.00, 9.50, 11.00),
       (101073, "Kampstraße 45-47, 44135 Dortmund", 0, 2.00, 12.50, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00),
       (101070, "Freistuhl 5, 44137 Dortmund", 1, 2.00, 14.00, 2.00, 4.00, 5.50, 7.00, 8.50, 10.00, 11.50),
       (101067, "Burgwall 8, 44135 Dortmund", 1, 2.00, 14.00, 2.00, 3.80, 5.00, 6.50, 8.00, 9.50, 11.00),
       (101065, "Gerberstraße 8, 44135 Dortmund", 0, 2.50, 16.00, 2.50, 5.00, 7.50, 10.00, 12.50, 15.00, 16.00),
       (101063, "Hövelstraße 2-8, 44137 Dortmund", 0, 2.00, 15.00, 2.00, 4.00, 6.00, 8.00, 10.00, 12.00, 14.00),
       (101061, "Westenhellweg 70, 44137 Dortmund", 0, 2.00, 16.00, 2.00, 4.00, 6.00, 8.00, 10.00, 12.00, 14.00),
       (101059, "Propsteihof 10, 44137 Dortmund", 0, 1.50, 10.00, 1.50, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00),
       (101057, "Hansaplatz 2, 44137 Dortmund", 1, 2.00, 14.00, 2.00, 3.80, 5.00, 6.50, 8.00, 9.50, 11.00),
       (101054, "Prinzenstraße 6, 44137 Dortmund", 1, 2.00, 14.00, 2.00, 3.80, 5.00, 6.50, 8.00, 9.50, 11.00),
       (101052, "Südwall, 44137 Dortmund", 1, 2.00, 14.00, 2.00, 4.00, 5.5, 7.00, 8.5, 10.00, 11.5),]

# insert all parking spaces of Dortmund into a db
c.executemany("""
INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", ids)

#commit commands
conn.commit()

# close connection
conn.close()
