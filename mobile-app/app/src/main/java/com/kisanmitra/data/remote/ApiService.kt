package com.kisanmitra.data.remote

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface ApiService {
    @Multipart
    @POST("/api/cases")
    suspend fun submitCase(
        @Part image: MultipartBody.Part,
        @Part("farmerId") farmerId: RequestBody,
        @Part("crop") crop: RequestBody,
        @Part("latitude") latitude: RequestBody,
        @Part("longitude") longitude: RequestBody,
        @Part("district") district: RequestBody,
        @Part("language") language: RequestBody
    ): Response<CaseResponse>
}