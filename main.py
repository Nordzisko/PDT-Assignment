import sys
import random
import json
from flask import Flask, render_template, jsonify
#from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__)


@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/plants/')
def plantsAll():
    plants = getAllPlants()
    coords = [[json.loads(point[1])["coordinates"][0],json.loads(point[1])["coordinates"][1],point[0] ] for point in plants]
    return jsonify({"data": coords}) 
    
def getAllPlants():
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password='****'")
    cursor = conn.cursor()
    cursor.execute("SELECT name,ST_AsGeoJSON(nuc_location) FROM nuclear")
    plants = cursor.fetchall()
    conn.close()
    cursor.close()
    return plants

#@app.route('/radius/')
#def radiusAll():
#    plants = getAllRadius()
#    coords = [[json.loads(point[0])["coordinates"][1],json.loads(point[0])["coordinates"][0] ] for point in plants]
#    return jsonify({"data": coords}) 
#    
#def getAllRadius():
#    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password='****'")
#    cursor = conn.cursor()
#    cursor.execute("SELECT ST_AsGeoJSON(geom) FROM \"gis.osm_traffic_free_1\" CROSS JOIN ( SELECT nuc_geom as nuc_geom FROM nuclear WHERE name = 'MOCHOVCE') a WHERE ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) < 50000 AND fclass='fuel' AND name != '';")
#    radius = cursor.fetchall()
#    conn.close()
#    cursor.close()
#    return radius
    
@app.route('/pumps/<params>')
def nearPumps(params):
    lat = float(params.split(",")[0].split("=")[1])
    lon = float(params.split(",")[1].split("=")[1])
    actualPump = params.split(",")[2].split("=")[1]
    distance = int(params.split(",")[3].split("=")[1])
    pumps = getNearPumps(lat,lon,actualPump,distance)
#    coords = [json.loads(point[0])["coordinates"] for point in plants]
    coords = [[json.loads(point[1])["coordinates"][0],json.loads(point[1])["coordinates"][1],point[0] ] for point in pumps]
    return jsonify({"data": coords}) 
    
def getNearPumps(lat,lon,actPump,distance):
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password='****'")
    cursor = conn.cursor()
    cursor.execute("""SELECT name,geom,dist_me FROM (
                    SELECT DISTINCT name,ST_AsGeoJSON(geom) as geom
                    , ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) as dist_pump 
                    , ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me 
                    FROM "gis.osm_traffic_free_1"
                    CROSS JOIN ( SELECT nuc_geom as nuc_geom FROM nuclear WHERE name = %s) a
                    WHERE fclass='fuel' AND ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) > %s  
                    ) a
                    CROSS JOIN ( SELECT  ST_Distance(ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography) AS ele_me FROM nuclear WHERE name = %s ) b
                    WHERE dist_pump > b.ele_me  
                    ORDER BY dist_me ASC
                    LIMIT 10;""",(lon,lat,actPump,distance,lon,lat,actPump,))
    radius = cursor.fetchall()
    conn.close()
    cursor.close()
    return radius
    
@app.route('/supermarkets/<params>')
def nearSupermarkets(params):
    lat = float(params.split(",")[0].split("=")[1])
    lon = float(params.split(",")[1].split("=")[1])
    actualPump = params.split(",")[2].split("=")[1]
    distance = int(params.split(",")[3].split("=")[1])
    pumps = getNearSupers(lat,lon,actualPump,distance)
#    coords = [json.loads(point[0])["coordinates"] for point in plants]
    coords = [[json.loads(point[1])["coordinates"][0],json.loads(point[1])["coordinates"][1],point[0] ] for point in pumps]
    return jsonify({"data": coords}) 
    
def getNearSupers(lat,lon,actPump,distance):
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password='****'")
    cursor = conn.cursor()
    cursor.execute("""SELECT name,geom,dist_me FROM (
                    SELECT DISTINCT name,ST_AsGeoJSON(geom) as geom
                    , ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) as dist_pump 
                    , ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me 
                    FROM "gis.osm_pois_free_1"
                    CROSS JOIN ( SELECT nuc_geom as nuc_geom FROM nuclear WHERE name = %s) a
                    WHERE fclass='supermarket' AND ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) > %s  
                    ) a
                    CROSS JOIN ( SELECT  ST_Distance(ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography) AS ele_me FROM nuclear WHERE name = %s ) b
                    WHERE dist_pump > b.ele_me  
                    ORDER BY dist_me ASC
                    LIMIT 10;""",(lon,lat,actPump,distance,lon,lat,actPump,))
    radius = cursor.fetchall()
    conn.close()
    cursor.close()
    return radius

@app.route('/rivers/<params>')
def contRivers(params):
    actualPlant = params.split(",")[0].split("=")[1]
    distance = int(params.split(",")[1].split("=")[1])
    rivers = getRivers(actualPlant,distance)
    coords = [json.loads(point[0]) for point in rivers]
    return jsonify({"data": coords}) 

def getRivers(actPlant,distance):
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password='****'")
    cursor = conn.cursor()
    cursor.execute("""SELECT ST_AsGeoJSON(geom),name,geom as river_geom  
                    FROM "gis.osm_water_a_free_1" 
                    CROSS JOIN ( SELECT nuc_geom as nuc_geom FROM nuclear WHERE name = %s) a
                    WHERE ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) < %s 
                    UNION 
                    SELECT ST_AsGeoJSON(geom),name,geom as river_geom  
                    FROM "gis.osm_waterways_free_1"
                    CROSS JOIN ( SELECT nuc_geom as nuc_geom FROM nuclear WHERE name = %s) a
                    WHERE ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) < %s """,
                    (
                     actPlant,
                     distance,
                     actPlant,
                     distance,
                    )
                    )
    radius = cursor.fetchall()
    conn.close()
    cursor.close()
    return radius   


@app.route('/safehouse/<params>')
def safeHouse(params):
    start_p_long = float(params.split(",")[1].split("=")[1])
    start_p_lat = float(params.split(",")[0].split("=")[1])
    end_p_long = float(params.split(",")[3].split("=")[1])
    end_p_lat = float(params.split(",")[2].split("=")[1])
    power_plant = params.split(",")[4].split("=")[1]
    distance = int(params.split(",")[5].split("=")[1])
    safehouse = getSafeHouse(start_p_long,start_p_lat,end_p_long,end_p_lat,power_plant,distance)
#    coords = [json.loads(point[0])["coordinates"] for point in plants]
    coords = [[json.loads(point[0])["coordinates"][0],json.loads(point[0])["coordinates"][1],point[1] ] for point in safehouse]
    return jsonify({"data": coords}) 

def getSafeHouse(start_p_long,start_p_lat,end_p_long,end_p_lat,power_plant,distance):
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password='****'")
    cursor = conn.cursor()
    cursor.execute("""SELECT
                    ST_AsGeoJSON(geom) 
                    ,name
                    ,ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(ST_MakeLine(ST_MakePoint(%s,%s),ST_MakePoint(%s,%s)), 4326)::Geography ) as dist_me 
                    FROM 
                    (
                    SELECT name,geom FROM "gis.osm_pois_free_1" WHERE fclass ='town_hall' 
                    ) ths 
                    CROSS JOIN ( SELECT nuc_geom as nuc_geom FROM nuclear WHERE name = %s) a
                    WHERE ST_Distance(ST_SetSRID(geom, 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) > (
                    	SELECT CASE WHEN ST_Distance(ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) > %s AND 
                    			 ST_Distance(ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography , ST_SetSRID(nuc_geom, 4326)::Geography ) > %s
                    			 THEN %s ELSE 0 END 
                    	FROM ( SELECT nuc_geom as nuc_geom FROM nuclear WHERE name = %s) a
                    )
                    ORDER BY dist_me ASC LIMIT 1""",
                    (
                    start_p_long,
                    start_p_lat,
                    end_p_long,
                    end_p_lat,
                    power_plant,
                    start_p_long,
                    start_p_lat,
                    distance,
                    end_p_long,
                    end_p_lat,
                    distance,
                    distance,
                    power_plant,
                     )
                    )
    radius = cursor.fetchall()
    conn.close()
    cursor.close()
    return radius    



if __name__ == '__main__':
    app.run(debug=True)
