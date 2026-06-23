param(
    [string]$RepositoryName = "us-ward-experience-lab",
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI 'gh' is not installed. Install it and run: gh auth login"
}

gh auth status | Out-Host

$releaseAsset = "outputs\USWardExperienceLab_v0.1.0-beta.exe"
if (-not (Test-Path $releaseAsset)) {
    throw "Missing release asset: $releaseAsset"
}

$owner = gh api user --jq ".login"
$repoFullName = "$owner/$RepositoryName"
$visibilityFlag = "--$Visibility"

if (-not (Test-Path ".git\HEAD")) {
    git init -b main
}

git add README.md FEEDBACK.md DISCLAIMER.md CHANGELOG.md LICENSE .gitignore RELEASE_NOTES_v0.1.0-beta.md .github screenshots work scripts
git commit -m "Release v0.1.0-beta"

$repoExists = $false
try {
    gh repo view $repoFullName | Out-Null
    $repoExists = $true
} catch {
    $repoExists = $false
}

if (-not $repoExists) {
    gh repo create $RepositoryName $visibilityFlag --source . --remote origin --push
} else {
    if (-not (git remote get-url origin 2>$null)) {
        git remote add origin "https://github.com/$repoFullName.git"
    }
    git push -u origin main
}

gh release create v0.1.0-beta $releaseAsset `
    --repo $repoFullName `
    --title "U.S. Ward Experience Lab v0.1.0-beta" `
    --notes-file RELEASE_NOTES_v0.1.0-beta.md

Write-Host "Published GitHub release v0.1.0-beta for $RepositoryName"
