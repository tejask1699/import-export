const axios = require('axios');

const API_KEY = 'bf98922579d3a372232f5f1736ece285';
const BASE_URL = 'https://api.openweathermap.org/data/2.5';

class WeatherService {
    static async getCurrentWeather(lat, lon) {
        try {
            const response = await axios.get(`${BASE_URL}/weather`, {
                params: {
                    lat: lat,
                    lon: lon,
                    appid: API_KEY,
                    units: 'metric'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching weather data:', error.message);
            throw new Error('Failed to fetch weather data');
        }
    }

    static async getWeatherByCity(city) {
        try {
            const response = await axios.get(`${BASE_URL}/weather`, {
                params: {
                    q: city,
                    appid: API_KEY,
                    units: 'metric'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching weather data for city:', error.message);
            throw new Error('Failed to fetch weather data for city');
        }
    }

    static async getForecast(lat, lon) {
        try {
            const response = await axios.get(`${BASE_URL}/forecast`, {
                params: {
                    lat: lat,
                    lon: lon,
                    appid: API_KEY,
                    units: 'metric'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching forecast data:', error.message);
            throw new Error('Failed to fetch forecast data');
        }
    }

    static isWeatherSuitableForShipping(weatherData) {
        const main = weatherData.weather[0].main.toLowerCase();
        const temp = weatherData.main.temp;
        const windSpeed = weatherData.wind.speed;
        const visibility = weatherData.visibility || 10000;
        const rain = weatherData.rain ? weatherData.rain['1h'] || 0 : 0;
        const snow = weatherData.snow ? weatherData.snow['1h'] || 0 : 0;

        // Weather conditions that prevent shipping
        const dangerousConditions = [
            'thunderstorm',
            'tornado',
            'hurricane',
            'extreme'
        ];

        // Check for dangerous weather conditions
        if (dangerousConditions.includes(main)) {
            return {
                suitable: false,
                reason: `Dangerous weather condition: ${main}`,
                risk: 'HIGH'
            };
        }

        // Check temperature extremes
        if (temp < -10 || temp > 45) {
            return {
                suitable: false,
                reason: `Extreme temperature: ${temp}°C`,
                risk: 'HIGH'
            };
        }

        // Check wind speed
        if (windSpeed > 20) {
            return {
                suitable: false,
                reason: `High wind speed: ${windSpeed} m/s`,
                risk: 'MEDIUM'
            };
        }

        // Check visibility
        if (visibility < 1000) {
            return {
                suitable: false,
                reason: `Poor visibility: ${visibility}m`,
                risk: 'MEDIUM'
            };
        }

        // Check heavy rain
        if (rain > 10) {
            return {
                suitable: false,
                reason: `Heavy rain: ${rain}mm/h`,
                risk: 'MEDIUM'
            };
        }

        // Check snow
        if (snow > 5) {
            return {
                suitable: false,
                reason: `Heavy snow: ${snow}mm/h`,
                risk: 'MEDIUM'
            };
        }

        // Moderate conditions that might need caution
        let warnings = [];
        let risk = 'LOW';

        if (windSpeed > 15) {
            warnings.push(`Moderate wind: ${windSpeed} m/s`);
            risk = 'MEDIUM';
        }

        if (rain > 2) {
            warnings.push(`Light to moderate rain: ${rain}mm/h`);
            risk = 'MEDIUM';
        }

        if (main === 'drizzle' || main === 'mist' || main === 'fog') {
            warnings.push(`Reduced visibility due to ${main}`);
            risk = 'MEDIUM';
        }

        return {
            suitable: true,
            reason: warnings.length > 0 ? warnings.join(', ') : 'Weather conditions are suitable for shipping',
            risk: risk,
            warnings: warnings
        };
    }

    static getShippingRecommendation(weatherData) {
        const analysis = this.isWeatherSuitableForShipping(weatherData);
        
        let recommendation = '';
        let action = '';

        if (analysis.suitable) {
            if (analysis.risk === 'LOW') {
                recommendation = '✅ Proceed with shipping - Weather conditions are optimal';
                action = 'PROCEED';
            } else {
                recommendation = '⚠️ Proceed with caution - Monitor weather conditions';
                action = 'CAUTION';
            }
        } else {
            if (analysis.risk === 'HIGH') {
                recommendation = '🚫 Do not ship - Dangerous weather conditions';
                action = 'CANCEL';
            } else {
                recommendation = '⏳ Delay shipping - Wait for better conditions';
                action = 'DELAY';
            }
        }

        return {
            ...analysis,
            recommendation,
            action
        };
    }
}

module.exports = WeatherService;
