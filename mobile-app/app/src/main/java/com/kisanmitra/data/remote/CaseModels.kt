package com.kisanmitra.data.remote

import com.google.gson.annotations.SerializedName

// --- Predict API Models ---
data class CaseResponse(
    val crop: String = "",
    val disease: String = "",
    val confidence: Float = 0f,
    val status: String = "",
    val response: String = "",
    val language: String = "mr",
    @SerializedName("audio_url")
    val audioUrl: String? = null
)

// --- Expert Desk Models ---
data class CasesListResponseDto(
    val status: String = "",
    val cases: List<CaseItemDto> = emptyList()
)

data class CaseItemDto(
    @SerializedName("case_id")
    val caseId: String = "",
    @SerializedName("farmer_id")
    val farmerId: String? = null,
    @SerializedName("farmer_name")
    val farmerName: String = "",
    val crop: String = "",
    val disease: String = "",
    val confidence: Int = 0,
    val district: String = "",
    val severity: String = "Medium",
    val latitude: Float? = null,
    val longitude: Float? = null,
    @SerializedName("image_url")
    val imageUrl: String? = null,
    val status: String = "Pending Expert",
    @SerializedName("expert_response")
    val expertResponse: String? = null,
    @SerializedName("audio_url")
    val audioUrl: String? = null,
    @SerializedName("created_at")
    val createdAt: String? = null
)

typealias ExpertDeskCaseDto = CaseItemDto

data class ExpertResolveRequestDto(
    @SerializedName("expert_response")
    val expertResponse: String,
    val language: String = "mr"
)

data class ExpertResolveResponseDto(
    val status: String = "",
    @SerializedName("case_id")
    val caseId: String = "",
    val message: String = "",
    @SerializedName("expert_response")
    val expertResponse: String = "",
    @SerializedName("audio_url")
    val audioUrl: String? = null
)

// --- Weather Risk & Advisory Models ---
data class WeatherRiskResponseDto(
    val status: String = "",
    val district: String = "",
    val crop: String = "",
    val weather: WeatherDataDto? = null,
    @SerializedName("risk_assessment")
    val riskAssessment: RiskAssessmentDto? = null
)

data class WeatherDataDto(
    val temperature: Float = 0f,
    val humidity: Float = 0f,
    @SerializedName("rain_prob")
    val rainProb: Float = 0f,
    @SerializedName("weather_desc")
    val weatherDesc: String = ""
)

data class RiskAssessmentDto(
    @SerializedName("is_outbreak_risk")
    val isOutbreakRisk: Boolean = false,
    @SerializedName("risk_level")
    val riskLevel: String = "LOW",
    @SerializedName("risk_percentage")
    val riskPercentage: Int = 0,
    @SerializedName("potential_disease")
    val potentialDisease: String? = null,
    @SerializedName("preventive_advisory")
    val preventiveAdvisory: String = ""
)

// --- Full Weather Dashboard & Simulation Models ---
data class FullWeatherDashboardDto(
    val status: String = "",
    val district: String = "",
    val crop: String = "",
    val weather: FullWeatherDataDto? = null,
    @SerializedName("risk_assessment")
    val riskAssessment: RiskAssessmentDto? = null
)

data class FullWeatherDataDto(
    val temperature: Float = 0f,
    val humidity: Float = 0f,
    @SerializedName("rain_prob")
    val rainProb: Float = 0f,
    @SerializedName("wind_speed")
    val windSpeed: Float = 0f,
    @SerializedName("uv_index")
    val uvIndex: Int = 5,
    @SerializedName("spray_safe")
    val spraySafe: Boolean = true,
    @SerializedName("forecast_5days")
    val forecast5days: List<DayForecastDto> = emptyList()
)

data class DayForecastDto(
    val date: String = "",
    @SerializedName("max_temp")
    val maxTemp: Float = 0f,
    @SerializedName("min_temp")
    val minTemp: Float = 0f,
    @SerializedName("rain_prob")
    val rainProb: Float = 0f
)

data class SimulationRequestDto(
    val crop: String,
    val district: String,
    val temperature: Float,
    val humidity: Float,
    @SerializedName("rain_prob")
    val rainProb: Float,
    val language: String = "mr",
    @SerializedName("trigger_telegram")
    val triggerTelegram: Boolean = true
)

data class SimulationResponseDto(
    val status: String = "",
    val simulated: Boolean = true,
    @SerializedName("is_outbreak_risk")
    val isOutbreakRisk: Boolean = false,
    @SerializedName("risk_percentage")
    val riskPercentage: Int = 0,
    @SerializedName("potential_disease")
    val potentialDisease: String? = null,
    val advisory: String = "",
    @SerializedName("telegram_dispatched")
    val telegramDispatched: Boolean = false
)