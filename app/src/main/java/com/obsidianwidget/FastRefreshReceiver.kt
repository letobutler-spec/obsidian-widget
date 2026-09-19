package com.obsidianwidget

import android.app.AlarmManager
import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.SystemClock

/**
 * Keeps the home-screen widget close to real time without a foreground service.
 *
 * We use a non-wakeup exact alarm so the phone is NOT woken every few seconds.
 * While the device is awake, the next refresh is requested after 5 seconds.
 * If Android does not allow exact alarms, we gracefully fall back to a normal
 * alarm (which may be batched by the OS).
 */
class FastRefreshReceiver : android.content.BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            ACTION_FAST_REFRESH -> {
                if (hasWidgets(context)) {
                    ObsidianWidgetProvider.updateAllWidgets(context)
                    schedule(context)
                } else {
                    cancel(context)
                }
            }
            AppWidgetManager.ACTION_APPWIDGET_UPDATE,
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_MY_PACKAGE_REPLACED -> {
                if (hasWidgets(context)) schedule(context)
            }
        }
    }

    companion object {
        const val ACTION_FAST_REFRESH = "com.obsidianwidget.ACTION_FAST_REFRESH"
        private const val REQUEST_CODE = 2405
        private const val FAST_INTERVAL_MS = 5_000L

        fun schedule(context: Context) {
            if (!hasWidgets(context)) return

            val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            val triggerAt = SystemClock.elapsedRealtime() + FAST_INTERVAL_MS
            val pendingIntent = pendingIntent(context)

            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && !alarmManager.canScheduleExactAlarms()) {
                    alarmManager.set(
                        AlarmManager.ELAPSED_REALTIME,
                        triggerAt,
                        pendingIntent
                    )
                } else {
                    alarmManager.setExact(
                        AlarmManager.ELAPSED_REALTIME,
                        triggerAt,
                        pendingIntent
                    )
                }
            } catch (_: SecurityException) {
                alarmManager.set(
                    AlarmManager.ELAPSED_REALTIME,
                    triggerAt,
                    pendingIntent
                )
            }
        }

        fun cancel(context: Context) {
            val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
            alarmManager.cancel(pendingIntent(context))
        }

        private fun pendingIntent(context: Context): PendingIntent {
            val intent = Intent(context, FastRefreshReceiver::class.java).apply {
                action = ACTION_FAST_REFRESH
            }
            return PendingIntent.getBroadcast(
                context,
                REQUEST_CODE,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        }

        private fun hasWidgets(context: Context): Boolean {
            val manager = AppWidgetManager.getInstance(context)
            val ids = manager.getAppWidgetIds(
                ComponentName(context, ObsidianWidgetProvider::class.java)
            )
            return ids.isNotEmpty()
        }
    }
}
