$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression
$taskDir = Join-Path (Get-Location) '.codex-tmp/owner-report'
$source = 'C:\Users\doann\Downloads\Mau_bao_cao_de_xuat_owner_POCS_dong_bo_schema.truoc_khi_dien.docx'
$output = Join-Path $taskDir 'Mau_bao_cao_de_xuat_owner_POCS_dong_bo_schema.docx'
$payload = Get-Content -LiteralPath (Join-Path $taskDir 'content.json') -Encoding UTF8 -Raw | ConvertFrom-Json
Copy-Item -LiteralPath $source -Destination $output -Force
$archive = [IO.Compression.ZipFile]::Open($output, [IO.Compression.ZipArchiveMode]::Update)
try {
    $entry = $archive.GetEntry('word/document.xml')
    $reader = [IO.StreamReader]::new($entry.Open())
    [xml]$document = $reader.ReadToEnd()
    $reader.Close()
    $ns = [Xml.XmlNamespaceManager]::new($document.NameTable)
    $uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    $ns.AddNamespace('w', $uri)
    function Read-Text($node) { return ($node.SelectNodes('.//w:t', $ns) | ForEach-Object { $_.InnerText }) -join '' }
    function Set-Text($node, [string]$text) {
        foreach ($child in @($node.ChildNodes)) { if ($child.LocalName -ne 'pPr') { [void]$node.RemoveChild($child) } }
        $run = $document.CreateElement('w', 'r', $uri)
        $textNode = $document.CreateElement('w', 't', $uri)
        $textNode.SetAttribute('space', 'http://www.w3.org/XML/1998/namespace', 'preserve')
        $textNode.InnerText = $text
        [void]$run.AppendChild($textNode)
        [void]$node.AppendChild($run)
    }
    $nodes = @($document.SelectNodes('//w:body/w:*', $ns))
    Set-Text $nodes[1] 'Phạm vi đề xuất: Toàn nhóm 4 | Ngày đối chiếu: 09/11/2026'
    $intro = $document.CreateElement('w', 'p', $uri)
    Set-Text $intro 'Đề xuất chung: tiếp tục dùng Parser và Text Diff hiện có làm nền tảng; phân tích ngữ nghĩa hiện mới là baseline phạm vi hẹp. Các phương án dưới đây để owner và bên nhận cùng review, chưa thay thế quyết định đã chốt. Những nội dung chưa đủ căn cứ lựa chọn được ghi Chưa có phương án.'
    [void]$nodes[2].ParentNode.InsertAfter($intro, $nodes[2])
    $note = $document.CreateElement('w', 'p', $uri)
    Set-Text $note 'Bản đối chiếu sau merge main ngày 09/11/2026 tại e0f5068, nhập origin/main f76610e: đã có contracts.py, validator, decision.md, docs/test_evaluation_plan.md và Pipeline/API upload. Module Linker, Context, AI Adapter và các file change_analysis mới vẫn là khung; analysis_runner mặc định chưa được nối. Schema chạy 51 ca với 2 expected failures; module Ngọc Anh đạt 16/16. Các đề xuất dưới đây phân biệt phần contract đã có với implementation và chất lượng nghiệp vụ còn cần kiểm chứng. Phân công theo decision.md và module.md sau merge.'
    [void]$intro.ParentNode.InsertAfter($note, $intro)
    $currentCode = $null
    $slot = -1
    $filled = 0
    foreach ($node in $nodes) {
        if ($node.LocalName -ne 'p') { continue }
        $text = Read-Text $node
        if ($text -match '^((?:CN|LK)-\d{2})\s+[—–-]') { $currentCode = $Matches[1]; $slot = -1 }
        if ($text -match '^Phương án 1') { $slot = 0; continue }
        if ($text -match '^Phương án 2') { $slot = 1; continue }
        if ($null -ne $currentCode -and $slot -ge 0 -and [string]::IsNullOrWhiteSpace($text)) {
            $property = $payload.PSObject.Properties[$currentCode]
            if ($null -eq $property) { throw "Missing content for $currentCode" }
            Set-Text $node $property.Value[$slot]
            $spacing = $node.SelectSingleNode('w:pPr/w:spacing', $ns)
            if ($null -ne $spacing) {
                $spacing.SetAttribute('line', $uri, '264')
                $spacing.SetAttribute('lineRule', $uri, 'auto')
                $spacing.SetAttribute('after', $uri, '100')
            }
            $slot = -1
            $filled++
        }
    }
    if ($filled -ne 42) { throw "Expected 42 filled slots, got $filled" }
    $entry.Delete()
    $newEntry = $archive.CreateEntry('word/document.xml')
    $stream = $newEntry.Open()
    $settings = [Xml.XmlWriterSettings]::new()
    $settings.Encoding = [Text.UTF8Encoding]::new($false)
    $writer = [Xml.XmlWriter]::Create($stream, $settings)
    $document.Save($writer)
    $writer.Close()
    $stream.Close()
    Write-Output "Filled $filled slots in $output"
} finally { $archive.Dispose() }

