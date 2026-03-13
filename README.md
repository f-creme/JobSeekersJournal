<div align="center">

# JobSeekersJournal

**Simple web application built with Streamlit to track and organize job applications**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)]()
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

</div>

## 📋 Features

<table width="100%">

<tr>
<td align="center" width="2%">
    <b>📌 Job Management</b>
</td>

<td align="center" width="2%">
    <b>🗂 Application Tracking</b>
</td>

<td align="center" width="2%">
    <b>📊 Analytics</b>
</td>

</tr>
<td valign="top">
    <ul>
        <li>Add and edit job offers</li>
        <li>Store company, locations and details</li>
        <li>List or detailed view of saved jobs</li>
    </ul>
</td>

<td valign="top">
    <ul>
        <li>Track application status</li>
        <li>Record application timeline</li>
        <li>Organize applications by status</li>
    </ul>
</td>

<td valign="top">
    <ul>
        <li>Application statistics</li>
        <li>Weekly activity overview</li>
        <li>Status distribution</li>
        <li>Map of job opportunities</li>
    </ul>
</td>

</table>


## 🚀 Quick Start with Docker

### 1. Clone the repository

```bash
git clone https://github.com/f-creme/JobSeekersJournal.git
cd JobSeekersJournal
```

### 2. Build the Docker image

```bash
docker build -t jobseekersjournal .
```

### 3. Run the container

* Application data is stored in `/app/data` inside the container. To persist data between runs, mount a local directory: `path/to/local/data`.
* Chose a user agent name (`NOMINATIM_USER`) to locate the job offers on the map with [Nominatim](https://nominatim.org) search engine.

```bash
export NOMINATIM_USER="jobseekersjournal/0.1 (your.email@domain.com)"

docker run -p 8501:8501 \
           -v path/to/local/data:/app/data \
           -e NOMINATIM_USER_AGENT="$NOMINATIM_USER" \
           --name jobseekersjournal \
           jobseekersjournal
```

### 4. Open the application

Once the container is running, open your browser and go to: http://localhost:8501.

## 📦 Manual installation

To run the app without Docker:

```bash
uv sync
uv run streamlit run entrypoint.py
```

## 📄 License
MIT License. See the [LICENSE](LICENSE) file for details.