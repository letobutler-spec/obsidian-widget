from pathlib import Path

# Keep Flo's dynamic daily-note path.
path = Path('app/src/main/java/com/obsidianwidget/VaultManager.kt')
s = path.read_text(encoding='utf-8')

old_read = '''        val targetDir = if (dailyFolder.isNotBlank()) {
            findSubDirectory(rootDoc, dailyFolder)
        } else {
            rootDoc
        } ?: return null'''
new_read = '''        val targetDir = getDynamicDailyDirectory(rootDoc, create = false) ?: return null'''
if s.count(old_read) != 2:
    raise SystemExit(f'Expected 2 read-directory blocks, found {s.count(old_read)}')
s = s.replace(old_read, new_read)

old_write = '''        val targetDir = if (dailyFolder.isNotBlank()) {
            findOrCreateSubDirectory(rootDoc, dailyFolder)
        } else {
            rootDoc
        } ?: return false'''
new_write = '''        val targetDir = getDynamicDailyDirectory(rootDoc, create = true) ?: return false'''
if s.count(old_write) != 1:
    raise SystemExit(f'Expected 1 write-directory block, found {s.count(old_write)}')
s = s.replace(old_write, new_write)

marker = '''    private fun findSubDirectory(root: DocumentFile, path: String): DocumentFile? {'''
helper = '''    private fun getDynamicDailyDirectory(root: DocumentFile, create: Boolean): DocumentFile? {
        val today = LocalDate.now()
        val chineseMonths = arrayOf(
            "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月"
        )
        val month = today.monthValue.toString().padStart(2, '0')
        val monthFolder = "$month ${chineseMonths[today.monthValue - 1]}"
        val base = dailyFolder.trim().trim('/').ifBlank { "01 Journal" }
        val path = "$base/${today.year}年/$monthFolder"
        return if (create) {
            findOrCreateSubDirectory(root, path)
        } else {
            findSubDirectory(root, path)
        }
    }

'''
if marker not in s:
    raise SystemExit('Could not find directory helper insertion point')
s = s.replace(marker, helper + marker, 1)
path.write_text(s, encoding='utf-8')

config = Path('app/src/main/java/com/obsidianwidget/WidgetConfigActivity.kt')
c = config.read_text(encoding='utf-8')
old_config = '        dailyFolderInput.setText(vaultManager.dailyFolder)'
new_config = '        dailyFolderInput.setText(vaultManager.dailyFolder.ifBlank { "01 Journal" })'
if old_config not in c:
    raise SystemExit('Could not find daily-folder config line')
c = c.replace(old_config, new_config, 1)
config.write_text(c, encoding='utf-8')

provider = Path('app/src/main/java/com/obsidianwidget/ObsidianWidgetProvider.kt')
p = provider.read_text(encoding='utf-8')
old_provider = '''        val base = vaultManager.dailyFolder.trim().trim('/')
        return if (base.isBlank()) {
            "${today.year}年/$monthFolder/$date"
        } else {
            "$base/${today.year}年/$monthFolder/$date"
        }'''
new_provider = '''        val base = vaultManager.dailyFolder.trim().trim('/').ifBlank { "01 Journal" }
        return "$base/${today.year}年/$monthFolder/$date"'''
if old_provider not in p:
    raise SystemExit('Could not find dynamic daily-note path block')
p = p.replace(old_provider, new_provider, 1)

old_pixels = '''        val pixels = PixelDataReader.readToday(context, vaultManager.vaultUri)
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
'''
new_pixels = '''        val pixels = PixelDataReader.readToday(context, vaultManager.vaultUri)

        // Dashboard-style Reading column. Keep it visible even when empty as a reminder.
        val readingText = pixels.bookText
            ?.trim()
            ?.takeIf { it.isNotEmpty() }
            ?.uppercase(Locale.getDefault())
            ?: "\u00A0"
        views.setTextViewText(R.id.widget_book_pixel, readingText)
        views.setViewVisibility(R.id.widget_book_pixel, View.VISIBLE)
        views.setOnClickPendingIntent(
            R.id.widget_book_pixel,
            createActionIntent(context, ACTION_OPEN, appWidgetId)
        )

        // Dashboard-style Lunch column. Keep it visible even when empty as a reminder.
        val lunchText = pixels.bentoText
            ?.trim()
            ?.takeIf { it.isNotEmpty() }
            ?: "\u00A0"
        views.setTextViewText(R.id.widget_bento_pixel, lunchText)
        views.setViewVisibility(R.id.widget_bento_pixel, View.VISIBLE)
        views.setOnClickPendingIntent(
            R.id.widget_bento_pixel,
            createActionIntent(context, ACTION_OPEN, appWidgetId)
        )
'''
if old_pixels not in p:
    raise SystemExit('Could not find Reading/Bento provider block')
p = p.replace(old_pixels, new_pixels, 1)
provider.write_text(p, encoding='utf-8')

# Compact planner list: small checkbox, no bullet prefix, tight spacing.
service = Path('app/src/main/java/com/obsidianwidget/ChecklistWidgetService.kt')
sv = service.read_text(encoding='utf-8')
sv = sv.replace(
'''            val displayText = if (item.isBullet) "•  ${item.text}" else item.text''',
'''            val displayText = if (item.isBullet) "•  ${item.text}" else item.text'''
)
old_pad = '''        views.setViewPadding(
            R.id.checklist_item_root,
            indentPx + (14 * density).toInt(),
            (3 * density).toInt(),
            (12 * density).toInt(),
            (3 * density).toInt()
        )'''
new_pad = '''        views.setViewPadding(
            R.id.checklist_item_root,
            indentPx,
            (1 * density).toInt(),
            0,
            (1 * density).toInt()
        )'''
if old_pad not in sv:
    raise SystemExit('Could not find checklist padding block')
sv = sv.replace(old_pad, new_pad, 1)
old_task_text = '''        views.setTextViewText(R.id.checklist_text, markdownToHtml("•  ${item.text}"))'''
new_task_text = '''        views.setTextViewText(R.id.checklist_text, markdownToHtml(item.text))'''
if old_task_text not in sv:
    raise SystemExit('Could not find checklist text line')
sv = sv.replace(old_task_text, new_task_text, 1)
service.write_text(sv, encoding='utf-8')

# Screenshot-inspired single frosted card with Reading / Lunch / Planner columns.
layout = Path('app/src/main/res/layout/widget_layout.xml')
layout.write_text('''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/widget_root"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@drawable/widget_today_background"
    android:orientation="vertical"
    android:padding="0dp">

    <LinearLayout
        android:id="@+id/widget_header"
        android:layout_width="match_parent"
        android:layout_height="38dp"
        android:background="@drawable/widget_today_header"
        android:gravity="center_vertical"
        android:orientation="horizontal"
        android:paddingStart="14dp"
        android:paddingEnd="14dp">

        <TextView
            android:id="@+id/widget_date"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:ellipsize="end"
            android:fontFamily="sans-serif-medium"
            android:maxLines="1"
            android:text="TODAY · Saturday 19 September"
            android:textColor="#FF16303F"
            android:textSize="13sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/widget_mood"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:fontFamily="sans-serif"
            android:maxLines="1"
            android:text="A calmer day  ☁"
            android:textColor="#8A607481"
            android:textSize="10sp"
            android:textStyle="italic" />

        <TextView
            android:id="@+id/widget_todo_count"
            android:layout_width="0dp"
            android:layout_height="0dp"
            android:visibility="gone" />
    </LinearLayout>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:gravity="center_vertical"
        android:orientation="horizontal"
        android:paddingStart="14dp"
        android:paddingTop="8dp"
        android:paddingEnd="12dp"
        android:paddingBottom="8dp">

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="0.95"
            android:gravity="center_vertical"
            android:orientation="vertical"
            android:paddingEnd="10dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="📕"
                android:textSize="16sp" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="1dp"
                android:fontFamily="sans-serif-medium"
                android:text="READING"
                android:textColor="#FF536977"
                android:textSize="9sp" />

            <TextView
                android:id="@+id/widget_book_pixel"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:ellipsize="end"
                android:fontFamily="sans-serif-medium"
                android:maxLines="2"
                android:text="RED RISING"
                android:textColor="#FF213746"
                android:textSize="11sp" />
        </LinearLayout>

        <View
            android:layout_width="1dp"
            android:layout_height="match_parent"
            android:layout_marginTop="2dp"
            android:layout_marginBottom="2dp"
            android:background="#2871818B" />

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="0.95"
            android:gravity="center_vertical"
            android:orientation="vertical"
            android:paddingStart="12dp"
            android:paddingEnd="10dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="🍱"
                android:textSize="16sp" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="1dp"
                android:fontFamily="sans-serif-medium"
                android:text="LUNCH"
                android:textColor="#FF536977"
                android:textSize="9sp" />

            <TextView
                android:id="@+id/widget_bento_pixel"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:ellipsize="end"
                android:fontFamily="sans-serif-medium"
                android:maxLines="2"
                android:text="Tonkatsu bento"
                android:textColor="#FF213746"
                android:textSize="11sp" />
        </LinearLayout>

        <View
            android:layout_width="1dp"
            android:layout_height="match_parent"
            android:layout_marginTop="2dp"
            android:layout_marginBottom="2dp"
            android:background="#2871818B" />

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="1.35"
            android:orientation="vertical"
            android:paddingStart="12dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="22dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="☑"
                    android:textColor="#FF5E7180"
                    android:textSize="13sp" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:fontFamily="sans-serif-medium"
                    android:text="PLANNER"
                    android:textColor="#FF536977"
                    android:textSize="9sp" />
            </LinearLayout>

            <TextView
                android:id="@+id/widget_note_preview"
                android:layout_width="match_parent"
                android:layout_height="0dp"
                android:layout_weight="1"
                android:ellipsize="end"
                android:fontFamily="sans-serif"
                android:gravity="top"
                android:maxLines="3"
                android:text="No planner tasks for today"
                android:textColor="#AA536977"
                android:textSize="10sp"
                android:visibility="gone" />

            <ListView
                android:id="@+id/widget_checklist"
                android:layout_width="match_parent"
                android:layout_height="0dp"
                android:layout_weight="1"
                android:clipToPadding="false"
                android:divider="@android:color/transparent"
                android:dividerHeight="0dp"
                android:fadingEdge="none"
                android:padding="0dp"
                android:scrollbars="none" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
''', encoding='utf-8')

check_item = Path('app/src/main/res/layout/widget_checklist_item.xml')
check_item.write_text('''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/checklist_item_root"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:minHeight="20dp"
    android:gravity="center_vertical"
    android:orientation="horizontal"
    android:padding="0dp">

    <FrameLayout
        android:id="@+id/checklist_checkbox"
        android:layout_width="13dp"
        android:layout_height="13dp"
        android:layout_marginEnd="5dp">

        <ImageView
            android:id="@+id/checklist_checkbox_bg"
            android:layout_width="13dp"
            android:layout_height="13dp"
            android:src="@drawable/ic_checkbox_unchecked"
            android:contentDescription="Toggle" />

        <ImageView
            android:id="@+id/checklist_checkbox_mark"
            android:layout_width="13dp"
            android:layout_height="13dp"
            android:src="@drawable/ic_checkmark"
            android:visibility="gone" />
    </FrameLayout>

    <TextView
        android:id="@+id/checklist_text"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:ellipsize="end"
        android:fontFamily="sans-serif"
        android:maxLines="1"
        android:textColor="#FF314A5B"
        android:textSize="10sp" />
</LinearLayout>
''', encoding='utf-8')

text_item = Path('app/src/main/res/layout/widget_text_item.xml')
text_item.write_text('''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/text_item_root"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:minHeight="20dp"
    android:gravity="center_vertical"
    android:orientation="horizontal"
    android:padding="0dp">

    <TextView
        android:id="@+id/text_item_content"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ellipsize="end"
        android:fontFamily="sans-serif"
        android:maxLines="1"
        android:textColor="#FF314A5B"
        android:textSize="10sp" />
</LinearLayout>
''', encoding='utf-8')

Path('app/src/main/res/drawable/widget_today_background.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#DDF7FBFA" />
    <corners android:radius="20dp" />
    <stroke android:width="1dp" android:color="#48FFFFFF" />
</shape>
''', encoding='utf-8')

Path('app/src/main/res/drawable/widget_today_header.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#CDEBF4F3" />
    <corners android:topLeftRadius="20dp" android:topRightRadius="20dp" />
</shape>
''', encoding='utf-8')

widget_info = Path('app/src/main/res/xml/widget_info.xml')
wi = widget_info.read_text(encoding='utf-8')
wi = wi.replace('android:minHeight="90dp"', 'android:minHeight="96dp"')
widget_info.write_text(wi, encoding='utf-8')

gradle = Path('app/build.gradle.kts')
g = gradle.read_text(encoding='utf-8')
g = g.replace('applicationId = "com.obsidianwidget"', 'applicationId = "com.flo.obsidiantodaywidget26"')
g = g.replace('versionName = "1.0"', 'versionName = "2.6-dashboard"')
gradle.write_text(g, encoding='utf-8')
