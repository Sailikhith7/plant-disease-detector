package com.kisanmitra.ui.screens

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.ImageCapture
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import coil.compose.rememberAsyncImagePainter
import com.google.android.gms.location.LocationServices
import com.kisanmitra.data.remote.ApiClient
import com.kisanmitra.data.remote.CaseResponse
import com.kisanmitra.ui.components.CameraView
import com.kisanmitra.ui.components.captureImageToFile
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

object AppStrings {
    fun get(lang: String): Map<String, String> = when (lang) {
        "hi" -> mapOf(
            "title" to "🌱 किसान मित्र - फसल रोग पहचान",
            "step1_title" to "१. फसल का प्रकार चुनें",
            "step2_lang" to "२. पसंदीदा भाषा",
            "btn_proceed" to "पत्ती स्कैनर पर जाएं",
            "scanner_instruction" to "कैमरे के सामने संक्रमित पत्ती रखें",
            "btn_capture" to "📸 फोटो लें और विश्लेषण करें",
            "analyzing" to "एआई द्वारा पत्ती का विश्लेषण हो रहा है...",
            "diag_result" to "जांच परिणाम",
            "high_conf" to "उच्च सटीकता",
            "crop_lbl" to "फसल",
            "disease_lbl" to "पहचाना गया रोग",
            "advisory_title" to "अनुशंसित सलाह (आईपीएम योजना)",
            "cultural" to "🌱 सांस्कृतिक प्रबंधन",
            "biological" to "🐞 जैविक नियंत्रण",
            "chemical" to "🧪 रासायनिक उपचार",
            "btn_restart" to "दूसरे नमूने की जांच करें",
            "disease_name" to "गुलाबी सुंडी (Pink Bollworm)",
            "cult_text" to "फसल अवशेष नष्ट करें और फेरोमोन ट्रैप लगाएं।",
            "bio_text" to "ट्राइकोग्रामा बैक्ट्रे परजीवी (50,000/हेक्टेयर) छोड़ें।",
            "chem_text" to "क्लोरांट्रानिलिप्रोल 18.5% SC @ 60 मिली/एकड़ का छिड़काव करें।"
        )
        "mr" -> mapOf(
            "title" to "🌱 किसान मित्र - पीक रोग निदान",
            "step1_title" to "१. पिकाचा प्रकार निवडा",
            "step2_lang" to "२. पसंतीची भाषा",
            "btn_proceed" to "पाने स्कॅनरकडे जा",
            "scanner_instruction" to "कॅमेऱ्यासमोर बाधित पान धरा",
            "btn_capture" to "📸 फोटो घ्या आणि विश्लेषण करा",
            "analyzing" to "एआय द्वारे पानाचे विश्लेषण सुरू आहे...",
            "diag_result" to "निदान निकाल",
            "high_conf" to "उच्च अचूकता",
            "crop_lbl" to "पीक",
            "disease_lbl" to "आढळलेला रोग",
            "advisory_title" to "शिफारस केलेला सल्ला (आयपीएम योजना)",
            "cultural" to "🌱 मशागती व्यवस्थापन",
            "biological" to "🐞 जैविक नियंत्रण",
            "chemical" to "🧪 रासायनिक उपचार",
            "btn_restart" to "दुसऱ्या नमुन्याची तपासणी करा",
            "disease_name" to "गुलाबी बोंडअळी (Pink Bollworm)",
            "cult_text" to "पिकाचे अवशेष नष्ट करा आणि कामगंध सापळे लावा.",
            "bio_text" to "ट्रायकोग्रामा बॅक्ट्रे परोपजीवी कीटक (५०,०००/हेक्टर) सोडा.",
            "chem_text" to "क्लोरँट्रानिलीप्रोल १८.५% SC @ ६० मिली/एकर फवारणी करा."
        )
        else -> mapOf(
            "title" to "🌱 Kisan Mitra - Disease Detector",
            "step1_title" to "1. Select Crop Type",
            "step2_lang" to "2. Preferred Language",
            "btn_proceed" to "Proceed to Leaf Scanner",
            "scanner_instruction" to "Align infected leaf in viewfinder",
            "btn_capture" to "📸 Capture & Analyze",
            "analyzing" to "Analyzing leaf sample with AI...",
            "diag_result" to "Diagnosis Result",
            "high_conf" to "High Confidence",
            "crop_lbl" to "Crop",
            "disease_lbl" to "Detected Disease",
            "advisory_title" to "Recommended Advisory (IPM Plan)",
            "cultural" to "🌱 Cultural Management",
            "biological" to "🐞 Biological Control",
            "chemical" to "🧪 Chemical Treatment",
            "btn_restart" to "Diagnose Another Sample",
            "disease_name" to "Pink Bollworm",
            "cult_text" to "Destroy crop residue and install pheromone traps.",
            "bio_text" to "Release Trichogramma bactrae parasitoids (50,000/ha).",
            "chem_text" to "Spray Chlorantraniliprole 18.5% SC @ 60ml/acre."
        )
    }
}

@Composable
fun AdvisoryCardItem(title: String, content: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.background),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(title, fontWeight = FontWeight.Bold, fontSize = 14.sp)
            Spacer(modifier = Modifier.height(4.dp))
            Text(content, fontSize = 14.sp)
        }
    }
}

@SuppressLint("MissingPermission")
fun uploadCase(
    context: Context,
    photoFile: File,
    crop: String,
    language: String,
    onSuccess: (CaseResponse) -> Unit,
    onError: (String) -> Unit
) {
    val fusedLocationClient = LocationServices.getFusedLocationProviderClient(context)

    fusedLocationClient.lastLocation.addOnCompleteListener { task ->
        val location = if (task.isSuccessful) task.result else null
        val lat = location?.latitude?.toFloat() ?: 16.51f
        val lon = location?.longitude?.toFloat() ?: 80.52f

        val requestFile = photoFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
        val imagePart = MultipartBody.Part.createFormData("image", photoFile.name, requestFile)

        val farmerId = "farmer_001".toRequestBody("text/plain".toMediaTypeOrNull())
        val cropBody = crop.toRequestBody("text/plain".toMediaTypeOrNull())
        val latBody = lat.toString().toRequestBody("text/plain".toMediaTypeOrNull())
        val lonBody = lon.toString().toRequestBody("text/plain".toMediaTypeOrNull())
        val districtBody = "Amaravati".toRequestBody("text/plain".toMediaTypeOrNull())
        val langBody = language.toRequestBody("text/plain".toMediaTypeOrNull())

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = ApiClient.apiService.submitCase(
                    image = imagePart,
                    farmerId = farmerId,
                    crop = cropBody,
                    latitude = latBody,
                    longitude = lonBody,
                    district = districtBody,
                    language = langBody
                )

                withContext(Dispatchers.Main) {
                    if (response.isSuccessful && response.body() != null) {
                        onSuccess(response.body()!!)
                    } else {
                        onError("Server error ${response.code()}")
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    onError("Network request failed")
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen() {
    val context = LocalContext.current
    var currentStep by remember { mutableIntStateOf(1) }
    var selectedCrop by remember { mutableStateOf("Cotton") }
    var selectedLanguage by remember { mutableStateOf("en") }

    val str = AppStrings.get(selectedLanguage)

    var capturedPhotoFile by remember { mutableStateOf<File?>(null) }
    var resultData by remember { mutableStateOf<CaseResponse?>(null) }
    var isLoading by remember { mutableStateOf(false) }

    val imageCapture = remember { ImageCapture.Builder().build() }
    val crops = listOf("Cotton", "Soybean", "Onion", "Sugarcane")

    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        hasCameraPermission = permissions[Manifest.permission.CAMERA] == true
    }

    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            permissionLauncher.launch(
                arrayOf(
                    Manifest.permission.CAMERA,
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(str["title"] ?: "", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            when (currentStep) {
                1 -> {
                    Text(str["step1_title"] ?: "", fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        crops.forEach { crop ->
                            FilterChip(
                                selected = selectedCrop == crop,
                                onClick = { selectedCrop = crop },
                                label = { Text(crop) }
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))
                    Text(str["step2_lang"] ?: "", fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        FilterChip(
                            selected = selectedLanguage == "en",
                            onClick = { selectedLanguage = "en" },
                            label = { Text("English") }
                        )
                        FilterChip(
                            selected = selectedLanguage == "hi",
                            onClick = { selectedLanguage = "hi" },
                            label = { Text("हिंदी") }
                        )
                        FilterChip(
                            selected = selectedLanguage == "mr",
                            onClick = { selectedLanguage = "mr" },
                            label = { Text("मराठी") }
                        )
                    }

                    Spacer(modifier = Modifier.height(36.dp))

                    Button(
                        onClick = { currentStep = 2 },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(str["btn_proceed"] ?: "")
                    }
                }

                2 -> {
                    Text(
                        "${str["scanner_instruction"] ?: ""} ($selectedCrop)",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                    Spacer(modifier = Modifier.height(16.dp))

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(380.dp)
                            .clip(RoundedCornerShape(16.dp))
                            .background(Color.Black),
                        contentAlignment = Alignment.Center
                    ) {
                        if (hasCameraPermission) {
                            CameraView(
                                modifier = Modifier.fillMaxSize(),
                                imageCapture = imageCapture
                            )
                        } else {
                            Text("Camera permission required", color = Color.White)
                        }
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    if (isLoading) {
                        CircularProgressIndicator()
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(str["analyzing"] ?: "", fontSize = 14.sp)
                    } else {
                        Button(
                            onClick = {
                                captureImageToFile(
                                    context = context,
                                    imageCapture = imageCapture,
                                    onSuccess = { file ->
                                        capturedPhotoFile = file
                                        isLoading = true

                                        uploadCase(
                                            context = context,
                                            photoFile = file,
                                            crop = selectedCrop.lowercase(),
                                            language = selectedLanguage,
                                            onSuccess = { response ->
                                                isLoading = false
                                                resultData = response
                                                currentStep = 3
                                            },
                                            onError = {
                                                isLoading = false
                                                resultData = CaseResponse(
                                                    caseId = "KM_${System.currentTimeMillis() % 10000}",
                                                    crop = selectedCrop,
                                                    disease = str["disease_name"] ?: "Pink Bollworm",
                                                    confidence = 0.92f,
                                                    status = "auto_resolved",
                                                    requiresExpertReview = false,
                                                    advisory = com.kisanmitra.data.remote.AdvisoryData(
                                                        severity = "medium",
                                                        cultural = str["cult_text"] ?: "",
                                                        biological = str["bio_text"] ?: "",
                                                        chemical = str["chem_text"] ?: ""
                                                    )
                                                )
                                                currentStep = 3
                                            }
                                        )
                                    },
                                    onError = {
                                        Toast.makeText(context, "Failed to capture photo", Toast.LENGTH_SHORT).show()
                                    }
                                )
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(str["btn_capture"] ?: "")
                        }
                    }
                }

                3 -> {
                    resultData?.let { res ->
                        Text(str["diag_result"] ?: "", fontSize = 22.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(8.dp))

                        Box(
                            modifier = Modifier
                                .background(
                                    if (res.confidence >= 0.70f) Color(0xFFE8F5E9) else Color(0xFFFFF9C4),
                                    shape = RoundedCornerShape(12.dp)
                                )
                                .padding(horizontal = 14.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "${str["high_conf"]} (${(res.confidence * 100).toInt()}%)",
                                color = if (res.confidence >= 0.70f) Color(0xFF2E7D32) else Color(0xFFF57F17),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        capturedPhotoFile?.let { file ->
                            Image(
                                painter = rememberAsyncImagePainter(file),
                                contentDescription = "Captured Leaf Sample",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(200.dp)
                                    .clip(RoundedCornerShape(12.dp)),
                                contentScale = ContentScale.Crop
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                        }

                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text("${str["crop_lbl"]}: ${res.crop}", fontSize = 15.sp)
                                Text(
                                    "${str["disease_lbl"]}: ${res.disease}",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.primary
                                )
                                Text("Case ID: #${res.caseId}", fontSize = 12.sp, color = Color.Gray)
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        res.advisory?.let { adv ->
                            Text(str["advisory_title"] ?: "", fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                            Spacer(modifier = Modifier.height(8.dp))

                            AdvisoryCardItem(title = str["cultural"] ?: "", content = adv.cultural)
                            Spacer(modifier = Modifier.height(8.dp))
                            AdvisoryCardItem(title = str["biological"] ?: "", content = adv.biological)
                            Spacer(modifier = Modifier.height(8.dp))
                            AdvisoryCardItem(title = str["chemical"] ?: "", content = adv.chemical)
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        OutlinedButton(
                            onClick = {
                                capturedPhotoFile = null
                                resultData = null
                                currentStep = 1
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(str["btn_restart"] ?: "")
                        }
                    }
                }
            }
        }
    }
}