# Pest Control CRM

This is a custom CRM I built for my friends Pest Control Buisness in Odoo19.

I used docker containers: odoo19, posgres15, browserless/chromium, and caddy to run the server, the versions are frozen to the sha256 of their versions to avoid breaking.

## Features

- Service Record management with in depth detail about the service and payment status
- Invoice Generation and archiving of PDF invoices WITHIN the posgres database (120kb)
- A calendar tracking the time of service jobs
- Contact page
- Tracking of locations, customers, job types, chemicals and traps used, automatic tax calculations etc..
- HTTPS reverse proxy using Caddy

## Technology Stack

- Odoo 19
- PostgreSQL 15
- Docker / Docker Compose
- Browserless / Chromium
- Caddy
- Python
- XML / QWeb
- HTML / CSS

## Setup

Clone the repository and copy `.env.example` to `.env`.

Edit `.env` with your PostgreSQL credentials, Browserless token, and domain name.

Start the project with:

```bash
docker compose up -d