param(
  [string]$WikiRepo = 'https://github.com/bantiagrawal/dr-pooja-clinic.wiki.git'
)

$tmp = Join-Path $PSScriptRoot '..\\.wiki-publish'
if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
New-Item -ItemType Directory -Force $tmp | Out-Null
Set-Location $tmp
git init -b master | Out-Null
git config user.name 'bantiagrawal'
git config user.email 'banti.agrawal@gmail.com'
Copy-Item (Join-Path $PSScriptRoot '..\\wiki\\*.md') -Destination $tmp -Force
git add .
git commit -m 'Publish wiki pages' | Out-Null
git remote add origin $WikiRepo
git push -u origin master

