# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenSCAD parametric model for magnetic labels designed for multi-material 3D printing. The model generates two-color labels with embedded magnet cavities.

## Working with OpenSCAD Files

- Open `magnetic_label.scad` in OpenSCAD to preview and export
- Use the Customizer panel (View → Customizer) to adjust parameters interactively
- Parameters use OpenSCAD Customizer syntax: `// [min:step:max]` for sliders, `// [opt1, opt2]` for dropdowns

## Multi-Color Export Workflow

The model uses `render_mode` to export separate STL files for multi-material printing:

1. Set `render_mode = "color1"` → Render (F6) → Export STL (base/frame/text)
2. Set `render_mode = "color2"` → Render (F6) → Export STL (inlay/background)
3. Import both STLs into slicer, assign different colors/extruders

## Architecture

**Layer Structure (bottom to top):**
- `base_plate()` - Base with magnet cavities (Color 1)
- `frame()` - Raised border around inlay (Color 1)
- `inlay()` - Background area (Color 2)
- `label_text_3d()` + `icon()` - Raised text/icons on inlay (Color 1)

**Color Groups:**
- `color1_parts()` - All parts for primary color (typically black)
- `color2_parts()` - All parts for secondary color (typically white)

**Key Calculated Value:**
- `base_thickness` is auto-calculated as `magnet_height + min_base_under_magnet`

## Icons

- Place SVG files in `icons/` directory
- SVGs are assumed to be 100x100 units and scaled via `icon_size`
- Alternative: Use Unicode/emoji characters with `icon_type = "text"`
