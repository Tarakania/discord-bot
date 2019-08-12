def codeblock(string: str, language: str = "") -> str:
    """Wrap string in codeblock"""

    return f"```{language}\n{string}```"
