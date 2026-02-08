// ============================================================
// PARAMETRIC MAGNETIC LABEL
// Multi-color design for multi-material 3D printing
// ============================================================

/* [Render Mode] */
// Select which parts to render for export
render_mode = "all"; // [all:Preview with colors, color1:Color 1 only (base/frame/text), color2:Color 2 only (inlay)]

/* [Text] */
// Text to display on the label
label_text = "PLA+";
// Font name and style (e.g. "Arial:style=Bold")
font_name = "Arial:style=Bold";
// Font size in mm
font_size = 12; // [4:1:30]

/* [Label Dimensions] */
// Total width of the label in mm
label_width = 60; // [20:1:150]
// Total height of the label in mm
label_height = 25; // [15:1:80]
// Corner radius in mm
corner_radius = 8; // [0:1:20]
// Border/frame width in mm
border_width = 2; // [1:0.5:10]

/* [Magnets] */
// Magnet diameter in mm (common: 6 or 10)
magnet_diameter = 6; // [4:1:15]
// Magnet height in mm (common: 2 or 3)
magnet_height = 3; // [1:0.5:5]
// Tolerance for press fit (increase if too tight)
magnet_tolerance = 0.2; // [0:0.05:0.5]
// Number of magnets
magnet_count = 2; // [2, 4]
// Distance from edge to magnet center in mm
magnet_inset = 10; // [5:1:30]

/* [Layer Thickness] */
// Minimum thickness above magnet cavity in mm
min_base_under_magnet = 0.6; // [0.4:0.1:1.2]
// Inlay/background thickness in mm (color 2)
inlay_thickness = 0.8; // [0.4:0.1:1.6]
// Raised text thickness in mm (color 1)
text_thickness = 0.6; // [0.4:0.1:1.2]

/* [Icon] */
// Enable icon display
use_icon = false;
// Icon source type
icon_type = "text"; // [text:Unicode/Emoji, svg:SVG file, none:No icon]
// Path to SVG file (for svg type)
icon_file = "icons/sun.svg";
// Unicode character or emoji (for text type)
icon_text = "\u2600";
// Font for text icons (e.g. "Noto Emoji")
icon_font = "Noto Emoji";
// Icon size in mm
icon_size = 10; // [4:1:25]
// Icon X position relative to center
icon_position_x = -18; // [-50:1:50]
// Icon Y position relative to center
icon_position_y = 0; // [-30:1:30]

/* [Fine Tuning] */
// Resolution for curves (higher = smoother)
$fn = 64; // [16:8:128]
// Text horizontal offset in mm
text_offset_x = 0; // [-20:0.5:20]
// Text vertical offset in mm
text_offset_y = 0; // [-20:0.5:20]

/* [Preview Colors] */
// Preview color for base, frame, and text
preview_color1 = "Black"; // [Black, DimGray, Gray, Navy, DarkRed, DarkGreen, SaddleBrown, Purple]
// Preview color for inlay/background
preview_color2 = "White"; // [White, Yellow, LightGray, Cyan, Lime, Orange, Pink, LightBlue]

/* [Calculated Values] */
// Base thickness is calculated automatically
base_thickness = magnet_height + min_base_under_magnet;
// Total label thickness (for reference)
total_thickness = base_thickness + inlay_thickness + text_thickness;
// Icon position as vector (internal use)
icon_position = [icon_position_x, icon_position_y];

// ============================================================
// MODULES
// ============================================================

// Rounded rectangle as 2D shape
module rounded_rect_2d(w, h, r) {
    offset(r) offset(-r) square([w, h], center = true);
}

// Rounded rectangle as 3D body
module rounded_rect(w, h, r, thickness) {
    linear_extrude(height = thickness)
        rounded_rect_2d(w, h, r);
}

// Magnet cavities (from the bottom/back side)
module magnet_holes() {
    hole_d = magnet_diameter + magnet_tolerance;

    if (magnet_count == 2) {
        // 2 magnets: left and right
        for (x = [-1, 1]) {
            translate([x * (label_width/2 - magnet_inset), 0, -0.1])
                cylinder(d = hole_d, h = magnet_height + 0.1);
        }
    } else if (magnet_count == 4) {
        // 4 magnets: in the corners
        for (x = [-1, 1], y = [-1, 1]) {
            translate([
                x * (label_width/2 - magnet_inset),
                y * (label_height/2 - magnet_inset),
                -0.1
            ])
                cylinder(d = hole_d, h = magnet_height + 0.1);
        }
    }
}

// Base plate with magnet cavities
module base_plate() {
    difference() {
        rounded_rect(label_width, label_height, corner_radius, base_thickness);
        magnet_holes();
    }
}

// Frame (raised border around the inlay)
module frame() {
    frame_height = inlay_thickness + text_thickness;
    inner_width = label_width - 2 * border_width;
    inner_height = label_height - 2 * border_width;
    inner_radius = max(0, corner_radius - border_width);

    translate([0, 0, base_thickness])
    difference() {
        rounded_rect(label_width, label_height, corner_radius, frame_height);
        // Cutout for inlay - extends to text surface
        translate([0, 0, -0.1])
            rounded_rect(inner_width, inner_height, inner_radius, frame_height + 0.2);
    }
}

// Inlay (background, typically white)
module inlay() {
    inner_width = label_width - 2 * border_width;
    inner_height = label_height - 2 * border_width;
    inner_radius = max(0, corner_radius - border_width);

    translate([0, 0, base_thickness])
        rounded_rect(inner_width, inner_height, inner_radius, inlay_thickness);
}

// 3D text module
module label_text_3d() {
    translate([text_offset_x, text_offset_y, base_thickness + inlay_thickness])
    linear_extrude(height = text_thickness)
        text(label_text,
             size = font_size,
             font = font_name,
             halign = "center",
             valign = "center");
}

// Icon module
module icon() {
    if (use_icon && icon_type != "none") {
        translate([icon_position[0], icon_position[1], base_thickness + inlay_thickness])
        linear_extrude(height = text_thickness) {
            if (icon_type == "svg") {
                // SVG import - scaled to icon_size
                scale_factor = icon_size / 100; // Assumption: SVG is 100x100
                scale([scale_factor, scale_factor, 1])
                    import(icon_file, center = true);
            } else if (icon_type == "text") {
                // Unicode text as icon
                text(icon_text,
                     size = icon_size,
                     font = icon_font,
                     halign = "center",
                     valign = "center");
            }
        }
    }
}

// ============================================================
// COLOR GROUPS
// ============================================================

// Color 1: Base + frame + text + icon (typically black)
module color1_parts() {
    base_plate();
    frame();
    label_text_3d();
    icon();
}

// Color 2: Inlay/background (typically white)
module color2_parts() {
    inlay();
}

// ============================================================
// RENDER OUTPUT
// ============================================================

if (render_mode == "all") {
    // Preview with colors
    color(preview_color1) color1_parts();
    color(preview_color2) color2_parts();
} else if (render_mode == "color1") {
    // Export: Color 1 only
    color1_parts();
} else if (render_mode == "color2") {
    // Export: Color 2 only
    color2_parts();
}

// ============================================================
// INFO OUTPUT
// ============================================================
echo("=== LABEL PARAMETERS ===");
echo(str("Label: ", label_width, " x ", label_height, " x ", total_thickness, " mm"));
echo(str("Text: \"", label_text, "\""));
echo(str("Magnets: ", magnet_count, "x ", magnet_diameter, "x", magnet_height, " mm"));
echo(str("Base thickness (auto): ", base_thickness, " mm"));
echo("=========================");
