package com.kisanmitra.data.remote

import com.google.gson.annotations.SerializedName

// --- Weather Risk & Advisory Models (used by WeatherScreen.kt) ---

data class DayForecastDto(
    val date: String = "",
    @SerializedName("max_temp") val maxTemp: Float = 0f,
    @SerializedName("min_temp") val minTemp: Float = 0f,
    @SerializedName("rain_prob") val rainProb: Float = 0f
)

data class FullWeatherDataDto(
    val temperature: Float = 0f,
    val humidity: Float = 0f,
    @SerializedName("rain_prob") val rainProb: Float = 0f,
    @SerializedName("wind_speed") val windSpeed: Float = 0f,
    @SerializedName("uv_index") val uvIndex: Int = 5,
    @SerializedName("spray_safe") val spraySafe: Boolean = true,
    @SerializedName("forecast_5days") val forecast5days: List<DayForecastDto> = emptyList()
)

data class RiskAssessmentDto(
    @SerializedName("is_outbreak_risk") val isOutbreakRisk: Boolean = false,
    @SerializedName("risk_percentage") val riskPercentage: Int = 0,
    @SerializedName("potential_disease") val potentialDisease: String? = null,
    @SerializedName("preventive_advisory") val preventiveAdvisory: String = ""
)

data class FullWeatherDashboardDto(
    val status: String = "",
    val district: String = "",
    val crop: String = "",
    val weather: FullWeatherDataDto? = null,
    @SerializedName("risk_assessment") val riskAssessment: RiskAssessmentDto? = null
)

data class SimulationRequestDto(
    val crop: String,
    val district: String,
    val temperature: Float,
    val humidity: Float,
    @SerializedName("rain_prob") val rainProb: Float,
    val language: String = "mr",
    @SerializedName("trigger_telegram") val triggerTelegram: Boolean = true
)

data class SimulationResponseDto(
    val status: String = "",
    val simulated: Boolean = true,
    @SerializedName("is_outbreak_risk") val isOutbreakRisk: Boolean = false,
    @SerializedName("risk_percentage") val riskPercentage: Int = 0,
    @SerializedName("potential_disease") val potentialDisease: String? = null,
    val advisory: String = "",
    @SerializedName("telegram_dispatched") val telegramDispatched: Boolean = false
)
