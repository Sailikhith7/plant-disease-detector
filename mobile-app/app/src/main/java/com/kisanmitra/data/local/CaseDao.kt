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

    @Query("SELECT * FROM cached_cases WHERE isSynced = 0")
    suspend fun getUnsyncedCases(): List<CaseEntity>

    @Query("UPDATE cached_cases SET isSynced = 1, detectedDisease = :disease, confidence = :confidence WHERE id = :id")
    suspend fun markCaseSynced(id: Long, disease: String, confidence: Float)

    @Query("SELECT * FROM cached_cases ORDER BY createdAt DESC")
    fun getAllCasesFlow(): Flow<List<CaseEntity>>
}