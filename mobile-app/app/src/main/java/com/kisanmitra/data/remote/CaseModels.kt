package com.kisanmitra.data.remote

import com.google.gson.annotations.SerializedName

data class CaseResponse(

    @SerializedName("case_id")
    val caseId: String? = null,

    @SerializedName("crop")
    val crop: String = "",

    @SerializedName("disease")
    val disease: String = "",

    @SerializedName("confidence")
    val confidence: Float = 0f,

    @SerializedName("status")
    val status: String = "",

    @SerializedName("response")
    val response: String = "",

    @SerializedName("language")
    val language: String = "en",

    @SerializedName("audio_url")
    val audioUrl: String? = null
)