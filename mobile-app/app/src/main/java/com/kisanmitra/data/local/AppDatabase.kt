package com.kisanmitra.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [CaseEntity::class], version = 2, exportSchema = false) // Increment version from 1 to 2 (or +1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun caseDao(): CaseDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "peekrakshak_db"
                )
                    .fallbackToDestructiveMigration() // Safely clears old table structure on version change
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}