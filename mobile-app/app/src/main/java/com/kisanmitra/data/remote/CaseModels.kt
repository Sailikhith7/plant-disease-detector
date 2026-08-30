package com.kisanmitra.data.remote

import com.google.gson.annotations.SerializedName

data class CaseListResponse(
    @SerializedName("status") val status: String = "",
    @SerializedName("cases") val cases: List<ExpertDeskCaseDto> = emptyList()
)

data class ExpertDeskCaseDto(
    @SerializedName("case_id") val caseId: String = "",
    @SerializedName("farmer_id") val farmerId: String? = null,
    @SerializedName("farmer_name") val farmerName: String? = null,
    @SerializedName("crop") val crop: String? = null,
    @SerializedName("disease") val disease: String? = null,
    @SerializedName("confidence") val confidence: Int? = 0,
    @SerializedName("district") val district: String? = null,
    @SerializedName("severity") val severity: String? = "Medium",
    @SerializedName("image_url") val imageUrl: String? = null,
    @SerializedName("status") val status: String? = "Pending Expert",
    @SerializedName("expert_response") val expertResponse: String? = null,
    @SerializedName("audio_url") val audioUrl: String? = null,
    @SerializedName("created_at") val createdAt: String? = null
)

data class CaseResponse(
    @SerializedName("case_id")
    val caseId: String? = null,

    @SerializedName("crop")
    val crop: String = "",

    @SerializedName("disease")
    val disease: String = "",

    @SerializedName("confidence")
    val confidence: Float = 0.0f,

    @SerializedName("status")
    val status: String = "",

    @SerializedName("response")
    val response: String = "",

    @SerializedName("language")
    val language: String = "en",

    @SerializedName("audio_url")
    val audioUrl: String? = null
)