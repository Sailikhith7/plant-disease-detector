package com.kisanmitra

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.kisanmitra.sync.SyncWorker
import com.kisanmitra.ui.screens.CaptureScreen
import com.kisanmitra.ui.screens.DiagnosisResultScreen
import com.kisanmitra.ui.screens.HomeScreen
import com.kisanmitra.ui.screens.HistoryScreen
import java.util.concurrent.TimeUnit

// Data model to store the prediction payload across screens
data class PredictionData(
    val crop: String,
    val disease: String,
    val confidence: Float,
    val status: String,
    val response: String
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Schedule periodic sync when connected to network
        scheduleOfflineSync()

        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AppNavigation()
                }
            }
        }
    }

    private fun scheduleOfflineSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(applicationContext).enqueueUniquePeriodicWork(
            "KisanMitraSync",
            ExistingPeriodicWorkPolicy.KEEP,
            syncRequest
        )
    }
}

@Composable
fun AppNavigation() {
    var currentScreen by remember { mutableStateOf("home") }
    var predictionResult by remember { mutableStateOf<PredictionData?>(null) }

    // Replace with your local machine's IPv4 address (e.g., "http://192.168.1.10:8000")
    val backendBaseUrl = "http://192.168.137.1:8000"

    when (currentScreen) {
    "home" -> {
        HomeScreen(
            // Your HomeScreen callbacks
        )
    }

    "capture" -> {
        BackHandler {
            currentScreen = "home"
        }

        CaptureScreen(
            backendUrl = backendBaseUrl,
            selectedLanguage = "en",
            onDiagnosisSuccess = { crop, disease, confidence, status, response ->
                predictionResult =
                    PredictionData(crop, disease, confidence, status, response)

                currentScreen = "result"
            },
            onBackClick = {
                currentScreen = "home"
            }
        )
    }

    "result" -> {
        BackHandler {
            currentScreen = "capture"
        }

        predictionResult?.let { result ->
            DiagnosisResultScreen(
                crop = result.crop,
                disease = result.disease,
                confidence = result.confidence,
                status = result.status,
                advisoryText = result.response,
                onBackClick = {
                    currentScreen = "capture"
                },
                onViewCaseStatusClick = {
                    currentScreen = "home"
                }
            )
        }
    }

    "history" -> {
        BackHandler {
            currentScreen = "home"
        }

        HistoryScreen(
            selectedLanguage = "en"
        )
    }
}
}