import os

def generate_subtitles_filter(text_lines, font_path, font_size=55, color="white"):
    """
    Generates dynamic CapCut-style subtitle text with pop-in/fade effects and styling.
    text_lines: [{'text': '...', 'start': 0.0, 'end': 2.5}]
    """
    drawtext_filters = []
    
    for line in text_lines:
        safe_text = line['text'].replace("'", "\\'").replace(":", "\\:").upper()
        font_conf = f":fontfile='{font_path}'" if os.path.exists(font_path) else ""
        
        start = line['start']
        end = line['end']
        
        # Animations:
        # Alpha fade-in over 0.1s, fade-out over 0.1s. 
        # Modern bold look, centered horizontally, bottom third position.
        # Dropshadow to pop off the screen like CapCut presets.
        
        filter_str = (
            f"drawtext=text='{safe_text}'{font_conf}:"
            f"fontsize={font_size}:fontcolor={color}:"
            f"bordercolor=black:borderw=5:shadowcolor=black@0.9:shadowx=5:shadowy=5:"
            f"x=(w-text_w)/2:y=h-(h*0.40):"
            f"alpha='if(lt(t,{start}+0.1), (t-{start})/0.1, if(gt(t,{end}-0.1), ({end}-t)/0.1, 1))':"
            f"enable='between(t,{start},{end})'"
        )
        drawtext_filters.append(filter_str)
        
    return ",".join(drawtext_filters)
