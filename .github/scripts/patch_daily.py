from pathlib import Path

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
        // Keep the whole vault selected so the widget can read both Journal notes
        // and .obsidian/plugins/reading-year-pixels/data.json.
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

# Show the correct Journal path in configuration when a new widget has no saved folder.
config = Path('app/src/main/java/com/obsidianwidget/WidgetConfigActivity.kt')
c = config.read_text(encoding='utf-8')
old_config = '        dailyFolderInput.setText(vaultManager.dailyFolder)'
new_config = '        dailyFolderInput.setText(vaultManager.dailyFolder.ifBlank { "01 Journal" })'
if old_config not in c:
    raise SystemExit('Could not find daily-folder config line')
c = c.replace(old_config, new_config, 1)
config.write_text(c, encoding='utf-8')

# Make tapping the header open the same nested daily note path.
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
provider.write_text(p, encoding='utf-8')

gradle = Path('app/build.gradle.kts')
g = gradle.read_text(encoding='utf-8')
g = g.replace('applicationId = "com.obsidianwidget"', 'applicationId = "com.flo.obsidiantodaywidget"')
g = g.replace('versionName = "1.0"', 'versionName = "2.2-today"')
gradle.write_text(g, encoding='utf-8')
