<# 
Manual/live network test for the Agentic Newsroom RSS registry.

This script is intentionally not part of normal pytest. It calls a running
Python Agent Runner and may cause live network access through the runner.
#>

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$ApiKey = ""
)

$headers = @{}
if ($ApiKey) {
    $headers["X-Newsroom-Api-Key"] = $ApiKey
}

$body = @{
    topic = "ZDI vulnerability advisory"
    source_provider = "rss"
    source_ids = @("zdi_published_2026")
    max_sources = 5
    category = "cybersecurity"
    tags = @("vulnerabilities", "advisories", "zdi")
    output_format = "json"
} | ConvertTo-Json -Depth 8

Write-Host "Manual/live network test: ZDI RSS registry source"
Write-Host "Endpoint: $BaseUrl/research"
Write-Host "Source ID: zdi_published_2026"

$response = Invoke-RestMethod `
    -Method Post `
    -Uri "$BaseUrl/research" `
    -ContentType "application/json" `
    -Headers $headers `
    -Body $body

$response.story.sources | ForEach-Object {
    Write-Host "---"
    Write-Host "Provider: $($_.provider)"
    Write-Host "Title: $($_.title)"
    Write-Host "URL: $($_.url)"
    Write-Host "Metadata:"
    $_.metadata | ConvertTo-Json -Depth 8
}
