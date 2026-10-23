$ErrorActionPreference = "Stop"
$raiz = $PSScriptRoot
$directorioBuild = Join-Path $raiz "build"
$directorioDistribucion = Join-Path $raiz "dist"
$backend = Join-Path $directorioBuild "caminata_backend.exe"

if (-not (Get-Command g++ -ErrorAction SilentlyContinue)) {
    throw "No se encontró g++. Instala un compilador MinGW-w64 y agrégalo al PATH."
}
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "No se encontró PyInstaller. Instálalo con: python -m pip install pyinstaller"
}

New-Item -ItemType Directory -Force -Path $directorioBuild | Out-Null
New-Item -ItemType Directory -Force -Path $directorioDistribucion | Out-Null

$fuentes = @(
    (Join-Path $raiz "main.cpp"),
    (Join-Path $raiz "simulacion\sistema.cpp"),
    (Join-Path $raiz "simulacion\particula.cpp")
)
& g++ -std=c++17 -O2 -Wall -Wextra -pedantic -static -static-libgcc -static-libstdc++ @fuentes -o $backend
if ($LASTEXITCODE -ne 0) {
    throw "Falló la compilación del backend C++."
}

$argumentosPyInstaller = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", "CaminataAleatoria",
    "--add-binary", "$backend;.",
    "--distpath", $directorioDistribucion,
    "--workpath", (Join-Path $directorioBuild "pyinstaller"),
    "--specpath", $directorioBuild,
    (Join-Path $raiz "interfaz.py")
)
& pyinstaller @argumentosPyInstaller
if ($LASTEXITCODE -ne 0) {
    throw "Falló el empaquetado de la interfaz."
}

Write-Host "Ejecutable creado: $(Join-Path $directorioDistribucion 'CaminataAleatoria.exe')"
