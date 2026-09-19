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
        val base = dailyFolder.trim().trim('/')
        val path = if (base.isBlank()) {
            "${today.year}年/$monthFolder"
        } else {
            "$base/${today.year}年/$monthFolder"
        }
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

gradle = Path('app/build.gradle.kts')
g = gradle.read_text(encoding='utf-8')
g = g.replace('applicationId = "com.obsidianwidget"', 'applicationId = "com.flo.obsidiandailywidget"')
g = g.replace('versionName = "1.0"', 'versionName = "2.0-flo"')
gradle.write_text(g, encoding='utf-8')
