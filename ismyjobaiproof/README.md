# Is My Job AI-Proof?

Lightweight static assessment for `ismyjobaiproof.com`. The browser receives only a thin occupation search/scoring index; full career data stays on the related sites.

## Build the occupation index

```powershell
node .\ismyjobaiproof\build-data.mjs
```

The script reads `site/src/data/occupations_v2.json`, deduplicates occupations by slug and writes only these fields to `data/occupations.json`:

- name, slug and category
- available countries
- baseline AI exposure
- human moat
- AI augmentation upside

## Preview locally

```powershell
node .\ismyjobaiproof\serve.mjs
```

Open `http://127.0.0.1:4177/`.

After building, preview the generated occupation and trust pages with:

```powershell
$env:PREVIEW_DIST='1'; node .\ismyjobaiproof\serve.mjs
```

## Deploy

Generate a clean production directory. No Node.js runtime is required on the server.

```powershell
node .\ismyjobaiproof\build-data.mjs
node .\ismyjobaiproof\build-site.mjs
```

The build creates four methodology and trust pages, 550 diverse occupation baseline
pages, a filterable ranking page, a complete sitemap, `robots.txt`, `llms.txt`, and
the compact occupation index. The first 50 roles are curated in `site-content.mjs`;
500 additional roles are selected deterministically with category balancing and
title-similarity filtering.
Run production checks after each build:

```powershell
node .\ismyjobaiproof\test-site.mjs
```

Occupation pages are selected in `site-content.mjs`. Do not hand-edit generated
files under `dist/job/`.

The deployable files are written to `ismyjobaiproof/dist/`. Upload them with the repository's atomic release script from Git Bash or WSL:

```bash
bash scripts/deploy_dist.sh \
  --host YOUR_SERVER_IP \
  --user deploy \
  --local-dist ismyjobaiproof/dist \
  --remote-root /var/www/ismyjobaiproof \
  --identity-file ~/.ssh/id_ed25519
```

Test the command first by adding `--dry-run`. The script uploads into a timestamped release and switches `/var/www/ismyjobaiproof/current` only after `index.html` is present, so the live site keeps serving the previous release during upload.

Point Nginx at `/var/www/ismyjobaiproof/current`. A complete virtual-host example is provided in `nginx-ismyjobaiproof.conf.example`. The TLS certificate paths in that file assume Certbot and must be adjusted if the server uses another certificate manager.

Initial server preparation:

```bash
sudo mkdir -p /var/www/ismyjobaiproof/releases
sudo chown -R deploy:deploy /var/www/ismyjobaiproof
```

Run the first deployment, then copy both Nginx examples to the server. Enable the HTTP bootstrap configuration first:

```bash
sudo cp nginx-http-bootstrap.conf.example /etc/nginx/sites-available/ismyjobaiproof.com
sudo ln -s /etc/nginx/sites-available/ismyjobaiproof.com /etc/nginx/sites-enabled/ismyjobaiproof.com
sudo nginx -t
sudo systemctl reload nginx
```

Create a certificate covering both hostnames, then replace the bootstrap configuration with the final HTTPS configuration:

```bash
sudo certbot certonly --webroot \
  -w /var/www/ismyjobaiproof/current \
  -d ismyjobaiproof.com \
  -d www.ismyjobaiproof.com
sudo cp nginx-ismyjobaiproof.conf.example /etc/nginx/sites-available/ismyjobaiproof.com
sudo nginx -t
sudo systemctl reload nginx
```

External destinations are configured at the top of `app.js`. Update them if the final URL structures of the related sites change.

The browser also dispatches privacy-minimised `ijap:event` events and pushes the
same payloads to `window.dataLayer` when one exists. These events contain no task
answers, country, career level, or goal. Analytics and consent configuration remain
an operator-level deployment choice.

Enable Brotli or gzip on the web server. The generated occupation index is about 1 MB uncompressed and about 100–130 KB over Brotli/gzip. A suitable cache policy is:

- `index.html`, `robots.txt`, `sitemap.xml`: short cache or revalidation;
- `styles.css`, `app.js`: one hour until filenames are content-hashed;
- `data/occupations.json`: one day, refreshed whenever the source data changes.

## Scoring boundary

The assessment is an interpretable planning tool, not an individual job-loss probability. It combines:

1. occupation-level AI exposure, human moat and augmentation baselines;
2. the user's task mix;
3. digital, repeatability, accountability, relationship and uncertainty factors;
4. career level and workplace AI adoption.

Answers remain in browser memory and are not transmitted.
