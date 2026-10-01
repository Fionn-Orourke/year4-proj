[CmdletBinding()]param([string]$RepositoryRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')),[switch]$DryRun)
$ErrorActionPreference='Stop'; $a=@((Join-Path $PSScriptRoot 'processor.py'),'--root',$RepositoryRoot); if($DryRun){$a+='--dry-run'}; & python @a; if($LASTEXITCODE){exit $LASTEXITCODE}
