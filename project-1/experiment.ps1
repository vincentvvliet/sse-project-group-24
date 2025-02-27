# PowerShell Script to install Python 3.11 and 3.14, set up environment, install dependencies, and run a benchmark
# Note: Run this script as Administrator to allow software installation and environment variable changes.

# Define Python versions and download URLs
$python311Version = "3.11.5"    # Adjust to the desired 3.11.x version available on python.org
$python314Version = "3.14.0"    # Adjust to the desired 3.14.x version (if not yet released, this download may fail)
$python311Installer = "python-$python311Version-amd64.exe"
$python314Installer = "python-3.14.0a5-amd64.exe"
$downloadUrl311 = "https://www.python.org/ftp/python/$python311Version/$python311Installer"
$downloadUrl314 = "https://www.python.org/ftp/python/$python314Version/$python314Installer"
$installerPath311 = "$env:TEMP\$python311Installer"
$installerPath314 = "$env:TEMP\$python314Installer"
$targetDir311 = "C:\Python311"
$targetDir314 = "C:\Python314"
$pythonExe311 = "$targetDir311\python.exe"
$pythonExe314 = "$targetDir314\python.exe"

# Define EnergiBridge paths
$energiBridgeUrl = "https://github.com/tdurieux/EnergiBridge/releases/download/v0.0.7/energibridge-v0.0.7-x86_64-pc-windows-msvc.zip"
$energiBridgeZip = "$env:TEMP\energibridge.zip"
$energiBridgeDir = "C:\EnergiBridge"

# Function to check if Python is installed
function Is-PythonInstalled {
    param ($pythonPath)
    return Test-Path $pythonPath
}

# Step 1: Check if Python 3.11 is already installed
if (Is-PythonInstalled $pythonExe311) {
    Write-Host "Python 3.11 is already installed at $targetDir311. Skipping installation."
} else {
    # Download Python 3.11
    Write-Host "Downloading Python $python311Version installer..."  
    try {
        Invoke-WebRequest -Uri $downloadUrl311 -OutFile $installerPath311 -ErrorAction Stop
        Write-Host "Python $python311Version installer downloaded to $installerPath311"
    } catch {
        Write-Error "Failed to download Python $python311Version installer. `nError: $($_.Exception.Message)"
        exit 1
    }

    Write-Host "Installing Python $python311Version to $targetDir311 (silent mode)..."
    # Use silent install options: /quiet for no UI, InstallAllUsers=1 for all users, PrependPath=0 to not modify PATH, Include_pip=1 to ensure pip is installed, and our TargetDir
    $installArgs311 = '/quiet PrependPath=1 Include_pip=1 InstallAllUsers=0 TargetDir="{0}"' -f $targetDir311
    $process311 = Start-Process -FilePath $installerPath311 -ArgumentList $installArgs311 -Wait -Passthru
    Write-Host "Python 3.11 installed successfully in $targetDir311."

    # Ensure pip is installed for Python 3.11
    Write-Host "Checking if pip is installed for Python 3.11..."
    if (-not (Test-Path $pythonExe311)) {
    Write-Error "Python 3.11 executable not found. Skipping pip installation."
    } else {
        try {
            & $pythonExe311  -m ensurepip --default-pip
            Write-Host "pip installed successfully using ensurepip."
        } catch {
            Write-Host "ensurepip failed. Installing pip manually..."
            Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "$env:TEMP\get-pip.py"
            & $pythonExe311 "$env:TEMP\get-pip.py"
            Write-Host "pip installed manually."
        }
    }
}

# Step 2: Check if Python 3.14 is already installed
if (Is-PythonInstalled $pythonExe314) {
    Write-Host "Python 3.14 is already installed at $targetDir314. Skipping installation."
} else {

    Write-Host "Downloading Python 3.14..."
    Invoke-WebRequest -Uri $downloadUrl314 -OutFile $installerPath314 -ErrorAction Stop
    Write-Host "Installing Python 3.14..."
    $installArgs314 = '/quiet InstallAllUsers=0 PrependPath=0 Include_pip=1 TargetDir="{0}"' -f $targetDir314
    $process311 = Start-Process -FilePath $installerPath314 -ArgumentList $installArgs314 -Wait -Passthru
    Write-Host "Python 3.14 installed successfully in $targetDir314."
}

# Step 3: Configure PATH environment variable to include the new Python install locations
Write-Host "Updating PATH environment variable to include Python installations..."
# Get the current system PATH, append new paths if not already present
$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$pathsToAdd = "$targetDir311;$targetDir314"
if ($machinePath -notlike "*$targetDir311*") {
    $newMachinePath = $machinePath.TrimEnd(';') + ";" + $pathsToAdd  # append to existing PATH
    [Environment]::SetEnvironmentVariable("Path", $newMachinePath, "Machine")  # set system PATH
}
# Also update the current session PATH so subsequent commands in this script can find the executables
if ($env:PATH -notlike "*$targetDir311*") {
    $env:PATH += ";$pathsToAdd"
}
Write-Host "PATH updated. (New entries: $pathsToAdd)"

# Step 4: Set PYTHON_3_11_PATH and PYTHON_3_14_PATH environment variables (for current session and system)
$env:PYTHON_3_11_PATH = "$targetDir311\python.exe"
$env:PYTHON_3_14_PATH = "$targetDir314\python.exe"
$env:PATH += ";C:\Python311\Scripts"
Write-Host "Set PYTHON_3_11_PATH and PYTHON_3_14_PATH environment variables."

# Verify that the Python executables are accessible and print their versions
try {
    $py311VersionOutput = & $env:PYTHON_3_11_PATH --version
    $py314VersionOutput = & $env:PYTHON_3_14_PATH --version
    Write-Host "Verified Python versions:" 
    Write-Host " - $py311VersionOutput (installed at $targetDir311)"
    Write-Host " - $py314VersionOutput (installed at $targetDir314)"
} catch {
    Write-Error "Verification failed: One of the Python executables is not accessible. `nError: $($_.Exception.Message)"
    exit 1
}

# Step 5: Install dependencies from requirements.txt using Python 3.11's pip
$requirementsFile = "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Installing Python 3.11 dependencies from $requirementsFile..."
    try {
        # Upgrade pip to the latest version, then install the requirements
        & $env:PYTHON_3_11_PATH -m pip install --upgrade pip
        & $env:PYTHON_3_11_PATH -m pip install -r $requirementsFile
        Write-Host "Dependencies installed successfully into Python 3.11 environment."
    } catch {
        Write-Error "Failed to install dependencies with pip. `nError: $($_.Exception.Message)"
        # Continue script execution even if pip installation fails (or use exit 1 to stop here if preferred)
        exit 1
    }
} else {
    Write-Warning "No requirements.txt found. Skipping dependency installation."
}

# Step 6: Download and Extract EnergiBridge
if (-not (Test-Path $energiBridgeDir)) {
    Write-Host "Downloading EnergiBridge..."
    Invoke-WebRequest -Uri $energiBridgeUrl -OutFile $energiBridgeZip -ErrorAction Stop
    Expand-Archive -Path $energiBridgeZip -DestinationPath $energiBridgeDir -Force
    Write-Host "EnergiBridge extracted to $energiBridgeDir."
} else {
    Write-Host "EnergiBridge is already installed at $energiBridgeDir. Skipping download."
}

# Step 7: Locate and Install the RAPL Kernel Driver
$raplDriver = Get-ChildItem -Path $energiBridgeDir -Filter "LibreHardwareMonitor.sys" -Recurse | Select-Object -ExpandProperty FullName

if ($raplDriver) {
    Write-Host "LibreHardwareMonitor.sys found at $raplDriver"
    
    # Check if the RAPL service already exists
    $existingService = sc.exe query rapl 2>$null
    if ($existingService -like "*does not exist*") {
        Write-Host "Creating RAPL kernel service..."
        sc.exe create rapl type=kernel binPath= "$raplDriver"
    } else {
        Write-Host "RAPL service already exists. Skipping creation."
    }
    
    # Start the service
    Write-Host "Starting RAPL service..."
    sc.exe start rapl
} else {
    Write-Error "Error: LibreHardwareMonitor.sys not found in $energiBridgeDir."
    exit 1
}

# Step 8: Execute the experiment script using Python 3.11
$experimentScript = "main.py"
if (Test-Path $experimentScript) {
    Write-Host "Running experiment script ($experimentScript) with Python 3.11..."
    try {
        & $env:PYTHON_3_11_PATH $experimentScript
        Write-Host "experiment script completed."
    } catch {
        Write-Error "experiment script execution failed. `nError: $($_.Exception.Message)"
        exit 1
    }
} else {
    Write-Error "experiment script '$experimentScript' not found. Ensure the script is in the current directory."
    exit 1
}