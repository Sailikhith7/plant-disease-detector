package com.kisanmitra.data.remote

import com.google.gson.annotations.SerializedName

data class AdvisoryData(
    @SerializedName("severity") val severity: String? = "medium",
    @SerializedName("cultural") val cultural: String,
    @SerializedName("biological") val biological: String,
    @SerializedName("chemical") val chemical: String
)

data class CaseResponse(
    @SerializedName("caseId") val caseId: String,
    @SerializedName("crop") val crop: String,
    @SerializedName("disease") val disease: String,
    @SerializedName("confidence") val confidence: Float,
    @SerializedName("status") val status: String,
    @SerializedName("requiresExpertReview") val requiresExpertReview: Boolean,
    @SerializedName("advisory") val advisory: AdvisoryData?,
    @SerializedName("createdAt") val createdAt: String? = null
)