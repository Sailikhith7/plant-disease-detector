package com.kisanmitra.ui.screens

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
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
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private val HOME_DISTRICTS = listOf(
    "Ahilyanagar (Ahmednagar)", "Akola", "Amravati", "Beed", "Bhandara",
    "Buldhana", "Chandrapur", "Chhatrapati Sambhajinagar (Aurangabad)",
    "Dharashiv (Osmanabad)", "Dhule", "Gadchiroli", "Gondia", "Hingoli",
    "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban",
    "Nagpur", "Nanded", "Nandurbar", "Nashik", "Palghar", "Parbhani",
    "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg",
    "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"
)

object AppStrings {
    fun get(lang: String): Map<String, String> = when (lang) {
        "hi" -> mapOf(
            "title" to "🌱 किसान मित्र",
            "step1_lang" to "१. पसंदीदा भाषा",
            "step2_farmer" to "२. किसान का नाम",
            "step3_district" to "३. जिला (महाराष्ट्र)",
            "btn_proceed" to "पत्ती स्कैनर पर जाएं",
            "scanner_instruction" to "कैमरे के सामने संक्रमित पत्ती रखें",
            "btn_capture" to "📸 फोटो लें और विश्लेषण करें",
            "analyzing" to "एआई और आरएजी द्वारा विश्लेषण हो रहा है...",
            "diag_result" to "जांच परिणाम",
            "high_conf" to "उच्च सटीकता (High Confidence)",
            "low_conf" to "समीक्षा आवश्यक (Under Expert Review)",
            "crop_lbl" to "फसल",
            "farmer_lbl" to "किसान",
            "district_lbl" to "जिला",
            "disease_lbl" to "पहचाना गया रोग",
            "advisory_title" to "एआई उपचार सलाह (RAG Guidance)",
            "btn_restart" to "दूसरे नमूने की जांच करें",
            "disease_name" to "गुलाबी सुंडी (Pink Bollworm)",
            "fallback_advisory" to "फसल अवशेष नष्ट करें, फेरोमोन ट्रैप लगाएं और क्लोरांट्रानिलिप्रोल 18.5% SC @ 60 मिली/एकड़ का छिड़काव करें।",
            "tab_scan" to "स्कैन",
            "tab_history" to "इतिहास",
            "tab_guide" to "गाइडलाइन",
            "hist_title" to "पिछले निदान रिकॉर्ड",
            "hist_empty" to "अभी तक कोई इतिहास रिकॉर्ड नहीं मिला।",
            "hist_synced" to "क्लाउड पर सिंक किया गया",
            "hist_pending" to "लोकल सेव (सिंक लंबित)",
            "help_title" to "महाराष्ट्र कृषि सहायता (Help & Support)",
            "help_desc" to "यदि आपको फसल निदान या सहायता चाहिए, तो नीचे दिए गए माध्यमों से संपर्क करें:",
            "help_helpline_lbl" to "📞 हेल्पलाइन / फोन: ",
            "help_email_lbl" to "✉️ ईमेल: ",
            "help_website_lbl" to "🌐 वेबसाइट: ",
            "close_btn" to "बंद करें"
        )
        "mr" -> mapOf(
            "title" to "🌱 किसान मित्र",
            "step1_lang" to "१. पसंतीची भाषा",
            "step2_farmer" to "२. शेतकऱ्याचे नाव",
            "step3_district" to "३. जिल्हा (महाराष्ट्र)",
            "btn_proceed" to "पाने स्कॅनरकडे जा",
            "scanner_instruction" to "कॅमेऱ्यासमोर बाधित पान धरा",
            "btn_capture" to "📸 फोटो घ्या आणि विश्लेषण करा",
            "analyzing" to "एआई व आरएजी द्वारे विश्लेषण सुरू आहे...",
            "diag_result" to "निदान निकाल",
            "high_conf" to "उच्च अचूकता (High Confidence)",
            "low_conf" to "तज्ज्ञ पुनरावलोकन (Under Expert Review)",
            "crop_lbl" to "पीक",
            "farmer_lbl" to "शेतकरी",
            "district_lbl" to "जिल्हा",
            "disease_lbl" to "आढळलेला रोग",
            "advisory_title" to "एआय उपचार सल्ला (RAG Guidance)",
            "btn_restart" to "दुसऱ्या नमुन्याची तपासणी करा",
            "disease_name" to "गुलाबी बोंडअळी (Pink Bollworm)",
            "fallback_advisory" to "पिकाचे अवशेष नष्ट करा, कामगंध सापळे लावा आणि योग्य कीटकनाशकाची फवारणी करा.",
            "tab_scan" to "स्कॅन",
            "tab_history" to "इतिहास",
            "tab_guide" to "मार्गदर्शक",
            "hist_title" to "मागील निदान नोंदी",
            "hist_empty" to "अद्याप कोणताही इतिहास आढळला नाही.",
            "hist_synced" to "क्लाउडवर सिंक केले",
            "hist_pending" to "स्थानिक सेव्ह (प्रलंबित)",
            "help_title" to "महाराष्ट्र कृषी मदत (Help & Support)",
            "help_desc" to "आपल्याला शेतीविषयी किंवा पिकांच्या रोगांबाबतीत मदत हवी असल्यास खालील संपर्कांवर संपर्क साधा:",
            "help_helpline_lbl" to "📞 हेल्पलाईन / फोन: ",
            "help_email_lbl" to "✉️ ई-मेल: ",
            "help_website_lbl" to "🌐 संकेतस्थळ: ",
            "close_btn" to "बंद करा"
        )
        else -> mapOf(
            "title" to "🌱 Kisan Mitra",
            "step1_lang" to "1. Preferred Language",
            "step2_farmer" to "2. Farmer Full Name",
            "step3_district" to "3. District (Maharashtra)",
            "btn_proceed" to "Proceed to Leaf Scanner",
            "scanner_instruction" to "Align infected leaf in viewfinder",
            "btn_capture" to "📸 Capture & Analyze",
            "analyzing" to "Analyzing leaf with ML & RAG...",
            "diag_result" to "Diagnosis Result",
            "high_conf" to "High Confidence",
            "low_conf" to "Under Expert Review",
            "crop_lbl" to "Crop",
            "farmer_lbl" to "Farmer",
            "district_lbl" to "District",
            "disease_lbl" to "Detected Disease",
            "advisory_title" to "AI Treatment Advisory (RAG Guidance)",
            "btn_restart" to "Diagnose Another Sample",
            "disease_name" to "Pink Bollworm",
            "fallback_advisory" to "Destroy crop residues, deploy pheromone traps, and apply recommended bio-pesticides or chemical sprays as per IPM guidelines.",
            "tab_scan" to "Scan",
            "tab_history" to "History",
            "tab_guide" to "Guide",
            "hist_title" to "Diagnosis History",
            "hist_empty" to "No scan records found yet.",
            "hist_synced" to "Synced to Cloud",
            "hist_pending" to "Local Saved (Pending Sync)",
            "help_title" to "Maharashtra Farmer Help & Support",
            "help_desc" to "If you need immediate assistance or expert agronomy support across Maharashtra, please reach out via:",
            "help_helpline_lbl" to "📞 Helpline / Tel: ",
            "help_email_lbl" to "✉️ Email: ",
            "help_website_lbl" to "🌐 Website: ",
            "close_btn" to "Close"
        )
    }
}

suspend fun processAndSaveCase(
    context: Context,
    photoFile: File,
    crop: String = "",
    language: String,
    farmerName: String,
    district: String,
    defaultDisease: String
): CaseResponse = withContext(Dispatchers.IO) {

    val appContext = context.applicationContext

    try {
        val requestFile =
            photoFile.asRequestBody("image/jpeg".toMediaTypeOrNull())

        val imagePart =
            MultipartBody.Part.createFormData(
                "image",
                photoFile.name,
                requestFile
            )

        val langBody =
            language.toRequestBody(
                "text/plain".toMediaTypeOrNull()
            )

        val cropBody =
            crop.toRequestBody(
                "text/plain".toMediaTypeOrNull()
            )

        val farmerNameBody =
            farmerName.ifBlank { "App Farmer" }
                .toRequestBody(
                    "text/plain".toMediaTypeOrNull()
                )

        val districtBody =
            district.toRequestBody(
                "text/plain".toMediaTypeOrNull()
            )

        val farmerIdBody =
            "MH_${district.take(3).uppercase()}_001"
                .toRequestBody(
                    "text/plain".toMediaTypeOrNull()
                )

        android.util.Log.d(
            "NetworkAPI",
            "Sending crop='$crop' to /api/predict"
        )

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

            android.util.Log.d(
                "NetworkAPI",
                "Prediction: crop=${body.crop}, " +
                    "disease=${body.disease}, " +
                    "confidence=${body.confidence}"
            )

            // Save the ACTUAL ML prediction
            val db = AppDatabase.getDatabase(appContext)

            val localId = db.caseDao().insertCase(
                CaseEntity(
                    localImagePath = photoFile.absolutePath,
                    crop = body.crop,
                    language = language,
                    latitude = 16.51f,
                    longitude = 80.52f,
                    detectedDisease = body.disease,
                    confidence = body.confidence,
                    isSynced = true,
                    createdAt = System.currentTimeMillis()
                )
            )

            android.util.Log.d(
                "RoomDB",
                "Saved prediction ID=$localId, crop=${body.crop}"
            )

            return@withContext body
        }

        android.util.Log.e(
            "NetworkAPI",
            "Backend returned HTTP ${response.code()}"
        )

    } catch (e: Throwable) {

        android.util.Log.e(
            "NetworkAPI",
            "Prediction/save failed",
            e
        )
    }

    // Fallback if backend is unavailable
    val str = AppStrings.get(language)

    val db = AppDatabase.getDatabase(appContext)

    db.caseDao().insertCase(
        CaseEntity(
            localImagePath = photoFile.absolutePath,
            crop = crop.ifBlank { "Unknown" },
            language = language,
            latitude = 16.51f,
            longitude = 80.52f,
            detectedDisease = defaultDisease,
            confidence = 0f,
            isSynced = false,
            createdAt = System.currentTimeMillis()
        )
    )

    CaseResponse(
        crop = crop.ifBlank { "Unknown" },
        disease = defaultDisease,
        confidence = 0f,
        status = "Pending Expert",
        response = str["fallback_advisory"] ?: "",
        language = language
    )
}

@Composable
fun HistoryTabContent(selectedLanguage: String) {
    val context = LocalContext.current
    val str = AppStrings.get(selectedLanguage)

    var casesList by remember {
        mutableStateOf<List<CaseEntity>>(emptyList())
    }

    var isLoading by remember {
        mutableStateOf(true)
    }

    LaunchedEffect(Unit) {
        try {
            val db = withContext(Dispatchers.IO) {
                AppDatabase.getDatabase(context.applicationContext)
            }

            db.caseDao()
                .getAllCasesFlow()
                .collect { cases ->
                    casesList = cases
                    isLoading = false

                    android.util.Log.d(
                        "HistoryTab",
                        "History updated: ${cases.size} records"
                    )
                }

        } catch (e: Exception) {
            android.util.Log.e(
                "HistoryTab",
                "Failed to observe history",
                e
            )

            casesList = emptyList()
            isLoading = false
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {

        Text(
            text = str["hist_title"] ?: "Diagnosis History",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(12.dp))

        when {
            isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(bottom = 60.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }

            casesList.isEmpty() -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(bottom = 60.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            "🌿",
                            fontSize = 42.sp
                        )

                        Spacer(
                            modifier = Modifier.height(8.dp)
                        )

                        Text(
                            text = str["hist_empty"]
                                ?: "No scan records found yet.",
                            color = Color.Gray,
                            fontSize = 15.sp
                        )
                    }
                }
            }

            else -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    contentPadding = PaddingValues(bottom = 80.dp)
                ) {
                    items(casesList) { item ->
                        HistoryCardView(
                            item = item,
                            str = str
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun HistoryCardView(item: CaseEntity, str: Map<String, String>) {
    val dateString = remember(item.createdAt) {
        try {
            SimpleDateFormat("dd MMM yyyy, hh:mm a", Locale.getDefault()).format(Date(item.createdAt))
        } catch (_: Throwable) {
            ""
        }
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            val file = remember(item.localImagePath) {
                try {
                    val f = File(item.localImagePath)
                    if (f.exists() && f.length() > 0) f else null
                } catch (_: Throwable) {
                    null
                }
            }

            if (file != null) {
                Image(
                    painter = rememberAsyncImagePainter(model = file),
                    contentDescription = "Scanned Leaf",
                    modifier = Modifier
                        .size(80.dp)
                        .clip(RoundedCornerShape(8.dp)),
                    contentScale = ContentScale.Crop
                )
            } else {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color(0xFFE0E0E0)),
                    contentAlignment = Alignment.Center
                ) {
                    Text("🌿", fontSize = 28.sp)
                }
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "${str["crop_lbl"]}: ${item.crop.replaceFirstChar { it.uppercase() }}",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp
                )
                Text(
                    text = "${str["disease_lbl"]}: ${item.detectedDisease}",
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "${str["high_conf"]}: ${(item.confidence * 100).toInt()}%",
                    fontSize = 12.sp,
                    color = Color.DarkGray
                )
                Text(
                    text = dateString,
                    fontSize = 11.sp,
                    color = Color.Gray
                )

                Spacer(modifier = Modifier.height(4.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (item.isSynced) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Synced",
                            tint = Color(0xFF2E7D32),
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = str["hist_synced"] ?: "Synced to Cloud",
                            fontSize = 11.sp,
                            color = Color(0xFF2E7D32),
                            fontWeight = FontWeight.SemiBold
                        )
                    } else {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Pending Sync",
                            tint = Color(0xFFF57F17),
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = str["hist_pending"] ?: "Local Saved (Pending Sync)",
                            fontSize = 11.sp,
                            color = Color(0xFFF57F17),
                            fontWeight = FontWeight.SemiBold
                        )
                    }
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
            GuideItem(
                cropName = "कपास (Cotton)",
                pests = "गुलाबी सुंडी, सफेद मक्खी, लीफ कर्ल",
                stage = "फूल और बोंड बनने की अवस्था",
                tip = "प्रति हेक्टेयर 5 फेरोमोन ट्रैप लगाएं; अत्यधिक नाइट्रोजन खाद के प्रयोग से बचें।"
            ),
            GuideItem(
                cropName = "मूंगफली (Groundnut)",
                pests = "टिक्का रोग, कॉलर रोट, तना सड़न",
                stage = "अंकुरण और फली विकास",
                tip = "ट्राइकोडर्मा से बीज उपचार करें; जलभराव रोकने के लिए उचित जल निकासी रखें।"
            ),
            GuideItem(
                cropName = "रागी (Ragi)",
                pests = "ब्लास्ट (करपा) रोग, तना छेदक",
                stage = "टिलरिंग और बाल, फूल आने की अवस्था",
                tip = "रोग-प्रतिरोधी किस्मों का चयन करें; निवारक उपाय के रूप में नीम के अर्क का छिड़काव करें।"
            ),
            GuideItem(
                cropName = "चावल (Rice)",
                pests = "धान का ब्लास्ट, शीथ ब्लाइट, बैक्टीरियल ब्लाइट",
                stage = "फुटाव और बाली निकलते समय",
                tip = "संतुलित उर्वरक (NPK) दें; खेत में पानी का ठहराव रोकें और प्रमाणित बीजों का उपयोग करें।"
            ),
            GuideItem(
                cropName = "गन्ना (Sugarcane)",
                pests = "लाल सड़न (रेड रॉट), कण्डवा (स्मट), शीर्ष छेदक",
                stage = "अंकुरण और कल्ले फूटने की अवस्था",
                tip = "स्वस्थ व रोगमुक्त बीजों (सेट) का उपयोग करें; फसल चक्र अपनाएं और खेत की सफाई रखें।"
            )
        )
        "mr" -> listOf(
            GuideItem(
                cropName = "कापूस (Cotton)",
                pests = "गुलाबी बोंडअळी, पांढरी माशी, मावा",
                stage = "फुलोरा व बोंडे धरण्याची अवस्था",
                tip = "हेक्टरी ५ कामगंध सापळे (Pheromone Traps) लावा; अतिरिक्त नत्र (युरिया) खताचा वापर टाळा."
            ),
            GuideItem(
                cropName = "भुईमूग (Groundnut)",
                pests = "टिक्का रोग, खोडकुज, मूळकुज",
                stage = "उगवण व शेंगा भरण्याची अवस्था",
                tip = "ट्रायकोडर्माने बीजप्रक्रिया करा; पाण्याचा निचरा व्यवस्थित ठेवून साचू देऊ नका."
            ),
            GuideItem(
                cropName = "नाचणी/रागी (Ragi)",
                pests = "करपा (Blast), खोड कीड",
                stage = "फुटावे फुटण्याची व पोंगा अवस्था",
                tip = "प्रतिकारक्षम वाणांची निवड करा; प्रतिबंधात्मक उपाय म्हणून निंबोळी अर्काची फवारणी करा."
            ),
            GuideItem(
                cropName = "भात/तांदूळ (Rice)",
                pests = "करपा (Blast), शीथ ब्लाइट, जिवाणू करपा",
                stage = "फुटावे फुटणे व लोंबी भरण्याची वेळ",
                tip = "संतुलित खत व्यवस्थापन ठेवा; शेतात पाणी साचू देऊ नका व प्रमाणित बियाणे वापर करा."
            ),
            GuideItem(
                cropName = "ऊस (Sugarcane)",
                pests = "लाल कुज (Red Rot), काजळी, खोड कीड",
                stage = "उगवण व फुटवे फुटण्याची अवस्था",
                tip = "निरोगी व रोगमुक्त बेणे वापरा; फेरपालट पद्धत अवलंबा व शेत तणमुक्त ठेवा."
            )
        )
        else -> listOf(
            GuideItem(
                cropName = "Cotton",
                pests = "Pink Bollworm, Whitefly, Leaf Curl",
                stage = "Flowering & Boll Formation Stage",
                tip = "Install 5 pheromone traps per hectare; avoid excessive chemical nitrogen fertilizer applications."
            ),
            GuideItem(
                cropName = "Groundnut",
                pests = "Tikka Disease, Collar Rot, Stem Rot",
                stage = "Seedling & Pod Development Stage",
                tip = "Treat seeds with Trichoderma viride; maintain proper soil drainage to prevent waterlogging."
            ),
            GuideItem(
                cropName = "Ragi",
                pests = "Blast Disease, Stem Borer",
                stage = "Tillering & Flowering Stage",
                tip = "Use certified blast-resistant varieties; spray neem seed kernel extract (1500 ppm) preventively."
            ),
            GuideItem(
                cropName = "Rice",
                pests = "Rice Blast, Sheath Blight, Bacterial Blight",
                stage = "Tillering & Panicle Initiation Stage",
                tip = "Apply balanced NPK fertilizers; avoid water stagnation and use certified disease-free seeds."
            ),
            GuideItem(
                cropName = "Sugarcane",
                pests = "Red Rot, Smut, Early Shoot Borer",
                stage = "Germination & Tillering Stage",
                tip = "Plant disease-free certified setts; practice field sanitation and regular crop rotation."
            )
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "📚 Crop Protection Guidelines",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(12.dp))

        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            contentPadding = PaddingValues(bottom = 80.dp)
        ) {
            items(guides) { item ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text(item.cropName, fontSize = 17.sp, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(6.dp))
                        Text("⚠️ Target: ${item.pests}", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                        Text("⏳ Critical Stage: ${item.stage}", fontSize = 13.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("🛡️ Prevention: ${item.tip}", fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var selectedTab by remember { mutableIntStateOf(0) }
    var currentStep by remember { mutableIntStateOf(1) }

    // User Selection States
    var selectedLanguage by remember { mutableStateOf("en") }
    var farmerName by remember { mutableStateOf("") }
    var selectedDistrict by remember { mutableStateOf("Yavatmal") }
    var isDistrictDropdownExpanded by remember { mutableStateOf(false) }

    // Help Dialog State
    var showHelpDialog by remember { mutableStateOf(false) }

    val str = AppStrings.get(selectedLanguage)

    var capturedPhotoFile by remember { mutableStateOf<File?>(null) }
    var resultData by remember { mutableStateOf<CaseResponse?>(null) }
    var isLoading by remember { mutableStateOf(false) }

    val imageCapture = remember { ImageCapture.Builder().build() }

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

    // Gallery Picker Launcher
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
                        district = selectedDistrict,
                        defaultDisease = str["disease_name"] ?: "Pink Bollworm"
                    )
                    withContext(Dispatchers.Main) {
                        isLoading = false
                        resultData = result
                        currentStep = 3
                    }
                } catch (e: Throwable) {
                    android.util.Log.e("GalleryPicker", "Failed to process selected image", e)
                    withContext(Dispatchers.Main) {
                        isLoading = false
                        Toast.makeText(context, "Failed to load image from gallery", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
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

    // Help & Support Dialog with Clickable Intents (Call, Mail, Browser)
    if (showHelpDialog) {
        AlertDialog(
            onDismissRequest = { showHelpDialog = false },
            title = {
                Text(text = str["help_title"] ?: "Help & Support", fontWeight = FontWeight.Bold)
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text(text = str["help_desc"] ?: "", fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(2.dp))

                    // 1. Interactive Helpline Phone Number
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                try {
                                    val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:02026123648"))
                                    context.startActivity(dialIntent)
                                } catch (_: Throwable) {
                                    Toast.makeText(context, "Unable to open dialer", Toast.LENGTH_SHORT).show()
                                }
                            }
                            .padding(vertical = 2.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = str["help_helpline_lbl"] ?: "📞 Helpline: ",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "020-26123648",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary,
                            textDecoration = TextDecoration.Underline
                        )
                    }

                    // 2. Interactive Support Email
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                try {
                                    val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
                                        data = Uri.parse("mailto:comm.agripune-mh@gov.in")
                                        putExtra(Intent.EXTRA_SUBJECT, "Kisan Mitra - Crop Disease Advisory Assistance")
                                    }
                                    context.startActivity(emailIntent)
                                } catch (_: Throwable) {
                                    Toast.makeText(context, "No email client found", Toast.LENGTH_SHORT).show()
                                }
                            }
                            .padding(vertical = 2.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = str["help_email_lbl"] ?: "✉️ Email: ",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "comm.agripune-mh@gov.in",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary,
                            textDecoration = TextDecoration.Underline
                        )
                    }

                    // 3. Interactive Official Website
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                try {
                                    val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://krishi.maharashtra.gov.in"))
                                    context.startActivity(browserIntent)
                                } catch (_: Throwable) {
                                    Toast.makeText(context, "Unable to open browser", Toast.LENGTH_SHORT).show()
                                }
                            }
                            .padding(vertical = 2.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = str["help_website_lbl"] ?: "🌐 Website: ",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "krishi.maharashtra.gov.in",
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary,
                            textDecoration = TextDecoration.Underline
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showHelpDialog = false }) {
                    Text(str["close_btn"] ?: "Close")
                }
            }
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(str["title"] ?: "🌱 Kisan Mitra", fontWeight = FontWeight.Bold) },
                actions = {
                    IconButton(onClick = { showHelpDialog = true }) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = "Help & Support"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
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
                    icon = { Icon(Icons.AutoMirrored.Filled.List, contentDescription = "History") },
                    label = { Text(str["tab_history"] ?: "History") },
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Info, contentDescription = "Guide") },
                    label = { Text(str["tab_guide"] ?: "Guide") },
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 }
                )
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
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
                                // 1. Language Selection
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

                                // 2. Farmer Name Input
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
                                    placeholder = { Text("e.g. Kasim Sheikh") },
                                    singleLine = true,
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(8.dp)
                                )

                                Spacer(modifier = Modifier.height(20.dp))

                                // 3. Maharashtra 36 Districts Dropdown
                                Text(
                                    str["step3_district"] ?: "3. District (Maharashtra)",
                                    fontSize = 17.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    modifier = Modifier.align(Alignment.Start)
                                )
                                Spacer(modifier = Modifier.height(8.dp))

                                ExposedDropdownMenuBox(
                                    expanded = isDistrictDropdownExpanded,
                                    onExpandedChange = { isDistrictDropdownExpanded = !isDistrictDropdownExpanded },
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    OutlinedTextField(
                                        value = selectedDistrict,
                                        onValueChange = {},
                                        readOnly = true,
                                        label = { Text("District") },
                                        trailingIcon = {
                                            ExposedDropdownMenuDefaults.TrailingIcon(
                                                expanded = isDistrictDropdownExpanded
                                            )
                                        },
                                        colors = ExposedDropdownMenuDefaults.outlinedTextFieldColors(),
                                        shape = RoundedCornerShape(8.dp),
                                        modifier = Modifier
                                            .menuAnchor()
                                            .fillMaxWidth()
                                    )

                                    ExposedDropdownMenu(
                                        expanded = isDistrictDropdownExpanded,
                                        onDismissRequest = { isDistrictDropdownExpanded = false }
                                    ) {
                                        HOME_DISTRICTS.forEach { districtOption ->
                                            DropdownMenuItem(
                                                text = { Text(districtOption) },
                                                onClick = {
                                                    selectedDistrict = districtOption
                                                    isDistrictDropdownExpanded = false
                                                }
                                            )
                                        }
                                    }
                                }

                                Spacer(modifier = Modifier.height(32.dp))

                                Button(
                                    onClick = { currentStep = 2 },
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(50.dp),
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
                                                                district = selectedDistrict,
                                                                defaultDisease = str["disease_name"] ?: "Pink Bollworm"
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
                                                                district = selectedDistrict,
                                                                defaultDisease = str["disease_name"] ?: "Pink Bollworm"
                                                            )
                                                            isLoading = false
                                                            resultData = result
                                                            currentStep = 3
                                                        }
                                                    }
                                                )
                                            } catch (e: Throwable) {
                                                android.util.Log.e("CameraCapture", "Capture failed", e)
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
                                                        district = selectedDistrict,
                                                        defaultDisease = str["disease_name"] ?: "Pink Bollworm"
                                                    )
                                                    isLoading = false
                                                    resultData = result
                                                    currentStep = 3
                                                }
                                            }
                                        },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(50.dp),
                                        shape = RoundedCornerShape(10.dp)
                                    ) {
                                        Text(str["btn_capture"] ?: "📸 Capture & Analyze", fontSize = 16.sp)
                                    }

                                    Spacer(modifier = Modifier.height(10.dp))

                                    OutlinedButton(
                                        onClick = { galleryLauncher.launch("image/*") },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(50.dp),
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
                                            text = if (isHighConfidence) {
                                                "${str["high_conf"]} ($confidencePercent%)"
                                            } else {
                                                "${str["low_conf"]} ($confidencePercent%)"
                                            },
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
                                            Text(
                                                "${str["crop_lbl"]}: ${res.crop.replaceFirstChar { it.uppercase() }}",
                                                fontSize = 15.sp
                                            )
                                            Text(
                                                "${str["farmer_lbl"]}: ${farmerName.ifBlank { "Kasim" }} | ${str["district_lbl"]}: $selectedDistrict",
                                                fontSize = 13.sp,
                                                color = Color.DarkGray
                                            )
                                            Spacer(modifier = Modifier.height(4.dp))
                                            Text(
                                                "${str["disease_lbl"]}: ${res.disease.replace('_', ' ').replaceFirstChar { it.uppercase() }}",
                                                fontSize = 18.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = MaterialTheme.colorScheme.primary
                                            )
                                            Text("Status: ${res.status}", fontSize = 12.sp, color = Color.Gray)
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
                                            Text(
                                                text = res.response,
                                                modifier = Modifier.padding(14.dp),
                                                fontSize = 14.sp,
                                                lineHeight = 20.sp
                                            )
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(24.dp))

                                    OutlinedButton(
                                        onClick = {
                                            capturedPhotoFile = null
                                            resultData = null
                                            currentStep = 1
                                        },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(50.dp),
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
                2 -> GuideTabContent(selectedLanguage = selectedLanguage)
            }
        }
    }
}