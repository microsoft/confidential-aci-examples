param($ipAddress)

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add('http://*:8000/')
$listener.Prefixes.Add('http://*:8001/')
$listener.Start()

while ($listener.IsListening)
{
    $context = $listener.GetContext()
    $requestUrl = $context.Request.Url
    $endpoint = $requestUrl.Segments[-1]
    $port = $requestUrl.Port
    $response = $context.Response

    echo "Received request for $($requestUrl.AbsoluteUri)"

    $passthroughCall = "http://${ipAddress}:$port/$endpoint"
    $buffer = Invoke-WebRequest -Uri $passthroughCall -UseBasicParsing | Select-Object -ExpandProperty Content
    $bufferBytes = [System.Text.Encoding]::UTF8.GetBytes($buffer)
    $response.ContentLength64 = $bufferBytes.Length
    $response.OutputStream.Write($bufferBytes, 0, $bufferBytes.Length)
    $response.Close()
}