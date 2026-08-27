package com.kisanmitra.network
import android.content.Context
import android.net.Uri
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import java.io.FileOutputStream

fun uriToFile(context: Context, uri: Uri): File {
    val inputStream = context.contentResolver.openInputStream(uri)
    val tempFile = File(context.cacheDir, "upload_image.jpg")
    FileOutputStream(tempFile).use { output ->
        inputStream?.copyTo(output)
    }
    return tempFile
}

suspend fun uploadImage(context: Context, imageUri: Uri, language: String): PredictionResponse {
    val file = uriToFile(context, imageUri)
    val requestFile = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
    val imagePart = MultipartBody.Part.createFormData("image", file.name, requestFile)
    val languagePart = language.toRequestBody("text/plain".toMediaTypeOrNull())
    return RetrofitClient.api.predictDisease(imagePart, languagePart)
}
