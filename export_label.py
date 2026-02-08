#!/usr/bin/env python3
"""
Export Tool for Parametric Magnetic Labels
Calculates optimal label size and exports STL files for multi-material printing.
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    from PIL import ImageFont
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich import print as rprint
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Initialize Rich console
console = Console()

# Script directory
SCRIPT_DIR = Path(__file__).parent.resolve()
SCAD_FILE = SCRIPT_DIR / "magnetic_label.scad"

# OpenSCAD executable paths
OPENSCAD_PATHS = [
    "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",  # macOS
    "/usr/bin/openscad",  # Linux
    "openscad",  # PATH
]

# Common font paths by platform
# IMPORTANT: Arial Bold must come FIRST since OpenSCAD uses "Arial:style=Bold"
FONT_PATHS = {
    "Arial": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS Bold (preferred!)
        "/Library/Fonts/Arial Bold.ttf",  # macOS Bold alternate
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",  # Linux Bold
        "C:/Windows/Fonts/arialbd.ttf",  # Windows Bold
        "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS regular (fallback)
        "/Library/Fonts/Arial.ttf",  # macOS regular fallback
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",  # Linux fallback
        "C:/Windows/Fonts/arial.ttf",  # Windows fallback
    ],
    "Helvetica": [
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/Library/Fonts/Helvetica.ttc",  # macOS alternate
    ],
}

# Available colors for selection
COLORS_DARK = [
    ("Black", "Black"),
    ("Dark Gray", "DimGray"),
    ("Gray", "Gray"),
    ("Navy Blue", "Navy"),
    ("Dark Red", "DarkRed"),
    ("Dark Green", "DarkGreen"),
    ("Brown", "SaddleBrown"),
    ("Purple", "Purple"),
]

COLORS_LIGHT = [
    ("White", "White"),
    ("Yellow", "Yellow"),
    ("Light Gray", "LightGray"),
    ("Cyan", "Cyan"),
    ("Lime Green", "Lime"),
    ("Orange", "Orange"),
    ("Pink", "Pink"),
    ("Light Blue", "LightBlue"),
]

# Default values
DEFAULTS = {
    "font_size": 12,
    "border_width": 2,
    "corner_radius": 8,
    "min_padding": 4,  # Minimum padding around text
    "min_width": 30,
    "min_height": 15,
    "magnet_inset": 10,
    "magnet_diameter": 6,
}


def find_openscad():
    """Find OpenSCAD executable."""
    for path in OPENSCAD_PATHS:
        if path == "openscad":
            # Check if in PATH
            try:
                subprocess.run(["openscad", "--version"], capture_output=True, check=True)
                return "openscad"
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        elif os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def find_font(font_name="Arial"):
    """Find font file path."""
    # Check known paths
    for name, paths in FONT_PATHS.items():
        if name.lower() in font_name.lower():
            for path in paths:
                if os.path.isfile(path):
                    return path

    # Try to find any Arial font on macOS
    font_dirs = [
        "/Library/Fonts",
        "/System/Library/Fonts",
        "/System/Library/Fonts/Supplemental",
        os.path.expanduser("~/Library/Fonts"),
    ]

    for font_dir in font_dirs:
        if os.path.isdir(font_dir):
            for f in os.listdir(font_dir):
                if "arial" in f.lower() and f.endswith((".ttf", ".otf")):
                    return os.path.join(font_dir, f)

    return None


def calculate_text_dimensions_openscad(text, font_size, font_name="Arial:style=Bold"):
    """Calculate text dimensions by actually rendering in OpenSCAD.

    This is the most accurate method as it uses OpenSCAD's actual text rendering.
    """
    openscad = find_openscad()
    if not openscad:
        return None, None

    import tempfile

    # Create temporary OpenSCAD file
    scad_content = f'''
linear_extrude(1)
    text("{text}", size={font_size}, font="{font_name}", halign="left", valign="baseline");
'''

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scad', delete=False) as f:
            f.write(scad_content)
            scad_file = f.name

        stl_file = scad_file.replace('.scad', '.stl')

        # Run OpenSCAD
        result = subprocess.run(
            [openscad, '-o', stl_file, scad_file],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0 or not os.path.isfile(stl_file):
            return None, None

        # Parse ASCII STL to get bounding box
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        with open(stl_file, 'r') as f:
            for line in f:
                if 'vertex' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        x, y = float(parts[1]), float(parts[2])
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)

        # Cleanup
        os.unlink(scad_file)
        os.unlink(stl_file)

        if min_x == float('inf'):
            return None, None

        width_mm = max_x - min_x
        height_mm = max_y - min_y

        return width_mm, height_mm

    except Exception as e:
        return None, None


def calculate_text_dimensions(text, font_size, font_path=None):
    """Calculate text dimensions - tries OpenSCAD first, falls back to PIL."""

    # Try OpenSCAD measurement first (most accurate)
    width, height = calculate_text_dimensions_openscad(text, font_size)
    if width is not None:
        return width, height

    # Fallback to PIL measurement
    try:
        if font_path and os.path.isfile(font_path):
            reference_size = 100
            ref_font = ImageFont.truetype(font_path, reference_size)
            cap_bbox = ref_font.getbbox("H")
            cap_height_px = cap_bbox[3] - cap_bbox[1]
            pixels_per_mm = reference_size / cap_height_px
            pixel_size = int(font_size * pixels_per_mm)
            font = ImageFont.truetype(font_path, pixel_size)
            bbox = font.getbbox(text)
            width_px = bbox[2] - bbox[0]
            height_px = bbox[3] - bbox[1]

            # Apply correction factor (OpenSCAD renders ~40% wider)
            width_mm = (width_px / pixels_per_mm) * 1.4
            height_mm = height_px / pixels_per_mm

            return width_mm, height_mm
    except Exception:
        pass

    # Final fallback: character-based approximation
    width_mm = len(text) * font_size * 0.87  # ~0.87 per char for Arial Bold
    height_mm = font_size
    return width_mm, height_mm


def calculate_optimal_label_size(text, font_size, use_icon=False, icon_size=10):
    """Calculate optimal label dimensions based on text."""
    font_path = find_font("Arial")
    text_width, text_height = calculate_text_dimensions(text, font_size, font_path)

    # Add padding and border
    padding = DEFAULTS["min_padding"]
    border = DEFAULTS["border_width"]

    # Calculate minimum dimensions
    content_width = text_width + (2 * padding)
    if use_icon:
        content_width += icon_size + padding

    content_height = max(font_size, icon_size if use_icon else 0) + (2 * padding)

    # Add border
    label_width = content_width + (2 * border)
    label_height = content_height + (2 * border)

    # Ensure minimum size for magnets
    min_width_for_magnets = (2 * DEFAULTS["magnet_inset"]) + DEFAULTS["magnet_diameter"]
    label_width = max(label_width, min_width_for_magnets, DEFAULTS["min_width"])
    label_height = max(label_height, DEFAULTS["min_height"])

    # Round to nice values
    label_width = round(label_width)
    label_height = round(label_height)

    return label_width, label_height, text_width, text_height


def select_color(color_type, colors):
    """Interactive color selection using numbered list."""
    console.print(f"  Available {color_type} colors:")
    for i, (name, value) in enumerate(colors, 1):
        console.print(f"    [cyan]{i})[/cyan] {name}")

    while True:
        choice = Prompt.ask(f"  Select {color_type} color", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(colors):
                name, value = colors[idx]
                console.print(f"  Selected: [green]{name}[/green]")
                return name, value
            else:
                console.print(f"  [red]Please enter a number between 1 and {len(colors)}[/red]")
        except ValueError:
            console.print(f"  [red]Please enter a valid number[/red]")


def display_summary(config):
    """Display configuration summary."""
    console.print()

    # Create summary table
    table = Table(title="Label Configuration", show_header=True, header_style="bold cyan")
    table.add_column("Parameter", style="white")
    table.add_column("Value", style="green")

    table.add_row("Text", f'"{config["text"]}"')
    table.add_row("Font Size", f'{config["font_size"]} mm')
    table.add_row("Label Size", f'{config["width"]} x {config["height"]} mm')
    table.add_row("Text Size (calc.)", f'{config["text_width"]:.1f} x {config["text_height"]:.1f} mm')
    table.add_row("", "")
    table.add_row("Foreground", f'{config["color1_name"]} ({config["color1"]})')
    table.add_row("Background", f'{config["color2_name"]} ({config["color2"]})')
    table.add_row("", "")
    table.add_row("Output Files", f'{config["output_color1"]}')
    table.add_row("", f'{config["output_color2"]}')

    console.print(table)
    console.print()


def export_stl(openscad_path, config, render_mode, output_file):
    """Export STL file using OpenSCAD."""
    cmd = [
        openscad_path,
        "-o", output_file,
        "-D", f'render_mode="{render_mode}"',
        "-D", f'label_text="{config["text"]}"',
        "-D", f'font_size={config["font_size"]}',
        "-D", f'label_width={config["width"]}',
        "-D", f'label_height={config["height"]}',
        "-D", f'preview_color1="{config["color1"]}"',
        "-D", f'preview_color2="{config["color2"]}"',
        str(SCAD_FILE),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        console.print(f"[red]Error: {result.stderr}[/red]")
        return False

    if os.path.isfile(output_file):
        size = os.path.getsize(output_file) / 1024
        console.print(f"  [green]✓[/green] {output_file} ({size:.0f} KB)")
        return True

    return False


def main():
    """Main function."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]Magnetic Label Export Tool[/bold blue]\n"
        "[dim]Generate optimized labels for multi-material 3D printing[/dim]",
        border_style="blue"
    ))
    console.print()

    # Check prerequisites
    openscad_path = find_openscad()
    if not openscad_path:
        console.print("[red]Error: OpenSCAD not found![/red]")
        console.print("Please install OpenSCAD: https://openscad.org/")
        sys.exit(1)

    if not SCAD_FILE.exists():
        console.print(f"[red]Error: {SCAD_FILE} not found![/red]")
        sys.exit(1)

    # Step 1: Get label text
    console.print("[bold]Step 1:[/bold] Enter label text")
    text = Prompt.ask("  Text", default="ASA")

    if not text.strip():
        console.print("[red]Error: Text cannot be empty[/red]")
        sys.exit(1)

    # Step 2: Get font size
    console.print()
    console.print("[bold]Step 2:[/bold] Font size")
    font_size = int(Prompt.ask("  Font size (mm)", default=str(DEFAULTS["font_size"])))

    # Step 3: Calculate optimal size
    console.print()
    console.print("[bold]Step 3:[/bold] Calculating optimal label size...")
    width, height, text_width, text_height = calculate_optimal_label_size(text, font_size)

    console.print(f"  Calculated text size: [cyan]{text_width:.1f} x {text_height:.1f} mm[/cyan]")
    console.print(f"  Recommended label size: [green]{width} x {height} mm[/green]")

    # Allow override
    if Confirm.ask("  Use recommended size?", default=True):
        pass
    else:
        width = int(Prompt.ask("  Label width (mm)", default=str(width)))
        height = int(Prompt.ask("  Label height (mm)", default=str(height)))

    # Step 4: Select foreground color
    console.print()
    console.print("[bold]Step 4:[/bold] Select foreground color (base, frame, text)")
    color1_name, color1 = select_color("foreground", COLORS_DARK)

    # Step 5: Select background color
    console.print()
    console.print("[bold]Step 5:[/bold] Select background color (inlay)")
    color2_name, color2 = select_color("background", COLORS_LIGHT)

    # Step 6: Output filenames
    console.print()
    console.print("[bold]Step 6:[/bold] Output files")
    safe_text = "".join(c if c.isalnum() else "_" for c in text.lower())
    default_name1 = f"label_{safe_text}_color1.stl"
    default_name2 = f"label_{safe_text}_color2.stl"

    output_color1 = Prompt.ask("  Filename (foreground)", default=default_name1)
    output_color2 = Prompt.ask("  Filename (background)", default=default_name2)

    # Ensure .stl extension
    if not output_color1.endswith(".stl"):
        output_color1 += ".stl"
    if not output_color2.endswith(".stl"):
        output_color2 += ".stl"

    # Build configuration
    config = {
        "text": text,
        "font_size": font_size,
        "width": width,
        "height": height,
        "text_width": text_width,
        "text_height": text_height,
        "color1": color1,
        "color1_name": color1_name,
        "color2": color2,
        "color2_name": color2_name,
        "output_color1": output_color1,
        "output_color2": output_color2,
    }

    # Display summary
    display_summary(config)

    # Confirm export
    if not Confirm.ask("[bold]Export STL files?[/bold]", default=True):
        console.print("[yellow]Export cancelled.[/yellow]")
        sys.exit(0)

    # Export
    console.print()
    console.print("[bold]Exporting...[/bold]")

    success1 = export_stl(openscad_path, config, "color1", output_color1)
    success2 = export_stl(openscad_path, config, "color2", output_color2)

    if success1 and success2:
        console.print()
        console.print(Panel.fit(
            "[bold green]Export complete![/bold green]\n\n"
            "[white]Next steps:[/white]\n"
            "1. Import both STL files into your slicer\n"
            "2. Assign different colors/extruders\n"
            "3. Slice and print!",
            border_style="green"
        ))
    else:
        console.print()
        console.print("[red]Export failed. Check errors above.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)
