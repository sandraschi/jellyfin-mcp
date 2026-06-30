# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [("src/jellyfin_mcp", "jellyfin_mcp")]
for pkg in ("fastmcp", "fastapi", "uvicorn", "pydantic", "starlette", "httpx"):
    datas += copy_metadata(pkg)

a = Analysis(
    ["run_server.py"],
    pathex=["src"],
    binaries=[],
    
    datas=datas,
    hiddenimports=[

    "_datetime",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "jellyfin_mcp.tools.portmanteau",
        "jellyfin_mcp.services.registry",
        "jellyfin_mcp.transport",
    "_strptime",
],
    hookspath=[],
    
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "torch",
        "torchvision",
        "torchaudio",
        "sentence_transformers",
        "transformers",
        "lancedb",
        "tensorboard",
    ],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    
    name="jellyfin-mcp-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)





