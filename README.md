# Bollyarr - Indian Movie Releases for Radarr

<div align="center">
  <img src="src/web/static/bollyarr-logo.png" alt="Bollyarr Logo" width="200"/>
  
  **Discover Indian movie releases each week and send them to Radarr**
  
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Wiki](https://img.shields.io/badge/wiki-documentation-blue)](https://github.com/kishlaymishra19/bollyarr/wiki)
</div>

---


Bollyarr discovers Indian-produced movies with releases in India during the selected week, then matches them against your Radarr library. Results come from TMDB and are ordered by popularity, not box-office revenue. You can review them in the web UI or enable filters and automatic adding.

For other regions, Bollyarr can continue to use Box Office Mojo's regional weekend charts.

## 📚 Documentation

**[View the full documentation in our Wiki](https://github.com/kishlaymishra19/bollyarr/wiki)** for detailed guides, configuration options, and troubleshooting.

## Indian Releases

Select **India** as the region to discover Indian-origin movies with an India release date in the selected week. TMDB popularity determines the order; it is not a box-office-gross ranking.

Enter the TMDB API key in the setup page. It is saved in `config/local.yaml`. Alternatively, set `TMDB_API_KEY` in the environment; that value takes precedence over the saved key.

## ✨ Key Features

- **Indian releases from TMDB** - Filters to Indian-origin movies with an India release date in the selected week
- **Popularity ranking** - Uses TMDB popularity because reliable Indian weekly gross data is not available
- **Radarr matching** - Matches discovered movies against your existing library
- **Optional automatic adding** - Apply language, genre, rating, release-year, and other filters
- **Weekly scheduling** - Review or process the selected release week automatically
- **Regional charts** - Use Box Office Mojo for non-India regions

## 📋 Requirements

- **Radarr** v3.0+ (required)
- **Docker** (recommended) or Python 3.10+
- Network access to TMDB for India, or Box Office Mojo for other regions
- A TMDB API key when India is selected

## 🚀 Quick Start

### Docker (Recommended)

```bash
docker run -d \
  --name bollyarr \
  -p 8888:8888 \
  -v /path/to/config:/config \
  ghcr.io/kishlaymishra19/bollyarr:latest
```

Visit `http://localhost:8888`, configure Radarr, select **India**, and enter your TMDB API key in the setup page.

### Docker Compose

```yaml
version: '3.8'

services:
  bollyarr:
    image: ghcr.io/kishlaymishra19/bollyarr:latest
    container_name: bollyarr
    ports:
      - 8888:8888
    volumes:
      - ./config:/config
    restart: unless-stopped
    environment:
      - TZ=America/New_York  # Optional: Set your timezone
```

The setup page stores the key in `config/local.yaml`. You can instead set `TMDB_API_KEY` in the environment; an environment key takes precedence over the saved key.

## ⚙️ Initial Setup

1. Open `http://localhost:8888`
2. Enter your Radarr URL and API key, then test the connection
3. Select **India** as the region and provide a TMDB API key
4. Choose your quality profile, root folder, and automatic-add preferences
5. Save; Bollyarr will use TMDB popularity to rank Indian releases for each selected week

**[View detailed setup guide →](https://github.com/kishlaymishra19/bollyarr/wiki/Initial-Setup)**

## 📖 Configuration & Features

- [India releases](#indian-releases) - TMDB filters and API key setup
- [Configuration](#advanced-configuration) - Region, timeout, and environment options
- [API](#api-access) - REST API access

## 🔧 Advanced Configuration

### Reverse Proxy Support

Bollyarr can run behind reverse proxies (nginx, Traefik, Caddy) with custom URL base support.

```yaml
environment:
  - BOXARR_URL_BASE=bollyarr  # Access at /bollyarr/
```

The `BOXARR_*` environment variable names remain supported for existing deployments.

**[View reverse proxy setup guide →](https://github.com/kishlaymishra19/bollyarr/wiki/Configuration-Guide#reverse-proxy-configuration)**

### Box Office Region & Timeout

By default Bollyarr tracks the US & Canada domestic chart. Set a Box Office Mojo `area` code to follow a different region, and tune the scraper timeout for slow connections.

```yaml
environment:
  - BOXARR_FEATURES_BOX_OFFICE_REGION=NL  # BOM area code (e.g. NL, DE, GB); empty = US & Canada domestic
  - BOXOFFICE_TIMEOUT=120                 # Box Office Mojo request timeout in seconds (default 120, range 5-600)
```

Select India (`IN`) to fetch Indian-origin releases from TMDB. Enter the TMDB API
key on the setup page, or set `TMDB_API_KEY` in the environment to override it.

### API Access

Bollyarr provides a REST API for integration and automation.

- **[Full API Reference →](https://github.com/kishlaymishra19/bollyarr/wiki/API-Reference)**

## 📸 Screenshots

<table>
  <tr>
    <td align="center">
      <img src="docs/dashboard.png" width="400"/>
      <br><b>Dashboard View</b>
    </td>
    <td align="center">
      <img src="docs/week-view.png" width="400"/>
      <br><b>Weekly Box Office</b>
    </td>
  </tr>
</table>

## 🆘 Help & Support

- **[Documentation Wiki](https://github.com/kishlaymishra19/bollyarr/wiki)** - Full documentation
- **[FAQ](https://github.com/kishlaymishra19/bollyarr/wiki/FAQ)** - Frequently asked questions
- **[Troubleshooting Guide](https://github.com/kishlaymishra19/bollyarr/wiki/Troubleshooting)** - Common issues and solutions
- **[GitHub Discussions](https://github.com/kishlaymishra19/bollyarr/discussions)** - Community support
- **[Report Issues](https://github.com/kishlaymishra19/bollyarr/issues)** - Bug reports and feature requests

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/kishlaymishra19/bollyarr/wiki/Contributing) for guidelines.

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Boxarr](https://github.com/iongpt/boxarr), the original project this fork builds on
- [Radarr](https://radarr.video/) for the excellent movie management platform
- [Box Office Mojo](https://www.boxofficemojo.com/) for box office data
- The self-hosting community for inspiration and feedback

## Disclaimer

This project is not affiliated with Box Office Mojo, IMDb, or Radarr. It's an independent tool created for personal media management.

---

Made with ❤️ for the self-hosting community
