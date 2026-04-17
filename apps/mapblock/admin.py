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
    readonly_fields     = ['map_shape_editor', 'cropped_preview', 'manual_crop_tool']
    save_on_top = True

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'main_image', 'cropped_preview', 'manual_crop_tool', 'built_years', 'description', 'published'),
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
            'background:rgba(255,255,255,0.2);border:1px solid #FFFFFF;box-sizing:border-box;{rot}{clip}">'
            '</div></div>',
            bg=bg_url,
            l=obj.map_left, t=obj.map_top,
            w=obj.map_width, h=obj.map_height,
            rot=rotation_style, clip=clip_style,
        )
    map_preview_thumb.short_description = 'Позиция'

    def cropped_preview(self, obj):
        if obj.main_image:
            # main_image_cropped is an ImageSpecField from models.py
            return format_html(
                '<div style="margin-bottom:10px;"><img src="{}" style="max-width:300px; border-radius:4px; border:1px solid #444;"></div>'
                '<div style="color:#aaa; font-size:11px;">Это автоматическая обрезка (16:9) для окна на карте.</div>',
                obj.main_image_cropped.url
            )
        return "Сначала загрузите изображение"
    cropped_preview.short_description = 'Предпросмотр (16:9)'

    def manual_crop_tool(self, obj):
        if not obj.main_image:
            return "Сначала загрузите изображение"
        
        img_url = obj.main_image.url
        crop_data = obj.manual_crop_data or "0,0,100,100" # fallback

        return format_html('''
<div style="margin-top:16px; border:1px solid #444; padding:20px; background:#1a1a1a; border-radius:8px; font-family:sans-serif;">
  <div style="font-size:12px;color:#fff;margin-bottom:15px; font-weight:bold; text-transform:uppercase; letter-spacing:0.05em;">
    Инструмент ручной обрезки фото (16:9)
  </div>
  
  <div id="crop-viewport" style="width:100%; max-width:600px; position:relative; cursor: crosshair; user-select: none; overflow:hidden; border:1px solid #333;">
    <img src="{img_url}" id="crop-source-img" style="width:100%; display:block; opacity:0.6;">
    <div id="crop-frame" style="position:absolute; border:2px solid #ff4444; box-shadow: 0 0 0 4000px rgba(0,0,0,0.5); cursor:move;">
        <div style="position:absolute; right:-5px; bottom:-5px; width:10px; height:10px; background:#ff4444; cursor:nwse-resize;"></div>
    </div>
  </div>

  <div style="margin-top:15px; display:flex; gap:10px;">
    <button type="button" onclick="applyManualCrop()" id="crop-apply-btn" style="font-size:11px;padding:8px 20px;background:#fff;color:#000;border:none;cursor:pointer;font-weight:bold;border-radius:4px;">ПРИМЕНИТЬ ОБРЕЗКУ</button>
  </div>
</div>

<script>
(function() {{
  const viewport = document.getElementById('crop-viewport');
  const img = document.getElementById('crop-source-img');
  const frame = document.getElementById('crop-frame');
  const dataInput = document.querySelector('input[name="manual_crop_data"]');
  
  let isDragging = false;
  let isResizing = false;
  let startX, startY, startLeft, startTop, startWidth, startHeight;

  img.onload = () => {{
    const currentData = dataInput.value || "10,10,80,45";
    const [x, y, w, h] = currentData.split(',').map(parseFloat);
    
    frame.style.left = x + '%';
    frame.style.top = y + '%';
    frame.style.width = w + '%';
    frame.style.height = (w * (9/16) * (img.naturalWidth / img.naturalHeight)) + '%';
    
    if (h) frame.style.height = h + '%';
  }};

  frame.onmousedown = e => {{
    e.preventDefault();
    const rect = frame.getBoundingClientRect();
    if (e.clientX > rect.right - 15 && e.clientY > rect.bottom - 15) {{
        isResizing = true;
    }} else {{
        isDragging = true;
    }}
    startX = e.clientX; startY = e.clientY;
    startLeft = frame.offsetLeft; startTop = frame.offsetTop;
    startWidth = frame.offsetWidth; startHeight = frame.offsetHeight;
  }};

  window.addEventListener('mousemove', e => {{
    if (!isDragging && !isResizing) return;
    
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    const vRect = viewport.getBoundingClientRect();

    if (isDragging) {{
        let nl = ((startLeft + dx) / vRect.width) * 100;
        let nt = ((startTop + dy) / vRect.height) * 100;
        frame.style.left = Math.max(0, Math.min(100 - (frame.offsetWidth/vRect.width*100), nl)) + '%';
        frame.style.top = Math.max(0, Math.min(100 - (frame.offsetHeight/vRect.height*100), nt)) + '%';
    }} else if (isResizing) {{
        let nw = ((startWidth + dx) / vRect.width) * 100;
        frame.style.width = Math.max(10, Math.min(100 - (frame.offsetLeft/vRect.width*100), nw)) + '%';
        // Force 16:9 ratio
        const ratio = (9/16) * (img.naturalWidth / img.naturalHeight);
        frame.style.height = (parseFloat(frame.style.width) * ratio) + '%';
    }}
  }});

  window.addEventListener('mouseup', () => {{ isDragging = false; isResizing = false; }});

  window.applyManualCrop = () => {{
    const x = parseFloat(frame.style.left);
    const y = parseFloat(frame.style.top);
    const w = parseFloat(frame.style.width);
    const h = parseFloat(frame.style.height);
    dataInput.value = `${{x.toFixed(2)}},${{y.toFixed(2)}},${{w.toFixed(2)}},${{h.toFixed(2)}}`;
    
    const btn = document.getElementById('crop-apply-btn');
    btn.style.background = "#4CAF50"; btn.innerText = "ОБРЕЗКА ПРИМЕНЕНА! СОХРАНИТЕ ЗДАНИЕ";
    setTimeout(() => {{ btn.style.background = "#fff"; btn.innerText = "ПРИМЕНИТЬ ОБРЕЗКУ"; }}, 3000);
  }};
}})();
</script>
''', img_url=img_url)
    manual_crop_tool.short_description = 'Ручная обрезка'

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
        
        # Pre-load existing data
        existing_points = []
        if obj.map_clip_path:
            import re
            matches = re.findall(r'([\d.]+)%\s+([\d.]+)%', obj.map_clip_path)
            # Width and height in pixels
            w_px = (obj.map_width / 100) * 7368
            h_px = (obj.map_height / 100) * 4144
            for mx, my in matches:
                # clip-path % are relative to the building's bounding box
                # pos_x/pos_y are the center of the building
                px = (float(mx) / 100 - 0.5) * w_px
                py = (float(my) / 100 - 0.5) * h_px
                existing_points.append([obj.pos_x + px, obj.pos_y + py])

        import json
        points_json = json.dumps(existing_points)

        return format_html('''
<div style="margin-top:16px; border:1px solid #444; padding:20px; background:#1a1a1a; border-radius:8px; font-family:sans-serif;">
  <div style="font-size:12px;color:#fff;margin-bottom:15px; font-weight:bold; text-transform:uppercase; letter-spacing:0.05em;">
    Инструмент настройки формы здания
  </div>
  
  <div style="margin-bottom:15px; display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="color:#888; font-size:11px;">МАСШТАБ:</span>
      <input type="range" id="b-draw-zoom" min="0.05" max="2" step="0.05" value="0.1" style="width:150px;">
      <span id="b-zoom-val" style="color:#fff; font-weight:bold; font-family:monospace; font-size:12px; width:40px;">10%</span>
    </div>
    <div style="color:#aaa; font-size:11px; line-height:1.4;">
      • <b>ЛКМ</b>: Рисовать (удерживайте <b>Ctrl</b>)<br>
      • <b>Смещение</b>: Тяните область за центр или точки<br>
      • <b>Навигация</b>: Тяните карту (без Ctrl)
    </div>
  </div>

  <div id="b-viewport" style="width:100%; height:600px; overflow:hidden; background:#000; border:1px solid #333; position:relative; cursor: grab; user-select: none;">
    <div id="b-canvas-container" style="position:absolute; top:0; left:0; width:7368px; height:4144px; transform-origin: 0 0; background:#000;">
      <img src="{map_url}" id="b-map-img" style="width:100%; height:100%; display:block; pointer-events:none; opacity: 0.8;">
      <canvas id="b-canvas" width="7368" height="4144" 
        style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events: auto;"></canvas>
    </div>
    <div id="b-stats" style="position:absolute; bottom:20px; right:20px; background:rgba(0,0,0,0.8); color:#fff; padding:10px; font-family:monospace; font-size:11px; border:1px solid #444; pointer-events:none; z-index:100; border-radius:4px;">
      Загрузка...
    </div>
  </div>

  <div style="margin-top:15px; display:flex; gap:10px; flex-wrap:wrap;">
    <button type="button" onclick="bUndo()" style="font-size:11px;padding:8px 15px;background:#333;color:#fff;border:1px solid #444;cursor:pointer;border-radius:4px;">Отменить точку</button>
    <button type="button" onclick="bClear()" style="font-size:11px;padding:8px 15px;background:#333;color:#fff;border:1px solid #444;cursor:pointer;border-radius:4px;">Очистить</button>
    <button type="button" onclick="bApply()" id="b-apply-btn" style="font-size:11px;padding:8px 25px;background:#fff;color:#000;border:none;cursor:pointer;font-weight:bold;border-radius:4px;">ПРИМЕНИТЬ ФОРМУ</button>
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
  const stats = document.getElementById('b-stats');
  
  const MAP_W = 7368;
  const MAP_H = 4144;

  let points = {points_json}; 
  let scale = parseFloat(zoomSlider.value);
  let offsetX = 0;
  let offsetY = 0;
  
  let isPanning = false;
  let isDraggingShape = false;
  let dragPointIndex = -1;
  let startX, startY;
  let ctrlDown = false;

  function updateTransform() {{
    zoomVal.innerText = Math.round(scale * 100) + '%';
    container.style.transform = `translate(${{offsetX}}px, ${{offsetY}}px) scale(${{scale}})`;
  }}

  // Initial centering
  if (points.length > 0) {{
    offsetX = (viewport.clientWidth / 2) - (points[0][0] * scale);
    offsetY = (viewport.clientHeight / 2) - (points[0][1] * scale);
  }} else {{
    offsetX = (viewport.clientWidth / 2) - (MAP_W * scale / 2);
    offsetY = (viewport.clientHeight / 2) - (MAP_H * scale / 2);
  }}
  updateTransform();

  zoomSlider.oninput = function() {{
    const newScale = parseFloat(this.value);
    const centerX = viewport.clientWidth / 2;
    const centerY = viewport.clientHeight / 2;
    const worldX = (centerX - offsetX) / scale;
    const worldY = (centerY - offsetY) / scale;
    scale = newScale;
    offsetX = centerX - (worldX * scale);
    offsetY = centerY - (worldY * scale);
    updateTransform();
  }};

  viewport.addEventListener('wheel', e => {{
    if (e.ctrlKey) {{
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      const newScale = Math.min(Math.max(scale * delta, 0.02), 4);
      zoomSlider.value = newScale;
      zoomSlider.dispatchEvent(new Event('input'));
    }} else {{
      offsetX -= e.deltaX;
      offsetY -= e.deltaY;
      updateTransform();
      e.preventDefault();
    }}
  }}, {{ passive: false }});

  window.addEventListener('keydown', e => {{ if(e.ctrlKey) ctrlDown = true; }});
  window.addEventListener('keyup', e => {{ if(!e.ctrlKey) ctrlDown = false; }});

  viewport.onmousedown = e => {{
    const rect = viewport.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const wx = (mx - offsetX) / scale;
    const wy = (my - offsetY) / scale;

    if (ctrlDown) {{
      points.push([wx, wy]);
      draw();
      return;
    }}

    for (let i = 0; i < points.length; i++) {{
      const [px, py] = points[i];
      const dist = Math.sqrt((wx-px)**2 + (wy-py)**2);
      if (dist < 25 / scale) {{
        dragPointIndex = i;
        isDraggingShape = true;
        startX = wx; startY = wy;
        return;
      }}
    }}

    if (points.length > 2 && isPointInPoly(wx, wy, points)) {{
      isDraggingShape = true;
      dragPointIndex = -1;
      startX = wx; startY = wy;
      return;
    }}

    isPanning = true;
    startX = e.clientX - offsetX;
    startY = e.clientY - offsetY;
    viewport.style.cursor = 'grabbing';
  }};

  window.addEventListener('mousemove', e => {{
    if (isPanning) {{
      offsetX = e.clientX - startX;
      offsetY = e.clientY - startY;
      updateTransform();
    }} else if (isDraggingShape) {{
      const rect = viewport.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const wx = (mx - offsetX) / scale;
      const wy = (my - offsetY) / scale;
      const dx = wx - startX;
      const dy = wy - startY;

      if (dragPointIndex !== -1) {{
        points[dragPointIndex] = [wx, wy];
      }} else {{
        points = points.map(([px, py]) => [px + dx, py + dy]);
      }}
      startX = wx; startY = wy;
      draw();
    }}
  }});

  window.addEventListener('mouseup', () => {{ 
    isPanning = false; isDraggingShape = false;
    viewport.style.cursor = 'grab'; 
  }});

  function isPointInPoly(x, y, pts) {{
    let inside = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {{
      const xi = pts[i][0], yi = pts[i][1], xj = pts[j][0], yj = pts[j][1];
      const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }}
    return inside;
  }}

  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (points.length === 0) {{ stats.innerText = "Ctrl+Click для рисования"; return; }}
    ctx.beginPath();
    points.forEach(([x, y], i) => {{ if (i===0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }});
    if (points.length > 2) ctx.closePath();
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'; ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 10 / Math.max(0.5, scale); ctx.stroke();
    points.forEach(([x, y]) => {{
      ctx.beginPath(); ctx.arc(x, y, 12 / Math.max(0.5, scale), 0, Math.PI*2);
      ctx.fillStyle = "#fff"; ctx.fill();
    }});
    updateStats();
  }}

  function updateStats() {{
    if (points.length < 1) return;
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
    points.forEach(([x, y]) => {{
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }});
    const cx = Math.round((minX + maxX) / 2), cy = Math.round((minY + maxY) / 2);
    stats.innerHTML = `ЦЕНТР: ${{cx}},${{cy}} | ТОЧЕК: ${{points.length}}`;
  }}

  window.bUndo = () => {{ points.pop(); draw(); }};
  window.bClear = () => {{ points = []; draw(); }};

  window.bApply = () => {{
    if (points.length < 3) return alert("Нужно минимум 3 точки");
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
    points.forEach(([x, y]) => {{
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }});
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const w = maxX - minX;
    const h = maxY - minY;
    
    // Update all relevant building fields
    document.querySelector('input[name="pos_x"]').value = Math.round(cx);
    document.querySelector('input[name="pos_y"]').value = Math.round(cy);
    document.querySelector('input[name="map_width"]').value = Math.round(w / 7368 * 1000) / 10;
    document.querySelector('input[name="map_height"]').value = Math.round(h / 4144 * 1000) / 10;
    document.querySelector('input[name="map_left"]').value = Math.round(minX / 7368 * 1000) / 10;
    document.querySelector('input[name="map_top"]').value = Math.round(minY / 4144 * 1000) / 10;
    
    const clipStr = points.map(([x, y]) => {{
      const rx = (x - minX) / w;
      const ry = (y - minY) / h;
      return `${{Math.round(rx*1000)/10}}% ${{Math.round(ry*1000)/10}}%`;
    }}).join(', ');
    
    document.querySelector('input[name="map_clip_path"]').value = clipStr;
    const btn = document.getElementById('b-apply-btn');
    btn.style.background = "#4CAF50"; btn.innerText = "ГОТОВО! НЕ ЗАБУДЬТЕ НАЖАТЬ 'СОХРАНИТЬ'";
    setTimeout(() => {{ btn.style.background = "#fff"; btn.innerText = "ПРИМЕНИТЬ ФОРМУ"; }}, 3000);
  }};

  draw();
}})();
</script>
''', map_url=map_url, points_json=points_json)
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
        
        # Pre-load existing data
        existing_points = []
        if obj.territory_clip_path:
            import re
            matches = re.findall(r'([\d.]+)%\s+([\d.]+)%', obj.territory_clip_path)
            for mx, my in matches:
                # Convert back from percentages to local pixels relative to center
                px = (float(mx) / 100 - 0.5) * obj.territory_w
                py = (float(my) / 100 - 0.5) * obj.territory_h
                existing_points.append([obj.territory_x + px, obj.territory_y + py])

        import json
        points_json = json.dumps(existing_points)

        return format_html('''
<div style="margin-top:20px; border:1px solid #444; padding:20px; background:#222; border-radius:8px; font-family:sans-serif;">
  <h4 style="color:#fff; margin-top:0; text-transform:uppercase; letter-spacing:1px; font-size:13px; font-weight:bold;">
    Инструмент настройки территории
  </h4>
  
  <div style="margin-bottom:15px; display:flex; align-items:center; gap:20px; flex-wrap:wrap;">
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="color:#fff; font-size:11px;">МАСШТАБ:</span>
      <input type="range" id="t-draw-zoom" min="0.05" max="2" step="0.05" value="0.1" style="width:150px;">
      <span id="t-zoom-val" style="color:#fff; font-weight:bold; font-family:monospace; font-size:12px; width:40px;">10%</span>
    </div>
    <div style="color:#aaa; font-size:11px; line-height:1.4;">
      • <b>ЛКМ</b>: Рисовать точки (удерживайте <b>Ctrl</b>)<br>
      • <b>Перетаскивание</b>: Тяните область за центр или точки для смещения<br>
      • <b>Навигация</b>: Тяните карту мышкой (без Ctrl)
    </div>
  </div>

  <div id="t-viewport" style="width:100%; height:600px; overflow:hidden; background:#111; border:1px solid #555; position:relative; cursor: grab; user-select: none;">
    <div id="t-canvas-container" style="position:absolute; top:0; left:0; width:7368px; height:4144px; transform-origin: 0 0; background:#000;">
        <img src="{map_url}" style="width:100%; height:100%; display:block; pointer-events:none; opacity: 0.8;">
        <canvas id="t-canvas" width="7368" height="4144" 
          style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events: auto;"></canvas>
    </div>
    <div id="t-stats" style="position:absolute; bottom:20px; right:20px; background:rgba(0,0,0,0.8); color:#fff; padding:10px; font-family:monospace; font-size:11px; border:1px solid #444; pointer-events:none; z-index:100; border-radius:4px;">
      Загрузка...
    </div>
  </div>

  <div style="margin-top:15px; display:flex; gap:10px; flex-wrap:wrap;">
    <button type="button" onclick="tUndo()" style="background:#444; color:#fff; border:none; padding:8px 15px; border-radius:4px; cursor:pointer;">Отменить точку</button>
    <button type="button" onclick="tClear()" style="background:#444; color:#fff; border:none; padding:8px 15px; border-radius:4px; cursor:pointer;">Очистить</button>
    <button type="button" onclick="tApply()" id="t-apply-btn" style="background:#fff; color:#000; border:none; padding:8px 25px; border-radius:4px; cursor:pointer; font-weight:bold;">ПРИМЕНИТЬ ИЗМЕНЕНИЯ</button>
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
  
  const MAP_W = 7368;
  const MAP_H = 4144;

  let points = {points_json}; 
  let scale = parseFloat(zoomSlider.value);
  let offsetX = 0; // Current pan X
  let offsetY = 0; // Current pan Y
  
  let isPanning = false;
  let isDraggingShape = false;
  let dragPointIndex = -1;
  let startX, startY;
  let ctrlDown = false;

  function updateTransform() {{
    zoomVal.innerText = Math.round(scale * 100) + '%';
    container.style.transform = `translate(${{offsetX}}px, ${{offsetY}}px) scale(${{scale}})`;
  }}

  // Initial centering
  if (points.length > 0) {{
    offsetX = (viewport.clientWidth / 2) - (points[0][0] * scale);
    offsetY = (viewport.clientHeight / 2) - (points[0][1] * scale);
  }} else {{
    offsetX = (viewport.clientWidth / 2) - (MAP_W * scale / 2);
    offsetY = (viewport.clientHeight / 2) - (MAP_H * scale / 2);
  }}
  updateTransform();

  zoomSlider.oninput = function() {{
    const newScale = parseFloat(this.value);
    // Zoom relative to viewport center
    const centerX = viewport.clientWidth / 2;
    const centerY = viewport.clientHeight / 2;
    
    // Calculate world point at center before zoom
    const worldX = (centerX - offsetX) / scale;
    const worldY = (centerY - offsetY) / scale;
    
    scale = newScale;
    
    // New offsets to keep same world point at center
    offsetX = centerX - (worldX * scale);
    offsetY = centerY - (worldY * scale);
    
    updateTransform();
  }};

  viewport.addEventListener('wheel', e => {{
    if (e.ctrlKey) {{
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      const newScale = Math.min(Math.max(scale * delta, 0.02), 4);
      zoomSlider.value = newScale;
      zoomSlider.dispatchEvent(new Event('input'));
    }} else {{
      offsetX -= e.deltaX;
      offsetY -= e.deltaY;
      updateTransform();
      e.preventDefault();
    }}
  }}, {{ passive: false }});

  window.addEventListener('keydown', e => {{ if(e.ctrlKey) ctrlDown = true; }});
  window.addEventListener('keyup', e => {{ if(!e.ctrlKey) ctrlDown = false; }});

  viewport.onmousedown = e => {{
    const rect = viewport.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    
    // World coordinates
    const wx = (mx - offsetX) / scale;
    const wy = (my - offsetY) / scale;

    if (ctrlDown) {{
      points.push([wx, wy]);
      draw();
      return;
    }}

    // Check points
    for (let i = 0; i < points.length; i++) {{
      const [px, py] = points[i];
      const dist = Math.sqrt((wx-px)**2 + (wy-py)**2);
      if (dist < 25 / scale) {{
        dragPointIndex = i;
        isDraggingShape = true;
        startX = wx; startY = wy;
        return;
      }}
    }}

    // Check shape
    if (points.length > 2 && isPointInPoly(wx, wy, points)) {{
      isDraggingShape = true;
      dragPointIndex = -1;
      startX = wx; startY = wy;
      return;
    }}

    isPanning = true;
    startX = e.clientX - offsetX;
    startY = e.clientY - offsetY;
    viewport.style.cursor = 'grabbing';
  }};

  window.addEventListener('mousemove', e => {{
    if (isPanning) {{
      offsetX = e.clientX - startX;
      offsetY = e.clientY - startY;
      updateTransform();
    }} else if (isDraggingShape) {{
      const rect = viewport.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const wx = (mx - offsetX) / scale;
      const wy = (my - offsetY) / scale;

      const dx = wx - startX;
      const dy = wy - startY;

      if (dragPointIndex !== -1) {{
        points[dragPointIndex] = [wx, wy];
      }} else {{
        points = points.map(([px, py]) => [px + dx, py + dy]);
      }}
      startX = wx; startY = wy;
      draw();
    }}
  }});

  window.addEventListener('mouseup', () => {{ 
    isPanning = false; 
    isDraggingShape = false;
    viewport.style.cursor = 'grab'; 
  }});

  function isPointInPoly(x, y, pts) {{
    let inside = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {{
      const xi = pts[i][0], yi = pts[i][1];
      const xj = pts[j][0], yj = pts[j][1];
      const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }}
    return inside;
  }}

  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (points.length === 0) {{ stats.innerText = "Ctrl+Click для рисования"; return; }}
    
    ctx.beginPath();
    points.forEach(([x, y], i) => {{ if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }});
    if (points.length > 2) ctx.closePath();
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'; ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 10 / Math.max(0.5, scale); ctx.stroke();
    
    points.forEach(([x, y]) => {{
      ctx.beginPath(); ctx.arc(x, y, 12 / Math.max(0.5, scale), 0, Math.PI*2);
      ctx.fillStyle = "#fff"; ctx.fill();
    }});
    updateStats();
  }}

  function updateStats() {{
    if (points.length < 1) return;
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
    points.forEach(([x, y]) => {{
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }});
    const cx = Math.round((minX + maxX) / 2), cy = Math.round((minY + maxY) / 2);
    stats.innerHTML = `ЦЕНТР: ${{cx}},${{cy}} | ТОЧЕК: ${{points.length}}`;
  }}

  window.tUndo = () => {{ points.pop(); draw(); }};
  window.tClear = () => {{ points = []; draw(); }};

  window.tApply = () => {{
    if (points.length < 3) return alert("Нужно минимум 3 точки");
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity;
    points.forEach(([x, y]) => {{
      if (x < minX) minX = x; if (x > maxX) maxX = x;
      if (y < minY) minY = y; if (y > maxY) maxY = y;
    }});
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const w = maxX - minX;
    const h = maxY - minY;
    
    document.querySelector('input[name="territory_x"]').value = Math.round(cx);
    document.querySelector('input[name="territory_y"]').value = Math.round(cy);
    document.querySelector('input[name="territory_w"]').value = Math.round(w);
    document.querySelector('input[name="territory_h"]').value = Math.round(h);
    
    const clipStr = points.map(([x, y]) => {{
      const rx = (x - cx) / w + 0.5;
      const ry = (y - cy) / h + 0.5;
      return `${{Math.round(rx*1000)/10}}% ${{Math.round(ry*1000)/10}}%`;
    }}).join(', ');
    
    document.querySelector('input[name="territory_clip_path"]').value = clipStr;
    const btn = document.getElementById('t-apply-btn');
    btn.style.background = "#4CAF50"; btn.innerText = "ГОТОВО! НЕ ЗАБУДЬТЕ НАЖАТЬ 'СОХРАНИТЬ'";
    setTimeout(() => {{ btn.style.background = "#fff"; btn.innerText = "ПРИМЕНИТЬ ИЗМЕНЕНИЯ"; }}, 3000);
  }};

  draw();
}})();
</script>
''', map_url=map_url, points_json=points_json)
    map_shape_editor.short_description = ''
