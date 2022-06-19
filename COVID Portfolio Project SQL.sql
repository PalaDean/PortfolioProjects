SELECT *
FROM portfolio_1.CovidDeaths

SELECT *
FROM portfolio_1.CovidVaccinations

-- Select Data to be used

SELECT	location,
		TO_DATE(date, 'DD MM YYYY') AS new_date,
		total_cases,
		new_cases,
		total_deaths,
		population
FROM portfolio_1.CovidDeaths
ORDER BY location, new_date

-- Looking at Total Cases vs Total Deaths 
-- Show likelihood of dying in UK

SELECT	location,
		TO_DATE(date, 'DD MM YYYY') AS new_date,
		total_cases,
		total_deaths,
		ROUND((total_deaths/total_cases) * 100, 2) AS DeathPercentage
FROM portfolio_1.CovidDeaths
WHERE location = 'United Kingdom'
ORDER BY location, new_date DESC

-- Looking at Total Cases vs Population

SELECT	location,
		TO_DATE(date, 'DD MM YYYY') AS new_date,
		population,
		total_cases,
		ROUND((total_cases/population) * 100, 2) AS DeathPercentage
FROM portfolio_1.CovidDeaths
WHERE location = 'United Kingdom'
ORDER BY location, new_date DESC


-- Looking at Countries with Highest Infection Rate compared to Population

SELECT	location,
		population,
		MAX(total_cases) as HighestInfectionCount,
		MAX(ROUND((total_cases/population) * 100, 2)) AS PercentPopulationInfected
FROM portfolio_1.CovidDeaths
WHERE total_cases IS NOT null and population IS NOT null
GROUP BY location, population
ORDER BY PercentPopulationInfected DESC


-- Show countries with highest death count per population

SELECT	location,
		MAX(CAST(total_deaths AS int)) as HighestDeathCount
FROM portfolio_1.CovidDeaths
WHERE total_deaths IS NOT null AND continent IS NOT null
GROUP BY location
ORDER BY HighestDeathCount DESC


-- highest death count by continent

SELECT	continent,
		MAX(CAST(total_deaths AS int)) as HighestDeathCount
FROM portfolio_1.CovidDeaths
WHERE total_deaths IS NOT null AND continent IS NOT null
GROUP BY continent
ORDER BY HighestDeathCount DESC


-- Showing continents with highest death count per population

SELECT	continent,
		MAX(CAST(total_deaths AS int)) as HighestDeathCount
FROM portfolio_1.CovidDeaths
WHERE total_deaths IS NOT null AND continent IS NOT null
GROUP BY continent
ORDER BY HighestDeathCount DESC


-- Total Population vs Vaccinations

--Using CTE

WITH PopVsVac (continent,
			   location,
			   new_date,
			   population, 
			   new_vaccination, 
			   RollingPeopleVaccinated
			  )
AS
(
SELECT	d.continent,
		d.location,
		TO_DATE(d.date, 'DD MM YYYY') AS new_date,
		d.population,
		v.new_vaccinations,
		SUM(CAST(v.new_vaccinations AS INTEGER))
			OVER (PARTITION BY d.location
				 	ORDER BY d.location, TO_DATE(d.date, 'DD MM YYYY')
				 ) AS RollingPeopleVaccinated
FROM portfolio_1.CovidDeaths AS d
JOIN portfolio_1.CovidVaccinations AS v
	ON d.location = v.location
	AND d.date = v.date
WHERE v.new_vaccinations IS NOT null AND d.continent IS NOT null
)

SELECT 	*,
		ROUND((RollingPeopleVaccinated/population)*100, 2)
FROM PopVsVAc
ORDER BY location, new_date


-- TEMP TABLE

DROP TABLE IF EXISTS PercentPopulationVaccinated
CREATE TABLE PercentPopulationVaccinated
	(
	continent varchar,
	location varchar,
	date date,
	population numeric,
	new_vaccinations numeric,
	RollingPeopleVaccinated numeric
	)

INSERT INTO PercentPopulationVaccinated
SELECT	d.continent,
		d.location,
		TO_DATE(d.date, 'DD MM YYYY') AS new_date,
		d.population,
		CAST(v.new_vaccinations AS INTEGER),
		SUM(CAST(v.new_vaccinations AS INTEGER))
			OVER (PARTITION BY d.location
				 	ORDER BY d.location, TO_DATE(d.date, 'DD MM YYYY')
				 ) AS RollingPeopleVaccinated
FROM portfolio_1.CovidDeaths AS d
JOIN portfolio_1.CovidVaccinations AS v
	ON d.location = v.location
	AND d.date = v.date
WHERE v.new_vaccinations IS NOT null AND d.continent IS NOT null

SELECT 	*,
		ROUND((RollingPeopleVaccinated/population)*100, 2)
FROM PercentPopulationVaccinated
ORDER BY location, date


-- Creating view to store data for later visualisations

CREATE VIEW PercentPopulationVaccinatedView AS
SELECT	d.continent,
		d.location,
		TO_DATE(d.date, 'DD MM YYYY') AS new_date,
		d.population,
		CAST(v.new_vaccinations AS INTEGER),
		SUM(CAST(v.new_vaccinations AS INTEGER))
			OVER (PARTITION BY d.location
				 	ORDER BY d.location, TO_DATE(d.date, 'DD MM YYYY')
				 ) AS RollingPeopleVaccinated
FROM portfolio_1.CovidDeaths AS d
JOIN portfolio_1.CovidVaccinations AS v
	ON d.location = v.location
	AND d.date = v.date
WHERE v.new_vaccinations IS NOT null AND d.continent IS NOT null

SELECT *
FROM PercentPopulationVaccinatedView



