# Per-repo fleet start config for jellyfin-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'jellyfin-mcp'
    BackendPort  = 10934
    FrontendPort = 10935
    HealthPath   = '/health'
    WebRoot      = 'webapp\frontend'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'app.main:app'
        WorkDir       = 'webapp\backend'
        PythonPath    = 'webapp\backend;src'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10934' }
    }
    Frontend = @{
        Kind           = 'next'
        PackageManager = 'npm'
        PortEnvVar     = 'PORT'
        ApiTargetEnv   = 'API_URL'
    }
}
