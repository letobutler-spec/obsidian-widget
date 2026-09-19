from pathlib import Path

layout = Path('app/src/main/res/layout/widget_layout.xml')
s = layout.read_text(encoding='utf-8')

# AppWidget RemoteViews cannot reliably inflate a plain android.view.View on
# every launcher. Use TextView for the 1dp dashboard dividers; TextView is
# explicitly RemoteViews-safe and renders the same visual separator.
s2 = s.replace('''        <View\n            android:layout_width="1dp"''', '''        <TextView\n            android:layout_width="1dp"''')
if s2 == s:
    raise SystemExit('No dashboard separator <View> elements found to replace')
layout.write_text(s2, encoding='utf-8')

# Build as a separate install so a previously installed debug-signed build
# never causes an Android signature/update conflict.
gradle = Path('app/build.gradle.kts')
g = gradle.read_text(encoding='utf-8')
g = g.replace('applicationId = "com.flo.obsidiantodaywidget26"', 'applicationId = "com.flo.obsidiantodaywidget261"')
g = g.replace('versionName = "2.6-dashboard"', 'versionName = "2.6.1-remoteviews-fix"')
gradle.write_text(g, encoding='utf-8')
