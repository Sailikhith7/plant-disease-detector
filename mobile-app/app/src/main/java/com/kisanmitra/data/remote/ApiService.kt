package com.kisanmitra.data.remote

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

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
}