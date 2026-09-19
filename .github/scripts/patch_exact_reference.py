from pathlib import Path
import re

# --- Provider: reference-style date typography and keep dynamic data behavior ---
provider = Path('app/src/main/java/com/obsidianwidget/ObsidianWidgetProvider.kt')
p = provider.read_text(encoding='utf-8')
if 'import android.graphics.Typeface' not in p:
    p = p.replace(
        'import android.graphics.Color\n',
        'import android.graphics.Color\nimport android.graphics.Typeface\nimport android.text.SpannableString\nimport android.text.Spanned\nimport android.text.style.StyleSpan\n'
    )
old_date = '''        val today = LocalDate.now()\n        val prettyDate = today.format(DateTimeFormatter.ofPattern("EEEE d MMMM", Locale.ENGLISH))\n        views.setTextViewText(R.id.widget_date, "TODAY · $prettyDate")\n        views.setTextColor(R.id.widget_date, Color.rgb(17, 17, 17))'''
new_date = '''        val today = LocalDate.now()\n        val prettyDate = today.format(DateTimeFormatter.ofPattern("EEEE d MMMM", Locale.ENGLISH))\n        val dateLabel = SpannableString("TODAY · $prettyDate")\n        dateLabel.setSpan(\n            StyleSpan(Typeface.BOLD),\n            0,\n            5,\n            Spanned.SPAN_EXCLUSIVE_EXCLUSIVE\n        )\n        views.setTextViewText(R.id.widget_date, dateLabel)\n        views.setTextColor(R.id.widget_date, Color.rgb(37, 55, 68))'''
if old_date not in p:
    raise SystemExit('Could not find date/header provider block')
p = p.replace(old_date, new_date, 1)
provider.write_text(p, encoding='utf-8')

# --- Main widget layout: match picture 2 proportions/style, RemoteViews-safe only ---
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
        android:layout_height="29dp"
        android:background="@drawable/widget_today_header"
        android:gravity="center_vertical"
        android:orientation="horizontal"
        android:paddingStart="12dp"
        android:paddingEnd="12dp">

        <TextView
            android:id="@+id/widget_date"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:ellipsize="end"
            android:fontFamily="sans-serif"
            android:includeFontPadding="false"
            android:maxLines="1"
            android:text="TODAY · Saturday 19 September"
            android:textColor="#253744"
            android:textSize="11.5sp" />

        <TextView
            android:id="@+id/widget_mood"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:fontFamily="sans-serif"
            android:includeFontPadding="false"
            android:maxLines="1"
            android:text="A calmer day  ☁"
            android:textColor="#768995"
            android:textSize="9sp"
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
        android:paddingTop="6dp"
        android:paddingEnd="10dp"
        android:paddingBottom="7dp">

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="0.84"
            android:gravity="center_vertical"
            android:orientation="vertical"
            android:paddingEnd="9dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:fontFamily="sans-serif"
                android:includeFontPadding="false"
                android:text="📕"
                android:textSize="15sp" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:fontFamily="sans-serif-medium"
                android:includeFontPadding="false"
                android:text="READING"
                android:textColor="#627782"
                android:textSize="8.5sp" />

            <TextView
                android:id="@+id/widget_book_pixel"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:ellipsize="end"
                android:fontFamily="sans-serif"
                android:includeFontPadding="false"
                android:maxLines="1"
                android:text="RED RISING"
                android:textColor="#2F4654"
                android:textSize="10.5sp" />
        </LinearLayout>

        <TextView
            android:layout_width="1dp"
            android:layout_height="44dp"
            android:background="#22728690"
            android:includeFontPadding="false"
            android:text="" />

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="1.00"
            android:gravity="center_vertical"
            android:orientation="vertical"
            android:paddingStart="11dp"
            android:paddingEnd="9dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:fontFamily="sans-serif"
                android:includeFontPadding="false"
                android:text="🍱"
                android:textSize="15sp" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:fontFamily="sans-serif-medium"
                android:includeFontPadding="false"
                android:text="LUNCH"
                android:textColor="#627782"
                android:textSize="8.5sp" />

            <TextView
                android:id="@+id/widget_bento_pixel"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"
                android:ellipsize="end"
                android:fontFamily="sans-serif"
                android:includeFontPadding="false"
                android:maxLines="1"
                android:text="Tonkatsu bento"
                android:textColor="#2F4654"
                android:textSize="10.5sp" />
        </LinearLayout>

        <TextView
            android:layout_width="1dp"
            android:layout_height="44dp"
            android:background="#22728690"
            android:includeFontPadding="false"
            android:text="" />

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="match_parent"
            android:layout_weight="1.10"
            android:orientation="vertical"
            android:paddingStart="11dp">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="17dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <TextView
                    android:layout_width="14dp"
                    android:layout_height="14dp"
                    android:background="@drawable/planner_header_check"
                    android:fontFamily="sans-serif-medium"
                    android:gravity="center"
                    android:includeFontPadding="false"
                    android:text="✓"
                    android:textColor="#F3F7F7"
                    android:textSize="8.5sp" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginStart="6dp"
                    android:fontFamily="sans-serif-medium"
                    android:includeFontPadding="false"
                    android:text="PLANNER"
                    android:textColor="#627782"
                    android:textSize="8.5sp" />
            </LinearLayout>

            <TextView
                android:id="@+id/widget_note_preview"
                android:layout_width="match_parent"
                android:layout_height="0dp"
                android:layout_weight="1"
                android:ellipsize="end"
                android:fontFamily="sans-serif"
                android:gravity="top"
                android:includeFontPadding="false"
                android:maxLines="2"
                android:paddingTop="4dp"
                android:text="No planner tasks for today"
                android:textColor="#6A7C87"
                android:textSize="9.5sp"
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
                android:paddingTop="2dp"
                android:paddingBottom="0dp"
                android:scrollbars="none" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
''', encoding='utf-8')

# --- Planner list rows: compact square boxes and regular-weight text ---
check_item = Path('app/src/main/res/layout/widget_checklist_item.xml')
check_item.write_text('''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/checklist_item_root"
    android:layout_width="match_parent"
    android:layout_height="18dp"
    android:gravity="center_vertical"
    android:orientation="horizontal"
    android:padding="0dp">

    <FrameLayout
        android:id="@+id/checklist_checkbox"
        android:layout_width="13dp"
        android:layout_height="13dp"
        android:layout_marginEnd="6dp">

        <ImageView
            android:id="@+id/checklist_checkbox_bg"
            android:layout_width="13dp"
            android:layout_height="13dp"
            android:contentDescription="Toggle"
            android:src="@drawable/ic_checkbox_unchecked" />

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
        android:includeFontPadding="false"
        android:maxLines="1"
        android:textColor="#536B79"
        android:textSize="10sp" />
</LinearLayout>
''', encoding='utf-8')

text_item = Path('app/src/main/res/layout/widget_text_item.xml')
text_item.write_text('''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/text_item_root"
    android:layout_width="match_parent"
    android:layout_height="18dp"
    android:gravity="center_vertical"
    android:orientation="horizontal"
    android:padding="0dp">

    <TextView
        android:id="@+id/text_item_content"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:ellipsize="end"
        android:fontFamily="sans-serif"
        android:includeFontPadding="false"
        android:maxLines="1"
        android:textColor="#536B79"
        android:textSize="10sp" />
</LinearLayout>
''', encoding='utf-8')

# --- Reference card surfaces ---
Path('app/src/main/res/drawable/widget_today_background.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#D9EEF7F5" />
    <corners android:radius="20dp" />
    <stroke android:width="1dp" android:color="#22FFFFFF" />
</shape>
''', encoding='utf-8')

Path('app/src/main/res/drawable/widget_today_header.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#BBD8ECEF" />
    <corners android:topLeftRadius="20dp" android:topRightRadius="20dp" />
</shape>
''', encoding='utf-8')

Path('app/src/main/res/drawable/planner_header_check.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#6E818D" />
    <corners android:radius="2.5dp" />
</shape>
''', encoding='utf-8')

# Square planner checkbox, matching the reference rather than the original circle.
Path('app/src/main/res/drawable/ic_checkbox_unchecked.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#16FFFFFF" />
    <stroke android:width="1dp" android:color="#7D909B" />
    <corners android:radius="2dp" />
</shape>
''', encoding='utf-8')

# --- Ask launcher for a short 4x1 widget like picture 2 ---
Path('app/src/main/res/xml/widget_info.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="300dp"
    android:minHeight="78dp"
    android:maxResizeWidth="530dp"
    android:maxResizeHeight="105dp"
    android:updatePeriodMillis="0"
    android:initialLayout="@layout/widget_layout"
    android:configure="com.obsidianwidget.WidgetConfigActivity"
    android:resizeMode="horizontal|vertical"
    android:widgetCategory="home_screen"
    android:widgetFeatures="reconfigurable"
    android:previewLayout="@layout/widget_layout"
    android:description="@string/widget_description"
    android:targetCellWidth="4"
    android:targetCellHeight="1" />
''', encoding='utf-8')

# --- Separate install for safe A/B testing ---
gradle = Path('app/build.gradle.kts')
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'applicationId\s*=\s*"[^"]+"', 'applicationId = "com.flo.obsidiantodaywidget27"', g, count=1)
g = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "2.7-reference-exact"', g, count=1)
gradle.write_text(g, encoding='utf-8')
