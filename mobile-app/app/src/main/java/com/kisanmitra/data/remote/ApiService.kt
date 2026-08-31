package com.kisanmitra.data.remote

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    @Multipart
    @POST("api/predict")
    suspend fun predictDisease(
        @Part image: MultipartBody.Part,
        @Part("language") language: RequestBody,
        @Part("crop") crop: RequestBody,
        @Part("farmer_name") farmerName: RequestBody,
        @Part("district") district: RequestBody,
        @Part("farmer_id") farmerId: RequestBody
    ): Response<CaseResponse>

    @GET("api/cases")
    suspend fun listCases(
        @Query("farmer_name") farmerName: String? = null,
        @Query("farmer_id") farmerId: String? = null
    ): Response<CasesListResponseDto>

    @GET("api/cases")
    suspend fun getCases(
        @Query("farmer_name") farmerName: String? = null,
        @Query("farmer_id") farmerId: String? = null
    ): Response<CasesListResponseDto>

    @POST("api/cases/{case_id}/resolve")
    suspend fun resolveCase(
        @Path("case_id") caseId: String,
        @Body request: ExpertResolveRequestDto
    ): Response<ExpertResolveResponseDto>

    @GET("api/weather/risk-advisory")
    suspend fun getWeatherRiskAdvisory(
        @Query("crop") crop: String,
        @Query("district") district: String,
        @Query("language") language: String,
        @Query("simulate_outbreak") simulate: Boolean = false
    ): Response<WeatherRiskResponseDto>

    @GET("api/weather/full-dashboard")
    suspend fun getFullWeatherDashboard(
        @Query("crop") crop: String,
        @Query("district") district: String,
        @Query("language") language: String
    ): Response<FullWeatherDashboardDto>

    @POST("api/weather/simulate")
    suspend fun simulateWeatherRisk(
        @Body payload: SimulationRequestDto
    ): Response<SimulationResponseDto>
}