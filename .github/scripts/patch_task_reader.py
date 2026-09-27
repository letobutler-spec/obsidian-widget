from pathlib import Path
import re

path = Path('app/src/main/java/com/obsidianwidget/VaultManager.kt')
s = path.read_text(encoding='utf-8')

# Replace only readDailyNote with a fault-tolerant lookup. The normal dynamic path
# remains the fast path; recursive search is only a fallback for folder naming changes.
pattern = re.compile(
    r'''    fun readDailyNote\(\): String\? \{.*?\n    \}\n\n    /\*\*\n     \* Append text to today's daily note''',
    re.S,
)
replacement = '''    fun readDailyNote(): String? {
        val uri = vaultUri ?: return null
        val rootDoc = DocumentFile.fromTreeUri(context, uri) ?: return null
        val todayFileName = getTodayFileName()

        // Fast path: use Flo's expected year/month journal directory.
        val expectedDir = getDynamicDailyDirectory(rootDoc, create = false)
        val expectedFile = expectedDir?.findFile(todayFileName)
        if (expectedFile != null && expectedFile.isFile) {
            return readFileContent(expectedFile.uri)
        }

        // Fallback: locate today's note anywhere below the configured daily folder.
        // This handles renamed month/year folders without requiring widget reconfiguration.
        val baseFolder = dailyFolder.trim().trim('/').ifBlank { "01 Journal" }
        val baseDir = findSubDirectory(rootDoc, baseFolder) ?: rootDoc
        val found = findFileRecursive(baseDir, todayFileName, 4) ?: return null
        return readFileContent(found.uri)
    }

    private fun findFileRecursive(
        directory: DocumentFile,
        targetName: String,
        remainingDepth: Int
    ): DocumentFile? {
        val direct = directory.findFile(targetName)
        if (direct != null && direct.isFile) return direct
        if (remainingDepth <= 0) return null

        for (child in directory.listFiles()) {
            if (!child.isDirectory) continue
            val found = findFileRecursive(child, targetName, remainingDepth - 1)
            if (found != null) return found
        }
        return null
    }

    /**
     * Append text to today's daily note'''

s2, count = pattern.subn(replacement, s, count=1)
if count != 1:
    raise SystemExit(f'Could not replace readDailyNote; replacements={count}')
path.write_text(s2, encoding='utf-8')

# Keep this as a separate install for safe testing.
gradle = Path('app/build.gradle.kts')
g = gradle.read_text(encoding='utf-8')
g = re.sub(r'applicationId\s*=\s*"[^"]+"', 'applicationId = "com.flo.obsidiantodaywidget29"', g, count=1)
g = re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "2.9-task-reader-fix"', g, count=1)
gradle.write_text(g, encoding='utf-8')
