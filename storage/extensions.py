def get_extensions():
    extensions = []
    extensions.append("jishaku")
    for file in Path("cogs").glob("**/*.py"):
        if "!" in file.name or "DEV" in file.name:
            continue
        extensions.append(str(file).replace("/", ".").replace(".py", ""))
    return extensions
