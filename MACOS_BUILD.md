# macOS Experimental Build

This project can produce an unsigned macOS app through GitHub Actions.

## What this provides

- `USWardExperienceLab.app`
- Packaged as `USWardExperienceLab_macos_unsigned_v0.1.0-beta.zip`
- Built on a GitHub-hosted macOS runner
- No Apple Developer Program membership required

## Important limitation

This macOS app is not code-signed or notarized.

Because of that, macOS Gatekeeper may show an "unidentified developer" warning or block the first launch.

For a public beta, label this build clearly as:

```text
macOS experimental unsigned build
```

## How to create the macOS build

1. Open the GitHub repository.
2. Go to `Actions`.
3. Select `Build macOS unsigned app`.
4. Click `Run workflow`.
5. Download the generated artifact after the workflow finishes.

The workflow file is:

```text
.github/workflows/build-macos.yml
```

## Suggested release label

```text
USWardExperienceLab_macos_unsigned_v0.1.0-beta.zip
```

## Suggested user note

```text
Mac version is experimental and unsigned. macOS may show an unidentified developer warning.
```
