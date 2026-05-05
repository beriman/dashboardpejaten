# Dashboard Progress Renovasi Pejaten

Static site package untuk Vercel/GitHub.

File `public/index.html` digenerate otomatis dari dashboard di Google Drive lokal dan file data pendampingnya.

## Local build

```powershell
python ..\..\scripts\build_pejaten_dashboard_web.py
```

## Publish flow

```powershell
..\..\scripts\publish_pejaten_dashboard_web.ps1
```

Setelah folder ini dihubungkan ke GitHub + Vercel, setiap `git push` akan memicu deploy otomatis.
