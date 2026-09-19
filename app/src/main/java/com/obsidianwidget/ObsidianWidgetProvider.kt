package com.obsidianwidget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.provider.DocumentsContract
import android.view.View
import android.widget.RemoteViews
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

class ObsidianWidgetProvider : AppWidgetProvider() {

    companion object {
        private const val ACTION_REFRESH = "com.obsidianwidget.ACTION_REFRESH"
        private const val ACTION_CAPTURE = "com.obsidianwidget.ACTION_CAPTURE"
        private const val ACTION_OPEN = "com.obsidianwidget.ACTION_OPEN"
        private const val ACTION_TOGGLE = "com.obsidianwidget.ACTION_TOGGLE"
        private const val ACTION_ADD = "com.obsidianwidget.ACTION_ADD"
        private const val ACTION_NAV_LEFT = "com.obsidianwidget.ACTION_NAV_LEFT"
        private const val ACTION_NAV_RIGHT = "com.obsidianwidget.ACTION_NAV_RIGHT"
        const val EXTRA_LINE_INDEX = "extra_line_index"
        const val EXTRA_APPEND_TO_WIDGET = "extra_append_to_widget"
        const val EXTRA_WIDGET_ID = "extra_widget_id"
        const val EXTRA_URL = "extra_url"

        fun updateAllWidgets(context: Context) {
            val intent = Intent(context, ObsidianWidgetProvider::class.java).apply {
                action = AppWidgetManager.ACTION_APPWIDGET_UPDATE
            }
            val appWidgetManager = AppWidgetManager.getInstance(context)
            val widgetIds = appWidgetManager.getAppWidgetIds(
                ComponentName(context, ObsidianWidgetProvider::class.java)
            )
            intent.putExtra(AppWidgetManager.EXTRA_APPWIDGET_IDS, widgetIds)
            context.sendBroadcast(intent)
        }
    }

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (appWidgetId in appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    override fun onDeleted(context: Context, appWidgetIds: IntArray) {
        for (id in appWidgetIds) VaultManager.deleteWidgetPrefs(context, id)
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        when (intent.action) {
            ACTION_REFRESH -> updateAllWidgets(context)
            ACTION_CAPTURE -> {
                val widgetId = intent.getIntExtra(EXTRA_WIDGET_ID, -1)
                context.startActivity(Intent(context, QuickCaptureActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                    putExtra(EXTRA_WIDGET_ID, widgetId)
                })
            }
            ACTION_ADD -> {
                val widgetId = intent.getIntExtra(EXTRA_WIDGET_ID, -1)
                context.startActivity(Intent(context, QuickCaptureActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                    putExtra(EXTRA_APPEND_TO_WIDGET, true)
                    putExtra(EXTRA_WIDGET_ID, widgetId)
                })
            }
            ACTION_OPEN -> {
                val widgetId = intent.getIntExtra(EXTRA_WIDGET_ID, -1)
                openObsidian(context, widgetId)
            }
            ACTION_TOGGLE -> {
                val url = intent.getStringExtra(EXTRA_URL)
                if (!url.isNullOrEmpty()) {
                    try {
                        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK
                        })
                    } catch (_: Exception) { }
                    return
                }
                val lineIndex = intent.getIntExtra(EXTRA_LINE_INDEX, -1)
                val widgetId = intent.getIntExtra(EXTRA_WIDGET_ID, -1)
                if (lineIndex >= 0 && widgetId >= 0) {
                    val vaultManager = VaultManager(context, widgetId)
                    vaultManager.toggleChecklistItem(lineIndex)
                    updateWidget(context, AppWidgetManager.getInstance(context), widgetId)
                }
            }
            ACTION_NAV_LEFT, ACTION_NAV_RIGHT -> {
                val widgetId = intent.getIntExtra(EXTRA_WIDGET_ID, -1)
                if (widgetId >= 0) {
                    val vaultManager = VaultManager(context, widgetId)
                    vaultManager.navigateNote(if (intent.action == ACTION_NAV_LEFT) -1 else 1)
                    updateWidget(context, AppWidgetManager.getInstance(context), widgetId)
                }
            }
        }
    }

    private fun updateWidget(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int
    ) {
        val views = RemoteViews(context.packageName, R.layout.widget_layout)
        val vaultManager = VaultManager(context, appWidgetId)

        val today = LocalDate.now()
        val prettyDate = today.format(DateTimeFormatter.ofPattern("EEEE d MMMM", Locale.ENGLISH))
        views.setTextViewText(R.id.widget_date, "TODAY · $prettyDate")
        views.setTextColor(R.id.widget_date, Color.rgb(17, 17, 17))

        val allItems = vaultManager.parseChecklist()
        val agendaItems = allItems.filter { item ->
            !item.isHeading && (!item.isPlainText || item.isBullet)
        }
        val hasAgenda = agendaItems.isNotEmpty()

        if (vaultManager.showTodoCount && agendaItems.any { !it.isPlainText }) {
            val unchecked = agendaItems.count { !it.isPlainText && !it.isChecked }
            val total = agendaItems.count { !it.isPlainText }
            views.setTextViewText(R.id.widget_todo_count, "$unchecked of $total remaining")
            views.setViewVisibility(R.id.widget_todo_count, View.VISIBLE)
        } else {
            views.setViewVisibility(R.id.widget_todo_count, View.GONE)
        }

        // Reading + Bento are read directly from .obsidian/plugins/reading-year-pixels/data.json.
        val pixels = PixelDataReader.readToday(context, vaultManager.vaultUri)
        if (!pixels.bookText.isNullOrBlank()) {
            views.setTextViewText(R.id.widget_book_pixel, pixels.bookText.uppercase(Locale.getDefault()))
            views.setViewVisibility(R.id.widget_book_pixel, View.VISIBLE)
            tintBand(
                views,
                R.id.widget_book_pixel,
                PixelDataReader.translucent(pixels.bookColor, Color.rgb(167, 218, 213), 82)
            )
            views.setOnClickPendingIntent(
                R.id.widget_book_pixel,
                createActionIntent(context, ACTION_OPEN, appWidgetId)
            )
        } else {
            views.setViewVisibility(R.id.widget_book_pixel, View.GONE)
        }

        if (!pixels.bentoText.isNullOrBlank()) {
            views.setTextViewText(
                R.id.widget_bento_pixel,
                "🍱  ${pixels.bentoText.uppercase(Locale.getDefault())}"
            )
            views.setViewVisibility(R.id.widget_bento_pixel, View.VISIBLE)
            tintBand(
                views,
                R.id.widget_bento_pixel,
                PixelDataReader.translucent(pixels.bentoColor, Color.rgb(167, 184, 230), 92)
            )
            views.setOnClickPendingIntent(
                R.id.widget_bento_pixel,
                createActionIntent(context, ACTION_OPEN, appWidgetId)
            )
        } else {
            views.setViewVisibility(R.id.widget_bento_pixel, View.GONE)
        }

        if (hasAgenda) {
            views.setViewVisibility(R.id.widget_checklist, View.VISIBLE)
            views.setViewVisibility(R.id.widget_note_preview, View.GONE)

            val serviceIntent = Intent(context, ChecklistWidgetService::class.java).apply {
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
                data = Uri.parse(toUri(Intent.URI_INTENT_SCHEME))
            }
            views.setRemoteAdapter(R.id.widget_checklist, serviceIntent)

            val toggleIntent = Intent(context, ObsidianWidgetProvider::class.java).apply {
                action = ACTION_TOGGLE
                putExtra(EXTRA_WIDGET_ID, appWidgetId)
            }
            val togglePendingIntent = PendingIntent.getBroadcast(
                context,
                appWidgetId,
                toggleIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE
            )
            views.setPendingIntentTemplate(R.id.widget_checklist, togglePendingIntent)
            appWidgetManager.notifyAppWidgetViewDataChanged(appWidgetId, R.id.widget_checklist)
        } else {
            views.setViewVisibility(R.id.widget_checklist, View.GONE)
            views.setViewVisibility(R.id.widget_note_preview, View.VISIBLE)
            val message = if (vaultManager.isVaultConfigured) {
                "No planner tasks for today"
            } else {
                context.getString(R.string.no_vault_selected)
            }
            views.setTextViewText(R.id.widget_note_preview, message)
            views.setTextColor(R.id.widget_note_preview, Color.rgb(17, 17, 17))
        }

        val openIntent = createActionIntent(context, ACTION_OPEN, appWidgetId)
        views.setOnClickPendingIntent(R.id.widget_header, openIntent)
        views.setOnClickPendingIntent(R.id.widget_date, openIntent)

        // Tapping empty widget space performs a refresh, while agenda rows remain interactive.
        views.setOnClickPendingIntent(
            R.id.widget_root,
            createActionIntent(context, ACTION_REFRESH, appWidgetId)
        )

        views.setFloat(R.id.widget_root, "setAlpha", vaultManager.widgetAlpha / 100f)
        appWidgetManager.updateAppWidget(appWidgetId, views)
    }

    private fun tintBand(views: RemoteViews, viewId: Int, color: Int) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            views.setColorStateList(viewId, "setBackgroundTintList", ColorStateList.valueOf(color))
        } else {
            views.setInt(viewId, "setBackgroundColor", color)
        }
    }

    private fun createActionIntent(context: Context, action: String, appWidgetId: Int): PendingIntent {
        val intent = Intent(context, ObsidianWidgetProvider::class.java).apply {
            this.action = action
            putExtra(EXTRA_WIDGET_ID, appWidgetId)
        }
        return PendingIntent.getBroadcast(
            context,
            action.hashCode() + appWidgetId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    private fun openObsidian(context: Context, widgetId: Int) {
        val vaultManager = VaultManager(context, widgetId)
        val vaultName = vaultManager.vaultName
        val vaultUri = vaultManager.vaultUri

        if (vaultName != null) {
            val noteName = when (vaultManager.noteMode) {
                VaultManager.NoteMode.PINNED -> resolvePinnedNotePath(vaultUri, vaultManager)
                VaultManager.NoteMode.DAILY -> dynamicDailyNotePath(vaultManager)
            }

            if (noteName != null) {
                try {
                    val obsidianUri = Uri.Builder()
                        .scheme("obsidian")
                        .authority("open")
                        .appendQueryParameter("vault", vaultName)
                        .appendQueryParameter("file", noteName)
                        .build()
                    context.startActivity(Intent(Intent.ACTION_VIEW, obsidianUri).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                            Intent.FLAG_ACTIVITY_CLEAR_TOP or
                            Intent.FLAG_ACTIVITY_SINGLE_TOP
                    })
                    return
                } catch (_: Exception) { }
            }
        }

        try {
            context.packageManager.getLaunchIntentForPackage("md.obsidian")?.let {
                it.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                context.startActivity(it)
                return
            }
        } catch (_: Exception) { }

        context.startActivity(Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        })
    }

    private fun dynamicDailyNotePath(vaultManager: VaultManager): String {
        val today = LocalDate.now()
        val chineseMonths = arrayOf(
            "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        )
        val month = today.monthValue.toString().padStart(2, '0')
        val monthFolder = "$month ${chineseMonths[today.monthValue - 1]}"
        val date = today.format(DateTimeFormatter.ofPattern(vaultManager.dateFormat))
        val base = vaultManager.dailyFolder.trim().trim('/')
        return if (base.isBlank()) {
            "${today.year}年/$monthFolder/$date"
        } else {
            "$base/${today.year}年/$monthFolder/$date"
        }
    }

    private fun resolvePinnedNotePath(vaultUri: Uri?, vaultManager: VaultManager): String? {
        val fallbackName = vaultManager.getCurrentPinnedNoteName()?.removeSuffix(".md")
        val noteUri = vaultManager.getCurrentPinnedNoteUri() ?: return fallbackName
        val rootUri = vaultUri ?: return fallbackName

        return try {
            val treeId = DocumentsContract.getTreeDocumentId(rootUri)
            val docId = DocumentsContract.getDocumentId(noteUri)
            val relativePath = when {
                docId.startsWith("$treeId/") -> docId.removePrefix("$treeId/")
                docId == treeId -> ""
                ':' in docId -> docId.substringAfter(':')
                else -> docId
            }
            relativePath.trim('/').takeIf { it.isNotEmpty() }?.removeSuffix(".md") ?: fallbackName
        } catch (_: Exception) {
            fallbackName
        }
    }
}
