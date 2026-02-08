# Parametric Magnetic Label Generator

An OpenSCAD model for creating customizable magnetic labels, optimized for multi-material 3D printing.

![Label Preview](/docs/preview2.jpeg)

## Features

- **Fully parametric** - Adjust all dimensions via OpenSCAD Customizer
- **Multi-color support** - Separate exports for two-color printing
- **Embedded magnets** - Cavities for 6x3mm or 10x2mm disc magnets
- **Rounded corners** - Adjustable corner radius
- **Optional icons** - SVG import or Unicode/emoji characters

## Requirements

- [OpenSCAD](https://openscad.org/) 2021.01 or later
- Python 3.8+ (for the export tool)
- Multi-material 3D printer (e.g., Bambu Lab with AMS, Prusa MMU) - optional

![Editing in OpenSCAD](/docs/openscad.png)

## Quick Start

### Using the Export Tool (Recommended)

The export tool automatically calculates the optimal label size based on your text:

```bash
./export
```

Features:
- **Automatic size calculation** - Measures exact text width using OpenSCAD
- **Interactive color selection** - Choose foreground and background colors
- **Preview before export** - See all parameters before exporting
- **Exports both STL files** - Ready for multi-material printing

### Using OpenSCAD Directly

1. Open `magnetic_label.scad` in OpenSCAD
2. Open the Customizer panel: **View → Customizer**
3. Adjust parameters as needed
4. Preview with **F5**, render with **F6**
5. Export STL with **File → Export → Export as STL**

## Parameters

### Text
| Parameter | Default | Description |
|-----------|---------|-------------|
| `label_text` | "ASA" | Text displayed on the label |
| `font_name` | "Arial:style=Bold" | Font name and style |
| `font_size` | 12 | Font size in mm |

### Label Dimensions
| Parameter | Default | Description |
|-----------|---------|-------------|
| `label_width` | 60 | Total width in mm |
| `label_height` | 25 | Total height in mm |
| `corner_radius` | 8 | Corner radius in mm |
| `border_width` | 2 | Frame/border width in mm |

### Magnets
| Parameter | Default | Description |
|-----------|---------|-------------|
| `magnet_diameter` | 6 | Magnet diameter in mm |
| `magnet_height` | 3 | Magnet height in mm |
| `magnet_tolerance` | 0.2 | Extra clearance for press fit |
| `magnet_count` | 2 | Number of magnets (2 or 4) |
| `magnet_inset` | 10 | Distance from edge to magnet center |

### Layer Thickness
| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_base_under_magnet` | 0.6 | Minimum material above magnet cavity |
| `inlay_thickness` | 0.8 | Background layer thickness (color 2) |
| `text_thickness` | 0.6 | Raised text height (color 1) |

> **Note:** `base_thickness` is calculated automatically as `magnet_height + min_base_under_magnet`

## Multi-Color Export

For two-color printing, export separate STL files:

### Method 1: Export Tool (Recommended)
```bash
./export
```
The tool guides you through text input, size calculation, color selection, and exports both STL files automatically.

### Method 2: Using Customizer
1. Set `render_mode` to **"color1"**
2. Render (**F6**) and export as `label_color1.stl`
3. Set `render_mode` to **"color2"**
4. Render (**F6**) and export as `label_color2.stl`

### Method 3: Command Line
```bash
# Export color 1 (base, frame, text)
openscad -o label_color1.stl -D 'render_mode="color1"' magnetic_label.scad

# Export color 2 (inlay/background)
openscad -o label_color2.stl -D 'render_mode="color2"' magnetic_label.scad
```

### Slicer Setup
1. Import both STL files
2. They should align automatically (same origin)
3. Assign different colors/extruders to each part

## Layer Structure

```
Side view:

    Text (0.6mm)      ███         ← Color 1
    Inlay (0.8mm)     ░░░░░░░     ← Color 2
    Frame             ███   ███   ← Color 1
    Base (3.6mm)      █████████   ← Color 1
                      ○       ○   ← Magnet cavities
```

## Adding Icons

### SVG Icons
1. Place SVG file in `icons/` directory
2. Set `use_icon = true`
3. Set `icon_type = "svg"`
4. Set `icon_file = "icons/your-icon.svg"`

> SVGs are assumed to be 100x100 units and scaled via `icon_size`

### Unicode/Emoji Icons
1. Set `use_icon = true`
2. Set `icon_type = "text"`
3. Set `icon_text` to your character (e.g., `"\u2600"` for ☀)
4. Set `icon_font` to a font supporting the character (e.g., "Noto Emoji")

## Common Magnet Sizes

| Size | Use Case |
|------|----------|
| 6x3mm | Standard, good holding force |
| 10x2mm | Larger surface, thinner label |

## Tips

- Increase `magnet_tolerance` if magnets don't fit (try 0.3-0.4mm)
- Use `$fn = 32` for faster preview, `$fn = 64` or higher for final export
- Test magnet fit with a small test print before printing full labels

## License

MIT License - Feel free to use and modify.
