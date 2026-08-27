package com.kisanmitra.ui.screens

import androidx.compose.runtime.Composable

@Composable
fun HistoryScreen(selectedLanguage: String = "en") {
    HistoryTabContent(selectedLanguage = selectedLanguage)
}