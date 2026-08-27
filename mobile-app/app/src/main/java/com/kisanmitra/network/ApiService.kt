package com.kisanmitra.network
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

data class PredictionResponse(
    val disease: String,
    val confidence: Float,
    val prevention_info: String? = null
)

interface ApiService {
    @Multipart
    @POST("/api/predict")
    suspend fun predictDisease(
        @Part image: MultipartBody.Part,
        @Part("language") language: RequestBody
    ): PredictionResponse
}
