SELECT
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    schemaname = 'public'
ORDER BY
    tablename,
    indexname;

ALTER TABLE yellow146m 
ADD COLUMN l_pickup geometry(Point, 4326),
ADD COLUMN l_dropoff geometry(Point, 4326);

UPDATE yellow146m 
SET l_pickup = ST_SetSRID(ST_MakePoint(l_pickup_lon, l_pickup_lat), 4326)

UPDATE yellow146m
SET l_dropoff = ST_SetSRID(ST_MakePoint(l_dropoff_lon, l_dropoff_lat), 4326)

CREATE INDEX index_point ON public.yellow146m USING gist (l_pickup)
CREATE INDEX index_point2 ON public.yellow146m USING gist (l_dropoff)

CREATE INDEX index_time ON public.yellow146m USING btree (t_pickup)

SELECT * FROM yellow146m
	WHERE 	40.27 < l_pickup_lon
	OR 		l_pickup_lon > 45.02
	OR		40.27 < l_dropoff_lon 
	OR 		l_dropoff_lon > 45.02
	OR		-79.77 > l_pickup_lat 
	OR 		l_pickup_lat < -71.8	
	OR		-79.77 > l_dropoff_lat 
	OR		l_dropoff_lat < -71.8
	
SELECT * FROM yellow146m 
	WHERE	l_pickup_lon = 0
	OR 		l_pickup_lat = 0
	OR		l_dropoff_lon = 0
	OR		l_dropoff_lat = 0

ALTER TABLE yellow146m
ADD COLUMN bird_dist double precision

select ST_Distance(l_pickup, l_dropoff)*1000 from yellow146m limit 5

select ST_Distance(ST_Transform(l_pickup, 2263), 
					ST_Transform(l_dropoff, 2263))*1.2/3937 as dist_2263,
		ST_Distance(l_pickup, l_dropoff)*100 as dist_4326,
		trip_distance
from yellow146m limit 5
					
					
select * from spatial_ref_sys

UPDATE yellow146m
SET bird_dist = ST_Distance(l_pickup,l_dropoff)*100

select * from yellow limit 5

ST_Distance(ST_Transform(l_pickup, 2263), ST_Transform(l_dropoff, 2263))

select ST_Distance(ST_Transform(ST_MakeValid(l_pickup), 2263), 
					ST_Transform(ST_MakeValid(l_dropoff), 2263)) from yellow
					
select ST_Transform(ST_SetSRID(ST_MakePoint(0,0),4326), 2263) from yellow limit 10000

select ST_Transform(ST_SetSRID(ST_MakePoint(2048,0),4326), 4326)

select ST_SetSRID(ST_MakePoint(204844444444444444,0),4326)

select * from yellow
limit 5

select * from yellow limit 2

select ST_Distance(l_pickup, l_dropoff)*100 from yellow limit 2