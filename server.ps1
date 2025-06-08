param (
    [int]$Port = 8000
)

Add-Type -AssemblyName System.Net.HttpListener
$listener = New-Object System.Net.HttpListener
$prefix = "http://*:$Port/"
$listener.Prefixes.Add($prefix)
$listener.Start()
Write-Host "Simple PowerShell HTTP server running on $prefix"
Write-Host "Serving files from $(Get-Location)"

while ($true) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response

    $urlPath = [System.Web.HttpUtility]::UrlDecode($request.Url.AbsolutePath.TrimStart('/'))
    if ([string]::IsNullOrEmpty($urlPath)) {
        $urlPath = "."
    }
    $localPath = Join-Path -Path (Get-Location) -ChildPath $urlPath

    if (Test-Path $localPath) {
        if (Test-Path $localPath -PathType Container) {
            $files = Get-ChildItem $localPath
            $html = "<html><body><h2>Index of /$urlPath</h2><ul>"
            if ($urlPath -ne '.') {
                $parent = [System.IO.Path]::GetDirectoryName($urlPath.TrimEnd('/'))
                if (-not $parent) { $parent = '.' }
                $html += "<li><a href='/$parent'>.. (parent directory)</a></li>"
            }
            foreach ($file in $files) {
                $name = $file.Name
                $link = [System.Web.HttpUtility]::UrlEncode($name)
                if ($urlPath -ne '.') {
                    $link = "$urlPath/$link"
                }
                if ($file.PSIsContainer) {
                    $html += "<li><b><a href='/$link/'>$name/</a></b></li>"
                }
                else {
                    $html += "<li><a href='/$link'>$name</a></li>"
                }
            }
            $html += "</ul></body></html>"
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($html)
            $response.ContentType = "text/html; charset=utf-8"
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }
        else {
            try {
                $fileStream = [System.IO.File]::OpenRead($localPath)
                $response.ContentType = "application/octet-stream"
                $response.ContentLength64 = $fileStream.Length
                $buffer = New-Object byte[] 65536
                while (($read = $fileStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                    $response.OutputStream.Write($buffer, 0, $read)
                }
                $fileStream.Close()
            }
            catch {
                $response.StatusCode = 500
                $errorMsg = "Internal Server Error: $_"
                $buffer = [System.Text.Encoding]::UTF8.GetBytes($errorMsg)
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            }
        }
    }
    else {
        $response.StatusCode = 404
        $msg = "<html><body><h1>404 Not Found</h1><p>$urlPath</p></body></html>"
        $buffer = [System.Text.Encoding]::UTF8.GetBytes($msg)
        $response.ContentType = "text/html; charset=utf-8"
        $response.ContentLength64 = $buffer.Length
        $response.OutputStream.Write($buffer, 0, $buffer.Length)
    }
    $response.OutputStream.Close()
}
