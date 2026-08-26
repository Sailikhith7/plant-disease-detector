package com.kisanmitra.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "cached_cases")
data class CaseEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val localImagePath: String,
    val crop: String,
    val language: String,
    val latitude: Float,
    val longitude: Float,
    val detectedDisease: String = "Analyzing...",
    val confidence: Float = 0f,
    val isSynced: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
)