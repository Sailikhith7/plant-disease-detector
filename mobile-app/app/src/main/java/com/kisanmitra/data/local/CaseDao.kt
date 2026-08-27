package com.kisanmitra.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface CaseDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCase(caseEntity: CaseEntity): Long

    @Query("SELECT * FROM offline_cases ORDER BY id DESC")
    fun getAllCasesFlow(): Flow<List<CaseEntity>>

    @Query("SELECT * FROM offline_cases ORDER BY id DESC")
    suspend fun getAllCases(): List<CaseEntity>

    @Query("SELECT * FROM offline_cases WHERE isSynced = 0")
    suspend fun getUnsyncedCases(): List<CaseEntity>

    @Query("UPDATE offline_cases SET isSynced = 1, detectedDisease = :disease, confidence = :confidence WHERE id = :caseId")
    suspend fun markCaseSynced(caseId: Long, disease: String, confidence: Float)
}