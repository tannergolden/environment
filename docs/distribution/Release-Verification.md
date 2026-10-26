<!--
title: '🔏 RELEASE VERIFICATION'
description: 'How to check that an image of the environment was built by this repository from its source, from the provenance attestation on its digest, how to pin that digest, and how to read the SBOM of each architecture on its release.'
type: guide
-->

<div align="center">

# 🔏 RELEASE VERIFICATION

<a name="top"></a>

**How to check that the image you pull was built here, from this source.**

_Trust the signature and the digest, not the tag._

</div>

---

## 📦 1. What A Release Carries

🏷️ Cut Release publishes each version in three places:

| Where                                    | What                                                                                                                                              | Attested                                                                        |
| :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------ |
| `ghcr.io/tannergolden/environment:X.Y.Z` | The image: a list of one image per architecture, `linux/amd64` and `linux/arm64`. `X` and `latest` name the same list when the release moved them | Yes: a build provenance attestation on the list's digest                        |
| The release page for `vX.Y.Z`            | `sbom-linux-amd64.cdx.json` and `sbom-linux-arm64.cdx.json`: a CycloneDX SBOM of each architecture's image                                        | No                                                                              |
| The git tag `vX.Y.Z`                     | The source, including the files a pinned cloud setup script downloads                                                                             | No: the [cloud setup script](../../setup/README.md) checks each against its pin |

The attestation is a signed statement that names the image's digest, the
repository and commit it was built from, and the workflow that built it. There
is no long-lived key to fetch: GitHub signs each attestation with a short-lived
certificate issued to the workflow run, and `gh` checks it against Sigstore's
public trust root.

---

## 🔐 2. Verify The Image

This needs the GitHub CLI, `gh`, signed in with `gh auth login`:

```bash
gh attestation verify oci://ghcr.io/tannergolden/environment:1.0.0 \
  --repo tannergolden/environment \
  --signer-workflow tannergolden/standards/.github/workflows/publish-package.yml
```

- **`oci://`** has `gh` resolve the tag to the image's digest and check the
  attestation recorded for that digest. A tag can move; what passed is the
  digest it resolved to.
- **`--repo tannergolden/environment`** checks that the image was built from
  this repository.
- **`--signer-workflow`** pins the identity that signed it. The attestation is
  made inside the standards' shared `publish-package.yml`, which 🏷️ Cut Release
  calls, so that workflow is the signer, and a valid attestation from any other
  workflow fails.
- **A pass**: `gh` says verification succeeded and exits with status 0.
  Anything else is a failure.

To keep what passed, read its digest, and name the image by it where nothing
may move:

```bash
docker buildx imagetools inspect ghcr.io/tannergolden/environment:1.0.0
```

The `Digest:` line it prints is the list's digest, which a
`devcontainer.json` can name in place of the tag:
`"image": "ghcr.io/tannergolden/environment@sha256:<digest>"`.

> [!NOTE]
> **The package has to be public** for a machine to pull it, and to check it,
> without signing in to the registry. A private package needs
> `docker login ghcr.io` first.

---

## 🧾 3. Inspect The SBOMs

```bash
gh release download v1.0.0 --repo tannergolden/environment --pattern 'sbom-linux-*.cdx.json'
jq -r '.components[] | "\(.name) \(.version)"' sbom-linux-arm64.cdx.json | sort | head
```

Each SBOM is CycloneDX JSON, made from the published image of one
architecture: Ubuntu's packages, the Python and npm packages, and the tools the
image holds. Each entry under `components` has a name, a version and a package
URL (`purl`). Read it with any JSON tool, as above, or load it into a scanner
that reads CycloneDX to see whether a release ships a component with a known
vulnerability.

The SBOMs are not attested: they list what each image holds, and prove nothing
about who built it.

---

## ☁️ 4. The Cloud Setup Script

`make cloud-setup VERSION=vX.Y.Z` prints the script with the SHA-256 of every
file it downloads, taken from the tag in your own clone, and the script refuses
any file that does not match. So print it from a clone whose tags came from
this repository (`git fetch --tags`), and check that the version it names is
the release you meant.

---

## 🚩 5. If Verification Fails

1. **Do not use the image.** Remove it with `docker image rm`, and do not open
   a container from it.
2. **Rule out the simple causes**: a mistyped image name or `--repo`, `gh` not
   signed in, or a version from before `v1.0.0`, the first release.
3. **If it still fails, report it privately.** Follow
   [SECURITY.md](../../.github/SECURITY.md): choose **Report a vulnerability**
   on the **Security** tab. Give the image reference, its digest, the exact
   command and its full output. Do not open a public issue: treat an image that
   fails verification as tampered with until it is shown not to be.

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**Checked before it runs, reported before it spreads.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
