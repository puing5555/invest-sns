# Get all .tsx files in app/ and components/ directories
$files = Get-ChildItem -Path "C:\Users\Mario\work\invest-sns" -Filter "*.tsx" -Recurse | Where-Object { $_.FullName -like "*\app\*" -or $_.FullName -like "*\components\*" }

# Color replacement mappings
$replacements = @{
    # Background colors - keep bg-white as is
    'bg-\[#f7f9fa\]' = 'bg-[#f4f4f4]'
    'bg-\[#f0f2f5\]' = 'bg-[#f2f4f6]'
    'bg-gray-50' = 'bg-[#f2f4f6]'
    'bg-gray-100' = 'bg-[#f2f4f6]'
    
    # Accent color replacements - IMPORTANT #00d4aa -> #3182f6
    'bg-\[#00d4aa\]' = 'bg-[#3182f6]'
    'text-\[#00d4aa\]' = 'text-[#3182f6]'
    'border-\[#00d4aa\]' = 'border-[#3182f6]'
    '#00d4aa' = '#3182f6'
    'hover:bg-\[#00b894\]' = 'hover:bg-[#1b64da]'
    
    # Text colors
    'text-\[#111827\]' = 'text-[#191f28]'
    'text-gray-900' = 'text-[#191f28]'
    'text-gray-500' = 'text-[#8b95a1]'
    'text-gray-400' = 'text-[#8b95a1]'
    'text-\[#888\]' = 'text-[#8b95a1]'
    
    # Success/failure colors
    'text-\[#22c55e\]' = 'text-[#00c853]'
    'text-\[#16a34a\]' = 'text-[#00c853]'
    'bg-\[#22c55e\]' = 'bg-[#00c853]'
    'bg-\[#16a34a\]' = 'bg-[#00c853]'
    'text-\[#dc2626\]' = 'text-[#f44336]'
    'text-\[#ef4444\]' = 'text-[#f44336]'
    'bg-\[#dc2626\]' = 'bg-[#f44336]'
    'bg-\[#ef4444\]' = 'bg-[#f44336]'
    'bg-\[#ff4444\]' = 'bg-[#f44336]'
    'text-\[#ff4444\]' = 'text-[#f44336]'
    
    # Borders
    'border-\[#e5e7eb\]' = 'border-[#e8e8e8]'
    'border-\[#eff3f4\]' = 'border-[#f0f0f0]'
    
    # Card styling
    'rounded-xl' = 'rounded-2xl'
    'rounded-lg' = 'rounded-xl'
    'shadow-sm' = 'shadow-[0_2px_8px_rgba(0,0,0,0.04)]'
}

# Sidebar specific replacements (will be handled separately)
$sidebarSpecific = @{
    # Sidebar background should be white, not #f4f4f4
    # Selected menu styling
    # These will be handled separately for Sidebar.tsx
}

# Process each file
foreach ($file in $files) {
    Write-Host "Processing: $($file.FullName)"
    
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    
    # Apply all replacements
    foreach ($pattern in $replacements.Keys) {
        $replacement = $replacements[$pattern]
        $content = $content -replace $pattern, $replacement
    }
    
    # Only write if content changed
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        Write-Host "  Updated: $($file.Name)"
    } else {
        Write-Host "  No changes: $($file.Name)"
    }
}

Write-Host "Bulk color replacement completed!"