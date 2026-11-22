# Renders each slide of what-goes-dark.pptx to presentacion/render/slide-NN.png using PowerPoint.
param([int[]]$Solo = @())
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$out = Join-Path $dir "render"
New-Item -ItemType Directory -Force $out | Out-Null
$pp = New-Object -ComObject PowerPoint.Application
try {
  $pres = $pp.Presentations.Open((Join-Path $dir "what-goes-dark.pptx"), $true, $false, $false)
  "Slides: " + $pres.Slides.Count
  foreach ($s in $pres.Slides) {
    if ($Solo.Count -eq 0 -or $Solo -contains $s.SlideIndex) {
      $s.Export((Join-Path $out ("slide-{0:D2}.png" -f $s.SlideIndex)), "PNG", 1600, 900)
    }
  }
  $pres.Close()
} finally { $pp.Quit() }
