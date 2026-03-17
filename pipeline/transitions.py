def build_transition_complex_filter(images_data, width=1080, height=1920):
    """
    Builds the exact FFmpeg chaining for dynamic CapCut-style zoom + slight pan between clips.
    images_data: [{'file': 'img.jpg', 'duration': 3.0}, ...]
    """
    filter_chain = ""
    
    for i, data in enumerate(images_data):
        duration = float(data['duration'])
        if duration <= 0:
            duration = 1.0
            
        frames = int(duration * 30)
        
        # Alternating Zoom Effects (Zoom In vs Zoom Out)
        # CapCut style dynamic zooms
        if i % 2 == 0:
            # Zoom In slightly and center
            zoom_expr = "z='min(max(zoom,1.0)+0.0015,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        else:
            # Pan effect (Slide slight right without zoom out which sometimes breaks aspect ratio)
            # Starting zoomed in slightly (1.1), panning right
            zoom_expr = "z='1.1':x='x+1':y='ih/2-(ih/zoom/2)'"
            
        # Crop to avoid black bars entirely, and color correction for premium feel
        filter_chain += (
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height}:(in_w-{width})/2:(in_h-{height})/2,"
            # Enhance Colors (Glow/Vibrant Effect)
            f"eq=contrast=1.1:saturation=1.2:brightness=0.03,"
            # Zoom and Pan
            f"zoompan={zoom_expr}:d={frames}:s={width}x{height}:fps=30,"
            f"format=yuv420p[v_vfx{i}];"
        )
        
    # CapCut-style True Transitions using Xfade
    if len(images_data) > 1:
        fade_duration = 0.4
        current_offset = max(float(images_data[0]['duration']) - fade_duration, 0.1)
        
        last_out = f"[v_vfx0]"
        for i in range(1, len(images_data)):
            next_in = f"[v_vfx{i}]"
            out_node = f"[xfade{i}]" if i < len(images_data) - 1 else "[base_video_raw]"
            
            filter_chain += f"{last_out}{next_in}xfade=transition=fade:duration={fade_duration}:offset={current_offset:.2f}{out_node};"
            
            last_out = out_node
            current_offset += max(float(images_data[i]['duration']) - fade_duration, 0.1)
    else:
        filter_chain += f"[v_vfx0]null[base_video_raw];"
        
    # Add Premium Gradient Overlay to make the bright texts snap out
    filter_chain += (
        f"color=black@0.2:size={width}x{height}[overlay];"
        f"[base_video_raw][overlay]overlay=0:0[base_video]"
    )
    
    return filter_chain
