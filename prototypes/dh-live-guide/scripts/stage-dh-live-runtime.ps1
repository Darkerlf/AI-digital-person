param(
    [Parameter(Mandatory = $true)]
    [string] $SourceStaticDir,
    [string] $RuntimeDir = ''
)

$ErrorActionPreference = 'Stop'
$prototypeRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = (Resolve-Path $SourceStaticDir).Path
$runtime = if ($RuntimeDir) {
    [System.IO.Path]::GetFullPath($RuntimeDir)
} else {
    Join-Path $prototypeRoot 'runtime'
}
if ([System.IO.Path]::GetPathRoot($runtime) -eq $runtime) {
    throw "Refusing to replace a filesystem root as the DH_live runtime directory."
}
$required = @(
    'DHLiveMini.wasm',
    'js\DHLiveMini.js',
    'js\MiniMateLoader.js',
    'js\MiniLive2.js',
    'js\pako.min.js',
    'assets\01.mp4',
    'assets\combined_data.json.gz',
    'background\bg.mp4'
)

foreach ($relativePath in $required) {
    if (-not (Test-Path (Join-Path $source $relativePath))) {
        throw "DH_live runtime file missing: $relativePath"
    }
}

if (Test-Path $runtime) {
    Remove-Item -LiteralPath $runtime -Recurse -Force
}
New-Item -ItemType Directory -Path $runtime | Out-Null

Copy-Item -LiteralPath (Join-Path $source 'DHLiveMini.wasm') -Destination $runtime
foreach ($directory in @('js', 'assets', 'background', 'common')) {
    $candidate = Join-Path $source $directory
    if (Test-Path $candidate) {
        Copy-Item -LiteralPath $candidate -Destination $runtime -Recurse
    }
}

$idleStill = Join-Path $prototypeRoot 'assets\idle-open-cover.png'
$runtimeIdleStill = Join-Path $runtime 'assets\idle-open-cover.png'
if ((-not (Test-Path $runtimeIdleStill)) -and (Test-Path $idleStill)) {
    New-Item -ItemType Directory -Path (Join-Path $runtime 'assets') -Force | Out-Null
    Copy-Item -LiteralPath $idleStill -Destination $runtimeIdleStill -Force
}

Copy-Item -LiteralPath (Join-Path $prototypeRoot 'shell\index.html') -Destination (Join-Path $runtime 'index.html')
Write-Output "DH_live runtime staged at $runtime"
