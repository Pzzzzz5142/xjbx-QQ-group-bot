def imageProxy(url: str) -> str:
    result = url.replace("i.pximg.net", "pximg.pixiv-viewer.workers.dev")

    result = result.replace("_10_webp", "_70")
    result = result.replace("_webp", "")

    return result


def imageProxy_cat(url):
    pass
