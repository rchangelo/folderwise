"""Configuration for FolderWise AI.

Central place for category definitions, instruction keywords, and the Payhip
upgrade URL so the app can be reconfigured without touching application logic.
"""

# Payhip product URL for the Pro upgrade. Change this to your own product link.
PAYHIP_PRO_URL = "https://payhip.com/b/5vjuz"

# Mapping of category name -> list of file extensions (lowercase, no dot).
CATEGORIES = {
    "Images": [
        "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp",
        "svg", "heic", "raw", "ico", "avif",
    ],
    "Videos": [
        "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v",
        "mpg", "mpeg", "3gp", "ts",
    ],
    "Documents": [
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt",
        "csv", "rtf", "odt", "ods", "odp", "pages", "numbers", "key",
        "md", "epub", "mobi",
    ],
    "CAD Models": [
        "dwg", "dxf", "step", "stp", "iges", "igs", "stl", "obj",
        "fbx", "3ds", "blend", "ipt", "sldprt", "sldasm", "slddrw",
        "x_t", "x_b", "ply", "dae",
    ],
    "Python Projects": [
        "py", "pyw", "ipynb", "pyc", "pyo", "whl", "egg",
    ],
    "Archives": [
        "zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso",
        "tgz", "tbz2", "lz",
    ],
    "Music": [
        "mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "aiff",
        "aif", "opus", "alac",
    ],
}

# Display order for categories (Others always last).
CATEGORY_ORDER = [
    "Images", "Videos", "Documents", "CAD Models",
    "Python Projects", "Archives", "Music", "Others",
]

# Default subfolder name when organizing into a new subfolder.
ORGANIZED_ROOT_NAME = "FolderWise_AI_Organized"

# Instruction keyword -> category to filter.
# When the keyword appears in the instruction text, only files in the mapped
# category are organized. A value of None means "all categories".
INSTRUCTION_KEYWORDS = {
    # Category-specific
    "images": "Images",
    "image": "Images",
    "photos": "Images",
    "photo": "Images",
    "videos": "Videos",
    "video": "Videos",
    "cad": "CAD Models",
    "documents": "Documents",
    "document": "Documents",
    "archives": "Archives",
    "archive": "Archives",
    "python": "Python Projects",
    "music": "Music",
    "songs": "Music",
    # Extension-specific (narrows within a category)
    "pdfs": ("Documents", {"pdf"}),
    "pdf": ("Documents", {"pdf"}),
    "zip": ("Archives", {"zip"}),
    "zip files": ("Archives", {"zip"}),
    # All files
    "everything": None,
    "downloads": None,
    "all files": None,
    "all": None,
}

# Phrases that trigger extension-based sorting instead of category-based.
EXTENSION_SORT_PHRASES = ["sort by extension", "by extension", "sort by ext"]

# Example instruction chips shown in the UI.
INSTRUCTION_EXAMPLES = [
    "Organize images",
    "Organize videos",
    "Organize CAD",
    "Organize documents",
    "Organize PDFs",
    "Organize ZIP files",
    "Organize Python projects",
    "Organize everything",
    "Clean Downloads",
    "Move CAD files",
    "Sort by extension",
]
