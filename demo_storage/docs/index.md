# Demo-storage Application

-{{% import 'icons.html' as icons %}}-

| <nbsp> {: .hide-th } |                                           |
| -------------------- |-------------------------------------------|
| **Group/Version**    | -{{ app_group }}-/-{{ app_api_version }}- |
| **Supported OS**     | -{{ supported_os_versions() }}-           |
| **Catalog**          | [eda-labs/catalog/demo-storage][manifest] |
| **Source Code**      | [eda-labs/demo-storage][source]           |

[manifest]: https://github.com/eda-labs/catalog/tree/main/apps/demo-storage.eda.labs
[source]: https://github.com/eda-labs/demo-storage


A minimal HTTP file server packaged as an EDA app. It provides a ready-to-use storage back-end for development clusters — no external object storage required.

> [!WARNING]
> **Lab / PoC only** — This server has no authentication and uses ephemeral (`emptyDir`) storage. Do not use it for production workloads.

## What it installs

| Resource | Kind | Namespace | Purpose |
|----------|------|-----------|---------|
| `demo-server` | `Deployment` + `Service` | `eda-system` | Python HTTP server on port 8080. Accepts file uploads and serves them back. Contents are lost on pod restart. |
| `demo-server-config` | `ConfigMap` | `eda-system` | Holds the embedded `http_server.py`, `index.css`, and `index.js`. |
| `demo-server` (HttpProxy) | `core.eda.nokia.com/v1 HttpProxy` | `eda-system` | Exposes the server through EDA's reverse proxy under `/core/httpproxy/v1/demo-server/`. |

The EDA system namespace (canonically `eda-system`) is not a fixed value — it is set at EDA install time and may differ across deployments. Manifests use `"${EDA_BASE_NAMESPACE}"` with `# eda-set:`.

## Installation

Register the [EDA Labs catalog](https://github.com/eda-labs/catalog) if you haven't already, then install from the EDA App Store (category *integrations*).

Verify the server is up after install:

```bash
kubectl -n eda-system get deployment demo-server
```

## Using the server

The server is available for in-cluster processes at `http://demo-server.eda-system.svc.cluster.local:8080`. It is exposed through the EDA reverse proxy at https://$EDA_FQDN/core/httpproxy/v1/demo-server

### Upload a file

```bash
curl -k -X PUT --upload-file ./myfile https://$EDA_FQDN/core/httpproxy/v1/demo-server/myfile
```

### Download a file

```bash
curl -k https://$EDA_FQDN/core/httpproxy/v1/demo-server/myfile
```

Open `https://$EDA_FQDN/core/httpproxy/v1/demo-server/` in a browser to list stored files, upload from the **Upload** button, download an entry, or delete it.

## Limitations

- **Ephemeral storage.** Files are lost when the pod restarts.
- **No authentication.** Anyone with network access can read and overwrite files.
- **HTTP only.** TLS is terminated by the EDA proxy; the pod listens on plain HTTP.
- **Single replica.** No high availability.

## Uninstall

From the EDA UI: **App Store -> Demo Storage -> Uninstall**.
