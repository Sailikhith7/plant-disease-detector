package com.kisanmitra.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.kisanmitra.data.remote.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

object WeatherStrings {
    fun get(lang: String): Map<String, String> = when (lang) {
        "hi" -> mapOf(
            "title" to "🌤️ कृषि मौसम केंद्र",
            "spray_safe" to " छिड़काव के लिए अनुकूल",
            "spray_avoid" to "🚫 आज छिड़काव न करें",
            "humidity" to "आर्द्रता",
            "rain" to "बारिश",
            "wind" to "हवा",
            "outlook_5day" to "📅 अगले ५ दिनों का पूर्वानुमान",
            "risk_warning" to "🔴 रोग का संभावित खतरा",
            "weather_safe" to "🟢 फसल के लिए मौसम सुरक्षित",
            "lab_title" to "🧪 Demo Lab: मौसम परिवर्तन सिमुलेटर",
            "lab_desc" to "तापमान व आर्द्रता स्लाइडर बदलें और Live AI अलर्ट + Telegram देखें।",
            "temp_lbl" to "तापमान",
            "hum_lbl" to "हवा में आर्द्रता (Humidity)",
            "btn_test" to "⚡ Test Risk & Send Telegram Alert",
            "alert_sent" to "🚨 टेलीग्राम पर अलर्ट भेजा गया!"
        )
        "mr" -> mapOf(
            "title" to "🌤️ कृषी हवामान केंद्र",
            "spray_safe" to " फवारणी योग्य",
            "spray_avoid" to "🚫 आज फवारणी टाळा",
            "humidity" to "आर्द्रता",
            "rain" to "पाऊस",
            "wind" to "वारा",
            "outlook_5day" to "📅 पुढील ५ दिवसांचा अंदाज",
            "risk_warning" to "🔴 रोगाचा संभाव्य इशारा",
            "weather_safe" to "🟢 पिकासाठी हवामान सुरक्षित",
            "lab_title" to "🧪 Demo Lab: हवामान बदल चाचणी",
            "lab_desc" to "Slider फिरवून तापमान/आर्द्रता बदला आणि Live AI Alert + Telegram बघा.",
            "temp_lbl" to "तापमान",
            "hum_lbl" to "हवेतील आर्द्रता (Humidity)",
            "btn_test" to "⚡ Test Risk & Send Telegram Alert",
            "alert_sent" to "🚨 टेलिग्रामवर अलर्ट पाठवला!"
        )
        else -> mapOf(
            "title" to "🌤️ Agro-Weather Center",
            "spray_safe" to "Safe for Spraying",
            "spray_avoid" to "🚫 Avoid Spraying Today",
            "humidity" to "Humidity",
            "rain" to "Rain",
            "wind" to "Wind",
            "outlook_5day" to "📅 5-Day Weather Outlook",
            "risk_warning" to "🔴 Disease Outbreak Warning",
            "weather_safe" to "🟢 Weather Safe for Crops",
            "lab_title" to "🧪 Demo Lab: Weather Simulator",
            "lab_desc" to "Adjust sliders to test climate change impact & trigger Telegram alerts.",
            "temp_lbl" to "Temperature",
            "hum_lbl" to "Relative Humidity",
            "btn_test" to "⚡ Test Risk & Send Telegram Alert",
            "alert_sent" to "🚨 Alert Sent to Telegram!"
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WeatherScreen(
    selectedLanguage: String,
    selectedDistrict: String,
    selectedCrop: String
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val str = WeatherStrings.get(selectedLanguage)

    var dashboardData by remember { mutableStateOf<FullWeatherDashboardDto?>(null) }
    var isLoading by remember { mutableStateOf(true) }

    // Simulation Sliders State
    var simTemp by remember { mutableFloatStateOf(26f) }
    var simHumidity by remember { mutableFloatStateOf(85f) } // Default set to 85% for quick demo
    var simRain by remember { mutableFloatStateOf(60f) }
    var simResult by remember { mutableStateOf<SimulationResponseDto?>(null) }
    var isSimulating by remember { mutableStateOf(false) }

    fun fetchLive() {
        isLoading = true
        scope.launch(Dispatchers.IO) {
            try {
                val res = ApiClient.apiService.getFullWeatherDashboard(
                    crop = selectedCrop.ifBlank { "rice" },
                    district = selectedDistrict.ifBlank { "Dhule" },
                    language = selectedLanguage
                )
                if (res.isSuccessful) {
                    withContext(Dispatchers.Main) {
                        dashboardData = res.body()
                        isLoading = false
                    }
                }
            } catch (_: Exception) {
                withContext(Dispatchers.Main) { isLoading = false }
            }
        }
    }

    LaunchedEffect(selectedDistrict, selectedCrop, selectedLanguage) {
        fetchLive()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        // Top Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = str["title"] ?: "🌤️ Agro-Weather Center",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
                Text(
                    text = "$selectedDistrict | ${selectedCrop.replaceFirstChar { it.uppercase() }}",
                    fontSize = 13.sp,
                    color = Color.DarkGray
                )
            }
            IconButton(onClick = { fetchLive() }) {
                Icon(Icons.Default.Refresh, contentDescription = "Refresh")
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // 1. Current Live Weather Overview Card
        dashboardData?.weather?.let { w ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("🌡️ ${w.temperature}°C", fontSize = 28.sp, fontWeight = FontWeight.Bold)
                        Text(
                            text = if (w.spraySafe) (str["spray_safe"] ?: "✅ Safe") else (str["spray_avoid"] ?: "🚫 Avoid"),
                            fontWeight = FontWeight.Bold,
                            color = if (w.spraySafe) Color(0xFF2E7D32) else Color(0xFFC62828)
                        )
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("💧 ${str["humidity"]}: ${w.humidity}%", fontSize = 13.sp)
                        Text("🌧️ ${str["rain"]}: ${w.rainProb}%", fontSize = 13.sp)
                        Text("💨 ${str["wind"]}: ${w.windSpeed} km/h", fontSize = 13.sp)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 2. 5-Day Horizontal Forecast Cards
        Text(str["outlook_5day"] ?: "📅 5-Day Outlook", fontWeight = FontWeight.Bold, fontSize = 16.sp)
        Spacer(modifier = Modifier.height(8.dp))

        LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            val list = dashboardData?.weather?.forecast5days ?: emptyList()
            items(list) { day ->
                Card(
                    modifier = Modifier.width(105.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(
                        modifier = Modifier.padding(10.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(day.date.takeLast(5), fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        Text("⛅", fontSize = 20.sp)
                        Text("${day.maxTemp.toInt()}° / ${day.minTemp.toInt()}°", fontSize = 12.sp)
                        Text("🌧️ ${day.rainProb.toInt()}%", fontSize = 11.sp, color = Color.Gray)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // 3. Outbreak Advisory Card
        val risk = dashboardData?.riskAssessment
        val isOutbreak = risk?.isOutbreakRisk == true
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (isOutbreak) Color(0xFFFFEBEE) else Color(0xFFE8F5E9)
            )
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text(
                    text = if (isOutbreak) "${str["risk_warning"]} (${risk?.riskPercentage}%)" else (str["weather_safe"] ?: "🟢 Safe"),
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = if (isOutbreak) Color(0xFFC62828) else Color(0xFF2E7D32)
                )
                if (isOutbreak && !risk?.potentialDisease.isNullOrBlank()) {
                    Text(
                        text = "Disease: ${risk?.potentialDisease}",
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(text = risk?.preventiveAdvisory ?: "", fontSize = 13.sp, color = Color.DarkGray)
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 4. SIH LIVE SIMULATION & TELEGRAM TEST LAB
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFFF3E5F5))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = str["lab_title"] ?: "🧪 SIH Demo Lab",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = Color(0xFF6A1B9A)
                )
                Text(
                    text = str["lab_desc"] ?: "Adjust sliders to test climate change impact.",
                    fontSize = 12.sp,
                    color = Color.DarkGray
                )

                Spacer(modifier = Modifier.height(12.dp))

                Text("${str["temp_lbl"]}: ${simTemp.toInt()}°C", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                Slider(
                    value = simTemp,
                    onValueChange = { simTemp = it },
                    valueRange = 15f..45f
                )

                Text("${str["hum_lbl"]}: ${simHumidity.toInt()}%", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                Slider(
                    value = simHumidity,
                    onValueChange = { simHumidity = it },
                    valueRange = 30f..100f
                )

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = {
                        isSimulating = true
                        scope.launch(Dispatchers.IO) {
                            try {
                                val res = ApiClient.apiService.simulateWeatherRisk(
                                    SimulationRequestDto(
                                        crop = selectedCrop,
                                        district = selectedDistrict,
                                        temperature = simTemp,
                                        humidity = simHumidity,
                                        rainProb = simRain,
                                        language = selectedLanguage,
                                        triggerTelegram = true
                                    )
                                )
                                if (res.isSuccessful) {
                                    withContext(Dispatchers.Main) {
                                        simResult = res.body()
                                        isSimulating = false
                                        Toast.makeText(
                                            context,
                                            if (simResult?.telegramDispatched == true) (str["alert_sent"] ?: "Alert Dispatched") else "Assessment Updated",
                                            Toast.LENGTH_SHORT
                                        ).show()
                                    }
                                }
                            } catch (_: Exception) {
                                withContext(Dispatchers.Main) { isSimulating = false }
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF7B1FA2))
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Simulate")
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(str["btn_test"] ?: "⚡ Test Risk & Send Telegram Alert")
                }

                simResult?.let { s ->
                    Spacer(modifier = Modifier.height(10.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                if (s.isOutbreakRisk) Color(0xFFFFCDD2) else Color(0xFFC8E6C9),
                                RoundedCornerShape(8.dp)
                            )
                            .padding(10.dp)
                    ) {
                        Column {
                            Text(
                                text = if (s.isOutbreakRisk) "🚨 ${s.potentialDisease} (${s.riskPercentage}% ${str["humidity"] ?: "Risk"})" else "✅ ${str["weather_safe"]} (${s.riskPercentage}%)",
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp,
                                color = if (s.isOutbreakRisk) Color(0xFFB71C1C) else Color(0xFF2E7D32)
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(text = s.advisory, fontSize = 12.sp)
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(80.dp))
    }
}

