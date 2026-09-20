# Put the ICM from this USB on Windows. Run in PowerShell:
#   powershell -ExecutionPolicy Bypass -File "D:\restore-windows.ps1"      (D: is the USB letter)
# trust: unverified. Rewritten from a script that was used for real; this version has not been run.
$ErrorActionPreference = "Stop"
$U = Split-Path -Parent $MyInvocation.MyCommand.Path
$cfg = @{}; Get-Content (Join-Path $U "usb.env") | ForEach-Object { $k, $v = $_ -split '=', 2; $cfg[$k] = $v }
$KEY = $cfg["KEY"]; $REPO = $cfg["REPO"]; $NAME = $cfg["NAME"]

function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
}

# 1. Git for Windows brings git, gpg and Git Bash
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
  Refresh-Path
}
$gitRoot = Split-Path (Split-Path (Get-Command git).Source)
$gpg = Join-Path $gitRoot "usr\bin\gpg.exe"
if (-not (Test-Path $gpg)) { throw "No gpg.exe in $gitRoot\usr\bin. Install Git for Windows from https://git-scm.com" }

# 2. git-remote-gcrypt into a user bin folder that git sees through PATH
$bin = Join-Path $env:USERPROFILE "bin"
New-Item -ItemType Directory -Force -Path $bin | Out-Null
Copy-Item (Join-Path $U "tools\git-remote-gcrypt") (Join-Path $bin "git-remote-gcrypt") -Force
$userPath = [Environment]::GetEnvironmentVariable("Path","User")
if ($userPath -notlike "*$bin*") { [Environment]::SetEnvironmentVariable("Path", "$userPath;$bin", "User"); Refresh-Path }

# 3. The key
& $gpg --import (Join-Path $U "key\secret-key.asc")
"$KEY`:6:" | & $gpg --import-ownertrust

# 4. The ICM
$dest = Join-Path $env:USERPROFILE $NAME
if (-not (Test-Path $dest)) { Set-Location $env:USERPROFILE; & git clone "gcrypt::$REPO" $NAME }
Set-Location $dest
& git log -1 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { throw "The clone is empty. Usually the GitHub account has no access to the repo. Delete the folder, fix access, run again." }
& git config remote.origin.gcrypt-participants $KEY
& git config remote.origin.gcrypt-signingkey $KEY
& git config user.signingkey $KEY
& git config core.hooksPath .githooks
Write-Host "DONE. The ICM is in $dest"
