# Plan and install Git Secret Guard prerequisites on Windows.
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Rahul Patidar

param(
    [ValidateSet('Check', 'Install')][string]$Action = 'Check',
    [ValidateSet('scan', 'pre-commit', 'pre-push')][string]$Workflow = 'pre-push',
    [string]$Approve = ''
)

$ErrorActionPreference = 'Stop'
$GitleaksVersion = '8.30.1'
$reportedArchitecture = if ($env:PROCESSOR_ARCHITEW6432) { $env:PROCESSOR_ARCHITEW6432 } else { $env:PROCESSOR_ARCHITECTURE }
$architecture = switch ($reportedArchitecture) {
    'AMD64' { 'x64' }
    'ARM64' { 'arm64' }
    default { throw "Unsupported Windows architecture: $reportedArchitecture" }
}
$needGit = $Workflow -ne 'scan'
$needPython = $Workflow -eq 'pre-push'
$installDir = Join-Path $env:LOCALAPPDATA 'GitSecretGuard\bin'

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
$gitVersion = if ($gitCommand) { (& git --version 2>$null) -join '' } else { 'missing' }
$pythonLauncher = $null
$pythonExecutable = $null
$pythonVersion = 'missing'
$pythonCandidates = @(
    [pscustomobject]@{ Command = 'py'; Prefix = @('-3') },
    [pscustomobject]@{ Command = 'python3'; Prefix = @() },
    [pscustomobject]@{ Command = 'python'; Prefix = @() }
)
foreach ($candidate in $pythonCandidates) {
    if (Get-Command $candidate.Command -ErrorAction SilentlyContinue) {
        $candidateCommand = $candidate.Command
        $versionArgs = @($candidate.Prefix) + @('-c', 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        $version = & $candidateCommand @versionArgs 2>$null
        $checkArgs = @($candidate.Prefix) + @('-c', 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)')
        & $candidateCommand @checkArgs 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonLauncher = $candidate
            $pathArgs = @($candidate.Prefix) + @('-c', 'import sys; print(sys.executable)')
            $pythonExecutable = ((& $candidateCommand @pathArgs 2>$null) -join '').Trim()
            $pythonVersion = ($version -join '')
            break
        }
    }
}
$localGitleaks = Join-Path $installDir 'gitleaks.exe'
$gitleaksCommand = Get-Command gitleaks -ErrorAction SilentlyContinue
$gitleaksCandidates = [System.Collections.Generic.List[string]]::new()
if ($gitleaksCommand) { $gitleaksCandidates.Add($gitleaksCommand.Source) }
if ((Test-Path $localGitleaks) -and -not $gitleaksCandidates.Contains($localGitleaks)) { $gitleaksCandidates.Add($localGitleaks) }
$gitleaksExecutable = $null
$gitleaksVersionFound = 'missing'
$gitleaksOk = $false
foreach ($candidate in $gitleaksCandidates) {
    $candidateVersion = ((& $candidate version 2>$null) -join '').Trim()
    if ($gitleaksVersionFound -eq 'missing') { $gitleaksVersionFound = $candidateVersion }
    if ($candidateVersion -match '^v?8\.(\d+)\.') {
        if ([int]$Matches[1] -ge 19) {
            $gitleaksExecutable = $candidate
            $gitleaksVersionFound = $candidateVersion
            $gitleaksOk = $true
            break
        }
    }
}

$missing = [System.Collections.Generic.List[string]]::new()
if ($needGit -and -not $gitCommand) { $missing.Add('git') }
if ($needPython -and -not $pythonLauncher) { $missing.Add('python3') }
if (-not $gitleaksOk) { $missing.Add('gitleaks') }

$winget = Get-Command winget -ErrorAction SilentlyContinue
$packages = [System.Collections.Generic.List[string]]::new()
if ($needGit -and -not $gitCommand) { $packages.Add('Git.Git') }
if ($needPython -and -not $pythonLauncher) { $packages.Add('Python.Python.3.12') }
$archive = "gitleaks_${GitleaksVersion}_windows_${architecture}.zip"
$releaseBase = "https://github.com/gitleaks/gitleaks/releases/download/v$GitleaksVersion"
$packageCommands = if ($packages.Count -eq 0) {
    'none'
} elseif (-not $winget) {
    'unsupported: winget is not available'
} else {
    ($packages | ForEach-Object { "winget install --id $_ --exact --source winget --accept-package-agreements --accept-source-agreements" }) -join '; '
}
$packageSourcePlan = if ($packages.Count -eq 0) { 'not-needed' } elseif ($winget) { 'winget' } else { 'none' }
$gitleaksPlan = if ($gitleaksOk) {
    @("gitleaks_action=reuse compatible installation", "gitleaks_path=$gitleaksExecutable")
} else {
    @(
        'gitleaks_action=install reviewed release'
        "gitleaks_source=$releaseBase/$archive"
        "gitleaks_checksums=$releaseBase/gitleaks_${GitleaksVersion}_checksums.txt"
        "gitleaks_destination=$(Join-Path $installDir 'gitleaks.exe')"
        'gitleaks_install_method=Invoke-WebRequest download, published SHA-256 verification, Expand-Archive, user-local copy'
    )
}
$plan = @(
    "workflow=$Workflow"
    "platform=windows/$architecture"
    "missing=$($missing -join ',')"
    "system_package_source=$packageSourcePlan"
    "system_package_commands=$packageCommands"
    $gitleaksPlan
    "network_required=$(if ($missing.Count) { 'yes' } else { 'no' })"
    "administrator_access=$(if ($packages.Count) { 'installer-dependent' } else { 'no' })"
) -join "`n"
$sha = [System.Security.Cryptography.SHA256]::Create()
try { $hash = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($plan)) } finally { $sha.Dispose() }
$planId = (([BitConverter]::ToString($hash)).Replace('-', '').ToLowerInvariant()).Substring(0, 16)

Write-Output 'Git Secret Guard prerequisite check'
Write-Output "workflow: $Workflow"
Write-Output "platform: windows/$architecture"
Write-Output "git: $gitVersion"
Write-Output "python3: $pythonVersion"
Write-Output "gitleaks: $gitleaksVersionFound"
if ($missing.Count -eq 0) {
    Write-Output 'status: ready'
    Write-Output 'No installation is required.'
    Write-Output "gitleaks-path: $gitleaksExecutable"
    if ($needPython) { Write-Output "python-path: $pythonExecutable" }
    if ($needGit) { Write-Output "git-path: $($gitCommand.Source)" }
    exit 0
}
Write-Output 'status: confirmation-required'
Write-Output "missing: $($missing -join ',')"
Write-Output "plan-id: $planId"
Write-Output 'plan:'
Write-Output $plan
if ($Action -eq 'Check') { exit 10 }
if (-not $Approve -or $Approve -ne $planId) {
    Write-Error 'Installation refused: rerun only after the user approves this exact plan ID.'
    exit 2
}
if ($packages.Count -gt 0 -and -not $winget) {
    Write-Error 'Cannot install required system packages automatically because winget is unavailable.'
    exit 2
}

Write-Output "Installing the user-approved prerequisites for plan $planId."
foreach ($package in $packages) {
    & winget install --id $package --exact --source winget --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "Package installation failed: $package" }
}
# Refresh PATH for installers that updated the registry in this process.
$machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$env:Path = "$machinePath;$userPath"
$gitleaksInstalled = $false
if (-not $gitleaksOk) {
    $temporary = Join-Path ([IO.Path]::GetTempPath()) ("git-secret-guard-" + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $temporary | Out-Null
    try {
        $archivePath = Join-Path $temporary $archive
        $checksumsPath = Join-Path $temporary 'checksums.txt'
        Invoke-WebRequest -UseBasicParsing -Uri "$releaseBase/$archive" -OutFile $archivePath
        Invoke-WebRequest -UseBasicParsing -Uri "$releaseBase/gitleaks_${GitleaksVersion}_checksums.txt" -OutFile $checksumsPath
        $line = Get-Content $checksumsPath | Where-Object { $_ -match "\s$([regex]::Escape($archive))$" }
        if (($line | Measure-Object).Count -ne 1) { throw 'Release checksum entry is missing or ambiguous.' }
        $expected = ($line -split '\s+')[0].ToLowerInvariant()
        $actual = (Get-FileHash $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { throw 'Gitleaks checksum verification failed.' }
        Expand-Archive -Path $archivePath -DestinationPath $temporary -Force
        New-Item -ItemType Directory -Force -Path $installDir | Out-Null
        Copy-Item (Join-Path $temporary 'gitleaks.exe') (Join-Path $installDir 'gitleaks.exe') -Force
        $gitleaksInstalled = $true
    } finally {
        Remove-Item -Recurse -Force $temporary -ErrorAction SilentlyContinue
    }
}

$gitleaksPath = if ($gitleaksInstalled) {
    $localGitleaks
} else {
    $gitleaksExecutable
}
if ($needGit -and -not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git verification failed; restart the terminal and retry check.' }
if ($needPython) {
    $pythonReady = $false
    foreach ($candidate in $pythonCandidates) {
        if (Get-Command $candidate.Command -ErrorAction SilentlyContinue) {
            $candidateCommand = $candidate.Command
            $checkArgs = @($candidate.Prefix) + @('-c', 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)')
            & $candidateCommand @checkArgs 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pathArgs = @($candidate.Prefix) + @('-c', 'import sys; print(sys.executable)')
                $pythonExecutable = ((& $candidateCommand @pathArgs 2>$null) -join '').Trim()
                $pythonReady = $true
                break
            }
        }
    }
    if (-not $pythonReady) { throw 'Python 3.9+ verification failed; restart the terminal and retry check.' }
}
& $gitleaksPath version | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Gitleaks verification failed.' }
Write-Output 'status: installed-and-verified'
Write-Output "gitleaks-path: $gitleaksPath"
if ($needPython) { Write-Output "python-path: $pythonExecutable" }
if ($needGit) { Write-Output "git-path: $((Get-Command git).Source)" }
Write-Output 'Use this absolute path in hooks because the user installation directory is not automatically added to PATH.'
