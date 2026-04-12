from django.contrib import admin
from django.utils.html import format_html
from .models import Building, MapSettings


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
                ('pos_x', 'pos_y'),
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
        from django.templatetags.static import static
        map_url = static('img/map2002.jpg')
        
        return format_html('''
<div style="margin-top:16px; border:1px solid #444; padding:15px; background:#1a1a1a; border-radius:6px; font-family:sans-serif;">
  <div style="font-size:11px;color:#888;margin-bottom:12px; font-family:Oswald,sans-serif;letter-spacing:.1em;text-transform:uppercase;">
    Инструмент рисования формы здания
  </div>
  
  <div style="margin-bottom:12px; display:flex; align-items:center; gap:15px; flex-wrap:wrap;">
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="color:#888; font-size:10px;">МАСШТАБ:</span>
      <input type="range" id="b-draw-zoom" min="0.1" max="2" step="0.05" value="0.1" style="width:150px;">
      <span id="b-zoom-val" style="color:#e74c3c; font-weight:bold; font-family:monospace; font-size:11px; width:40px;">10%</span>
    </div>
    <div style="color:#aaa; font-size:10px;">
      (<b>Тяните мышкой</b> для перемещения. Удерживайте <b>Ctrl</b> для рисования точек. <b>Ctrl+Zoom</b> — масштаб.)
    </div>
  </div>

  <div id="b-viewport" style="width:100%; height:500px; overflow:auto; background:#000; border:1px solid #333; position:relative; scroll-behavior: auto; cursor: grab;">
    <div id="b-canvas-container" style="position:relative; width:736px; height:414px; transform-origin:0 0;">
      <img src="{map_url}" id="b-map-img" style="width:100%; height:100%; display:block; pointer-events:none;">
      <canvas id="b-canvas" width="7368" height="4144" 
        style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events: auto;"></canvas>
    </div>
  </div>

  <div style="margin-top:15px; display:flex; gap:8px; flex-wrap:wrap;">
    <button type="button" onclick="bUndo()" style="font-size:11px;padding:6px 12px;background:#333;color:#fff;border:1px solid #444;cursor:pointer;">↶ ОТМЕНИТЬ ТОЧКУ</button>
    <button type="button" onclick="bClear()" style="font-size:11px;padding:6px 12px;background:#333;color:#fff;border:1px solid #444;cursor:pointer;">✕ ОЧИСТИТЬ ВСЁ</button>
    <button type="button" onclick="bApply()" style="font-size:11px;padding:6px 20px;background:#c0392b;color:#fff;border:none;cursor:pointer;font-weight:bold;box-shadow:0 2px 8px rgba(0,0,0,0.3);">✓ ПРИМЕНИТЬ ФОРМУ (CLIP-PATH)</button>
  </div>
</div>

<script>
(function() {{
  const canvas = document.getElementById('b-canvas');
  const ctx = canvas.getContext('2d');
  const zoomSlider = document.getElementById('b-draw-zoom');
  const zoomVal = document.getElementById('b-zoom-val');
  const container = document.getElementById('b-canvas-container');
  const viewport = document.getElementById('b-viewport');
  
  let points = []; 
  let isPanning = false;
  let lastMouseX, lastMouseY;
  let drawMode = false;

  // Initial height sync
  container.style.height = (4144 * parseFloat(zoomSlider.value)) + 'px';

  zoomSlider.oninput = function() {{
    const z = parseFloat(this.value);
    zoomVal.innerText = Math.round(z * 100) + '%';
    container.style.width = (7368 * z) + 'px';
    container.style.height = (4144 * z) + 'px';
  }};

  viewport.addEventListener('wheel', e => {{
    if (e.ctrlKey) {{
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.05 : 0.05;
      zoomSlider.value = Math.min(Math.max(parseFloat(zoomSlider.value) + delta, 0.1), 2);
      zoomSlider.dispatchEvent(new Event('input'));
    }} else if (e.altKey) {{
      e.preventDefault();
      viewport.scrollLeft += e.deltaY;
    }}
  }}, {{ passive: false }});

  window.addEventListener('keydown', e => {{ 
    if(e.ctrlKey) {{ drawMode = true; viewport.style.cursor='crosshair'; }}
    if(e.code==='Space' || e.key==='Alt') e.preventDefault();
  }});
  window.addEventListener('keyup', e => {{ 
    if(!e.ctrlKey) {{ drawMode = false; viewport.style.cursor='grab'; }}
  }});

  viewport.onmousedown = e => {{
    if (!drawMode || e.button === 1) {{
      isPanning = true;
      lastMouseX = e.clientX; lastMouseY = e.clientY;
      viewport.style.cursor = 'grabbing';
      e.preventDefault();
    }}
  }};

  canvas.onmousedown = e => {{
    if (isPanning) return;
    if (e.button === 0 && drawMode) {{
      const rect = canvas.getBoundingClientRect();
      const z = parseFloat(zoomSlider.value);
      const x = (e.clientX - rect.left) / z;
      const y = (e.clientY - rect.top) / z;
      points.push([x, y]);
      draw();
    }}
  }};

  window.addEventListener('mousemove', e => {{
    if (isPanning) {{
      viewport.scrollLeft -= (e.clientX - lastMouseX);
      viewport.scrollTop -= (e.clientY - lastMouseY);
      lastMouseX = e.clientX; lastMouseY = e.clientY;
    }}
  }});

  window.addEventListener('mouseup', () => {{ 
    isPanning = false; 
    viewport.style.cursor = drawMode ? 'crosshair' : 'grab'; 
  }});
  canvas.oncontextmenu = e => {{ e.preventDefault(); bUndo(); }};

  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (points.length === 0) return;
    ctx.beginPath();
    points.forEach(([x, y], i) => {{ if (i===0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }});
    if (points.length > 2) ctx.closePath();
    ctx.fillStyle = 'rgba(231, 76, 60, 0.3)'; ctx.fill();
    ctx.strokeStyle = '#e74c3c'; ctx.lineWidth = 15; ctx.stroke();
    points.forEach(([x, y]) => {{
      ctx.beginPath(); ctx.arc(x, y, 20, 0, Math.PI*2);
      ctx.fillStyle = "#fff"; ctx.fill(); ctx.strokeStyle = "#e74c3c"; ctx.stroke();
    }});
  }}

  window.bUndo = () => {{ points.pop(); draw(); }};
  window.bClear = () => {{ points = []; draw(); }};
  window.bApply = () => {{
    if (points.length < 3) return;
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
    points.forEach(([x,y]) => {{
      if(x<minX) minX=x; if(x>maxX) maxX=x; if(y<minY) minY=y; if(y>maxY) maxY=y;
    }});
    const w = maxX - minX, h = maxY - minY;
    const clipStr = points.map(([x, y]) => `${{Math.round((x-minX)/w*1000)/10}}% ${{Math.round((y-minY)/h*1000)/10}}%`).join(', ');
    const input = document.querySelector('input[name="map_clip_path"]');
    if (input) {{ input.value = clipStr; const btn = event.target; btn.innerText = "✓ ГОТОВО"; setTimeout(()=>btn.innerText="✓ ПРИМЕНИТЬ ФОРМУ (CLIP-PATH)", 1000); }}
  }};
}})();
</script>
''', map_url=map_url)
    map_shape_editor.short_description = ''



@admin.register(MapSettings)
class MapSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Начальная позиция карты', {'fields': (('center_x', 'center_y'), 'zoom')}),
        ('Масштабирование', {'fields': (('min_zoom', 'max_zoom'), 'building_zoom')}),
        ('Территория музея (на отдалении)', {
            'fields': (
                ('show_territory', 'show_territory_label'),
                'territory_label',
                ('territory_x', 'territory_y'),
                ('territory_w', 'territory_h'),
                'territory_rotation',
                ('territory_mirror_x', 'territory_mirror_y'),
                'territory_clip_path',
                'map_shape_editor',
            ),
            'description': 'Параметры рамки, которая видна при отдалении. По клику на неё карта приближается к стандартному виду.',
        }),
    )
    readonly_fields = ['map_shape_editor']

    def has_add_permission(self, request):
        return not MapSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def map_shape_editor(self, obj):
        from django.templatetags.static import static
        map_url = static('img/map2002.jpg')
        
        return format_html('''
<div style="margin-top:20px; border:1px solid #444; padding:20px; background:#222; border-radius:8px; font-family:sans-serif;">
  <h4 style="color:#e74c3c; margin-top:0; text-transform:uppercase; letter-spacing:1px; font-size:13px;">
    Инструмент рисования территории
  </h4>
  
  <div style="margin-bottom:15px; display:flex; align-items:center; gap:15px; flex-wrap:wrap;">
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="color:#fff; font-size:11px;">МАСШТАБ:</span>
      <input type="range" id="t-draw-zoom" min="0.1" max="2" step="0.05" value="0.1" style="width:200px;">
      <span id="t-zoom-val" style="color:#e74c3c; font-weight:bold; font-family:monospace; font-size:12px; width:40px;">10%</span>
    </div>
    <div style="color:#fff; font-size:11px;">
      (<b>Тяните мышкой</b> для перемещения. Удерживайте <b>Ctrl</b> для рисования точек. <b>Ctrl+Zoom</b> — масштаб.)
    </div>
  </div>

  <div id="t-viewport" style="width:100%; height:550px; overflow:auto; background:#000; border:1px solid #555; position:relative; scroll-behavior: auto; cursor: grab;">
    <div id="t-canvas-container" style="position:relative; width:736px; height:414px; transform-origin:0 0;">
      <img src="{map_url}" style="width:100%; height:100%; display:block; pointer-events:none;">
      <canvas id="t-canvas" width="7368" height="4144" 
        style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events: auto;"></canvas>
    </div>
    <div id="t-stats" style="position:fixed; bottom:30px; right:30px; background:rgba(0,0,0,0.85); color:#0f0; padding:12px; font-family:monospace; font-size:11px; border:1px solid #444; pointer-events:none; z-index:100; line-height:1.5;">
      Ожидание первой точки...
    </div>
  </div>

  <div style="margin-top:15px; display:flex; gap:10px; flex-wrap:wrap;">
    <button type="button" onclick="tUndo()" style="background:#444; color:#fff; border:none; padding:8px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">↶ ОТМЕНИТЬ ТОЧКУ</button>
    <button type="button" onclick="tClear()" style="background:#444; color:#fff; border:none; padding:8px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">✕ ОЧИСТИТЬ</button>
    <button type="button" onclick="tApply()" style="background:#c0392b; color:#fff; border:none; padding:8px 25px; border-radius:4px; cursor:pointer; font-weight:bold; box-shadow:0 2px 10px rgba(204,51,51,0.3);">✓ ПРИМЕНИТЬ ВСЕ ПАРАМЕТРЫ</button>
  </div>
</div>

<script>
(function() {{
  const canvas = document.getElementById('t-canvas');
  const ctx = canvas.getContext('2d');
  const zoomSlider = document.getElementById('t-draw-zoom');
  const zoomVal = document.getElementById('t-zoom-val');
  const container = document.getElementById('t-canvas-container');
  const viewport = document.getElementById('t-viewport');
  const stats = document.getElementById('t-stats');
  
  let points = []; 
  let isPanning = false;
  let lastMouseX, lastMouseY;
  let drawMode = false;

  // Initial height sync
  container.style.height = (4144 * parseFloat(zoomSlider.value)) + 'px';

  zoomSlider.oninput = function() {{
    const z = parseFloat(this.value);
    zoomVal.innerText = Math.round(z * 100) + '%';
    container.style.width = (7368 * z) + 'px';
    container.style.height = (4144 * z) + 'px';
  }};

  // Zoom with Ctrl + Wheel, Horizontal scroll with Alt + Wheel
  viewport.addEventListener('wheel', e => {{
    if (e.ctrlKey) {{
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.05 : 0.05;
      zoomSlider.value = Math.min(Math.max(parseFloat(zoomSlider.value) + delta, 0.1), 2);
      zoomSlider.dispatchEvent(new Event('input'));
    }} else if (e.altKey) {{
      e.preventDefault();
      viewport.scrollLeft += e.deltaY;
    }}
  }}, {{ passive: false }});

  window.addEventListener('keydown', e => {{ 
    if(e.ctrlKey) {{ drawMode = true; viewport.style.cursor='crosshair'; }}
    if(e.code==='Space' || e.key==='Alt') e.preventDefault();
  }});
  window.addEventListener('keyup', e => {{ 
    if(!e.ctrlKey) {{ drawMode = false; viewport.style.cursor='grab'; }}
  }});

  viewport.onmousedown = e => {{
    if (!drawMode || e.button === 1) {{
      isPanning = true;
      lastMouseX = e.clientX; lastMouseY = e.clientY;
      viewport.style.cursor = 'grabbing';
      e.preventDefault();
    }}
  }};

  canvas.onmousedown = e => {{
    if (isPanning) return;
    if (e.button === 0 && drawMode) {{
      const rect = canvas.getBoundingClientRect();
      const z = parseFloat(zoomSlider.value);
      const x = (e.clientX - rect.left) / z;
      const y = (e.clientY - rect.top) / z;
      points.push([x, y]);
      draw();
    }}
  }};

  window.addEventListener('mousemove', e => {{
    if (isPanning) {{
      viewport.scrollLeft -= (e.clientX - lastMouseX);
      viewport.scrollTop -= (e.clientY - lastMouseY);
      lastMouseX = e.clientX; lastMouseY = e.clientY;
    }}
  }});

  window.addEventListener('mouseup', () => {{ 
    isPanning = false; 
    viewport.style.cursor = drawMode ? 'crosshair' : 'grab'; 
  }});
  canvas.oncontextmenu = e => {{ e.preventDefault(); tUndo(); }};

  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (points.length === 0) return;
    ctx.beginPath();
    points.forEach(([x, y], i) => {{ if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }});
    if (points.length > 2) ctx.closePath();
    ctx.fillStyle = 'rgba(231, 76, 60, 0.25)'; ctx.fill();
    ctx.strokeStyle = '#e74c3c'; ctx.lineWidth = 20; ctx.stroke();
    points.forEach(([x, y]) => {{
      ctx.beginPath(); ctx.arc(x, y, 30, 0, Math.PI*2);
      ctx.fillStyle = "#fff"; ctx.fill(); ctx.strokeStyle = "#e74c3c"; ctx.stroke();
    }});
    updateStats();
  }}

  function updateStats() {{
    if (points.length < 2) return;
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
    points.forEach(([x, y]) => {{
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }});
    const cx = Math.round((minX + maxX) / 2), cy = Math.round((minY + maxY) / 2);
    const w = Math.round(maxX - minX), h = Math.round(maxY - minY);
    stats.innerHTML = `ЦЕНТР: X:${{cx}} Y:${{cy}}<br>РАЗМЕР: ${{w}}x${{h}}px<br>ТОЧЕК: ${{points.length}}`;
  }}

  window.tUndo = () => {{ points.pop(); draw(); }};
  window.tClear = () => {{ points = []; draw(); stats.innerText = "Ожидание..."; }};

  window.tApply = () => {{
    if (points.length < 3) return;
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
    points.forEach(([x, y]) => {{
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }});
    const cx = Math.round((minX + maxX) / 2), cy = Math.round((minY + maxY) / 2);
    const w = Math.round(maxX - minX), h = Math.round(maxY - minY);
    document.querySelector('input[name="territory_x"]').value = cx;
    document.querySelector('input[name="territory_y"]').value = cy;
    document.querySelector('input[name="territory_w"]').value = w;
    document.querySelector('input[name="territory_h"]').value = h;
    const clipStr = points.map(([x, y]) => `${{Math.round((x-minX)/w*1000)/10}}% ${{Math.round((y-minY)/h*1000)/10}}%`).join(', ');
    document.querySelector('input[name="territory_clip_path"]').value = clipStr;
    const btn = event.target;
    btn.innerText = "✓ ПАРАМЕТРЫ ПЕРЕНЕСЕНЫ";
    setTimeout(() => btn.innerText = "✓ ПРИМЕНИТЬ ВСЕ ПАРАМЕТРЫ", 1000);
  }};
}})();
</script>
''', map_url=map_url)
    map_shape_editor.short_description = ''
