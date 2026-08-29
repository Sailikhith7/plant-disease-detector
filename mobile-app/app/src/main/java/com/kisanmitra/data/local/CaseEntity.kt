package com.kisanmitra.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "offline_cases")
data class CaseEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val localImagePath: String,
    val crop: String,
    val language: String,
    val latitude: Float,
    val longitude: Float,
    val detectedDisease: String,
    val confidence: Float,
    val isSynced: Boolean = false,
    val createdAt: Long = System.currentTimeMillis() // or Long
)