param(
  [string]$WikiRepo = 'https://github.com/bantiagrawal/dr-pooja-clinic.wiki.git'
)

$ErrorActionPreference = 'Stop'
$tmp = Join-Path $PSScriptRoot '..\.wiki-publish'

if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }

try {
  git clone $WikiRepo $tmp | Out-Null
}
catch {
  Write-Host 'Wiki clone failed. Ensure wiki is enabled and at least one page exists:' -ForegroundColor Yellow
  Write-Host 'https://github.com/bantiagrawal/dr-pooja-clinic/wiki' -ForegroundColor Yellow
  throw
}

Set-Location $tmp
git config user.name 'bantiagrawal'
git config user.email 'banti.agrawal@gmail.com'

Copy-Item (Join-Path $PSScriptRoot '..\wiki\*.md') -Destination $tmp -Force

git add .
if ((git status --short).Length -eq 0) {
  Write-Host 'No wiki changes to publish.' -ForegroundColor Green
  exit 0
}

git commit -m 'Publish wiki pages' | Out-Null
git push origin master
Write-Host 'Wiki publish succeeded.' -ForegroundColor Green
