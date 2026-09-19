package com.obsidianwidget

import android.app.Application
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build

class ObsidianWidgetApp : Application() {

    private val screenUnlockReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == Intent.ACTION_USER_PRESENT || intent.action == Intent.ACTION_SCREEN_ON) {
                ObsidianWidgetProvider.updateAllWidgets(context)
                FastRefreshReceiver.schedule(context)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()

        // Start/restart the five-second refresh chain whenever this process is alive.
        FastRefreshReceiver.schedule(this)

        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_USER_PRESENT)
            addAction(Intent.ACTION_SCREEN_ON)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(screenUnlockReceiver, filter, Context.RECEIVER_EXPORTED)
        } else {
            registerReceiver(screenUnlockReceiver, filter)
        }
    }
}
