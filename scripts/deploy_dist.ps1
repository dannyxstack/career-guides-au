param(
  [string]$HostName,
  [string]$User,
  [string]$RemoteRoot = "/var/www/career-guides",
  [string]$LocalDist = "site/dist",
  [ValidateSet("rsync", "scp")]
  [string]$Method = "rsync",
  [int]$Port = 22,
  [string]$IdentityFile = "",
  [int]$KeepReleases = 3,
  [string]$ReleaseName = "",
  [switch]$DryRun,
  [switch]$Help
)

$ErrorActionPreference = "Stop"

function Show-Usage {
  Write-Host @"
Deploy a locally built Astro dist directory over SSH without touching the live
directory until upload succeeds.

Examples:
  .\scripts\deploy_dist.ps1 -HostName 1.2.3.4 -User deploy
  .\scripts\deploy_dist.ps1 -HostName example.com -User deploy -RemoteRoot /var/www/career-guides -Method rsync
  .\scripts\deploy_dist.ps1 -HostName example.com -User deploy -Method scp -IdentityFile ~/.ssh/id_ed25519

Expected server layout:
  /var/www/career-guides/
    current -> releases/20260713-153000
    releases/
      20260713-153000/

Point nginx root at:
  /var/www/career-guides/current

Parameters:
  -HostName       SSH host or IP. Required.
  -User           SSH username. Required.
  -RemoteRoot     Remote deploy root. Default: /var/www/career-guides
  -LocalDist      Local dist path. Default: site/dist
  -Method         rsync or scp. Default: rsync
  -Port           SSH port. Default: 22
  -IdentityFile   Optional private key path.
  -KeepReleases   Number of old releases to keep. Default: 3
  -ReleaseName    Optional release folder name. Default: yyyyMMdd-HHmmss
  -DryRun         Print commands without running upload/switch.
"@
}

if ($Help) {
  Show-Usage
  exit 0
}

if (-not $HostName -or -not $User) {
  Show-Usage
  throw "HostName and User are required."
}

$localDistItem = Get-Item -LiteralPath $LocalDist
if (-not $localDistItem.PSIsContainer) {
  throw "LocalDist must be a directory: $LocalDist"
}

function Resolve-Tool([string]$Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    throw "Required command '$Name' was not found in PATH."
  }
  return $cmd.Source
}

function Quote-Remote([string]$Value) {
  return "'" + ($Value -replace "'", "'\''") + "'"
}

function Invoke-Logged([string]$FilePath, [string[]]$ArgumentList) {
  $printable = @($FilePath) + $ArgumentList
  Write-Host ("`n> " + ($printable -join " "))
  if ($DryRun) {
    return
  }
  & $FilePath @ArgumentList
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code $LASTEXITCODE"
  }
}

$ssh = Resolve-Tool "ssh"
$scp = if ($Method -eq "scp") { Resolve-Tool "scp" } else { $null }
$rsync = if ($Method -eq "rsync") { Resolve-Tool "rsync" } else { $null }

$release = if ($ReleaseName) { $ReleaseName } else { Get-Date -Format "yyyyMMdd-HHmmss" }
$remote = "$User@$HostName"
$remoteRootQ = Quote-Remote $RemoteRoot
$releaseDir = "$RemoteRoot/releases/$release"
$releaseDirQ = Quote-Remote $releaseDir
$currentLink = "$RemoteRoot/current"
$nextLink = "$RemoteRoot/current.next"
$currentLinkQ = Quote-Remote $currentLink
$nextLinkQ = Quote-Remote $nextLink
$releasesDirQ = Quote-Remote "$RemoteRoot/releases"

$sshArgs = @("-p", "$Port")
if ($IdentityFile) {
  $sshArgs += @("-i", $IdentityFile)
}

$scpArgsBase = @("-P", "$Port")
if ($IdentityFile) {
  $scpArgsBase += @("-i", $IdentityFile)
}

$sshTransport = "ssh -p $Port"
if ($IdentityFile) {
  $sshTransport += " -i `"$IdentityFile`""
}

$remotePrepare = @"
set -e
mkdir -p $releaseDirQ
"@
Invoke-Logged $ssh (@($sshArgs) + @($remote, $remotePrepare))

if ($Method -eq "rsync") {
  $source = (Resolve-Path -LiteralPath $LocalDist).Path.TrimEnd("\", "/") + "/"
  $target = "${remote}:$releaseDir/"
  $rsyncArgs = @("-az", "--delete", "--info=progress2", "-e", $sshTransport, $source, $target)
  Invoke-Logged $rsync $rsyncArgs
} else {
  $source = (Resolve-Path -LiteralPath $LocalDist).Path.TrimEnd("\", "/") + "/."
  $target = "${remote}:$releaseDir/"
  Write-Warning "scp fallback uploads all files every time. For an 8GB dist, rsync is much faster after the first deploy."
  Invoke-Logged $scp (@($scpArgsBase) + @("-r", $source, $target))
}

$remoteSwitch = @"
set -e
test -f $releaseDirQ/index.html
ln -sfn $releaseDirQ $nextLinkQ
mv -Tf $nextLinkQ $currentLinkQ
find $releasesDirQ -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' | sort -rn | tail -n +$($KeepReleases + 1) | cut -d' ' -f2- | xargs -r rm -rf
echo "Activated $releaseDir"
"@
Invoke-Logged $ssh (@($sshArgs) + @($remote, $remoteSwitch))

Write-Host "`nDeploy complete."
Write-Host "Live symlink: $currentLink -> $releaseDir"
