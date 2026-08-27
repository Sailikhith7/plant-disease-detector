package com.kisanmitra.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.kisanmitra.data.local.AppDatabase
import com.kisanmitra.data.remote.ApiClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

class SyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val db = AppDatabase.getDatabase(applicationContext)
            val unsyncedCases = db.caseDao().getUnsyncedCases()

            for (case in unsyncedCases) {
                val imageFile = File(case.localImagePath)
                if (!imageFile.exists()) continue

                val requestFile = imageFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
                val imagePart = MultipartBody.Part.createFormData("image", imageFile.name, requestFile)
                val langBody = case.language.toRequestBody("text/plain".toMediaTypeOrNull())

                val response = ApiClient.apiService.predictDisease(
                    image = imagePart,
                    language = langBody
                )

                if (response.isSuccessful && response.body() != null) {
                    val body = response.body()!!
                    db.caseDao().markCaseSynced(case.id, body.disease, body.confidence)
                }
            }

            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}