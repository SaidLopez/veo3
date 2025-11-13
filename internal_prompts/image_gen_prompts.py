base_prompt = """
Generate {number_of_image_variations} distinct, highly detailed image generation prompts for Amazon product listing advertisements.  
  
PRODUCT REFERENCE: {product_description}.Use this reference as the foundation for each prompt.  
  
OUTPUT FORMAT: Provide only the prompts—no explanations, commentary, or additional text.  
  
PROMPT STRUCTURE: Each prompt must include:  
- Scene: Environment, setting, and context  
- Subject: Product positioning and focal point  
- Composition: Layout, framing, and spatial arrangement optimized for Amazon listings (product prominence, clean backgrounds, professional presentation)  
- Cinematography: Lighting setup, mood, and atmosphere  
- Lens Effects: Depth of field, focal length characteristics, perspective  
- Visual Details: Textures, materials, colors, and fine elements  
- Style: Aesthetic direction, artistic treatment, and overall visual approach  
  
REQUIREMENTS:  
- Optimize composition for e-commerce: ensure product is clearly visible, well-lit, and prominently featured  
- Each prompt must be substantially different in concept, style, and execution  
- Maintain commercial viability and Amazon listing standards  
- Be specific and descriptive to ensure accurate image generation  
  
USER INPUT: [concept/idea will be provided here]  
"""

infographic_prompt = """
Generate {number_of_image_variations} distinct, highly detailed infographic prompts for Amazon product listing advertisements.  
  
PRODUCT REFERENCE: {product_description}.Use this reference as the foundation for each prompt.  
  
OUTPUT FORMAT: Provide only the prompts—no explanations, commentary, or additional text.  
  
PROMPT STRUCTURE: Each prompt must include:  
- Scene: Background environment and contextual setting  
- Subject: Product placement and primary focal elements  
- Composition: Layout structure, information hierarchy, and spatial organization optimized for Amazon listings (product prominence, clear visual flow, scannable design)  
- Cinematography: Lighting treatment, visual mood, and tonal quality  
- Lens Effects: Depth simulation, perspective treatment, and dimensional qualities  
- Visual Details: Icons, graphics, data visualization elements, color schemes, textures, and decorative components  
- Style: Design aesthetic, graphic treatment, and overall visual language (modern, minimalist, bold, technical, etc.)  
- Text: Headline placement, key feature callouts, benefit statements, specifications, and typographic hierarchy (ensure readability and strategic positioning alongside product)  
  
REQUIREMENTS:  
- Optimize for e-commerce infographics: balance product visibility with informational content  
- Ensure text elements complement rather than overwhelm the product  
- Design for quick comprehension and conversion (highlight key benefits, features, USPs)  
- Each prompt must be substantially different in layout, style, information presentation, and visual approach  
- Maintain Amazon listing standards and professional commercial quality  
- Be specific about text placement, graphic elements, and information architecture  
  
USER INPUT: [concept/idea will be provided here]  
"""

product_highlight_prompt = """
Generate {number_of_image_variations} distinct, highly detailed product highlight prompts for Amazon product listing advertisements.  
  
PRODUCT REFERENCE: {product_description}.Use this reference as the foundation for each prompt.  
  
OUTPUT FORMAT: Provide only the prompts—no explanations, commentary, or additional text.  
  
PROMPT STRUCTURE: Each prompt must include:  
- Scene: Background treatment and environmental context that enhances product focus  
- Subject: Specific product feature or detail being highlighted (zoom areas, callout sections, key components)  
- Composition: Visual arrangement emphasizing the highlighted feature, directional flow guiding viewer attention, strategic use of negative space  
- Cinematography: Lighting that accentuates the highlighted area, contrast control, spotlight effects, and dramatic emphasis  
- Lens Effects: Selective focus, bokeh for background separation, macro detail rendering, depth of field manipulation to isolate features  
- Visual Details: Annotation elements (arrows, circles, lines), magnification indicators, texture close-ups, material quality showcase, finish details  
- Style: Visual treatment approach (clean and technical, lifestyle-oriented, dramatic and bold, minimal and elegant)  
- Text Integration: Feature labels, benefit callouts, specification annotations, and pointer text positioned to complement visual highlights without obscuring product  
  
REQUIREMENTS:  
- Optimize for feature-focused marketing: draw immediate attention to specific product advantages  
- Use visual cues (graphic overlays, contrast, lighting) to guide the eye to highlighted areas  
- Ensure the highlighted feature is unmistakably clear and visually compelling  
- Balance detailed focus with overall product context  
- Each prompt must showcase different features, angles, or highlighting techniques  
- Maintain Amazon listing standards with professional, conversion-optimized presentation  
- Be explicit about which product aspect is being highlighted and how it's visually emphasized  
  
USER INPUT: [concept/idea will be provided here]"""
