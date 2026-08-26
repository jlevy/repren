## Installing uv and Python

This project uses [**uv**](https://docs.astral.sh/uv/) to install Python versions and
manage Python tools and project environments.
This is a quick setup guide.

On macOS or Linux, if you don’t have `uv` installed, a quick way to install it:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On macOS, if you prefer [brew](https://brew.sh/), you can install or upgrade uv with:

```shell
brew update
brew install uv
```

See [uv’s docs](https://docs.astral.sh/uv/getting-started/installation/) for more
installation methods and platforms.

Now you can use uv to install a current Python environment:

```shell
uv python install 3.14 # Or pick another supported version.
```

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
