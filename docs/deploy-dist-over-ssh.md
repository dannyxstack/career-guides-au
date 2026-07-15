# 本地构建后上传 dist 到生产服务器

生产机内存不足以 `npm run build` 时，可以在本地完成构建，然后通过 SSH 上传 `site/dist`。

Windows PowerShell 脚本：

```powershell
.\scripts\deploy_dist.ps1 -HostName your.server.com -User deploy
```

Bash 脚本（Git Bash / WSL / macOS / Linux）：

```bash
scripts/deploy_dist.sh --host your.server.com --user deploy
```

默认行为：

- 本地目录：`site/dist`
- 远端目录：`/var/www/career-guides`
- 上传到：`/var/www/career-guides/releases/<timestamp>`
- 上传完成后切换：`/var/www/career-guides/current`
- 默认保留最近 3 个 release
- 默认使用 `rsync`，也可以用 `-Method scp`

## 推荐服务器目录

```text
/var/www/career-guides/
  current -> releases/20260713-153000
  releases/
    20260713-153000/
```

nginx 的静态站点 root 指向：

```nginx
root /var/www/career-guides/current;
index index.html;
```

这样上传期间 nginx 仍然读取旧的 `current`，只有上传成功后才会切到新目录。

## 常用命令

使用默认 SSH 端口：

```powershell
.\scripts\deploy_dist.ps1 -HostName example.com -User deploy
```

或：

```bash
scripts/deploy_dist.sh --host example.com --user deploy
```

指定远端目录：

```powershell
.\scripts\deploy_dist.ps1 -HostName example.com -User deploy -RemoteRoot /srv/career-guides
```

```bash
scripts/deploy_dist.sh --host example.com --user deploy --remote-root /srv/career-guides
```

指定 SSH key 和端口：

```powershell
.\scripts\deploy_dist.ps1 -HostName example.com -User deploy -Port 2222 -IdentityFile ~/.ssh/id_ed25519
```

```bash
scripts/deploy_dist.sh --host example.com --user deploy --port 2222 --identity-file ~/.ssh/id_ed25519
```

没有 rsync 时使用 scp：

```powershell
.\scripts\deploy_dist.ps1 -HostName example.com -User deploy -Method scp
```

```bash
scripts/deploy_dist.sh --host example.com --user deploy --method scp
```

scp 每次都会重传全部文件；`dist` 很大时，强烈建议在本机安装 `rsync`，后续部署会快很多。

## 首次部署前

服务器上需要能通过 SSH 登录，并且部署用户对远端目录有写权限：

```bash
sudo mkdir -p /var/www/career-guides/releases
sudo chown -R deploy:deploy /var/www/career-guides
```

如果 nginx 之前指向旧目录，改成：

```nginx
root /var/www/career-guides/current;
```

然后 reload nginx：

```bash
sudo nginx -t && sudo systemctl reload nginx
```

## 本地构建和发布

```powershell
cd site
npm run build
cd ..
.\scripts\deploy_dist.ps1 -HostName example.com -User deploy
```

Bash：

```bash
cd site
npm run build
cd ..
scripts/deploy_dist.sh --host example.com --user deploy
```

## 回滚

查看服务器上的 releases：

```bash
ls -lt /var/www/career-guides/releases
```

切回某个旧版本：

```bash
ln -sfn /var/www/career-guides/releases/20260713-153000 /var/www/career-guides/current.next
mv -Tf /var/www/career-guides/current.next /var/www/career-guides/current
```
