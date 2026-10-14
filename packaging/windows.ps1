# Klava installer for Windows (current user, no admin rights needed).
#   windows.ps1              - install or update, adds a Start menu shortcut
#   windows.ps1 -Desktop     - also add a desktop shortcut
#   windows.ps1 -Uninstall   - remove
param([switch]$Uninstall, [switch]$Desktop)
$ErrorActionPreference = 'Stop'

$Root     = Split-Path -Parent $PSScriptRoot
$Dest     = Join-Path $env:LOCALAPPDATA 'Klava'
# Create: if the folder does not exist yet, GetFolderPath would return an empty string
function Get-Folder([string]$Name) {
    [Environment]::GetFolderPath([Environment+SpecialFolder]$Name, [Environment+SpecialFolderOption]::Create)
}
$StartLnk = Join-Path (Get-Folder 'Programs') 'Klava.lnk'
$DeskLnk  = Join-Path (Get-Folder 'Desktop') 'Klava.lnk'

if ($Uninstall) {
    Remove-Item -LiteralPath $StartLnk, $DeskLnk -ErrorAction SilentlyContinue
    if (Test-Path -LiteralPath $Dest) { Remove-Item -LiteralPath $Dest -Recurse -Force }
    Write-Host 'Klava has been removed.'
    return
}

New-Item -ItemType Directory -Force -Path (Join-Path $Dest 'packaging') | Out-Null
foreach ($f in 'index.html', 'texts-ru.js', 'texts-en.js') {
    Copy-Item -LiteralPath (Join-Path $Root $f) -Destination $Dest -Force
}
foreach ($f in 'icon.svg', 'icon.ico') {
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot $f) -Destination (Join-Path $Dest 'packaging') -Force
}

$Index = Join-Path $Dest 'index.html'
$Url   = ([System.Uri]$Index).AbsoluteUri
# Edge is part of Windows 10/11; --app opens the trainer in its own window without browser UI
$Edge = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

function New-KlavaShortcut([string]$Path) {
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut($Path)
    if ($Edge) {
        $lnk.TargetPath = $Edge
        $lnk.Arguments  = "--app=`"$Url`""
    } else {
        $lnk.TargetPath = $Index
    }
    $lnk.WorkingDirectory = $Dest
    $lnk.IconLocation     = (Join-Path $Dest 'packaging\icon.ico') + ',0'
    $lnk.Description      = 'Klava - offline touch typing trainer'
    $lnk.Save()
}

New-KlavaShortcut $StartLnk
if ($Desktop) { New-KlavaShortcut $DeskLnk }

Write-Host "Klava installed to $Dest"
Write-Host 'Find it in the Start menu: Klava'
