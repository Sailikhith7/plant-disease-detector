package com.kisanmitra.ui.screens

import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.TimeUnit

val MAHARASHTRA_DISTRICTS = listOf(
    "Ahilyanagar (Ahmednagar)",
    "Akola",
    "Amravati",
    "Beed",
    "Bhandara",
    "Buldhana",
    "Chandrapur",
    "Chhatrapati Sambhajinagar (Aurangabad)",
    "Dharashiv (Osmanabad)",
    "Dhule",
    "Gadchiroli",
    "Gondia",
    "Hingoli",
    "Jalgaon",
    "Jalna",
    "Kolhapur",
    "Latur",
    "Mumbai City",
    "Mumbai Suburban",
    "Nagpur",
    "Nanded",
    "Nandurbar",
    "Nashik",
    "Palghar",
    "Parbhani",
    "Pune",
    "Raigad",
    "Ratnagiri",
    "Sangli",
    "Satara",
    "Sindhudurg",
    "Solapur",
    "Thane",
    "Wardha",
    "Washim",
    "Yavatmal"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    backendUrl: String = "http://192.168.137.1:8000",
    selectedLanguage: String = "mr",

    onDiagnosisSuccess: (
        caseId: String?,
        crop: String,
        disease: String,
        confidence: Float,
        status: String,
        response: String,
        audioUrl: String?
    ) -> Unit,

    onBackClick: () -> Unit
) {

    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    var isUploading by remember {
        mutableStateOf(false)
    }

    var tempImageFile by remember {
        mutableStateOf<File?>(null)
    }

    var farmerName by remember {
        mutableStateOf("")
    }

    var crop by remember {
        mutableStateOf("Cotton")
    }

    var selectedDistrict by remember {
        mutableStateOf("Yavatmal")
    }

    var districtExpanded by remember {
        mutableStateOf(false)
    }

    fun createTempImageFile(): File {

        val timestamp =
            SimpleDateFormat(
                "yyyyMMdd_HHmmss",
                Locale.getDefault()
            ).format(Date())

        return File.createTempFile(
            "LEAF_${timestamp}_",
            ".jpg",
            context.cacheDir
        ).also {
            tempImageFile = it
        }
    }

    fun uploadAndPredict(imageFile: File) {

        val farmer =
            if (farmerName.isNotBlank())
                farmerName.trim()
            else
                "App Farmer"

        val cropValue =
            if (crop.isNotBlank())
                crop.trim()
            else
                "Cotton"

        val districtValue =
            selectedDistrict

        isUploading = true

        scope.launch(Dispatchers.IO) {

            try {

                val client =
                    OkHttpClient.Builder()
                        .connectTimeout(
                            30,
                            TimeUnit.SECONDS
                        )
                        .readTimeout(
                            120,
                            TimeUnit.SECONDS
                        )
                        .writeTimeout(
                            120,
                            TimeUnit.SECONDS
                        )
                        .build()

                val requestBody =
                    MultipartBody.Builder()
                        .setType(MultipartBody.FORM)

                        .addFormDataPart(
                            "image",
                            imageFile.name,
                            imageFile.asRequestBody(
                                "image/jpeg"
                                    .toMediaTypeOrNull()
                            )
                        )

                        .addFormDataPart(
                            "language",
                            selectedLanguage
                        )

                        .addFormDataPart(
                            "farmer_name",
                            farmer
                        )

                        .addFormDataPart(
                            "crop",
                            cropValue
                        )

                        .addFormDataPart(
                            "district",
                            districtValue
                        )

                        .addFormDataPart(
                            "farmer_id",
                            "MH_OFFLINE_001"
                        )

                        .build()

                val request =
                    Request.Builder()
                        .url(
                            "${backendUrl.trimEnd('/')}/api/predict"
                        )
                        .post(requestBody)
                        .build()

                val response =
                    client
                        .newCall(request)
                        .execute()

                val responseText =
                    response.body?.string()

                withContext(Dispatchers.Main) {

                    isUploading = false

                    if (
                        response.isSuccessful &&
                        responseText != null
                    ) {

                        val json =
                            JSONObject(responseText)

                        val caseId =
                            json
                                .optString("case_id")
                                .takeIf {
                                    it.isNotBlank()
                                }

                        val returnedCrop =
                            json.optString(
                                "crop",
                                cropValue
                            )

                        val disease =
                            json.optString(
                                "disease",
                                "Unknown"
                            )

                        val confidence =
                            json.optDouble(
                                "confidence",
                                0.0
                            ).toFloat()

                        val status =
                            json.optString(
                                "status",
                                "Pending Expert"
                            )

                        val advisory =
                            json.optString(
                                "response",
                                "No advisory generated."
                            )

                        val audioUrl =
                            json
                                .optString("audio_url")
                                .takeIf {
                                    it.isNotBlank()
                                }

                        onDiagnosisSuccess(
                            caseId,
                            returnedCrop,
                            disease,
                            confidence,
                            status,
                            advisory,
                            audioUrl
                        )

                    } else {

                        Toast.makeText(
                            context,
                            "Analysis failed: HTTP ${response.code}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }

            } catch (e: Exception) {

                withContext(Dispatchers.Main) {

                    isUploading = false

                    Toast.makeText(
                        context,
                        "Server connection error: ${e.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }

    val cameraLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.TakePicture()
        ) { success ->

            if (
                success &&
                tempImageFile != null
            ) {

                uploadAndPredict(
                    tempImageFile!!
                )
            }
        }

    val galleryLauncher =
        rememberLauncherForActivityResult(
            ActivityResultContracts.GetContent()
        ) { uri: Uri? ->

            if (uri != null) {

                try {

                    val file =
                        createTempImageFile()

                    context.contentResolver
                        .openInputStream(uri)
                        ?.use { input ->

                            FileOutputStream(file)
                                .use { output ->

                                    input.copyTo(output)
                                }
                        }

                    uploadAndPredict(file)

                } catch (e: Exception) {

                    Toast.makeText(
                        context,
                        "Could not read selected image.",
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
                        "Enter Details & Scan",
                        fontWeight =
                            FontWeight.Bold
                    )
                },

                navigationIcon = {

                    IconButton(
                        onClick =
                            onBackClick
                    ) {

                        Icon(
                            imageVector =
                                Icons.Default.ArrowBack,
                            contentDescription =
                                "Back"
                        )
                    }
                },

                colors =
                    TopAppBarDefaults
                        .topAppBarColors(
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

        Box(

            modifier =
                Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(20.dp)
        ) {

            if (isUploading) {

                Column(

                    modifier =
                        Modifier.fillMaxSize(),

                    horizontalAlignment =
                        Alignment.CenterHorizontally,

                    verticalArrangement =
                        Arrangement.Center
                ) {

                    CircularProgressIndicator(
                        color =
                            Color(0xFF2E7D32)
                    )

                    Spacer(
                        modifier =
                            Modifier.height(16.dp)
                    )

                    Text(
                        "Analyzing & registering case...",
                        fontWeight =
                            FontWeight.Medium
                    )
                }

            } else {

                Column(

                    modifier =
                        Modifier
                            .fillMaxSize()
                            .verticalScroll(
                                scrollState
                            ),

                    horizontalAlignment =
                        Alignment.CenterHorizontally
                ) {

                    Card(

                        modifier =
                            Modifier.fillMaxWidth(),

                        colors =
                            CardDefaults
                                .cardColors(
                                    containerColor =
                                        Color(0xFFF1F8E9)
                                ),

                        shape =
                            RoundedCornerShape(12.dp)
                    ) {

                        Column(
                            modifier =
                                Modifier.padding(16.dp)
                        ) {

                            Text(
                                text =
                                    "Farmer & Field Details",

                                fontWeight =
                                    FontWeight.Bold,

                                color =
                                    Color(0xFF1B5E20),

                                fontSize =
                                    16.sp
                            )

                            Spacer(
                                modifier =
                                    Modifier.height(12.dp)
                            )

                            OutlinedTextField(

                                value =
                                    farmerName,

                                onValueChange = {
                                    farmerName = it
                                },

                                label = {
                                    Text(
                                        "Farmer Full Name"
                                    )
                                },

                                modifier =
                                    Modifier.fillMaxWidth(),

                                singleLine =
                                    true
                            )

                            Spacer(
                                modifier =
                                    Modifier.height(10.dp)
                            )

                            OutlinedTextField(

                                value =
                                    crop,

                                onValueChange = {
                                    crop = it
                                },

                                label = {
                                    Text(
                                        "Crop Type"
                                    )
                                },

                                modifier =
                                    Modifier.fillMaxWidth(),

                                singleLine =
                                    true
                            )

                            Spacer(
                                modifier =
                                    Modifier.height(10.dp)
                            )

                            Box(
                                modifier =
                                    Modifier.fillMaxWidth()
                            ) {

                                OutlinedButton(

                                    onClick = {
                                        districtExpanded =
                                            !districtExpanded
                                    },

                                    modifier =
                                        Modifier.fillMaxWidth(),

                                    shape =
                                        RoundedCornerShape(8.dp)
                                ) {

                                    Text(
                                        "District: $selectedDistrict"
                                    )
                                }

                                DropdownMenu(

                                    expanded =
                                        districtExpanded,

                                    onDismissRequest = {
                                        districtExpanded =
                                            false
                                    },

                                    modifier =
                                        Modifier.fillMaxWidth()
                                ) {

                                    MAHARASHTRA_DISTRICTS
                                        .forEach { district ->

                                            DropdownMenuItem(

                                                text = {
                                                    Text(
                                                        district
                                                    )
                                                },

                                                onClick = {

                                                    selectedDistrict =
                                                        district

                                                    districtExpanded =
                                                        false
                                                }
                                            )
                                        }
                                }
                            }
                        }
                    }

                    Spacer(
                        modifier =
                            Modifier.height(20.dp)
                    )

                    Button(

                        onClick = {

                            val file =
                                createTempImageFile()

                            val uri =
                                FileProvider
                                    .getUriForFile(
                                        context,
                                        "${context.packageName}.fileprovider",
                                        file
                                    )

                            cameraLauncher
                                .launch(uri)
                        },

                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(54.dp),

                        colors =
                            ButtonDefaults
                                .buttonColors(
                                    containerColor =
                                        Color(0xFF1B5E20)
                                )
                    ) {

                        Icon(
                            imageVector =
                                Icons.Default.Add,
                            contentDescription =
                                null
                        )

                        Spacer(
                            modifier =
                                Modifier.width(8.dp)
                        )

                        Text(
                            "Capture Photo with Camera"
                        )
                    }

                    Spacer(
                        modifier =
                            Modifier.height(10.dp)
                    )

                    OutlinedButton(

                        onClick = {
                            galleryLauncher
                                .launch("image/*")
                        },

                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(54.dp)
                    ) {

                        Icon(
                            imageVector =
                                Icons.Default.Check,
                            contentDescription =
                                null
                        )

                        Spacer(
                            modifier =
                                Modifier.width(8.dp)
                        )

                        Text(
                            "Choose from Gallery"
                        )
                    }
                }
            }
        }
    }
}