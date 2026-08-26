package com.kisanmitra.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.kisanmitra.data.local.AppDatabase
import com.kisanmitra.data.remote.ApiClient
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

class SyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val database = AppDatabase.getDatabase(applicationContext)
        val dao = database.caseDao()
        val unsyncedCases = dao.getUnsyncedCases()

        if (unsyncedCases.isEmpty()) {
            return Result.success()
        }

        var allSuccessful = true

        for (caseItem in unsyncedCases) {
            val file = File(caseItem.localImagePath)
            if (!file.exists()) {
                continue
            }

            try {
                val requestFile = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
                val imagePart = MultipartBody.Part.createFormData("image", file.name, requestFile)
                val farmerId = "farmer_001".toRequestBody("text/plain".toMediaTypeOrNull())
                val cropBody = caseItem.crop.toRequestBody("text/plain".toMediaTypeOrNull())
                val latBody = caseItem.latitude.toString().toRequestBody("text/plain".toMediaTypeOrNull())
                val lonBody = caseItem.longitude.toString().toRequestBody("text/plain".toMediaTypeOrNull())
                val districtBody = "Amaravati".toRequestBody("text/plain".toMediaTypeOrNull())
                val langBody = caseItem.language.toRequestBody("text/plain".toMediaTypeOrNull())

                val response = ApiClient.apiService.submitCase(
                    image = imagePart,
                    farmerId = farmerId,
                    crop = cropBody,
                    latitude = latBody,
                    longitude = lonBody,
                    district = districtBody,
                    language = langBody
                )

                if (response.isSuccessful && response.body() != null) {
                    val result = response.body()!!
                    dao.markCaseSynced(caseItem.id, result.disease, result.confidence)
                } else {
                    allSuccessful = false
                }
            } catch (e: Exception) {
                allSuccessful = false
            }
        }

        return if (allSuccessful) Result.success() else Result.retry()
    }
}