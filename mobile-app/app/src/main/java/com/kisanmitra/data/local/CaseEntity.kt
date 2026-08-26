package com.kisanmitra.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "offline_cases")
data class CaseEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val localImagePath: String = "",
    val crop: String = "",
    val language: String = "en",
    val latitude: Float = 0f,
    val longitude: Float = 0f,
    val detectedDisease: String = "Pink Bollworm",
    val confidence: Float = 0.92f,
    val isSynced: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
)