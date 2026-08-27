package com.kisanmitra.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class CropGuide(
    val cropName: String,
    val keyPests: String,
    val criticalStage: String,
    val preventiveTip: String
)

@Composable
fun GuidelinesScreen(selectedLanguage: String = "en") {
    val guides = remember(selectedLanguage) {
        when (selectedLanguage) {
            "hi" -> listOf(
                CropGuide("कपास (Cotton)", "गुलाबी सुंडी, सफेद मक्खी", "फूल और बोंड बनने का समय", "प्रति हेक्टेयर 5 फेरोमोन ट्रैप लगाएं और अत्यधिक यूरिया से बचें।"),
                CropGuide("सोयाबीन (Soybean)", "तंबाकू इल्ली, तना मक्खी", "अंकुरण और फली विकास", "ट्राइकोडर्मा से बीज उपचार करें और नीम तेल (1500 ppm) का छिड़काव करें।"),
                CropGuide("प्याज (Onion)", "थ्रिप्स, बैंगनी धब्बा", "कंद विकास अवस्था", "पीले चिपचिपे ट्रैप का उपयोग करें और खेत में उचित जल निकासी बनाए रखें।"),
                CropGuide("गन्ना (Sugarcane)", "शीर्ष तना छेदक, लाल सड़न", "टिलरिंग और ग्रैंड ग्रोथ", "स्वस्थ बीज सेट का चयन करें और ट्राइकोग्रामा परजीवी छोड़ें।")
            )
            "mr" -> listOf(
                CropGuide("कापूस (Cotton)", "गुलाबी बोंडअळी, पांढरी माशी", "फुलोरा व बोंडे धरण्याची वेळ", "हेक्टरी ५ कामगंध सापळे लावा आणि अतिरिक्त युरियाचा वापर टाळा."),
                CropGuide("सोयाबीन (Soybean)", "लष्करी अळी, खोड माशी", "उगवण व शेंगा भरणे", "ट्रायकोडर्माने बीजप्रक्रिया करा आणि निंबोळी अर्क (१५०० ppm) फवारा."),
                CropGuide("कांदा (Onion)", "फुलकिडे (थ्रिप्स), करपा", "कांदा फुगवणीचा काळ", "पिवळे चिकट सापळे वापरा आणि शेतात पाण्याचा योग्य निचरा ठेवा."),
                CropGuide("ऊस (Sugarcane)", "खोड कीड, तांबेरा / लाल कुज", "फुटवे व वाढीची अवस्था", "निरोगी बेणे वापरा आणि ट्रायकोकार्डचा नियमित वापर करा.")
            )
            else -> listOf(
                CropGuide("Cotton", "Pink Bollworm, Whitefly", "Flowering & Boll Formation", "Install 5 pheromone traps/ha; avoid excessive chemical nitrogen application."),
                CropGuide("Soybean", "Spodoptera / Leaf Miner, Stem Fly", "Seedling & Pod Development", "Treat seeds with Trichoderma viride; spray neem seed kernel extract (1500 ppm)."),
                CropGuide("Onion", "Thrips, Purple Blotch", "Bulb Enlargement Stage", "Deploy yellow sticky cards; ensure soil drainage to avoid fungal collar rot."),
                CropGuide("Sugarcane", "Early Shoot Borer, Red Rot", "Tillering & Rapid Growth", "Use disease-free setts; release Trichogramma chilonis egg parasitoids periodically.")
            )
        }
    }

    val headerTitle = when (selectedLanguage) {
        "hi" -> "📚 ऑफलाइन फसल सुरक्षा दिशानिर्देश"
        "mr" -> "📚 ऑफलाइन पीक संरक्षण मार्गदर्शक"
        else -> "📚 Offline Crop Protection Guidelines"
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = headerTitle,
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
                        Text("⚠️ Key Targets: ${item.keyPests}", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                        Text("⏳ Vulnerable Phase: ${item.criticalStage}", fontSize = 13.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("🛡️ Prevention: ${item.preventiveTip}", fontSize = 13.sp, color = MaterialTheme.colorScheme.primary)
                    }
                }
            }
        }
    }
}