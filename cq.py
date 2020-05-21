def at(num) -> str:
    return f"[CQ:at,qq={num}]"


def image(path: str) -> str:
    return f"[CQ:image,file={path}]"


def link(url: str, title: str = "", content: str = "", image: str = "") -> str:
    return f"[CQ:share,url={url},title={title},content={content},image={image}]"
