import requests
import time
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# You would receive this in the interview or use your own
API_KEY = os.getenv("WEATHER_API_KEY")  # In the interview, they'd likely provide this
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Data centers locations (example)
DATA_CENTERS = [
    {"name": "US-East", "lat": 37.7749, "lon": -122.4194},
    {"name": "EU-West", "lat": 53.3498, "lon": -6.2603},
    {"name": "Asia-Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "Australia-Sydney", "lat": -33.8688, "lon": 151.2093},
    {"name": "South America-Sao Paulo", "lat": -23.5505, "lon": -46.6333},
]

@dataclass
class WeatherData:
    location: str
    temperature: float
    humidity: float
    wind_speed: float
    conditions: str
    timestamp: int
    
    @property
    def temperature_celsius(self) -> float:
        """Convert Kelvin to Celsius"""
        return self.temperature - 273.15
    
    @property
    def cooling_cost_factor(self) -> float:
        """Calculate cooling cost factor based on temperature"""
        temp_c = self.temperature_celsius
        # Implement a realistic cooling cost algorithm
        # Higher temperatures require more cooling
        if temp_c <= 20:
            # Below optimal temperature, low cooling costs
            return 0.5
        elif temp_c <= 25:
            # Optimal temperature range, normal cooling costs
            return 1.0
        elif temp_c <= 30:
            # Above optimal, higher cooling costs
            return 1.5
        elif temp_c <= 35:
            # Much above optimal, significant cooling costs
            return 2.0
        else:
            # Extreme heat, very high cooling costs
            return 3.0

class RateLimiter:
    """Simple rate limiter to prevent API throttling"""
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_timestamps = []
    
    async def wait_if_needed(self):
        """Wait if we've exceeded our rate limit"""
        curr_time = time.time()
        # max 1 min old
        self.call_timestamps = [ts for ts in self.call_timestamps if curr_time - ts < 60]
        if len(self.call_timestamps)>=self.calls_per_minute:
            oldest_timestamp = min(self.call_timestamps)
            wait_time = 60 - (curr_time - oldest_timestamp)
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting for {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        self.call_timestamps.append(time.time())

class WeatherClient:
    """Client for fetching weather data"""
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limiter = RateLimiter()
        self.cache = {}  # Simple cache to store results
        
    async def get_weather(self, lat: float, lon: float, location_name: str) -> Optional[WeatherData]:
        """Fetch weather data for a location"""
        # Check cache first for the location
        cache_key = f"{lat}_{lon}"
        if cache_key in self.cache:
            # Check if cache is still fresh (less than 10 minutes old)
            if time.time() - self.cache[cache_key]["timestamp"] < 600:
                logger.info(f"Using cached data for {location_name}")
                return self.cache[cache_key]["data"]
        
        # Apply rate limiting before making a request
        await self.rate_limiter.wait_if_needed()
        
        # Build the request URL with parameters
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,  # This is where the API key goes
            "units": "standard"  # Use Kelvin for temperature
        }
        
        # Make the request with retries
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching weather data for {location_name} (Attempt {attempt+1}/{max_retries})")
                # Since we're using asyncio, we need to use asyncio-compatible requests
                # We use the synchronous requests library with asyncio.to_thread to make it work with asyncio
                response = await asyncio.to_thread(
                    requests.get, self.base_url, params=params, timeout=10
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", retry_delay))
                    logger.warning(f"Rate limited. Waiting for {retry_after} seconds.")
                    await asyncio.sleep(retry_after)
                    continue
                
                # Check for other errors
                if response.status_code != 200:
                    logger.error(f"HTTP error: {response.status_code}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    return None
                
                # Parse the response
                data = response.json()
                
                # Create WeatherData object
                weather_data = WeatherData(
                    location=location_name,
                    temperature=data["main"]["temp"],
                    humidity=data["main"]["humidity"],
                    wind_speed=data["wind"]["speed"],
                    conditions=data["weather"][0]["description"],
                    timestamp=data["dt"]
                )
                
                # Cache the result
                self.cache[cache_key] = {
                    "data": weather_data,
                    "timestamp": time.time()
                }
                
                logger.info(f"Successfully retrieved weather data for {location_name}")
                return weather_data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {location_name}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch weather data for {location_name} after {max_retries} attempts")
                    return None
                    
            except (KeyError, ValueError) as e:
                logger.error(f"Data parsing error for {location_name}: {e}")
                return None

class WeatherAnalyzer:
    """Analyzes weather data to generate insights"""
    def __init__(self):
        pass
        
    def identify_extreme_conditions(self, weather_data_list: List[WeatherData]) -> Dict[str, List[str]]:
        """Identify locations with extreme weather conditions"""
        extreme_conditions = {}
        
        for weather in weather_data_list:
            issues = []
            
            # Check temperature
            temp_c = weather.temperature_celsius
            if temp_c > 35:
                issues.append("Extreme heat")
            elif temp_c < 0:
                issues.append("Extreme cold")
            
            # Check humidity
            if weather.humidity > 80:
                issues.append("High humidity")
            elif weather.humidity < 20:
                issues.append("Low humidity")
            
            # Check wind speed (m/s)
            if weather.wind_speed > 10:
                issues.append("High winds")
            
            # Check for specific weather conditions
            condition_lower = weather.conditions.lower()
            if any(term in condition_lower for term in ["storm", "thunder", "hurricane", "tornado"]):
                issues.append("Severe weather")
            elif any(term in condition_lower for term in ["rain", "shower", "drizzle"]):
                issues.append("Precipitation")
            
            # Add to results if any issues found
            if issues:
                extreme_conditions[weather.location] = issues
        
        return extreme_conditions
    
    def calculate_cost_impacts(self, weather_data_list: List[WeatherData]) -> Dict[str, float]:
        """Calculate potential cost impacts based on weather conditions"""
        cost_impacts = {}
        
        for weather in weather_data_list:
            # Base cost factor starts with cooling cost
            cost_factor = weather.cooling_cost_factor
            
            # Adjust for humidity (higher humidity = more cooling needed)
            if weather.humidity > 60:
                humidity_factor = 1 + ((weather.humidity - 60) / 100)
                cost_factor *= humidity_factor
            
            # Adjust for weather conditions
            condition_lower = weather.conditions.lower()
            if any(term in condition_lower for term in ["storm", "thunder", "hurricane", "tornado"]):
                # Severe weather might require backup systems, increasing costs
                cost_factor *= 1.5
            
            # Convert factor to estimated daily additional cost (example)
            daily_impact = cost_factor * 100  # $100 base cost multiplied by factor
            
            cost_impacts[weather.location] = round(daily_impact, 2)
        
        return cost_impacts
    
    def generate_risk_assessment(self, weather_data_list: List[WeatherData]) -> Dict[str, str]:
        """Generate risk assessment for each location"""
        risk_assessment = {}
        
        for weather in weather_data_list:
            # Start with low risk
            risk_level = "Low"
            risk_factors = []
            
            # Temperature risks
            temp_c = weather.temperature_celsius
            if temp_c > 40:
                risk_level = "Critical"
                risk_factors.append("Extreme heat may cause equipment failure")
            elif temp_c > 35:
                risk_level = max(risk_level, "High")
                risk_factors.append("High heat increases cooling system strain")
            elif temp_c < -5:
                risk_level = max(risk_level, "High")
                risk_factors.append("Extreme cold may affect facility operations")
            
            # Weather condition risks
            condition_lower = weather.conditions.lower()
            if any(term in condition_lower for term in ["hurricane", "tornado"]):
                risk_level = "Critical"
                risk_factors.append("Severe weather threatens physical infrastructure")
            elif any(term in condition_lower for term in ["storm", "thunder"]):
                risk_level = max(risk_level, "High")
                risk_factors.append("Storms may cause power disruptions")
            elif any(term in condition_lower for term in ["rain", "shower", "drizzle"]):
                risk_level = max(risk_level, "Medium")
                risk_factors.append("Precipitation increases humidity concerns")
            
            # Wind risks
            if weather.wind_speed > 20:
                risk_level = max(risk_level, "High")
                risk_factors.append("High winds may damage cooling infrastructure")
            elif weather.wind_speed > 10:
                risk_level = max(risk_level, "Medium")
                risk_factors.append("Moderate winds may affect cooling efficiency")
            
            # Create assessment text
            if risk_factors:
                assessment = f"{risk_level} risk - {'; '.join(risk_factors)}"
            else:
                assessment = "Low risk - Normal operating conditions"
            
            risk_assessment[weather.location] = assessment
        
        return risk_assessment

async def main():
    """Main function to orchestrate the data pipeline"""
    # Initialize the weather client
    weather_client = WeatherClient(API_KEY, BASE_URL)
    
    # Fetch weather data for all data centers concurrently
    tasks = []
    for dc in DATA_CENTERS:
        task = weather_client.get_weather(dc["lat"], dc["lon"], dc["name"])
        tasks.append(task)
    
    # Wait for all tasks to complete
    weather_data_list = await asyncio.gather(*tasks)
    
    # Filter out any failed requests
    weather_data_list = [data for data in weather_data_list if data is not None]
    
    if not weather_data_list:
        logger.error("Failed to fetch weather data for all locations")
        return
    
    # Analyze the data
    analyzer = WeatherAnalyzer()
    extreme_conditions = analyzer.identify_extreme_conditions(weather_data_list)
    cost_impacts = analyzer.calculate_cost_impacts(weather_data_list)
    risk_assessment = analyzer.generate_risk_assessment(weather_data_list)
    
    # Generate report
    generate_report(weather_data_list, extreme_conditions, cost_impacts, risk_assessment)

def generate_report(
    weather_data_list: List[WeatherData],
    extreme_conditions: Dict[str, List[str]],
    cost_impacts: Dict[str, float],
    risk_assessment: Dict[str, str]
):
    """Generate a report of the analysis results"""
    print("\n" + "="*80)
    print(f"WEATHER IMPACT REPORT FOR CLOUD DATA CENTERS - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Current conditions summary
    print("\nCURRENT CONDITIONS:")
    print("-"*80)
    for weather in weather_data_list:
        print(f"Location: {weather.location}")
        print(f"  Temperature: {weather.temperature_celsius:.1f}°C")