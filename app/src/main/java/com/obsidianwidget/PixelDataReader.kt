package com.obsidianwidget

import android.content.Context
import android.graphics.Color
import android.net.Uri
import androidx.documentfile.provider.DocumentFile
import org.json.JSONObject
import java.time.LocalDate
import java.time.format.DateTimeFormatter

/** Reads today's Reading + Bento entries directly from the Obsidian
 * Year in Pixels plugin data.json inside the selected vault.
 */
object PixelDataReader {

    data class TodayPixels(
        val bookText: String? = null,
        val bookColor: Int? = null,
        val bentoText: String? = null,
        val bentoColor: Int? = null
    )

    fun readToday(context: Context, vaultUri: Uri?): TodayPixels {
        if (vaultUri == null) return TodayPixels()
        return try {
            val root = DocumentFile.fromTreeUri(context, vaultUri) ?: return TodayPixels()
            val dataFile = findRelative(root, ".obsidian/plugins/reading-year-pixels/data.json")
                ?: findRelative(root, ".obsidian/plugins/year-in-pixels/data.json")
                ?: return TodayPixels()

            val raw = context.contentResolver.openInputStream(dataFile.uri)
                ?.bufferedReader()
                ?.use { it.readText() }
                ?: return TodayPixels()

            val json = JSONObject(raw)
            val key = LocalDate.now().format(DateTimeFormatter.ISO_LOCAL_DATE)

            var bookText: String? = null
            var bookColor: Int? = null
            val readingEntries = json.optJSONObject("days")
                ?.optJSONObject(key)
                ?.optJSONArray("entries")
            if (readingEntries != null && readingEntries.length() > 0) {
                val labels = mutableListOf<String>()
                for (i in 0 until readingEntries.length()) {
                    val entry = readingEntries.optJSONObject(i) ?: continue
                    val title = entry.optString("title").trim()
                    if (title.isBlank()) continue
                    val finished = entry.optBoolean("finished", false)
                    labels += if (finished) "$title ✓" else title
                    if (bookColor == null) bookColor = parseColor(entry.optString("color"))
                }
                if (labels.isNotEmpty()) bookText = labels.take(3).joinToString("  •  ")
            }

            var bentoText: String? = null
            var bentoColor: Int? = null
            val trackers = json.optJSONArray("trackers")
            var bentoTrackerId: String? = null
            if (trackers != null) {
                for (i in 0 until trackers.length()) {
                    val tracker = trackers.optJSONObject(i) ?: continue
                    val type = tracker.optString("type").lowercase()
                    val name = tracker.optString("name").lowercase()
                    if (type == "bento" || name.contains("bento") || tracker.optString("symbol").contains("🍱")) {
                        bentoTrackerId = tracker.optString("id").takeIf { it.isNotBlank() }
                        if (bentoTrackerId != null) break
                    }
                }
            }

            if (bentoTrackerId != null) {
                val entries = json.optJSONObject("trackerDays")
                    ?.optJSONObject(bentoTrackerId)
                    ?.optJSONObject(key)
                    ?.optJSONArray("entries")
                if (entries != null && entries.length() > 0) {
                    var selected: JSONObject? = null
                    for (i in 0 until entries.length()) {
                        val entry = entries.optJSONObject(i) ?: continue
                        if (!entry.has("slot") || entry.optString("kind") == "bento") {
                            selected = entry
                            break
                        }
                        if (selected == null) selected = entry
                    }
                    selected?.let { entry ->
                        val title = entry.optString("title").trim()
                        val lunch = entry.optString("lunch").trim()
                        val fallback = listOf(
                            entry.optString("breakfast").trim(),
                            lunch,
                            entry.optString("dinner").trim(),
                            entry.optString("snacks").trim()
                        ).firstOrNull { it.isNotBlank() }
                        bentoText = title.ifBlank { fallback ?: "Bento" }
                        bentoColor = parseColor(entry.optString("color"))
                    }
                }
            }

            TodayPixels(bookText, bookColor, bentoText, bentoColor)
        } catch (_: Exception) {
            TodayPixels()
        }
    }

    fun translucent(color: Int?, fallback: Int, alpha: Int = 92): Int {
        val base = color ?: fallback
        return Color.argb(
            alpha.coerceIn(0, 255),
            Color.red(base),
            Color.green(base),
            Color.blue(base)
        )
    }

    private fun parseColor(value: String?): Int? {
        if (value.isNullOrBlank()) return null
        return try { Color.parseColor(value.trim()) } catch (_: Exception) { null }
    }

    private fun findRelative(root: DocumentFile, path: String): DocumentFile? {
        var current = root
        val parts = path.split('/').filter { it.isNotBlank() }
        for ((index, part) in parts.withIndex()) {
            val child = current.findFile(part) ?: return null
            if (index == parts.lastIndex) return child
            if (!child.isDirectory) return null
            current = child
        }
        return null
    }
}
