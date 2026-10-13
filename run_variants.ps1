param([string]$py = "python")

Set-Location $PSScriptRoot
$sizes = @{}

Write-Host "Using python: $py" -ForegroundColor Yellow
& $py -c "import sys, langchain_core; print(sys.executable)"
if ($LASTEXITCODE -ne 0) { throw "This python cannot import langchain_core. Pass the right path with -py." }

foreach ($v in "raw","title","strip","strip_title") {
    $label = "A-" + $v.Replace("_","-") + "-2"
    Write-Host "`n=== $v -> $label ===" -ForegroundColor Cyan

    if (Select-String -Path eval_log.csv -Pattern ",$label," -Quiet) {
        throw "Label $label is already in eval_log.csv. Use a new one."
    }

    if (Test-Path chroma_db) { Remove-Item -Recurse -Force chroma_db }
    if (Test-Path chroma_db) { throw "chroma_db could not be deleted. Close other Python terminals." }

    $env:INDEX_VARIANT = $v
    $out = & $py ingest.py
    if ($LASTEXITCODE -ne 0) { throw "ingest.py failed for $v" }
    $out | ForEach-Object { Write-Host $_ }
    if (($out | Out-String) -match "average embedded text: (\d+)") { $sizes[$v] = [int]$Matches[1] }

    $stamp = (& $py -c "from ask import vectorstore; print(vectorstore.get(limit=1)['metadatas'][0]['index_variant'])" | Select-Object -Last 1).Trim()
    Write-Host "stamp: $stamp"
    if ($stamp -ne $v) { throw "Stamp says '$stamp' but expected '$v'. Run stopped." }

    & $py eval_retrieval.py --label $label
    if ($LASTEXITCODE -ne 0) { throw "eval_retrieval.py failed for $label" }
}

Remove-Item Env:INDEX_VARIANT -ErrorAction SilentlyContinue

Write-Host "`nAverage embedded text per variant:" -ForegroundColor Cyan
$sizes.GetEnumerator() | Sort-Object Name | Format-Table -AutoSize
if ($sizes["strip"] -ge $sizes["raw"]) { Write-Warning "strip is not smaller than raw" }
if ($sizes["title"] -le $sizes["raw"]) { Write-Warning "title is not bigger than raw" }
if ($sizes["strip_title"] -le $sizes["strip"]) { Write-Warning "strip_title is not bigger than strip" }