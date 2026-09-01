package com.kisanmitra.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Refresh
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
import java.util.Locale

data class MahaDistrict(
    val nameEn: String,
    val nameHi: String,
    val nameMr: String,
    val lat: Float,
    val lon: Float
)

private val MAHARASHTRA_36_DISTRICTS = listOf(
    MahaDistrict("Ahilyanagar (Ahmednagar)", "अहिल्यानगर (अहमदनगर)", "अहिल्यानगर (अहमदनगर)", 19.0952f, 74.7496f),
    MahaDistrict("Akola", "अकोला", "अकोला", 20.7002f, 77.0082f),
    MahaDistrict("Amravati", "अमरावती", "अमरावती", 20.9374f, 77.7796f),
    MahaDistrict("Beed", "बीड", "बीड", 18.9891f, 75.7601f),
    MahaDistrict("Bhandara", "भंडारा", "भंडारा", 21.1714f, 79.6547f),
    MahaDistrict("Buldhana", "बुलढाणा", "बुलढाणा", 20.5293f, 76.1843f),
    MahaDistrict("Chandrapur", "चंद्रपुर", "चंद्रपूर", 19.9615f, 79.2961f),
    MahaDistrict("Chhatrapati Sambhajinagar", "छत्रपति संभाजीनगर", "छत्रपती संभाजीनगर", 19.8762f, 75.3433f),
    MahaDistrict("Dharashiv (Osmanabad)", "धाराशिव (उस्मानाबाद)", "धाराशिव (उस्मानाबाद)", 18.1856f, 76.0416f),
    MahaDistrict("Dhule", "धुले", "धुळे", 20.9042f, 74.7749f),
    MahaDistrict("Gadchiroli", "गडचिरोली", "गडचिरोली", 20.1849f, 79.9948f),
    MahaDistrict("Gondia", "गोंदिया", "गोंदिया", 21.4554f, 80.1961f),
    MahaDistrict("Hingoli", "हिंगोली", "हिंगोली", 19.7196f, 77.1477f),
    MahaDistrict("Jalgaon", "जलगांव", "जळगाव", 21.0077f, 75.5626f),
    MahaDistrict("Jalna", "जालना", "जालना", 19.8410f, 75.8864f),
    MahaDistrict("Kolhapur", "कोल्हापुर", "कोल्हापूर", 16.7050f, 74.2433f),
    MahaDistrict("Latur", "लातूर", "लातूर", 18.4088f, 76.5604f),
    MahaDistrict("Mumbai City", "मुंबई शहर", "मुंबई शहर", 18.9388f, 72.8354f),
    MahaDistrict("Mumbai Suburban", "मुंबई उपनगर", "मुंबई उपनगर", 19.0760f, 72.8777f),
    MahaDistrict("Nagpur", "नागपुर", "नागपूर", 21.1458f, 79.0882f),
    MahaDistrict("Nanded", "नांदेड़", "नांदेड", 19.1383f, 77.3210f),
    MahaDistrict("Nandurbar", "नंदुरबार", "नंदुरबार", 21.3700f, 74.2400f),
    MahaDistrict("Nashik", "नासिक", "नाशिक", 19.9975f, 73.7898f),
    MahaDistrict("Palghar", "पालघर", "पालघर", 19.6967f, 72.7655f),
    MahaDistrict("Parbhani", "परभणी", "परभणी", 19.2686f, 76.7708f),
    MahaDistrict("Pune", "पुणे", "पुणे", 18.5204f, 73.8567f),
    MahaDistrict("Raigad", "रायगढ़", "रायगड", 18.5158f, 73.1812f),
    MahaDistrict("Ratnagiri", "रत्नागिरी", "रत्नागिरी", 16.9902f, 73.3120f),
    MahaDistrict("Sangli", "सांगली", "सांगली", 16.8524f, 74.5815f),
    MahaDistrict("Satara", "सातारा", "सातारा", 17.6805f, 73.9936f),
    MahaDistrict("Sindhudurg", "सिंधुदुर्ग", "सिंधुदुर्ग", 16.1216f, 73.6934f),
    MahaDistrict("Solapur", "सोलापुर", "सोलापूर", 17.6599f, 75.9064f),
    MahaDistrict("Thane", "ठाणे", "ठाणे", 19.2183f, 72.9781f),
    MahaDistrict("Wardha", "वर्धा", "वर्धा", 20.7453f, 78.6022f),
    MahaDistrict("Washim", "वाशिम", "वाशिम", 20.1110f, 77.1340f),
    MahaDistrict("Yavatmal", "यवतमाल", "यवतमाळ", 20.3888f, 78.1204f)
)

private val WEATHER_CROPS = listOf(
    "cotton" to "कापूस (Cotton)",
    "rice" to "भात (Rice)",
    "groundnut" to "भुईमूग (Groundnut)",
    "ragi" to "नाचणी (Ragi)",
    "sugarcane" to "ऊस (Sugarcane)"
)

object WeatherStrings {
    fun get(lang: String): Map<String, String> = when (lang) {
        "hi" -> mapOf(
            "title" to "🌤️ कृषि मौसम व फसल अनुकूलता केंद्र",
            "spray_safe" to "✅ छिड़काव के लिए अनुकूल",
            "spray_avoid" to "🚫 आज छिड़काव न करें",
            "humidity" to "आर्द्रता",
            "rain" to "बारिश",
            "wind" to "हवा",
            "outlook_5day" to "📅 अगले ५ दिनों का पूर्वानुमान",
            "crop_suitability_header" to "🌾 फसलों के लिए मौसम अनुकूलता (Suitability & Warnings)",
            "status_optimal" to "🟢 सुरक्षित व रोगमुक्त",
            "status_moderate" to "🟡 मध्यम जोखिम (निगरानी रखें)",
            "status_high_risk" to "🔴 उच्च बीमारी का खतरा (Outbreak Risk)",
            "other_district_title" to "📍 महाराष्ट्र के अन्य जिले का मौसम जांचें",
            "select_district_prompt" to "महाराष्ट्र का जिला चुनें",
            "btn_reset_gps" to "🔄 वापस मेरी GPS लोकेशन पर जाएं",
            "lab_title" to "🧪 Demo Lab: मौसम परिवर्तन सिमुलेटर",
            "lab_desc" to "तापमान व आर्द्रता स्लाइडर बदलें और Live AI अलर्ट देखें।",
            "temp_lbl" to "तापमान",
            "hum_lbl" to "हवा में आर्द्रता (Humidity)",
            "btn_test" to "⚡ Test Weather Impact"
        )
        "mr" -> mapOf(
            "title" to "🌤️ कृषी हवामान व पीक अनुकूलता केंद्र",
            "spray_safe" to "✅ फवारणी योग्य",
            "spray_avoid" to "🚫 आज फवारणी टाळा",
            "humidity" to "आर्द्रता",
            "rain" to "पाऊस",
            "wind" to "वारा",
            "outlook_5day" to "📅 पुढील ५ दिवसांचा अंदाज",
            "crop_suitability_header" to "🌾 पिकांसाठी हवामान अनुकूलता (Suitability & Warnings)",
            "status_optimal" to "🟢 सुरक्षित व रोगमुक्त",
            "status_moderate" to "🟡 मध्यम धोका (काळजी घ्या)",
            "status_high_risk" to "🔴 उच्च रोगाचा धोका (Outbreak Risk)",
            "other_district_title" to "📍 महाराष्ट्रातील इतर जिल्ह्याचे हवामान तपासा",
            "select_district_prompt" to "महाराष्ट्रातील जिल्हा निवडा",
            "btn_reset_gps" to "🔄 परत माझ्या GPS लोकेशनवर जा",
            "lab_title" to "🧪 Demo Lab: हवामान बदल चाचणी",
            "lab_desc" to "Slider फिरवून तापमान/आर्द्रता बदला आणि Live AI Alert बघा.",
            "temp_lbl" to "तापमान",
            "hum_lbl" to "हवेतील आर्द्रता (Humidity)",
            "btn_test" to "⚡ Test Weather Impact"
        )
        else -> mapOf(
            "title" to "🌤️ Agro-Weather & Crop Suitability Center",
            "spray_safe" to "✅ Safe for Spraying",
            "spray_avoid" to "🚫 Avoid Spraying",
            "humidity" to "Humidity",
            "rain" to "Rain Chance",
            "wind" to "Wind Speed",
            "outlook_5day" to "📅 5-Day Weather Outlook",
            "crop_suitability_header" to "🌾 Crop Weather Suitability & Warnings",
            "status_optimal" to "🟢 Highly Favorable / Safe",
            "status_moderate" to "🟡 Moderate Risk (Monitoring Advised)",
            "status_high_risk" to "🔴 High Outbreak Risk",
            "other_district_title" to "📍 Check Weather for Other Maharashtra Districts",
            "select_district_prompt" to "Select Maharashtra District",
            "btn_reset_gps" to "🔄 Reset to My Live GPS Location",
            "lab_title" to "🧪 Demo Lab: Climate Change Simulator",
            "lab_desc" to "Adjust sliders to test climate change impact on crops.",
            "temp_lbl" to "Temperature",
            "hum_lbl" to "Relative Humidity",
            "btn_test" to "⚡ Test Weather Impact"
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WeatherScreen(
    selectedLanguage: String,
    selectedDistrict: String,
    selectedCrop: String,
    latitude: Float = 16.49f,
    longitude: Float = 80.50f
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val str = WeatherStrings.get(selectedLanguage)

    var currentActiveCrop by remember { mutableStateOf(selectedCrop.ifBlank { "cotton" }) }
    var currentDistrictName by remember { mutableStateOf(selectedDistrict) }
    var currentLat by remember { mutableFloatStateOf(latitude) }
    var currentLon by remember { mutableFloatStateOf(longitude) }
    var isManualSelection by remember { mutableStateOf(false) }

    var isDistrictDropdownExpanded by remember { mutableStateOf(false) }

    var suitabilityData by remember { mutableStateOf<CropsSuitabilityResponseDto?>(null) }
    var dashboardData by remember { mutableStateOf<FullWeatherDashboardDto?>(null) }
    var isLoading by remember { mutableStateOf(true) }

    var simTemp by remember { mutableFloatStateOf(26f) }
    var simHumidity by remember { mutableFloatStateOf(85f) }
    var simRain by remember { mutableFloatStateOf(60f) }
    var simResult by remember { mutableStateOf<SimulationResponseDto?>(null) }
    var isSimulating by remember { mutableStateOf(false) }

    fun fetchSuitabilityAndWeather() {
        isLoading = true
        scope.launch(Dispatchers.IO) {
            try {
                val suitabilityRes = ApiClient.apiService.getCropsSuitability(
                    lat = currentLat,
                    lon = currentLon,
                    district = currentDistrictName,
                    language = selectedLanguage
                )
                val fullRes = ApiClient.apiService.getFullWeatherDashboard(
                    crop = currentActiveCrop,
                    district = currentDistrictName,
                    lat = currentLat,
                    lon = currentLon,
                    language = selectedLanguage
                )

                withContext(Dispatchers.Main) {
                    if (suitabilityRes.isSuccessful) suitabilityData = suitabilityRes.body()
                    if (fullRes.isSuccessful) dashboardData = fullRes.body()
                    isLoading = false
                }
            } catch (_: Exception) {
                withContext(Dispatchers.Main) { isLoading = false }
            }
        }
    }

    LaunchedEffect(currentDistrictName, currentActiveCrop, selectedLanguage, currentLat, currentLon) {
        fetchSuitabilityAndWeather()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        // Top Location Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = str["title"] ?: "🌤️ Agro-Weather Center",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = "Location",
                        tint = Color(0xFF2E7D32),
                        modifier = Modifier.size(15.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "$currentDistrictName (${String.format(Locale.US, "%.2f", currentLat)}°N, ${String.format(Locale.US, "%.2f", currentLon)}°E)",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.DarkGray
                    )
                }
            }

            IconButton(onClick = { fetchSuitabilityAndWeather() }) {
                Icon(Icons.Default.Refresh, contentDescription = "Refresh")
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // 1. Live Weather Overview Card (Structured Layout with Fixed Grid Columns)
        val weatherObj = dashboardData?.weather ?: suitabilityData?.weather
        weatherObj?.let { w ->
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
                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = if (w.spraySafe) Color(0xFFDCFCE7) else Color(0xFFFFE4E6)
                        ) {
                            Text(
                                text = if (w.spraySafe) (str["spray_safe"] ?: "✅ Safe") else (str["spray_avoid"] ?: "🚫 Avoid"),
                                fontWeight = FontWeight.Bold,
                                color = if (w.spraySafe) Color(0xFF15803D) else Color(0xFFBE123C),
                                modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                                fontSize = 12.sp
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Surface(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.7f)
                        ) {
                            Column(
                                modifier = Modifier.padding(vertical = 8.dp, horizontal = 4.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text("💧 ${str["humidity"]}", fontSize = 11.sp, color = Color.DarkGray)
                                Spacer(modifier = Modifier.height(2.dp))
                                Text("${w.humidity.toInt()}%", fontSize = 14.sp, fontWeight = FontWeight.Bold)
                            }
                        }

                        Surface(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.7f)
                        ) {
                            Column(
                                modifier = Modifier.padding(vertical = 8.dp, horizontal = 4.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text("🌧️ ${str["rain"]}", fontSize = 11.sp, color = Color.DarkGray)
                                Spacer(modifier = Modifier.height(2.dp))
                                Text("${w.rainProb.toInt()}%", fontSize = 14.sp, fontWeight = FontWeight.Bold)
                            }
                        }

                        Surface(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            color = MaterialTheme.colorScheme.surface.copy(alpha = 0.7f)
                        ) {
                            Column(
                                modifier = Modifier.padding(vertical = 8.dp, horizontal = 4.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text("💨 ${str["wind"]}", fontSize = 11.sp, color = Color.DarkGray)
                                Spacer(modifier = Modifier.height(2.dp))
                                Text("${String.format(Locale.US, "%.1f", w.windSpeed)} km/h", fontSize = 13.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(18.dp))

        // 2. Crop Weather Suitability Selector
        Text(
            text = str["crop_suitability_header"] ?: "🌾 Crop Weather Suitability & Warnings",
            fontWeight = FontWeight.Bold,
            fontSize = 15.sp,
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(8.dp))

        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items(WEATHER_CROPS) { (cropKey, cropName) ->
                val cropInfo = suitabilityData?.crops?.get(cropKey)
                val riskVal = cropInfo?.riskPercentage ?: 20
                val status = cropInfo?.status ?: "OPTIMAL"

                val chipColor = when (status) {
                    "HIGH_RISK" -> Color(0xFFFEE2E2)
                    "MODERATE" -> Color(0xFFFEF3C7)
                    else -> Color(0xFFDCFCE7)
                }
                val textColor = when (status) {
                    "HIGH_RISK" -> Color(0xFF991B1B)
                    "MODERATE" -> Color(0xFF92400E)
                    else -> Color(0xFF166534)
                }

                FilterChip(
                    selected = currentActiveCrop == cropKey,
                    onClick = { currentActiveCrop = cropKey },
                    label = {
                        Column(modifier = Modifier.padding(vertical = 4.dp)) {
                            Text(cropName, fontSize = 13.sp, fontWeight = FontWeight.Bold)
                            Text(
                                text = when (status) {
                                    "HIGH_RISK" -> "🔴 Risk ($riskVal%)"
                                    "MODERATE" -> "🟡 Moderate ($riskVal%)"
                                    else -> "🟢 Safe ($riskVal%)"
                                },
                                fontSize = 11.sp,
                                color = textColor,
                                fontWeight = FontWeight.SemiBold
                            )
                        }
                    },
                    colors = FilterChipDefaults.filterChipColors(selectedContainerColor = chipColor)
                )
            }
        }

        Spacer(modifier = Modifier.height(14.dp))

        // 3. Dynamic Crop Warning Detail Card
        val selectedCropInfo = suitabilityData?.crops?.get(currentActiveCrop)
        val selectedRiskVal = selectedCropInfo?.riskPercentage ?: 20
        val currentStatus = selectedCropInfo?.status ?: "OPTIMAL"
        val isOutbreak = currentStatus == "HIGH_RISK"
        val isModerate = currentStatus == "MODERATE"

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp),
            colors = CardDefaults.cardColors(
                containerColor = when {
                    isOutbreak -> Color(0xFFFFEBEE)
                    isModerate -> Color(0xFFFFFBEB)
                    else -> Color(0xFFE8F5E9)
                }
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "🌾 ${currentActiveCrop.replaceFirstChar { it.uppercase() }}",
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp
                    )
                    Text(
                        text = when {
                            isOutbreak -> "${str["status_high_risk"]} ($selectedRiskVal%)"
                            isModerate -> "${str["status_moderate"]} ($selectedRiskVal%)"
                            else -> "${str["status_optimal"]} ($selectedRiskVal%)"
                        },
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp,
                        color = when {
                            isOutbreak -> Color(0xFFC62828)
                            isModerate -> Color(0xFFB45309)
                            else -> Color(0xFF2E7D32)
                        }
                    )
                }

                if (!selectedCropInfo?.potentialDisease.isNullOrBlank()) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "⚠️ रोग / कीड: ${selectedCropInfo?.potentialDisease}",
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                        color = if (isOutbreak) Color(0xFFB71C1C) else Color(0xFF92400E)
                    )
                }

                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = selectedCropInfo?.advisory ?: (dashboardData?.riskAssessment?.preventiveAdvisory ?: "Weather is currently optimal."),
                    fontSize = 13.sp,
                    color = Color.DarkGray,
                    lineHeight = 18.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(18.dp))

        // 4. 5-Day Horizontal Forecast Cards
        Text(str["outlook_5day"] ?: "📅 5-Day Forecast", fontWeight = FontWeight.Bold, fontSize = 15.sp)
        Spacer(modifier = Modifier.height(8.dp))

        val forecastList = (dashboardData?.weather?.forecast5days ?: suitabilityData?.weather?.forecast5days) ?: emptyList()
        LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            items(forecastList) { day ->
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

        Spacer(modifier = Modifier.height(22.dp))

        // 5. MAHARASHTRA DISTRICT SELECTOR CARD
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(14.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFFE8EAF6)),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = str["other_district_title"] ?: "📍 Check Other Maharashtra District",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = Color(0xFF283593)
                )
                Spacer(modifier = Modifier.height(8.dp))

                ExposedDropdownMenuBox(
                    expanded = isDistrictDropdownExpanded,
                    onExpandedChange = { isDistrictDropdownExpanded = !isDistrictDropdownExpanded },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    OutlinedTextField(
                        value = if (isManualSelection) currentDistrictName else (str["select_district_prompt"] ?: "Select Maharashtra District"),
                        onValueChange = {},
                        readOnly = true,
                        trailingIcon = { Icon(Icons.Default.ArrowDropDown, contentDescription = null) },
                        modifier = Modifier.menuAnchor().fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Color.White,
                            unfocusedContainerColor = Color.White
                        )
                    )

                    ExposedDropdownMenu(
                        expanded = isDistrictDropdownExpanded,
                        onDismissRequest = { isDistrictDropdownExpanded = false }
                    ) {
                        MAHARASHTRA_36_DISTRICTS.forEach { d ->
                            val label = when (selectedLanguage) {
                                "hi" -> d.nameHi
                                "mr" -> d.nameMr
                                else -> d.nameEn
                            }
                            DropdownMenuItem(
                                text = { Text(label, fontSize = 14.sp) },
                                onClick = {
                                    currentDistrictName = d.nameEn
                                    currentLat = d.lat
                                    currentLon = d.lon
                                    isManualSelection = true
                                    isDistrictDropdownExpanded = false
                                }
                            )
                        }
                    }
                }

                if (isManualSelection) {
                    Spacer(modifier = Modifier.height(10.dp))
                    TextButton(
                        onClick = {
                            currentDistrictName = selectedDistrict
                            currentLat = latitude
                            currentLon = longitude
                            isManualSelection = false
                        },
                        modifier = Modifier.align(Alignment.End)
                    ) {
                        Text(str["btn_reset_gps"] ?: "Reset to GPS Location", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 6. DEMO LAB
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
                    text = str["lab_desc"] ?: "Adjust sliders to test climate change impact on crops.",
                    fontSize = 12.sp,
                    color = Color.DarkGray
                )

                Spacer(modifier = Modifier.height(12.dp))

                Text("${str["temp_lbl"]}: ${simTemp.toInt()}°C", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                Slider(value = simTemp, onValueChange = { simTemp = it }, valueRange = 15f..45f)

                Text("${str["hum_lbl"]}: ${simHumidity.toInt()}%", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                Slider(value = simHumidity, onValueChange = { simHumidity = it }, valueRange = 30f..100f)

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = {
                        isSimulating = true
                        scope.launch(Dispatchers.IO) {
                            try {
                                val res = ApiClient.apiService.simulateWeatherRisk(
                                    SimulationRequestDto(
                                        crop = currentActiveCrop,
                                        district = currentDistrictName,
                                        temperature = simTemp,
                                        humidity = simHumidity,
                                        rainProb = simRain,
                                        language = selectedLanguage,
                                        triggerTelegram = false
                                    )
                                )
                                if (res.isSuccessful) {
                                    withContext(Dispatchers.Main) {
                                        simResult = res.body()
                                        isSimulating = false
                                        Toast.makeText(context, "Assessment Updated", Toast.LENGTH_SHORT).show()
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
                    Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Simulate")
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(str["btn_test"] ?: "⚡ Test Weather Impact")
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
                                text = if (s.isOutbreakRisk) "🚨 ${s.potentialDisease} (${s.riskPercentage}% Outbreak Risk)" else "✅ Safe (${s.riskPercentage}%)",
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