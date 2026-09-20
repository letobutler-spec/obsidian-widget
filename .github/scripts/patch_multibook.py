from pathlib import Path
import re

layout = Path('app/src/main/res/layout/widget_layout.xml')
s = layout.read_text(encoding='utf-8')

pattern = re.compile(r'(<TextView\s+android:id="@\+id/widget_book_pixel".*?)(/>)', re.S)
m = pattern.search(s)
if not m:
    raise SystemExit('Could not find widget_book_pixel TextView')
block = m.group(1)
block = block.replace('android:maxLines="1"', 'android:maxLines="2"')
block = block.replace('android:textSize="10.5sp"', 'android:textSize="9.5sp"')
if 'android:lineSpacingExtra=' not in block:
    block = block.replace('android:includeFontPadding="false"', 'android:includeFontPadding="false"\n                android:lineSpacingExtra="-1dp"')
s = s[:m.start()] + block + m.group(2) + s[m.end():]
layout.write_text(s, encoding='utf-8')

# Separate install so v2.7 remains untouched while testing.
gradle = Path('app/build.gradle.kts')
g = gradle.read_text(encoding='utf-8')
g = g.replace('applicationId = "com.flo.obsidiantodaywidget27"', 'applicationId = "com.flo.obsidiantodaywidget28"')
g = g.replace('versionName = "2.7-reference-exact"', 'versionName = "2.8-multibook"')
gradle.write_text(g, encoding='utf-8')
