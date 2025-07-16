# Investment Art Fugu Python Project

## Project Structure

```
python/
├── building_generator/           # Main module for image generation
│   ├── __init__.py
│   ├── api.py                    # Exposes the main function: generate_image(user_data, ...)
│   ├── core.py                   # Core logic for image selection and composition
│   ├── config.py                 # Configuration management
│   └── utils.py                  # Shared utilities
│
├── image_tools/                  # Tools for image preparation and management
│   ├── __init__.py
│   ├── cli.py                    # Command-line interface for all tools
│   ├── rename.py                 # Renaming images
│   ├── crop.py                   # Cropping images
│   ├── count.py                  # Counting images and writing to JSON
│   └── split.py                  # Splitting images by ratio
│
├── assets/                       # Static resources
├── imgset/                       # Image library
├── tests/                        # Unit and integration tests
│   └── test_building_generator.py
├── README.md
├── requirements.txt
└── todolist.md
```

## Usage

### Main Use Case: Generate Image

```python
from building_generator.api import generate_image

# user_data = ... (your data)
img = generate_image(user_data, config=...)
img.save('output.png')
```

### Preparation Tools

- Interactive:  
  `python -m image_tools.cli`
- Command-line:  
  `python -m image_tools.cli --rename imgset/asia/h0`
  `python -m image_tools.cli --crop imgset/asia/h0`
  `python -m image_tools.cli --count imgset/asia/h0 output.json`

## Development
- All core logic and configuration should be placed in `building_generator/`.
- All image management and preparation tools should be placed in `image_tools/`.
- Add tests to `tests/`.

---
For more details, see `todolist.md`. 