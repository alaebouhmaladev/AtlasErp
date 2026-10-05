from atlas_erp import __version__

no_cache = 1
sitemap = 0


def get_context(context):
    context.title = "About ATLASERP"
    context.atlas_version = __version__
    return context
