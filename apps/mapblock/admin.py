from django.contrib import admin
from django.utils.html import format_html
from .models import Building


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display  = ['map_preview_thumb', 'name', 'built_years',
                     'pos_display', 'order', 'published']
    list_display_links = ['map_preview_thumb', 'name']
    list_editable = ['order', 'published']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal   = ['photos']
    readonly_fields     = ['map_shape_editor']
    save_on_top = True

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'main_image', 'built_years', 'description', 'published'),
        }),
        ('📸 Галерея (Дополнительные фото)', {
            'fields': ('photos',),
            'description': 'Здесь можно выбрать дополнительные фотографии, которые появятся внизу страницы здания.',
        }),
        ('📐 Позиция и форма на карте', {
            'fields': (
                ('map_left', 'map_top'),
                ('map_width', 'map_height'),
                'map_rotation',
                'map_clip_path',
                'order',
                'map_shape_editor',
            ),
        }),
    )

    def map_preview_thumb(self, obj):
        from django.templatetags.static import static
        bg_url = static('img/map_aerial.png')
        rotation_style = f'transform:rotate({obj.map_rotation}deg);transform-origin:center;'
        clip_style = f'clip-path:polygon({obj.map_clip_path});' if obj.map_clip_path else ''
        return format_html(
            '<div style="position:relative;width:80px;height:50px;'
            'background:#222 url({bg}) no-repeat center;background-size:cover;'
            'border:1px solid #333;border-radius:2px;overflow:hidden;">'
            '<div style="position:absolute;left:{l}%;top:{t}%;width:{w}%;height:{h}%;'
            'background:rgba(192,57,43,0.5);border:1px solid #e74c3c;box-sizing:border-box;{rot}{clip}">'
            '</div></div>',
            bg=bg_url,
            l=obj.map_left, t=obj.map_top,
            w=obj.map_width, h=obj.map_height,
            rot=rotation_style, clip=clip_style,
        )
    map_preview_thumb.short_description = 'Позиция'

    def pos_display(self, obj):
        return format_html(
            '<span style="font-family:monospace;font-size:11px;color:#aaa">'
            'L:{} T:{} &nbsp; {}×{} &nbsp; {}°</span>',
            obj.map_left, obj.map_top, obj.map_width, obj.map_height, obj.map_rotation,
        )
    pos_display.short_description = 'L / T / W×H / °'

    def map_shape_editor(self, obj):
        clip_val = obj.map_clip_path or ''
        return format_html('''
<div style="margin-top:16px;">
  <div style="font-size:11px;color:#888;margin-bottom:8px;
    font-family:Oswald,sans-serif;letter-spacing:.1em;text-transform:uppercase;">
    Визуальный редактор формы
  </div>
  <div style="display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap;">

    <!-- Canvas editor -->
    <div>
      <canvas id="shape-canvas" width="260" height="180"
        style="background:#1a1a1a;border:1px solid #444;cursor:crosshair;display:block;"></canvas>
      <div style="margin-top:6px;display:flex;gap:6px;">
        <button type="button" onclick="resetShape()"
          style="font-size:11px;padding:4px 10px;background:#2a2a2a;color:#ccc;
          border:1px solid #444;cursor:pointer;">↺ Прямоугольник</button>
        <button type="button" onclick="clearPoints()"
          style="font-size:11px;padding:4px 10px;background:#2a2a2a;color:#ccc;
          border:1px solid #444;cursor:pointer;">✕ Очистить</button>
        <button type="button" onclick="applyShape()"
          style="font-size:11px;padding:4px 10px;background:#8b1a1a;color:#fff;
          border:1px solid #c0392b;cursor:pointer;font-weight:bold;">✓ Применить</button>
      </div>
      <p style="font-size:10px;color:#555;margin-top:4px;">
        Кликните по канвасу чтобы добавить точки. Перетащите точку для коррекции.
      </p>
    </div>

    <!-- Preset shapes -->
    <div>
      <div style="font-size:10px;color:#666;margin-bottom:6px;text-transform:uppercase;letter-spacing:.08em;">Пресеты</div>
      <div style="display:flex;flex-direction:column;gap:5px;">
        <button type="button" onclick="applyPreset('rect')"
          style="font-size:11px;padding:4px 10px;background:#222;color:#bbb;border:1px solid #444;cursor:pointer;text-align:left;">
          ▬ Прямоугольник</button>
        <button type="button" onclick="applyPreset('trap')"
          style="font-size:11px;padding:4px 10px;background:#222;color:#bbb;border:1px solid #444;cursor:pointer;text-align:left;">
          ⬡ Трапеция</button>
        <button type="button" onclick="applyPreset('para')"
          style="font-size:11px;padding:4px 10px;background:#222;color:#bbb;border:1px solid #444;cursor:pointer;text-align:left;">
          ▱ Параллелограмм</button>
        <button type="button" onclick="applyPreset('lshape')"
          style="font-size:11px;padding:4px 10px;background:#222;color:#bbb;border:1px solid #444;cursor:pointer;text-align:left;">
          ⌐ Г-образный</button>
        <button type="button" onclick="applyPreset('diamond')"
          style="font-size:11px;padding:4px 10px;background:#222;color:#bbb;border:1px solid #444;cursor:pointer;text-align:left;">
          ◆ Ромб</button>
      </div>
    </div>

  </div>
</div>

<script>
(function() {{
  const canvas = document.getElementById('shape-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let points = [];
  let dragging = null;

  const PRESETS = {{
    rect:    [[0,0],[100,0],[100,100],[0,100]],
    trap:    [[15,0],[85,0],[100,100],[0,100]],
    para:    [[20,0],[100,0],[80,100],[0,100]],
    lshape:  [[0,0],[60,0],[60,40],[100,40],[100,100],[0,100]],
    diamond: [[50,0],[100,50],[50,100],[0,50]],
  }};

  // Load existing clip-path value
  const existingClip = {clip_val!r};
  if (existingClip) {{
    const matches = [...existingClip.matchAll(/([\d.]+)%\s+([\d.]+)%/g)];
    if (matches.length >= 3) {{
      points = matches.map(m => [parseFloat(m[1]), parseFloat(m[2])]);
    }}
  }}
  if (points.length === 0) points = [...PRESETS.rect];

  function toCanvas(px, py) {{
    return [px / 100 * W, py / 100 * H];
  }}
  function fromCanvas(cx, cy) {{
    return [Math.round(cx / W * 100 * 10) / 10, Math.round(cy / H * 100 * 10) / 10];
  }}

  function draw() {{
    ctx.clearRect(0, 0, W, H);
    // Draw grid
    ctx.strokeStyle = '#2a2a2a';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 10; i++) {{
      ctx.beginPath(); ctx.moveTo(i*W/10, 0); ctx.lineTo(i*W/10, H); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(0, i*H/10); ctx.lineTo(W, i*H/10); ctx.stroke();
    }}
    if (points.length < 2) return;
    // Fill
    ctx.beginPath();
    const [sx, sy] = toCanvas(...points[0]);
    ctx.moveTo(sx, sy);
    for (let i = 1; i < points.length; i++) {{
      const [cx2, cy2] = toCanvas(...points[i]);
      ctx.lineTo(cx2, cy2);
    }}
    ctx.closePath();
    ctx.fillStyle = 'rgba(192,57,43,0.35)';
    ctx.fill();
    ctx.strokeStyle = '#e74c3c';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    // Draw points
    points.forEach(([px, py], i) => {{
      const [cx2, cy2] = toCanvas(px, py);
      ctx.beginPath();
      ctx.arc(cx2, cy2, 5, 0, Math.PI*2);
      ctx.fillStyle = '#e74c3c';
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.fillStyle = '#fff';
      ctx.font = '9px monospace';
      ctx.fillText(i+1, cx2+6, cy2-4);
    }});
  }}

  function getHitPoint(cx, cy) {{
    for (let i = 0; i < points.length; i++) {{
      const [px, py] = toCanvas(...points[i]);
      if (Math.hypot(cx-px, cy-py) < 8) return i;
    }}
    return -1;
  }}

  canvas.addEventListener('mousedown', e => {{
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;
    const hit = getHitPoint(cx, cy);
    if (hit >= 0) {{ dragging = hit; }}
    else {{
      points.push(fromCanvas(cx, cy));
      draw();
    }}
  }});

  canvas.addEventListener('mousemove', e => {{
    if (dragging === null) return;
    const rect = canvas.getBoundingClientRect();
    const cx = Math.max(0, Math.min(W, e.clientX - rect.left));
    const cy = Math.max(0, Math.min(H, e.clientY - rect.top));
    points[dragging] = fromCanvas(cx, cy);
    draw();
  }});

  canvas.addEventListener('mouseup', () => {{ dragging = null; }});
  canvas.addEventListener('mouseleave', () => {{ dragging = null; }});

  // Right-click to delete point
  canvas.addEventListener('contextmenu', e => {{
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;
    const hit = getHitPoint(cx, cy);
    if (hit >= 0) {{ points.splice(hit, 1); draw(); }}
  }});

  window.resetShape = function() {{
    points = [...PRESETS.rect];
    draw();
  }};

  window.clearPoints = function() {{
    points = [];
    draw();
  }};

  window.applyPreset = function(name) {{
    points = PRESETS[name].map(p => [...p]);
    draw();
  }};

  window.applyShape = function() {{
    const clipStr = points.map(([px, py]) => `${{px}}% ${{py}}%`).join(', ');
    // Find and update the clip-path input field
    const inputs = document.querySelectorAll('input[name="map_clip_path"], textarea[name="map_clip_path"]');
    inputs.forEach(inp => {{ inp.value = clipStr; }});
    // Flash confirmation
    const btn = event.target;
    btn.textContent = '✓ Применено!';
    btn.style.background = '#27ae60';
    setTimeout(() => {{ btn.textContent = '✓ Применить'; btn.style.background = '#8b1a1a'; }}, 1500);
  }};

  draw();
}})();
</script>
''', clip_val=clip_val)
    map_shape_editor.short_description = ''

