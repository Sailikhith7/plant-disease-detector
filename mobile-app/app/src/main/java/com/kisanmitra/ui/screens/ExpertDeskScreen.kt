package com.kisanmitra.ui.screens

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.kisanmitra.data.remote.ApiClient
import com.kisanmitra.data.remote.ExpertDeskCaseDto
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExpertDeskScreen(
    selectedLanguage: String,
    currentFarmerName: String = ""
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var casesList by remember { mutableStateOf<List<ExpertDeskCaseDto>>(emptyList()) }
    var isLoading by remember { mutableStateOf(false) }

    val fetchExpertCases = {
        isLoading = true
        coroutineScope.launch(Dispatchers.IO) {
            try {
                val filterName = if (currentFarmerName.isNotBlank()) currentFarmerName.trim() else null
                val response = ApiClient.apiService.getCases(farmerName = filterName)
                if (response.isSuccessful && response.body() != null) {
                    val cases = response.body()!!.cases
                    withContext(Dispatchers.Main) {
                        casesList = cases
                        isLoading = false
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        isLoading = false
                    }
                }
            } catch (e: Throwable) {
                withContext(Dispatchers.Main) {
                    isLoading = false
                }
            }
        }
    }

    LaunchedEffect(currentFarmerName) {
        fetchExpertCases()
    }

    val headerTitle = when (selectedLanguage) {
        "mr" -> "🩺 तज्ज्ञ सल्ला (Expert Desk)"
        "hi" -> "🩺 विशेषज्ञ सलाह (Expert Desk)"
        else -> "🩺 Expert Desk & Prescriptions"
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = headerTitle,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            IconButton(onClick = { fetchExpertCases() }) {
                Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = MaterialTheme.colorScheme.primary)
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (casesList.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(bottom = 60.dp),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("👨‍⚕️", fontSize = 42.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = if (selectedLanguage == "mr") "कोणतीही तज्ज्ञ तपासणी नोंद नाही." else "No expert review cases found.",
                        color = Color.Gray,
                        fontSize = 15.sp
                    )
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(14.dp),
                contentPadding = PaddingValues(bottom = 80.dp)
            ) {
                items(casesList) { item ->
                    ExpertDeskCard(
                        item = item,
                        selectedLanguage = selectedLanguage
                    )
                }
            }
        }
    }
}

@Composable
fun ExpertDeskCard(
    item: ExpertDeskCaseDto,
    selectedLanguage: String
) {
    val isResolved = item.status.equals("Resolved", ignoreCase = true) || !item.expertResponse.isNullOrBlank()

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isResolved) Color(0xFFF0FDF4) else Color(0xFFFFFBEB)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "🌱 ${item.crop?.replaceFirstChar { it.uppercase() } ?: "Crop"}",
                    fontWeight = FontWeight.Bold,
                    fontSize = 17.sp,
                    color = Color(0xFF1F2937)
                )

                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = if (isResolved) Color(0xFFDCFCE7) else Color(0xFFFEF3C7)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 10.dp, vertical = 5.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = if (isResolved) Icons.Default.CheckCircle else Icons.Default.Info,
                            contentDescription = null,
                            tint = if (isResolved) Color(0xFF15803D) else Color(0xFFB45309),
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = if (isResolved) {
                                if (selectedLanguage == "mr") "तज्ज्ञांची शिफारस उपलब्ध" else "Prescription Ready"
                            } else {
                                if (selectedLanguage == "mr") "तपासणी प्रलंबित" else "Pending Review"
                            },
                            color = if (isResolved) Color(0xFF15803D) else Color(0xFFB45309),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Row(verticalAlignment = Alignment.CenterVertically) {
                if (!item.imageUrl.isNullOrBlank()) {
                    val formattedImgUrl = if (item.imageUrl.startsWith("http")) {
                        item.imageUrl
                    } else {
                        "http://192.168.137.1:8000/${item.imageUrl.removePrefix("/")}"
                    }
                    AsyncImage(
                        model = formattedImgUrl,
                        contentDescription = "Leaf Preview",
                        modifier = Modifier
                            .size(72.dp)
                            .clip(RoundedCornerShape(8.dp)),
                        contentScale = ContentScale.Crop
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                }

                Column {
                    Text(
                        text = "AI तपासणी: ${item.disease?.replace('_', ' ') ?: "N/A"}",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color.DarkGray
                    )
                    Text(
                        text = "शेतकरी: ${item.farmerName ?: "Farmer"} | ${item.district ?: ""}",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                    Text(
                        text = "ID: ${item.caseId}",
                        fontSize = 11.sp,
                        color = Color.LightGray
                    )
                }
            }

            if (isResolved) {
                HorizontalDivider(
                    modifier = Modifier.padding(vertical = 12.dp),
                    color = Color(0xFFBBF7D0)
                )

                Text(
                    text = "👨‍⚕️ तज्ज्ञांचे निदान व औषधोपचार (Expert Prescription):",
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp,
                    color = Color(0xFF166534)
                )
                Spacer(modifier = Modifier.height(4.dp))
                Surface(
                    shape = RoundedCornerShape(8.dp),
                    color = Color.White,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = item.expertResponse ?: "Apply recommended IPM sprays as directed.",
                        fontSize = 13.sp,
                        color = Color(0xFF1F2937),
                        modifier = Modifier.padding(10.dp),
                        lineHeight = 18.sp
                    )
                }
            }
        }
    }
}