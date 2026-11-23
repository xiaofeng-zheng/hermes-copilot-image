# Copilot Image for Hermes Agent

A text-to-image backend for Hermes Agent’s existing `image_generate` tool. It calls GitHub Copilot over HTTPS using the Copilot account already configured in Hermes. No Copilot CLI or OpenAI API key is required.

## Requirements and setup

Enable the Hermes `github-copilot` provider plugin, sign in to Copilot in Hermes, and ensure image generation is allowed for your account. With this repository accessible to your GitHub account, install and select the backend:

```sh
hermes plugins install xiaofeng-zheng/hermes-copilot-image --enable
hermes config set image_gen.provider copilot-image
```

Ask Hermes to generate an image. The prompt and requested size go to the Copilot service; image generation counts toward your Copilot AI credits. The returned image is saved in Hermes’ local image cache. The plugin does not maintain a separate credential store.

## Image quality

The Copilot endpoint advertises `auto` (default), `low`, `medium`, and `high`. Set a persistent quality for this backend only, for example:

```sh
hermes config set image_gen.copilot-image.quality high
```

Set it back to `auto` to let the service choose. This controls rendering quality, not output dimensions. The tool result distinguishes the requested quality from the quality reported by the service. Invalid configuration is rejected before sending an image request. `xhigh` and `max` are not advertised by the tested Copilot endpoint.

## Compatibility and scope

Tested with Hermes Agent 0.23.3 and a Copilot Enterprise endpoint advertising `gpt-image-2.5-flare`. Text-to-image only. Image editing and other account types have not been tested. This is an unofficial integration; the account-advertised HTTP endpoint and Hermes internal credential/image helpers may change.
