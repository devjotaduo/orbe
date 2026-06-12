# Abre um Pull Request DENTRO do seu fork (base = devjotaduo/orbe),
# nunca no upstream agentscope-ai/QwenPaw.
#
# O GitHub não permite mudar o "base repository" padrão de um fork — ele
# sempre vem pré-marcado com o upstream. Este script contorna isso abrindo
# direto a URL de comparação do PRÓPRIO fork, então o seletor de base nem
# aparece. Uso:
#
#   git pr-fork                 # PR da branch atual -> main do fork
#   git pr-fork develop         # PR da branch atual -> develop do fork
#
# Se o alias 'git pr-fork' nao existir (ex.: clone novo), registre com:
#   git config alias.pr-fork '!powershell -NoProfile -ExecutionPolicy Bypass -File scripts/open-pr.ps1'
#
# Equivalente manual: no GitHub, trocar "base repository" para
# devjotaduo/orbe antes de criar o PR.

param([string]$Base = "main")

$ErrorActionPreference = "Stop"
$Fork = "devjotaduo/orbe"

$branch = (git rev-parse --abbrev-ref HEAD).Trim()

if ($branch -eq $Base) {
    Write-Host "Voce esta na branch '$Base' — nao da para abrir PR de '$Base' para '$Base'." -ForegroundColor Yellow
    Write-Host "Crie/troque para uma feature branch primeiro:  git switch -c minha-feature" -ForegroundColor Yellow
    exit 1
}

# Garante que a branch existe no remoto (senao o GitHub nao mostra o diff)
Write-Host "Enviando a branch '$branch' para o seu fork (origin)..." -ForegroundColor Cyan
git push -u origin $branch

$url = "https://github.com/$Fork/compare/$Base...$branch`?expand=1"
Write-Host ""
Write-Host "PR no SEU fork (base: $Fork`:$Base  <-  $branch):" -ForegroundColor Green
Write-Host "  $url"
Start-Process $url
