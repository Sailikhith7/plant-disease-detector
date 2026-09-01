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
        @Part("crop") crop: RequestBody? = null,
        @Part("farmer_name") farmerName: RequestBody? = null,
        @Part("district") district: RequestBody? = null,
        @Part("farmer_id") farmerId: RequestBody? = null
    ): Response<CaseResponse>

    @GET("api/cases")
    suspend fun getCases(
        @Query("farmer_name") farmerName: String? = null
    ): Response<CaseListResponse>

    @POST("api/cases/{case_id}/expert-request")
    suspend fun requestExpertReview(
        @Path("case_id") caseId: String,
        @Body payload: ExpertReviewRequestDto
    ): Response<GenericStatusResponseDto>

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