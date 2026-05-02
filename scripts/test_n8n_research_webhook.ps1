<#
Manual local test for the n8n Agentic Newsroom research webhook.

Requires n8n to be running and the placeholder workflow imported and active.
This script does not use paid APIs and does not include real secrets.
#>

param(
    [string]$WebhookUrl = "http://localhost:5678/webhook/newsroom-research",
    [string]$ApiKey = ""
)

$headers = @{}
if ($ApiKey) {
    $headers["X-Newsroom-Api-Key"] = $ApiKey
}

$body = @{
    topic = "latest software vulnerabilities"
    audience = "security researchers"
    angle = "newly published advisories"
    source_provider = "rss"
    source_ids = @("zdi_published_2026")
    max_sources = 50
    tags = @("vulnerabilities", "advisories")
    category = "cybersecurity"
    sort = "published_desc"
    output_format = "brief"
    page_size = 50
    cursor = $null
} | ConvertTo-Json -Depth 8

$response = Invoke-RestMethod `
    -Method Post `
    -Uri $WebhookUrl `
    -ContentType "application/json" `
    -Headers $headers `
    -Body $body

Write-Host "Run ID: $($response.run_id)"
Write-Host "Status: $($response.status)"
Write-Host "Result metadata:"
$response.metadata | ConvertTo-Json -Depth 8
