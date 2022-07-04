--creating table

DROP TABLE IF EXISTS portfolio_1.nashville_housing;
CREATE TABLE portfolio_1.nashville_housing (	
		unique_id numeric,
		parcel_id text,	
		land_use text,
		property_address text,
		sale_date date,
		sale_price text,
		legal_reference text,
		sold_as_vacant text,
		owner_name text,
		owner_address text,
		acreage numeric,
		tax_district text,
		land_value numeric,
		building_value numeric,
		total_value numeric,
		year_built numeric,
		bedrooms numeric,
		full_bath numeric,	
		half_bath numeric
)
;

-- importing CSV through PGAdmin


-- Selecting all data

SELECT *
FROM portfolio_1.nashville_housing


--DATA CLEANING
-- Populate address data

SELECT *
FROM portfolio_1.nashville_housing
WHERE property_address IS NULL
ORDER BY unique_id

-- Temp Table

DROP TABLE IF EXISTS populated_address;
CREATE TABLE populated_address (unique_id numeric,
								fill_address text);

INSERT INTO populated_address
SELECT DISTINCT ON (a.unique_id)
		a.unique_id,
--		a.property_address,
--		b.unique_id,
--		b.parcel_id, 
--		b.property_address,
		COALESCE(a.property_address, b.property_address) AS fill_address
FROM portfolio_1.nashville_housing AS a
LEFT JOIN portfolio_1.nashville_housing AS b
	ON a.parcel_id = b.parcel_id
	AND a.unique_id <> b.unique_id
ORDER by a.unique_id;

SELECT * FROM populated_address
ORDER BY unique_id


UPDATE portfolio_1.nashville_housing AS A 
SET property_address = b.fill_address
FROM populated_address AS b
WHERE a.unique_id = b.unique_id


-- breaking down address into parts

SELECT property_address,  POSITION(',' IN property_address) - POSITION(' ' IN property_address), POSITION(' ' IN property_address)
FROM portfolio_1.nashville_housing


SELECT	TRIM(SUBSTRING(property_address, 1, POSITION(',' IN property_address)-1)) AS property_street_address,
		TRIM(SUBSTRING(property_address, POSITION(',' IN property_address)+1)) AS property_city
FROM portfolio_1.nashville_housing

--and

SELECT 	TRIM(SPLIT_PART(owner_address,',',1)) AS owner_street_address,
		TRIM(SPLIT_PART(owner_address,',',2)) AS owner_city,
		TRIM(SPLIT_PART(owner_address,',',3)) AS owner_state
FROM portfolio_1.nashville_housing



ALTER TABLE portfolio_1.nashville_housing
	ADD property_street_address varchar;

UPDATE portfolio_1.nashville_housing
	SET property_street_address = TRIM(SUBSTRING(property_address, 1, POSITION(',' IN property_address)-1));
	

ALTER TABLE portfolio_1.nashville_housing
	ADD property_city varchar;

UPDATE portfolio_1.nashville_housing
	SET property_city = TRIM(SUBSTRING(property_address, POSITION(',' IN property_address)+1));

ALTER TABLE portfolio_1.nashville_housing
	ADD owner_street_address varchar;

UPDATE portfolio_1.nashville_housing
	SET owner_street_address = TRIM(SPLIT_PART(owner_address,',',1));
	
ALTER TABLE portfolio_1.nashville_housing
	ADD owner_city varchar;

UPDATE portfolio_1.nashville_housing
	SET owner_city = TRIM(SPLIT_PART(owner_address,',',2));
	
ALTER TABLE portfolio_1.nashville_housing
	ADD owner_state varchar;

UPDATE portfolio_1.nashville_housing
	SET owner_state = TRIM(SPLIT_PART(owner_address,',',3));


-- Change Y and N to Yes and No in sold_as_vacant column

UPDATE portfolio_1.nashville_housing
SET sold_as_vacant =
		CASE	WHEN sold_as_vacant = 'Y' THEN 'Yes'
				WHEN sold_as_vacant = 'N' THEN 'No'
				ELSE sold_as_vacant
		END


-- Removing duplicates

WITH row_number_cte AS (
						SELECT	*,
								ROW_NUMBER() OVER ( PARTITION BY	parcel_id,
																	property_address,
																	sale_price,
																	sale_date,
																	legal_reference
												   ORDER BY unique_id
												  ) AS row_num
						FROM portfolio_1.nashville_housing
						ORDER BY parcel_id
						)
						
-- SELECT *
-- FROM row_number_cte
-- WHERE row_num > 1

DELETE 
FROM portfolio_1.nashville_housing
WHERE unique_id IN (SELECT
				 	unique_id
				  FROM
				  	row_number_cte
				  WHERE
				  	row_num > 1
				 )
;


-- Delete column not to be used

SELECT *
FROM portfolio_1.nashville_housing;

ALTER TABLE portfolio_1.nashville_housing
DROP COLUMN owner_address;

ALTER TABLE portfolio_1.nashville_housing
DROP COLUMN tax_district;

ALTER TABLE portfolio_1.nashville_housing
DROP COLUMN property_address;

ALTER TABLE portfolio_1.nashville_housing
DROP COLUMN sale_date;



		