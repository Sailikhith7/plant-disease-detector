package com.kisanmitra.ui.screens

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.location.Geocoder
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.ImageCapture
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import coil.compose.rememberAsyncImagePainter
import com.google.android.gms.location.LocationServices
import com.kisanmitra.data.local.AppDatabase
import com.kisanmitra.data.local.CaseEntity
import com.kisanmitra.data.remote.ApiClient
import com.kisanmitra.data.remote.CaseResponse
import com.kisanmitra.ui.components.CameraView
import com.kisanmitra.ui.components.captureImageToFile
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit

object AppStrings {
    fun get(lang: String): Map<String, String> = when (lang) {
        "hi" -> mapOf(
            "title" to "🌱 किसान मित्र",
            "step1_lang" to "१. पसंदीदा भाषा",
            "step2_farmer" to "२. किसान का नाम",
            "step3_location" to "३. खेत का स्थान (GPS द्वारा स्वतः खोजा गया)",
            "btn_proceed" to "पत्ती स्कैनर पर जाएं",
            "scanner_instruction" to "कैमरे के सामने संक्रमित पत्ती रखें",
            "btn_capture" to "📸 फोटो लें और विश्लेषण करें",
            "analyzing" to "एआई द्वारा रोग पहचान हो रही है...",
            "diag_result" to "जांच परिणाम",
            "high_conf" to "उच्च सटीकता (High Confidence)",
            "low_conf" to "समीक्षा आवश्यक (Under Expert Review)",
            "crop_lbl" to "पहचानी गई फसल",
            "farmer_lbl" to "किसान",
            "district_lbl" to "स्थान",
            "disease_lbl" to "पहचाना गया रोग",
            "advisory_title" to "एआई उपचार सलाह (RAG Guidance)",
            "play_audio" to "🔊 ऑडियो सलाह सुनें (Play Audio)",
            "playing_audio" to "ऑडियो चल रहा है...",
            "btn_restart" to "दूसरे नमूने की जांच करें",
            "tab_scan" to "स्कैन",
            "tab_weather" to "मौसम",
            "tab_history" to "इतिहास",
            "tab_expert" to "विशेषज्ञ सलाह",
            "tab_guide" to "गाइडलाइन",
            "hist_title" to "पिछले निदान रिकॉर्ड",
            "hist_empty" to "अभी तक कोई इतिहास रिकॉर्ड नहीं मिला।",
            "hist_synced" to "क्लाउड पर सिंक किया गया",
            "hist_pending" to "लोकल सेव (सिंक लंबित)",
            "help_title" to "किसान सहायता (Help & Support)",
            "help_desc" to "यदि आपको फसल निदान या सहायता चाहिए, तो नीचे दिए गए माध्यमों से संपर्क करें:",
            "help_helpline_lbl" to "📞 हेल्पलाइन / फोन: ",
            "help_email_lbl" to "✉️ ईमेल: ",
            "help_website_lbl" to "🌐 वेबसाइट: ",
            "close_btn" to "बंद करें",
            "loc_detecting" to "📡 GPS लोकेशन खोज रहा है..."
        )
        "mr" -> mapOf(
            "title" to "🌱 किसान मित्र",
            "step1_lang" to "१. पसंतीची भाषा",
            "step2_farmer" to "२. शेतकऱ्याचे नाव",
            "step3_location" to "३. शेताचे ठिकाण (GPS द्वारे शोधलेले)",
            "btn_proceed" to "पाने स्कॅनरकडे जा",
            "scanner_instruction" to "कॅमेऱ्यासमोर बाधित पान धरा",
            "btn_capture" to "📸 फोटो घ्या आणि विश्लेषण करा",
            "analyzing" to "एआई द्वारे रोग तपासणी सुरू आहे...",
            "diag_result" to "निदान निकाल",
            "high_conf" to "उच्च अचूकता (High Confidence)",
            "low_conf" to "तज्ज्ञ पुनरावलोकन (Under Expert Review)",
            "crop_lbl" to "ओळखलेले पीक",
            "farmer_lbl" to "शेतकरी",
            "district_lbl" to "ठिकाण",
            "disease_lbl" to "आढळलेला रोग",
            "advisory_title" to "एआय उपचार सल्ला (RAG Guidance)",
            "play_audio" to "🔊 मराठी सल्ला ऐका (Play Audio)",
            "playing_audio" to "सल्ला वाजत आहे...",
            "btn_restart" to "दुसऱ्या नमुन्याची तपासणी करा",
            "tab_scan" to "स्कॅन",
            "tab_weather" to "हवामान",
            "tab_history" to "इतिहास",
            "tab_expert" to "तज्ज्ञ सल्ला",
            "tab_guide" to "मार्गदर्शक",
            "hist_title" to "मागील निदान नोंदी",
            "hist_empty" to "अद्याप कोणताही इतिहास आढळला नाही.",
            "hist_synced" to "क्लाउडवर सिंक केले",
            "hist_pending" to "स्थानिक सेव्ह (प्रलंबित)",
            "help_title" to "शेतकरी मदत (Help & Support)",
            "help_desc" to "आपल्याला शेतीविषयी किंवा पिकांच्या रोगांबाबतीत मदत हवी असल्यास खालील संपर्कांवर संपर्क साधा:",
            "help_helpline_lbl" to "📞 हेल्पलाईन / फोन: ",
            "help_email_lbl" to "✉️ ई-मेल: ",
            "help_website_lbl" to "🌐 संकेतस्थळ: ",
            "close_btn" to "बंद करा",
            "loc_detecting" to "📡 GPS लोकेशन शोधत आहे..."
        )
        else -> mapOf(
            "title" to "🌱 Kisan Mitra",
            "step1_lang" to "1. Preferred Language",
            "step2_farmer" to "2. Farmer Full Name",
            "step3_location" to "3. Farm Location (Auto GPS Detected)",
            "btn_proceed" to "Proceed to Leaf Scanner",
            "scanner_instruction" to "Align infected leaf in viewfinder",
            "btn_capture" to "📸 Capture & Analyze",
            "analyzing" to "Analyzing leaf with ML & RAG...",
            "diag_result" to "Diagnosis Result",
            "high_conf" to "High Confidence",
            "low_conf" to "Under Expert Review",
            "crop_lbl" to "Detected Crop",
            "farmer_lbl" to "Farmer",
            "district_lbl" to "Location",
            "disease_lbl" to "Detected Disease",
            "advisory_title" to "AI Treatment Advisory (RAG Guidance)",
            "play_audio" to "🔊 Listen Audio Advisory (Play)",
            "playing_audio" to "Playing Audio Advisory...",
            "btn_restart" to "Diagnose Another Sample",
            "tab_scan" to "Scan",
            "tab_weather" to "Weather",
            "tab_history" to "History",
            "tab_expert" to "Expert Desk",
            "tab_guide" to "Guide",
            "hist_title" to "Diagnosis History",
            "hist_empty" to "No scan records found yet.",
            "hist_synced" to "Synced to Cloud",
            "hist_pending" to "Local Saved (Pending Sync)",
            "help_title" to "Farmer Help & Support",
            "help_desc" to "If you need immediate assistance or expert agronomy support, please reach out via:",
            "help_helpline_lbl" to "📞 Helpline / Tel: ",
            "help_email_lbl" to "✉️ Email: ",
            "help_website_lbl" to "🌐 Website: ",
            "close_btn" to "Close",
            "loc_detecting" to "📡 Detecting GPS Location..."
        )
    }
}

suspend fun reverseGeocodeCoordinates(context: Context, lat: Double, lon: Double): String = withContext(Dispatchers.IO) {
    try {
        val client = OkHttpClient.Builder().connectTimeout(3, TimeUnit.SECONDS).build()
        val request = Request.Builder()
            .url("https://nominatim.openstreetmap.org/reverse?lat=$lat&lon=$lon&format=json")
            .header("User-Agent", "KisanMitraMobile/1.0")
            .build()
        val response = client.newCall(request).execute()
        if (response.isSuccessful) {
            val json = JSONObject(response.body?.string() ?: "")
            val address = json.optJSONObject("address")
            if (address != null) {
                val district = address.optString("state_district", "")
                    .ifBlank { address.optString("county", "") }
                    .ifBlank { address.optString("city", "") }
                    .ifBlank { address.optString("town", "") }
                val state = address.optString("state", "")
                if (district.isNotBlank() && state.isNotBlank()) {
                    return@withContext "$district, $state"
                } else if (district.isNotBlank()) {
                    return@withContext district
                }
            }
        }
    } catch (_: Exception) {}

    try {
        val geocoder = Geocoder(context, Locale.getDefault())
        val addresses = geocoder.getFromLocation(lat, lon, 1)
        if (!addresses.isNullOrEmpty()) {
            val addr = addresses[0]
            val district = addr.subAdminArea ?: addr.locality ?: addr.adminArea
            if (!district.isNullOrBlank()) {
                val state = addr.adminArea ?: ""
                return@withContext if (state.isNotBlank() && !district.contains(state)) "$district, $state" else district
            }
        }
    } catch (_: Exception) {}

    return@withContext "Guntur, Andhra Pradesh"
}

suspend fun processAndSaveCase(
    context: Context,
    photoFile: File,
    language: String,
    farmerName: String,
    district: String,
    latitude: Float,
    longitude: Float
): CaseResponse = withContext(Dispatchers.IO) {
    val appContext = context.applicationContext
    try {
        val requestFile = photoFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
        val imagePart = MultipartBody.Part.createFormData("image", photoFile.name, requestFile)
        val langBody = language.toRequestBody("text/plain".toMediaTypeOrNull())
        val cropBody = "".toRequestBody("text/plain".toMediaTypeOrNull())
        val farmerNameBody = farmerName.ifBlank { "Farmer" }.toRequestBody("text/plain".toMediaTypeOrNull())
        val districtBody = district.toRequestBody("text/plain".toMediaTypeOrNull())
        val farmerIdBody = "KM_${Math.abs(district.hashCode()).toString().take(5)}".toRequestBody("text/plain".toMediaTypeOrNull())

        val response = ApiClient.apiService.predictDisease(
            image = imagePart,
            language = langBody,
            crop = cropBody,
            farmerName = farmerNameBody,
            district = districtBody,
            farmerId = farmerIdBody
        )

        if (response.isSuccessful && response.body() != null) {
            val body = response.body()!!
            try {
                val db = AppDatabase.getDatabase(appContext)
                db.caseDao().insertCase(
                    CaseEntity(
                        localImagePath = photoFile.absolutePath,
                        crop = body.crop,
                        language = language,
                        latitude = latitude,
                        longitude = longitude,
                        detectedDisease = body.disease,
                        confidence = body.confidence,
                        isSynced = true,
                        createdAt = System.currentTimeMillis()
                    )
                )
            } catch (_: Throwable) {}
            return@withContext body
        }
    } catch (_: Throwable) {}

    CaseResponse(
        crop = "Unknown",
        disease = "Analysis Failed / Connection Error",
        confidence = 0f,
        status = "Error",
        response = "Could not connect to backend server. Please verify network.",
        language = language,
        audioUrl = null
    )
}

@Composable
fun HistoryTabContent(selectedLanguage: String) {
    val context = LocalContext.current
    val str = AppStrings.get(selectedLanguage)

    var casesList by remember { mutableStateOf<List<CaseEntity>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        try {
            val db = withContext(Dispatchers.IO) { AppDatabase.getDatabase(context.applicationContext) }
            db.caseDao().getAllCasesFlow().collect { cases ->
                casesList = cases
                isLoading = false
            }
        } catch (_: Exception) {
            casesList = emptyList()
            isLoading = false
        }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text(text = str["hist_title"] ?: "Diagnosis History", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
        Spacer(modifier = Modifier.height(12.dp))

        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
        } else if (casesList.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("🌿", fontSize = 42.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = str["hist_empty"] ?: "No scan records found yet.", color = Color.Gray, fontSize = 15.sp)
                }
            }
        } else {
            LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 80.dp)) {
                items(casesList) { item -> HistoryCardView(item = item, str = str) }
            }
        }
    }
}

@Composable
fun HistoryCardView(item: CaseEntity, str: Map<String, String>) {
    val dateString = remember(item.createdAt) {
        try { SimpleDateFormat("dd MMM yyyy, hh:mm a", Locale.getDefault()).format(Date(item.createdAt)) } catch (_: Throwable) { "" }
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(modifier = Modifier.fillMaxWidth().padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            val file = remember(item.localImagePath) {
                try { val f = File(item.localImagePath); if (f.exists() && f.length() > 0) f else null } catch (_: Throwable) { null }
            }

            if (file != null) {
                Image(painter = rememberAsyncImagePainter(model = file), contentDescription = "Scanned Leaf", modifier = Modifier.size(80.dp).clip(RoundedCornerShape(8.dp)), contentScale = ContentScale.Crop)
            } else {
                Box(modifier = Modifier.size(80.dp).clip(RoundedCornerShape(8.dp)).background(Color(0xFFE0E0E0)), contentAlignment = Alignment.Center) { Text("🌿", fontSize = 28.sp) }
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(text = "${str["crop_lbl"]}: ${item.crop.replaceFirstChar { it.uppercase() }}", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                Text(text = "${str["disease_lbl"]}: ${item.detectedDisease}", fontSize = 14.sp, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Medium)
                Text(text = "${str["high_conf"]}: ${(item.confidence * 100).toInt()}%", fontSize = 12.sp, color = Color.DarkGray)
                Text(text = dateString, fontSize = 11.sp, color = Color.Gray)
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(imageVector = Icons.Default.CheckCircle, contentDescription = "Synced", tint = Color(0xFF2E7D32), modifier = Modifier.size(14.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(text = str["hist_synced"] ?: "Synced", fontSize = 11.sp, color = Color(0xFF2E7D32), fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }
}

data class GuideItem(val cropName: String, val pests: String, val stage: String, val tip: String)

@Composable
fun GuideTabContent(selectedLanguage: String) {
    val guides = when (selectedLanguage) {
        "hi" -> listOf(
            GuideItem("कपास (Cotton)", "गुलाबी सुंडी, सफेद मक्खी", "फूल और बोंड बनने की अवस्था", "प्रति हेक्टेयर 5 फेरोमोन ट्रैप लगाएं; संतुलित खाद दें।"),
            GuideItem("मूंगफली (Groundnut)", "टिक्का रोग, कॉलर रोट", "अंकुरण और फली विकास", "ट्राइकोडर्मा से बीज उपचार करें; उचित जल निकासी रखें।"),
            GuideItem("चावल (Rice)", "धान का ब्लास्ट, शीथ ब्लाइट", "फुटाव और बाली निकलते समय", "संतुलित NPK दें; खेत में पानी का ठहराव रोकें।")
        )
        "mr" -> listOf(
            GuideItem("कापूस (Cotton)", "गुलाबी बोंडअळी, पांढरी माशी", "फुलोरा व बोंडे धरण्याची अवस्था", "हेक्टरी ५ कामगंध सापळे लावा; अतिरिक्त युरिया टाळा."),
            GuideItem("भुईमूग (Groundnut)", "टिक्का रोग, खोडकुज", "उगवण व शेंगा भरण्याची अवस्था", "ट्रायकोडर्माने बीजप्रक्रिया करा; पाण्याचा निचरा ठेवा."),
            GuideItem("भात (Rice)", "करपा (Blast), शीथ ब्लाइट", "फुटावे फुटणे व लोंबी भरण्याची वेळ", "संतुलित खत व्यवस्थापन ठेवा; पाणी साचू देऊ नका.")
        )
        else -> listOf(
            GuideItem("Cotton", "Pink Bollworm, Whitefly", "Flowering & Boll Formation", "Install 5 pheromone traps/ha; avoid excess chemical nitrogen."),
            GuideItem("Groundnut", "Tikka Disease, Collar Rot", "Seedling & Pod Development", "Treat seeds with Trichoderma; ensure good field drainage."),
            GuideItem("Rice", "Rice Blast, Sheath Blight", "Tillering & Panicle Initiation", "Apply balanced NPK; avoid prolonged water stagnation.")
        )
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text(text = "📚 Crop Protection Guidelines", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
        Spacer(modifier = Modifier.height(12.dp))
        LazyColumn(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 80.dp)) {
            items(guides) { item ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text(item.cropName, fontSize = 17.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("⚠️ Target: ${item.pests}", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                        Text("⏳ Stage: ${item.stage}", fontSize = 13.sp)
                        Spacer(modifier = Modifier.height(2.dp))
                        Text("🛡️ Prevention: ${item.tip}", fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                    }
                }
            }
        }
    }
}

@SuppressLint("MissingPermission")
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var selectedTab by remember { mutableIntStateOf(0) }
    var currentStep by remember { mutableIntStateOf(1) }

    var selectedLanguage by remember { mutableStateOf("en") }
    var farmerName by remember { mutableStateOf("") }

    var detectedDistrict by remember { mutableStateOf("Guntur, Andhra Pradesh") }
    var currentLatitude by remember { mutableFloatStateOf(16.49f) }
    var currentLongitude by remember { mutableFloatStateOf(80.50f) }
    var isLocationLoading by remember { mutableStateOf(false) }

    var showHelpDialog by remember { mutableStateOf(false) }
    val str = AppStrings.get(selectedLanguage)

    var capturedPhotoFile by remember { mutableStateOf<File?>(null) }
    var resultData by remember { mutableStateOf<CaseResponse?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var isAudioPlaying by remember { mutableStateOf(false) }
    var mediaPlayer by remember { mutableStateOf<MediaPlayer?>(null) }

    DisposableEffect(Unit) {
        onDispose {
            mediaPlayer?.release()
            mediaPlayer = null
        }
    }

    val imageCapture = remember { ImageCapture.Builder().build() }

    var hasPermissions by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED &&
                    ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        )
    }

    fun fetchCurrentLocation() {
        isLocationLoading = true
        val fusedLocationClient = LocationServices.getFusedLocationProviderClient(context)
        try {
            fusedLocationClient.lastLocation.addOnSuccessListener { location ->
                if (location != null) {
                    currentLatitude = location.latitude.toFloat()
                    currentLongitude = location.longitude.toFloat()

                    coroutineScope.launch {
                        val districtName = reverseGeocodeCoordinates(context, location.latitude, location.longitude)
                        detectedDistrict = districtName
                        isLocationLoading = false
                    }
                } else {
                    isLocationLoading = false
                }
            }.addOnFailureListener {
                isLocationLoading = false
            }
        } catch (_: SecurityException) {
            isLocationLoading = false
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val cam = permissions[Manifest.permission.CAMERA] == true
        val loc = permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true || permissions[Manifest.permission.ACCESS_COARSE_LOCATION] == true
        hasPermissions = cam && loc
        if (loc) fetchCurrentLocation()
    }

    LaunchedEffect(Unit) {
        if (!hasPermissions) {
            permissionLauncher.launch(
                arrayOf(Manifest.permission.CAMERA, Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
            )
        } else {
            fetchCurrentLocation()
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let { selectedUri ->
            isLoading = true
            coroutineScope.launch(Dispatchers.IO) {
                try {
                    val inputStream = context.contentResolver.openInputStream(selectedUri)
                    val cacheFile = File(context.cacheDir, "gallery_scan_${System.currentTimeMillis()}.jpg")
                    val outputStream = FileOutputStream(cacheFile)
                    inputStream?.copyTo(outputStream)
                    inputStream?.close()
                    outputStream.close()

                    capturedPhotoFile = cacheFile
                    val result = processAndSaveCase(
                        context = context,
                        photoFile = cacheFile,
                        language = selectedLanguage,
                        farmerName = farmerName,
                        district = detectedDistrict,
                        latitude = currentLatitude,
                        longitude = currentLongitude
                    )
                    withContext(Dispatchers.Main) {
                        isLoading = false
                        resultData = result
                        currentStep = 3
                    }
                } catch (_: Throwable) {
                    withContext(Dispatchers.Main) {
                        isLoading = false
                        Toast.makeText(context, "Failed to load image from gallery", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(str["title"] ?: "🌱 Kisan Mitra", fontWeight = FontWeight.Bold) },
                actions = {
                    IconButton(onClick = { showHelpDialog = true }) {
                        Icon(imageVector = Icons.Default.Info, contentDescription = "Help")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            )
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Home, contentDescription = "Scan") },
                    label = { Text(str["tab_scan"] ?: "Scan") },
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Refresh, contentDescription = "Weather") },
                    label = { Text(str["tab_weather"] ?: "Weather") },
                    selected = selectedTab == 4,
                    onClick = { selectedTab = 4 }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.AutoMirrored.Filled.List, contentDescription = "History") },
                    label = { Text(str["tab_history"] ?: "History") },
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Person, contentDescription = "Expert Desk") },
                    label = { Text(str["tab_expert"] ?: "Expert Desk") },
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Info, contentDescription = "Guide") },
                    label = { Text(str["tab_guide"] ?: "Guide") },
                    selected = selectedTab == 3,
                    onClick = { selectedTab = 3 }
                )
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            when (selectedTab) {
                0 -> {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                            .verticalScroll(rememberScrollState()),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        when (currentStep) {
                            1 -> {
                                Text(
                                    str["step1_lang"] ?: "1. Preferred Language",
                                    fontSize = 17.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    modifier = Modifier.align(Alignment.Start)
                                )
                                Spacer(modifier = Modifier.height(10.dp))

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

                                Spacer(modifier = Modifier.height(20.dp))

                                Text(
                                    str["step2_farmer"] ?: "2. Farmer Full Name",
                                    fontSize = 17.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    modifier = Modifier.align(Alignment.Start)
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                OutlinedTextField(
                                    value = farmerName,
                                    onValueChange = { farmerName = it },
                                    label = { Text("Farmer Name") },
                                    placeholder = { Text("e.g. Anna Sai") },
                                    singleLine = true,
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(8.dp)
                                )

                                Spacer(modifier = Modifier.height(20.dp))

                                Text(
                                    str["step3_location"] ?: "3. Farm Location (Auto GPS Detected)",
                                    fontSize = 17.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    modifier = Modifier.align(Alignment.Start)
                                )
                                Spacer(modifier = Modifier.height(8.dp))

                                Surface(
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(12.dp),
                                    color = MaterialTheme.colorScheme.surfaceVariant
                                ) {
                                    Row(
                                        modifier = Modifier.padding(14.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.LocationOn,
                                            contentDescription = "Location",
                                            tint = MaterialTheme.colorScheme.primary,
                                            modifier = Modifier.size(24.dp)
                                        )
                                        Spacer(modifier = Modifier.width(10.dp))
                                        Column(modifier = Modifier.weight(1f)) {
                                            Text(
                                                text = if (isLocationLoading) (str["loc_detecting"] ?: "Detecting Location...") else detectedDistrict,
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 15.sp
                                            )
                                            Text(
                                                text = "GPS: ${String.format(Locale.US, "%.2f", currentLatitude)}°N, ${String.format(Locale.US, "%.2f", currentLongitude)}°E",
                                                fontSize = 12.sp,
                                                color = Color.DarkGray
                                            )
                                        }
                                        IconButton(onClick = { fetchCurrentLocation() }) {
                                            Icon(
                                                imageVector = Icons.Default.Refresh,
                                                contentDescription = "Refresh GPS",
                                                tint = MaterialTheme.colorScheme.primary
                                            )
                                        }
                                    }
                                }

                                Spacer(modifier = Modifier.height(32.dp))

                                Button(
                                    onClick = { currentStep = 2 },
                                    modifier = Modifier.fillMaxWidth().height(50.dp),
                                    shape = RoundedCornerShape(10.dp)
                                ) {
                                    Text(str["btn_proceed"] ?: "Proceed to Leaf Scanner", fontSize = 16.sp)
                                }
                            }

                            2 -> {
                                Text(
                                    str["scanner_instruction"] ?: "Align infected leaf in viewfinder",
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
                                    if (hasPermissions) {
                                        CameraView(modifier = Modifier.fillMaxSize(), imageCapture = imageCapture)
                                    } else {
                                        Text("Camera & Location permissions required", color = Color.White)
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
                                            isLoading = true
                                            try {
                                                captureImageToFile(
                                                    context = context,
                                                    imageCapture = imageCapture,
                                                    onSuccess = { file ->
                                                        capturedPhotoFile = file
                                                        coroutineScope.launch {
                                                            val result = processAndSaveCase(
                                                                context = context,
                                                                photoFile = file,
                                                                language = selectedLanguage,
                                                                farmerName = farmerName,
                                                                district = detectedDistrict,
                                                                latitude = currentLatitude,
                                                                longitude = currentLongitude
                                                            )
                                                            isLoading = false
                                                            resultData = result
                                                            currentStep = 3
                                                        }
                                                    },
                                                    onError = {
                                                        val fallbackFile = File(context.cacheDir, "sample_scan.jpg").apply {
                                                            if (!exists()) {
                                                                createNewFile()
                                                                val bmp = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)
                                                                val out = FileOutputStream(this)
                                                                bmp.compress(Bitmap.CompressFormat.JPEG, 90, out)
                                                                out.flush()
                                                                out.close()
                                                            }
                                                        }
                                                        capturedPhotoFile = fallbackFile
                                                        coroutineScope.launch {
                                                            val result = processAndSaveCase(
                                                                context = context,
                                                                photoFile = fallbackFile,
                                                                language = selectedLanguage,
                                                                farmerName = farmerName,
                                                                district = detectedDistrict,
                                                                latitude = currentLatitude,
                                                                longitude = currentLongitude
                                                            )
                                                            isLoading = false
                                                            resultData = result
                                                            currentStep = 3
                                                        }
                                                    }
                                                )
                                            } catch (_: Throwable) {
                                                val fallbackFile = File(context.cacheDir, "sample_scan.jpg").apply {
                                                    if (!exists()) {
                                                        createNewFile()
                                                        val bmp = Bitmap.createBitmap(200, 200, Bitmap.Config.ARGB_8888)
                                                        val out = FileOutputStream(this)
                                                        bmp.compress(Bitmap.CompressFormat.JPEG, 90, out)
                                                        out.flush()
                                                        out.close()
                                                    }
                                                }
                                                capturedPhotoFile = fallbackFile
                                                coroutineScope.launch {
                                                    val result = processAndSaveCase(
                                                        context = context,
                                                        photoFile = fallbackFile,
                                                        language = selectedLanguage,
                                                        farmerName = farmerName,
                                                        district = detectedDistrict,
                                                        latitude = currentLatitude,
                                                        longitude = currentLongitude
                                                    )
                                                    isLoading = false
                                                    resultData = result
                                                    currentStep = 3
                                                }
                                            }
                                        },
                                        modifier = Modifier.fillMaxWidth().height(50.dp),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Text(str["btn_capture"] ?: "📸 Capture & Analyze", fontSize = 16.sp)
                                    }

                                    Spacer(modifier = Modifier.height(10.dp))

                                    OutlinedButton(
                                        onClick = { galleryLauncher.launch("image/*") },
                                        modifier = Modifier.fillMaxWidth().height(50.dp),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Text("📁 Choose from Gallery", fontSize = 16.sp)
                                    }
                                }
                            }

                            3 -> {
                                resultData?.let { res ->
                                    val isHighConfidence = res.confidence >= 0.75f
                                    val confidencePercent = (res.confidence * 100).toInt()

                                    Text(str["diag_result"] ?: "Diagnosis Result", fontSize = 22.sp, fontWeight = FontWeight.Bold)
                                    Spacer(modifier = Modifier.height(8.dp))

                                    Box(
                                        modifier = Modifier
                                            .background(
                                                if (isHighConfidence) Color(0xFFE8F5E9) else Color(0xFFFFF3E0),
                                                shape = RoundedCornerShape(12.dp)
                                            )
                                            .padding(horizontal = 14.dp, vertical = 6.dp)
                                    ) {
                                        Text(
                                            text = if (isHighConfidence) "${str["high_conf"]} ($confidencePercent%)" else "${str["low_conf"]} ($confidencePercent%)",
                                            color = if (isHighConfidence) Color(0xFF2E7D32) else Color(0xFFE65100),
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }

                                    Spacer(modifier = Modifier.height(16.dp))

                                    capturedPhotoFile?.let { file ->
                                        Image(
                                            painter = rememberAsyncImagePainter(file),
                                            contentDescription = "Captured Leaf Sample",
                                            modifier = Modifier.fillMaxWidth().height(200.dp).clip(RoundedCornerShape(12.dp)),
                                            contentScale = ContentScale.Crop
                                        )
                                        Spacer(modifier = Modifier.height(12.dp))
                                    }

                                    Card(
                                        modifier = Modifier.fillMaxWidth(),
                                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                                    ) {
                                        Column(modifier = Modifier.padding(16.dp)) {
                                            Text("${str["crop_lbl"]}: ${res.crop.replaceFirstChar { it.uppercase() }}", fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                                            Text("${str["farmer_lbl"]}: ${farmerName.ifBlank { "Farmer" }} | ${str["district_lbl"]}: $detectedDistrict", fontSize = 13.sp, color = Color.DarkGray)
                                            Spacer(modifier = Modifier.height(4.dp))
                                            Text("${str["disease_lbl"]}: ${res.disease.replace('_', ' ').replaceFirstChar { it.uppercase() }}", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(16.dp))

                                    if (res.response.isNotBlank()) {
                                        Text(str["advisory_title"] ?: "AI Treatment Advisory", fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                                        Spacer(modifier = Modifier.height(8.dp))

                                        Card(
                                            modifier = Modifier.fillMaxWidth(),
                                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.background),
                                            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                                        ) {
                                            Column(modifier = Modifier.padding(14.dp)) {
                                                Text(text = res.response, fontSize = 14.sp, lineHeight = 20.sp)

                                                if (!res.audioUrl.isNullOrEmpty()) {
                                                    Spacer(modifier = Modifier.height(12.dp))
                                                    Button(
                                                        onClick = {
                                                            val audioPath = res.audioUrl ?: ""
                                                            val fullUrl = if (audioPath.startsWith("http")) audioPath else "http://192.168.137.1:8000" + (if (audioPath.startsWith("/")) audioPath else "/$audioPath")
                                                            try {
                                                                if (mediaPlayer == null) {
                                                                    mediaPlayer = MediaPlayer().apply {
                                                                        setAudioAttributes(
                                                                            AudioAttributes.Builder().setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).setUsage(AudioAttributes.USAGE_MEDIA).build()
                                                                        )
                                                                        setDataSource(fullUrl)
                                                                        prepareAsync()
                                                                        setOnPreparedListener { start(); isAudioPlaying = true }
                                                                        setOnCompletionListener { isAudioPlaying = false; release(); mediaPlayer = null }
                                                                    }
                                                                } else {
                                                                    mediaPlayer?.let { player ->
                                                                        if (player.isPlaying) {
                                                                            player.pause()
                                                                            isAudioPlaying = false
                                                                        } else {
                                                                            player.start()
                                                                            isAudioPlaying = true
                                                                        }
                                                                    }
                                                                }
                                                            } catch (_: Exception) {
                                                                isAudioPlaying = false
                                                            }
                                                        },
                                                        modifier = Modifier.fillMaxWidth(),
                                                        shape = RoundedCornerShape(8.dp),
                                                        colors = ButtonDefaults.buttonColors(containerColor = if (isAudioPlaying) Color(0xFFC62828) else Color(0xFF2E7D32))
                                                    ) {
                                                        Icon(imageVector = Icons.Default.PlayArrow, contentDescription = null, tint = Color.White)
                                                        Spacer(modifier = Modifier.width(8.dp))
                                                        Text(text = if (isAudioPlaying) "⏸️ Pause Audio Advisory" else "🔊 Listen Audio Advisory", color = Color.White, fontWeight = FontWeight.SemiBold)
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(24.dp))

                                    Button(
                                        onClick = {
                                            capturedPhotoFile = null
                                            resultData = null
                                            currentStep = 1
                                        },
                                        modifier = Modifier.fillMaxWidth().height(50.dp),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Text(str["btn_restart"] ?: "Diagnose Another Sample", fontSize = 16.sp)
                                    }
                                }
                            }
                        }
                    }
                }
                1 -> HistoryTabContent(selectedLanguage = selectedLanguage)
                2 -> ExpertDeskScreen(selectedLanguage = selectedLanguage, currentFarmerName = farmerName)
                3 -> GuideTabContent(selectedLanguage = selectedLanguage)
                4 -> WeatherScreen(
                    selectedLanguage = selectedLanguage,
                    selectedDistrict = detectedDistrict,
                    selectedCrop = "cotton",
                    latitude = currentLatitude,
                    longitude = currentLongitude
                )
            }
        }
    }
}