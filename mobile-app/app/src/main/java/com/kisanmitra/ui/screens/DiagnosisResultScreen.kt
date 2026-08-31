package com.kisanmitra.ui.screens

import android.media.AudioAttributes
import android.media.MediaPlayer
import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiagnosisResultScreen(
    crop: String = "Cotton",
    disease: String = "Bacterial Blight",
    confidence: Float = 0.88f,
    status: String = "healthy",
    advisoryText: String =
        "Apply copper oxychloride at 2.5g per litre of water. Maintain proper drainage and remove infected leaves.",
    audioUrl: String? = null,
    caseId: String? = null,
    backendUrl: String = "http://192.168.137.1:8000",
    onBackClick: () -> Unit = {},
    onViewCaseStatusClick: () -> Unit = {}
) {

    /*
     * This is ONLY used for showing the uncertainty warning.
     *
     * The Expert Help button below is NOT restricted by this.
     */
    val isUncertain =
        status.equals("uncertain", ignoreCase = true) ||
        confidence < 0.70f

    val confidencePercentage =
        (confidence * 100).toInt()

    val context = LocalContext.current

    val scope = rememberCoroutineScope()

    var isPlaying by remember {
        mutableStateOf(false)
    }

    var isSendingToExpert by remember {
        mutableStateOf(false)
    }

    /*
     * Send the current case to the expert.
     *
     * This can now be called regardless of model confidence.
     */
    fun sendToExpert() {

        if (caseId.isNullOrBlank()) {

            Toast.makeText(
                context,
                "Case ID not available. Please scan again.",
                Toast.LENGTH_LONG
            ).show()

            return
        }

        if (isSendingToExpert) {
            return
        }

        isSendingToExpert = true

        scope.launch {

            try {

                val result = withContext(Dispatchers.IO) {

                    val client =
                        OkHttpClient.Builder()
                            .connectTimeout(
                                30,
                                TimeUnit.SECONDS
                            )
                            .readTimeout(
                                30,
                                TimeUnit.SECONDS
                            )
                            .build()

                    val json =
                        JSONObject().apply {

                            put(
                                "reason",
                                "Farmer is not satisfied with the model diagnosis."
                            )

                            put(
                                "description",
                                "Farmer requested expert review."
                            )
                        }

                    val requestBody =
                        json.toString()
                            .toRequestBody(
                                "application/json".toMediaType()
                            )

                    val cleanBaseUrl =
                        backendUrl.trimEnd('/')

                    val request =
                        Request.Builder()
                            .url(
                                "$cleanBaseUrl/api/cases/$caseId/expert-request"
                            )
                            .post(requestBody)
                            .build()

                    client.newCall(request).execute().use { response ->

                        Pair(
                            response.isSuccessful,
                            response.code
                        )
                    }
                }

                isSendingToExpert = false

                val success = result.first
                val responseCode = result.second

                if (success) {

                    Toast.makeText(
                        context,
                        "Your problem has been sent to an expert.",
                        Toast.LENGTH_LONG
                    ).show()

                } else {

                    Toast.makeText(
                        context,
                        "Could not send request to expert. HTTP $responseCode",
                        Toast.LENGTH_LONG
                    ).show()
                }

            } catch (e: Exception) {

                isSendingToExpert = false

                Toast.makeText(
                    context,
                    "Expert request failed: ${e.localizedMessage}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    Scaffold(

        topBar = {

            TopAppBar(

                title = {

                    Text(
                        "Diagnosis Result",
                        fontWeight = FontWeight.Bold
                    )
                },

                navigationIcon = {

                    IconButton(
                        onClick = onBackClick
                    ) {

                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },

                colors =
                    TopAppBarDefaults.topAppBarColors(

                        containerColor =
                            Color(0xFF1B5E20),

                        titleContentColor =
                            Color.White,

                        navigationIconContentColor =
                            Color.White
                    )
            )
        }

    ) { paddingValues ->

        Column(

            modifier =
                Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(16.dp)
                    .verticalScroll(
                        rememberScrollState()
                    ),

            verticalArrangement =
                Arrangement.spacedBy(16.dp)

        ) {

            /*
             * LOW CONFIDENCE / UNCERTAIN RESULT
             */
            if (isUncertain) {

                Card(

                    modifier =
                        Modifier.fillMaxWidth(),

                    shape =
                        RoundedCornerShape(12.dp),

                    colors =
                        CardDefaults.cardColors(
                            containerColor =
                                Color(0xFFFFF8E1)
                        ),

                    elevation =
                        CardDefaults.cardElevation(
                            defaultElevation = 2.dp
                        )

                ) {

                    Column(
                        modifier =
                            Modifier.padding(16.dp)
                    ) {

                        Row(
                            verticalAlignment =
                                Alignment.CenterVertically
                        ) {

                            Icon(
                                imageVector =
                                    Icons.Default.Warning,

                                contentDescription =
                                    "Warning",

                                tint =
                                    Color(0xFFF57F17),

                                modifier =
                                    Modifier.size(28.dp)
                            )

                            Spacer(
                                modifier =
                                    Modifier.width(8.dp)
                            )

                            Text(
                                text =
                                    "Uncertain Diagnosis",

                                style =
                                    MaterialTheme.typography.titleLarge,

                                fontWeight =
                                    FontWeight.Bold,

                                color =
                                    Color(0xFFE65100)
                            )
                        }

                        Spacer(
                            modifier =
                                Modifier.height(10.dp)
                        )

                        Text(
                            text =
                                "Confidence: $confidencePercentage%",

                            fontWeight =
                                FontWeight.SemiBold,

                            color =
                                Color(0xFFBF360C)
                        )

                        Spacer(
                            modifier =
                                Modifier.height(6.dp)
                        )

                        Text(
                            text =
                                "The system could not identify the disease with high confidence ($confidencePercentage%). Chemical recommendations are withheld for crop safety.",

                            style =
                                MaterialTheme.typography.bodyMedium,

                            color =
                                Color(0xFF5D4037)
                        )

                        Spacer(
                            modifier =
                                Modifier.height(8.dp)
                        )

                        Text(
                            text =
                                "Status: Escalated to Expert Triage Queue for manual review by an agricultural officer.",

                            style =
                                MaterialTheme.typography.bodySmall,

                            fontWeight =
                                FontWeight.Medium,

                            color =
                                Color(0xFFE65100)
                        )
                    }
                }

                OutlinedButton(

                    onClick =
                        onViewCaseStatusClick,

                    modifier =
                        Modifier.fillMaxWidth(),

                    shape =
                        RoundedCornerShape(8.dp)

                ) {

                    Text(
                        "Check Case Status in Triage"
                    )
                }

                Button(

                    onClick = {
                        sendToExpert()
                    },

                    modifier =
                        Modifier.fillMaxWidth(),

                    shape =
                        RoundedCornerShape(8.dp)

                ) {

                    Text("Check Case Status in Triage")
                }

            } else {

                /*
                 * NORMAL / HIGH CONFIDENCE RESULT
                 */
                Card(

                    modifier =
                        Modifier.fillMaxWidth(),

                    shape =
                        RoundedCornerShape(12.dp),

                    colors =
                        CardDefaults.cardColors(
                            containerColor =
                                Color(0xFFE8F5E9)
                        ),

                    elevation =
                        CardDefaults.cardElevation(
                            defaultElevation = 2.dp
                        )

                ) {

                    Column(
                        modifier =
                            Modifier.padding(16.dp)
                    ) {

                        Row(

                            modifier =
                                Modifier.fillMaxWidth(),

                            horizontalArrangement =
                                Arrangement.SpaceBetween,

                            verticalAlignment =
                                Alignment.CenterVertically

                        ) {

                            Text(
                                text =
                                    "Crop: $crop",

                                style =
                                    MaterialTheme.typography.labelLarge,

                                color =
                                    Color(0xFF2E7D32)
                            )

                            Row(
                                verticalAlignment =
                                    Alignment.CenterVertically
                            ) {

                                Icon(
                                    imageVector =
                                        Icons.Default.CheckCircle,

                                    contentDescription =
                                        "Verified",

                                    tint =
                                        Color(0xFF2E7D32),

                                    modifier =
                                        Modifier.size(18.dp)
                                )

                                Spacer(
                                    modifier =
                                        Modifier.width(4.dp)
                                )

                                Text(
                                    text =
                                        "$confidencePercentage% match",

                                    fontWeight =
                                        FontWeight.Bold,

                                    color =
                                        Color(0xFF2E7D32),

                                    fontSize =
                                        13.sp
                                )
                            }
                        }

                        Spacer(
                            modifier =
                                Modifier.height(6.dp)
                        )

                        Text(
                            text =
                                disease,

                            style =
                                MaterialTheme.typography.headlineMedium,

                            fontWeight =
                                FontWeight.Bold,

                            color =
                                Color(0xFF1B5E20)
                        )
                    }
                }

                /*
                 * ADVISORY
                 */
                Card(

                    modifier =
                        Modifier.fillMaxWidth(),

                    shape =
                        RoundedCornerShape(12.dp),

                    colors =
                        CardDefaults.cardColors(
                            containerColor =
                                Color.White
                        ),

                    elevation =
                        CardDefaults.cardElevation(
                            defaultElevation = 2.dp
                        )

                ) {

                    Column(
                        modifier =
                            Modifier.padding(16.dp)
                    ) {

                        Text(
                            text =
                                "Recommended Management & Remedies",

                            style =
                                MaterialTheme.typography.titleMedium,

                            fontWeight =
                                FontWeight.Bold,

                            color =
                                Color(0xFF212121)
                        )

                        Spacer(
                            modifier =
                                Modifier.height(10.dp)
                        )

                        Text(
                            text =
                                advisoryText,

                            style =
                                MaterialTheme.typography.bodyMedium,

                            lineHeight =
                                22.sp,

                            color =
                                Color(0xFF424242)
                        )

                        /*
                         * AUDIO ADVISORY
                         */
                        if (!audioUrl.isNullOrEmpty()) {

                            Spacer(
                                modifier =
                                    Modifier.height(14.dp)
                            )

                            Button(

                                onClick = {

                                    val fullUrl =
                                        if (
                                            audioUrl.startsWith("http")
                                        ) {

                                            audioUrl

                                        } else {

                                            backendUrl.trimEnd('/') +
                                                (
                                                    if (
                                                        audioUrl.startsWith("/")
                                                    ) {
                                                        audioUrl
                                                    } else {
                                                        "/$audioUrl"
                                                    }
                                                )
                                        }

                                    try {

                                        isPlaying = true

                                        MediaPlayer().apply {

                                            setAudioAttributes(

                                                AudioAttributes
                                                    .Builder()

                                                    .setContentType(
                                                        AudioAttributes
                                                            .CONTENT_TYPE_SPEECH
                                                    )

                                                    .setUsage(
                                                        AudioAttributes
                                                            .USAGE_MEDIA
                                                    )

                                                    .build()
                                            )

                                            setDataSource(fullUrl)

                                            prepareAsync()

                                            setOnPreparedListener {

                                                start()

                                                Toast.makeText(
                                                    context,
                                                    "Playing Audio Advisory...",
                                                    Toast.LENGTH_SHORT
                                                ).show()
                                            }

                                            setOnCompletionListener {

                                                isPlaying = false

                                                release()
                                            }

                                            setOnErrorListener { _, _, _ ->

                                                isPlaying = false

                                                release()

                                                Toast.makeText(
                                                    context,
                                                    "Audio playback failed",
                                                    Toast.LENGTH_SHORT
                                                ).show()

                                                true
                                            }
                                        }

                                    } catch (e: Exception) {

                                        isPlaying = false

                                        Toast.makeText(
                                            context,
                                            "Error: ${e.message}",
                                            Toast.LENGTH_SHORT
                                        ).show()
                                    }
                                },

                                modifier =
                                    Modifier.fillMaxWidth(),

                                shape =
                                    RoundedCornerShape(8.dp),

                                colors =
                                    ButtonDefaults.buttonColors(
                                        containerColor =
                                            Color(0xFF2E7D32)
                                    )

                            ) {

                                Icon(
                                    imageVector =
                                        Icons.Default.PlayArrow,

                                    contentDescription =
                                        "Play Audio",

                                    tint =
                                        Color.White
                                )

                                Spacer(
                                    modifier =
                                        Modifier.width(8.dp)
                                )

                                Text(

                                    text =
                                        if (isPlaying)
                                            "Playing Advisory..."
                                        else
                                            "Listen Audio Advisory (ऐका)",

                                    color =
                                        Color.White,

                                    fontWeight =
                                        FontWeight.SemiBold
                                )
                            }
                        }
                    }
                }
            }

/*
 * ==========================================================
 * EXPERT HELP
 * ==========================================================
 */

Spacer(
    modifier = Modifier.height(16.dp)
)

Text(
    text = "EXPERT HELP",
    fontSize = 20.sp,
    fontWeight = FontWeight.Bold,
    color = Color.Red
)

Spacer(
    modifier = Modifier.height(8.dp)
)

Button(
    onClick = {
        sendToExpert()
    },
    enabled = !isSendingToExpert,
    modifier = Modifier
        .fillMaxWidth()
        .height(55.dp),
    shape = RoundedCornerShape(8.dp),
    colors = ButtonDefaults.buttonColors(
        containerColor = Color(0xFF6A4C93)
    )
) {

    if (isSendingToExpert) {

        CircularProgressIndicator(
            modifier = Modifier.size(20.dp),
            color = Color.White,
            strokeWidth = 2.dp
        )

        Spacer(
            modifier = Modifier.width(8.dp)
        )

        Text(
            text = "Sending to Expert...",
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

    } else {

        Text(
            text = "I'm Not Satisfied - Ask an Expert",
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
    }
}

Spacer(
    modifier = Modifier.height(16.dp)
)
        }
    }
}