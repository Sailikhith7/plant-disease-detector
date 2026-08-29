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
    "Ahilyanagar (Ahmednagar)", "Akola", "Amravati", "Beed", "Bhandara",
    "Buldhana", "Chandrapur", "Chhatrapati Sambhajinagar (Aurangabad)",
    "Dharashiv (Osmanabad)", "Dhule", "Gadchiroli", "Gondia", "Hingoli",
    "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai City", "Mumbai Suburban",
    "Nagpur", "Nanded", "Nandurbar", "Nashik", "Palghar", "Parbhani",
    "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg",
    "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    backendUrl: String = "http://192.168.137.1:8000",
    selectedLanguage: String = "en",
    onDiagnosisSuccess: (crop: String, disease: String, confidence: Float, status: String, response: String) -> Unit,
    onBackClick: () -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val scrollState = rememberScrollState()

    var isUploading by remember { mutableStateOf(false) }
    var tempImageFile by remember { mutableStateOf<File?>(null) }

    // User Inputs (Default blank / first district)
    var enteredFarmerName by remember { mutableStateOf("") }
    var enteredCrop by remember { mutableStateOf("Cotton") }
    var selectedDistrict by remember { mutableStateOf("Yavatmal") }
    var isDistrictDropdownExpanded by remember { mutableStateOf(false) }

    fun createTempImageFile(): File {
        val timeStamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir = context.cacheDir
        return File.createTempFile("LEAF_${timeStamp}_", ".jpg", storageDir).apply {
            tempImageFile = this
        }
    }

    fun uploadAndPredict(imageFile: File) {
        val farmerToSubmit = if (enteredFarmerName.isNotBlank()) enteredFarmerName.trim() else "App Farmer"
        val districtToSubmit = selectedDistrict
        val cropToSubmit = if (enteredCrop.isNotBlank()) enteredCrop.trim() else "Cotton"

        isUploading = true
        coroutineScope.launch(Dispatchers.IO) {
            try {
                val client = OkHttpClient.Builder()
                    .connectTimeout(30, TimeUnit.SECONDS)
                    .readTimeout(60, TimeUnit.SECONDS)
                    .build()

                val requestBody = MultipartBody.Builder()
                    .setType(MultipartBody.FORM)
                    .addFormDataPart(
                        "image",
                        imageFile.name,
                        imageFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
                    )
                    .addFormDataPart("language", selectedLanguage)
                    .addFormDataPart("farmer_name", farmerToSubmit)
                    .addFormDataPart("crop", cropToSubmit)
                    .addFormDataPart("district", districtToSubmit)
                    .addFormDataPart("farmer_id", "FARMER_${UUID.randomUUID().toString().take(6).uppercase()}")
                    .build()

                val request = Request.Builder()
                    .url("$backendUrl/api/predict")
                    .post(requestBody)
                    .build()

                val response = client.newCall(request).execute()
                val responseData = response.body?.string()

                withContext(Dispatchers.Main) {
                    isUploading = false
                    if (response.isSuccessful && responseData != null) {
                        val json = JSONObject(responseData)
                        val crop = json.optString("crop", cropToSubmit)
                        val disease = json.optString("disease", "Unknown")
                        val confidence = json.optDouble("confidence", 0.0).toFloat()
                        val status = json.optString("status", "Pending Expert")
                        val advisory = json.optString("response", "No advisory generated.")

                        onDiagnosisSuccess(crop, disease, confidence, status, advisory)
                    } else {
                        Toast.makeText(
                            context,
                            "Analysis failed: ${response.message}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    isUploading = false
                    Toast.makeText(
                        context,
                        "Server Connection Error: ${e.localizedMessage}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }

    val cameraLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.TakePicture()
    ) { success ->
        if (success && tempImageFile != null) {
            uploadAndPredict(tempImageFile!!)
        }
    }

    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let { selectedUri ->
            val file = createTempImageFile()
            context.contentResolver.openInputStream(selectedUri)?.use { input ->
                FileOutputStream(file).use { output ->
                    input.copyTo(output)
                }
            }
            uploadAndPredict(file)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Enter Details & Scan", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFF1B5E20),
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(20.dp),
            contentAlignment = Alignment.Center
        ) {
            if (isUploading) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    CircularProgressIndicator(
                        color = Color(0xFF2E7D32),
                        strokeWidth = 4.dp
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Analyzing & registering case...",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Medium
                    )
                }
            } else {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(scrollState),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    // Field Inputs Card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFF1F8E9)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = "Farmer & Field Details",
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1B5E20),
                                fontSize = 16.sp
                            )
                            Spacer(modifier = Modifier.height(12.dp))

                            // 1. Farmer Name Input
                            OutlinedTextField(
                                value = enteredFarmerName,
                                onValueChange = { enteredFarmerName = it },
                                label = { Text("Farmer Full Name") },
                                placeholder = { Text("e.g. Kasim Sheikh") },
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(8.dp),
                                singleLine = true
                            )

                            Spacer(modifier = Modifier.height(10.dp))

                            // 2. Crop Selection
                            OutlinedTextField(
                                value = enteredCrop,
                                onValueChange = { enteredCrop = it },
                                label = { Text("Crop Type") },
                                modifier = Modifier.fillMaxWidth(),
                                shape = RoundedCornerShape(8.dp),
                                singleLine = true
                            )

                            Spacer(modifier = Modifier.height(10.dp))

                            // 3. 36 Maharashtra Districts Dropdown
                            ExposedDropdownMenuBox(
                                expanded = isDistrictDropdownExpanded,
                                onExpandedChange = { isDistrictDropdownExpanded = !isDistrictDropdownExpanded },
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                OutlinedTextField(
                                    value = selectedDistrict,
                                    onValueChange = {},
                                    readOnly = true,
                                    label = { Text("District (Maharashtra)") },
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
                                    MAHARASHTRA_DISTRICTS.forEach { districtOption ->
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
                        }
                    }

                    Spacer(modifier = Modifier.height(6.dp))

                    Button(
                        onClick = {
                            val file = createTempImageFile()
                            val uri = FileProvider.getUriForFile(
                                context,
                                "${context.packageName}.fileprovider",
                                file
                            )
                            cameraLauncher.launch(uri)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(54.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1B5E20)),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Icon(Icons.Default.Add, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Capture Photo with Camera", fontSize = 16.sp)
                    }

                    OutlinedButton(
                        onClick = { galleryLauncher.launch("image/*") },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(54.dp),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Icon(Icons.Default.Check, contentDescription = null)
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Choose from Gallery", fontSize = 16.sp)
                    }
                }
            }
        }
    }
}