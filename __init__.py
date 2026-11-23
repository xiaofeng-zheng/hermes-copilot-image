"""Text-to-image over Copilot's account-advertised HTTP endpoint."""
import httpx
from agent.image_gen_provider import resolve_aspect_ratio, save_b64_image, success_response
from hermes_cli.runtime_provider import resolve_runtime_provider
from plugins.image_gen._common import StaticImageGenProvider, error_factory, load_image_gen_config, size_for
from providers import get_provider_profile

MODEL = 'gpt-image-2.5-flare'
QUALITIES = ('auto', 'low', 'medium', 'high')
HOSTS = {f'https://{host}.githubcopilot.com' for host in ('api', 'api.individual', 'api.business', 'api.enterprise')}


class CopilotImage(StaticImageGenProvider):
    provider_id = 'copilot-image'
    label = 'GitHub Copilot (HTTP)'
    models = {MODEL: {'display': 'GPT Image 2.5 Flare', 'strengths': 'Text-to-image'}}
    default_model_id = MODEL

    def is_available(self):
        return get_provider_profile('copilot') is not None

    def capabilities(self):
        return {'modalities': ['text'], 'max_reference_images': 0}

    def generate(self, prompt, aspect_ratio='square', *, image_url=None, reference_image_urls=None, **kwargs):
        aspect = resolve_aspect_ratio(aspect_ratio)
        fail = error_factory(self.provider_id, aspect, model=MODEL, prompt=prompt)
        if not prompt.strip() or image_url or reference_image_urls:
            return fail('A nonempty text prompt without reference images is required.', 'invalid_input')
        quality = load_image_gen_config(self.provider_id).get('quality', 'auto')
        if quality not in QUALITIES:
            return fail('image_gen.copilot-image.quality must be auto, low, medium or high.', 'invalid_input')
        runtime = resolve_runtime_provider(requested='copilot')
        base = runtime['base_url'].rstrip('/')
        if runtime.get('provider') != 'copilot' or base not in HOSTS:
            return fail('Refusing to send credentials outside the GitHub Copilot API.', 'invalid_endpoint')
        profile = get_provider_profile('copilot')
        headers = {**profile.client_headers(base_url=base), 'Authorization': 'Bearer ' + runtime['api_key']}
        response = httpx.post(base + '/v1/images/generations', headers=headers, timeout=240,
                              json={'model': MODEL, 'prompt': prompt, 'size': size_for(aspect), 'quality': quality})
        if response.status_code != 200:
            return fail(f'Copilot image generation returned HTTP {response.status_code}.', 'api_error')
        body = response.json()
        fmt = body.get('output_format')
        if fmt not in ('png', 'webp', 'jpeg'):
            return fail('Missing or unsupported output format from Copilot.', 'invalid_response')
        image = save_b64_image(body['data'][0]['b64_json'], prefix='copilot', extension=fmt)
        return success_response(image=str(image), model=MODEL, prompt=prompt, aspect_ratio=aspect,
                                provider=self.provider_id, modality='text',
                                extra={'requested_quality': quality, 'reported_quality': body.get('quality')})


def register(ctx):
    ctx.register_image_gen_provider(CopilotImage())
