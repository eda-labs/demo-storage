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
| `demo-server-config` | `ConfigMap` | `eda-system` | Holds the embedded `http_server.py` and `upload.html`. |
| `demo-server` (HttpProxy) | `core.eda.nokia.com/v1 HttpProxy` | `eda-system` | Exposes the server through EDA's reverse proxy under `/core/httpproxy/v1/demo-server/`. |

## Installation

Register the [EDA Labs catalog](https://github.com/eda-labs/catalog) if you haven't already, then install from the EDA App Store (category *integrations*).

Verify the server is up after install:

```bash
kubectl -n eda-system get deployment demo-server
```

## Using the server

The server is available for in-cluster processes at `https://demo-server.eda-system.svc.cluster.local`. It is exposed through the EDA reverse proxy at https://$EDA_FQDN/core/httpproxy/v1/demo-server

### Upload a file

```bash
curl -k -X PUT --upload-file ./myfile https://$EDA_FQDN/core/httpproxy/v1/demo-server/myfile
```

There is also a web upload form at `https://$EDA_FQDN/core/httpproxy/v1/demo-server/upload.html`.

### Download a file

```bash
curl -k https://$EDA_FQDN/core/httpproxy/v1/demo-server/myfile
```

Open `https://$EDA_FQDN/core/httpproxy/v1/demo-server/` in a browser to see the list of stored files and click any entry to download it.

## Limitations

- **Ephemeral storage.** Files are lost when the pod restarts.
- **No authentication.** Anyone with network access can read and overwrite files.
- **HTTP only.** TLS is terminated by the EDA proxy; the pod listens on plain HTTP.
- **Single replica.** No high availability.

## Uninstall

From the EDA UI: **App Store -> Demo Storage -> Uninstall**.
