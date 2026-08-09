from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join

from .models import HistoryTextBlock


@admin.register(HistoryTextBlock)
class HistoryTextBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'text_preview', 'position_preview', 'font_size_px', 'font_weight', 'published', 'order')
    list_editable = ('published', 'order')
    list_filter = ('published', 'font_family', 'font_weight', 'text_align')
    search_fields = ('title', 'text')
    readonly_fields = ('position_editor',)
    save_on_top = True
    fieldsets = (
        ('Текст', {
            'fields': ('title', 'text', 'published', 'order'),
        }),
        ('Позиция на фоне', {
            'fields': (('left_percent', 'top_percent'), 'width_percent', 'position_editor'),
            'description': 'Позиции считаются в процентах от всей длинной картинки истории. Блок можно перетащить мышкой в предпросмотре.',
        }),
        ('Шрифт и вид', {
            'fields': (
                ('font_family', 'font_size_px'),
                ('font_weight', 'font_style'),
                ('color', 'text_align'),
                ('line_height', 'letter_spacing_px'),
                ('uppercase', 'text_shadow'),
            ),
        }),
    )

    @admin.display(description='Текст')
    def text_preview(self, obj):
        text = obj.text.replace('\n', ' / ')
        return text[:70] + ('...' if len(text) > 70 else '')

    @admin.display(description='X / Y / W')
    def position_preview(self, obj):
        return f'{obj.left_percent:g}% / {obj.top_percent:g}% / {obj.width_percent:g}%'

    @admin.display(description='Предпросмотр позиции')
    def position_editor(self, obj):
        bg_url = static('img/historyPageBG.webp')
        font_faces = format_html_join(
            '\n',
            "@font-face {{ font-family:'TT Hoves'; src:url('{}') format('woff2'); font-weight:{}; font-style:{}; font-display:swap; }}",
            (
                (static('fonts/TTHoves-Thin.woff2'), 100, 'normal'),
                (static('fonts/TTHoves-ThinItalic.woff2'), 100, 'italic'),
                (static('fonts/TTHoves-ExtraLight.woff2'), 200, 'normal'),
                (static('fonts/TTHoves-ExtraLightItalic.woff2'), 200, 'italic'),
                (static('fonts/TTHoves-Light.woff2'), 300, 'normal'),
                (static('fonts/TTHoves-LightItalic.woff2'), 300, 'italic'),
                (static('fonts/TTHoves-Regular.woff2'), 400, 'normal'),
                (static('fonts/TTHoves-Italic.woff2'), 400, 'italic'),
                (static('fonts/TTHoves-Medium.woff2'), 500, 'normal'),
                (static('fonts/TTHoves-MediumItalic.woff2'), 500, 'italic'),
                (static('fonts/TTHoves-DemiBold.woff2'), 600, 'normal'),
                (static('fonts/TTHoves-DemiBoldItalic.woff2'), 600, 'italic'),
                (static('fonts/TTHoves-Bold.woff2'), 700, 'normal'),
                (static('fonts/TTHoves-BoldItalic.woff2'), 700, 'italic'),
                (static('fonts/TTHoves-ExtraBold.woff2'), 800, 'normal'),
                (static('fonts/TTHoves-ExtraBoldItalic.woff2'), 800, 'italic'),
                (static('fonts/TTHoves-Black.woff2'), 900, 'normal'),
                (static('fonts/TTHoves-BlackItalic.woff2'), 900, 'italic'),
            ),
        )
        return format_html(
            '''
<style>
{font_faces}
.history-admin-editor {{
  --font:'TT Hoves', sans-serif;
  max-width:980px;
}}
.history-admin-editor .history-preview-help {{
  margin:0 0 10px;
  color:#444;
}}
.history-preview-toolbar {{
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:10px 14px;
  margin:0 0 10px;
}}
.history-preview-toolbar label {{
  font-weight:600;
}}
#history-preview-zoom {{
  min-width:92px;
}}
.history-preview-readout {{
  color:#555;
}}
#history-preview-scroll {{
  max-height:680px;
  overflow:auto;
  border:1px solid #bbb;
  background:#777;
}}
#history-preview-canvas {{
  position:relative;
  width:100vw;
  aspect-ratio:1400/8815;
  background:url('{bg_url}') center top / 100% auto no-repeat;
}}
#history-preview-block {{
  position:absolute;
  box-sizing:border-box;
  padding:0;
  outline:1px dashed rgba(255,255,255,.85);
  cursor:move;
  white-space:pre-wrap;
  overflow-wrap:anywhere;
}}
#history-preview-resize {{
  position:absolute;
  top:-3px;
  right:-8px;
  bottom:-3px;
  width:16px;
  cursor:ew-resize;
}}
#history-preview-resize::after {{
  content:"";
  position:absolute;
  top:50%;
  right:3px;
  width:5px;
  height:38px;
  min-height:22px;
  transform:translateY(-50%);
  border-radius:4px;
  background:rgba(255,255,255,.92);
  box-shadow:0 0 0 1px rgba(0,0,0,.25), 0 2px 8px rgba(0,0,0,.25);
}}
</style>
<div class="history-admin-editor">
  <div class="history-preview-help">
    Перетащите текст по фону. Поля X и Y обновятся автоматически, затем нажмите "Сохранить".
  </div>
  <div class="history-preview-toolbar">
    <label for="history-preview-zoom">Масштаб предпросмотра</label>
    <select id="history-preview-zoom">
      <option value="100" selected>100%</option>
      <option value="125">125%</option>
      <option value="150">150%</option>
      <option value="200">200%</option>
    </select>
    <span class="history-preview-readout">Размер текста: <strong id="history-preview-font-value"></strong></span>
    <span class="history-preview-readout">Ширина блока: <strong id="history-preview-width-value"></strong></span>
  </div>
  <div id="history-preview-scroll">
    <div id="history-preview-canvas">
      <div id="history-preview-block">
        <span id="history-preview-text"></span>
        <span id="history-preview-resize" title="Потяните, чтобы изменить ширину"></span>
      </div>
    </div>
  </div>
</div>
<script>
(function() {{
  const canvas = document.getElementById('history-preview-canvas');
  const block = document.getElementById('history-preview-block');
  const textNode = document.getElementById('history-preview-text');
  const resizeHandle = document.getElementById('history-preview-resize');
  const zoomInput = document.getElementById('history-preview-zoom');
  const widthValue = document.getElementById('history-preview-width-value');
  const fontValue = document.getElementById('history-preview-font-value');
  const leftInput = document.getElementById('id_left_percent');
  const topInput = document.getElementById('id_top_percent');
  const widthInput = document.getElementById('id_width_percent');
  const textInput = document.getElementById('id_text');
  const fontInput = document.getElementById('id_font_family');
  const sizeInput = document.getElementById('id_font_size_px');
  const weightInput = document.getElementById('id_font_weight');
  const styleInput = document.getElementById('id_font_style');
  const colorInput = document.getElementById('id_color');
  const alignInput = document.getElementById('id_text_align');
  const lineHeightInput = document.getElementById('id_line_height');
  const letterInput = document.getElementById('id_letter_spacing_px');
  const uppercaseInput = document.getElementById('id_uppercase');
  const shadowInput = document.getElementById('id_text_shadow');
  const HISTORY_REFERENCE_WIDTH = 1365;
  if (!canvas || !block || !textNode || !resizeHandle || !leftInput || !topInput || !widthInput) return;

  function numberValue(input, fallback) {{
    const value = parseFloat(input && input.value);
    return Number.isFinite(value) ? value : fallback;
  }}

  function clamp(value, min, max) {{
    return Math.max(min, Math.min(max, value));
  }}

  function renderBlock() {{
    const left = numberValue(leftInput, 50);
    const top = numberValue(topInput, 10);
    const width = numberValue(widthInput, 24);
    const zoom = clamp(numberValue(zoomInput, 100), 100, 240) / 100;
    const liveWidth = Math.max(320, window.innerWidth || HISTORY_REFERENCE_WIDTH);
    const liveFontSize = numberValue(sizeInput, 32) * liveWidth / HISTORY_REFERENCE_WIDTH;
    const previewFontValue = (numberValue(sizeInput, 32) * zoom).toFixed(4).replace(/[.]?0+$/, '');
    canvas.style.width = (100 * zoom) + 'vw';
    block.style.left = left + '%';
    block.style.top = top + '%';
    block.style.width = width + '%';
    block.style.fontFamily = fontInput ? fontInput.value : 'Arial, sans-serif';
    block.style.fontSize = 'calc(' + previewFontValue + ' * 0.0732600733vw)';
    block.style.fontWeight = weightInput ? weightInput.value : '700';
    block.style.fontStyle = styleInput ? styleInput.value : 'normal';
    block.style.color = colorInput ? colorInput.value : '#ffffff';
    block.style.textAlign = alignInput ? alignInput.value : 'left';
    block.style.lineHeight = numberValue(lineHeightInput, 1.1);
    block.style.letterSpacing = numberValue(letterInput, 0) + 'px';
    block.style.textTransform = uppercaseInput && uppercaseInput.checked ? 'uppercase' : 'none';
    block.style.textShadow = shadowInput && shadowInput.checked ? '0 2px 10px rgba(0,0,0,.45)' : 'none';
    textNode.textContent = textInput && textInput.value ? textInput.value : 'Текст';
    if (widthValue) widthValue.textContent = width.toFixed(2).replace(/[.]00$/, '') + '%';
    if (fontValue) fontValue.textContent = liveFontSize.toFixed(1).replace(/[.]0$/, '') + 'px';
  }}

  let mode = null;
  let offsetX = 0;
  let offsetY = 0;

  block.addEventListener('pointerdown', function(event) {{
    if (event.target === resizeHandle) return;
    mode = 'drag';
    const rect = block.getBoundingClientRect();
    offsetX = event.clientX - rect.left;
    offsetY = event.clientY - rect.top;
    block.setPointerCapture(event.pointerId);
    event.preventDefault();
  }});

  resizeHandle.addEventListener('pointerdown', function(event) {{
    mode = 'resize';
    resizeHandle.setPointerCapture(event.pointerId);
    event.preventDefault();
    event.stopPropagation();
  }});

  window.addEventListener('pointermove', function(event) {{
    if (!mode) return;
    const canvasRect = canvas.getBoundingClientRect();
    if (mode === 'drag') {{
      const blockRect = block.getBoundingClientRect();
      const nextLeft = ((event.clientX - canvasRect.left - offsetX) / canvasRect.width) * 100;
      const nextTop = ((event.clientY - canvasRect.top - offsetY) / canvasRect.height) * 100;
      const maxLeft = 100 - (blockRect.width / canvasRect.width) * 100;
      const maxTop = 100 - (blockRect.height / canvasRect.height) * 100;
      leftInput.value = clamp(nextLeft, 0, maxLeft).toFixed(2);
      topInput.value = clamp(nextTop, 0, maxTop).toFixed(2);
    }} else if (mode === 'resize') {{
      const left = numberValue(leftInput, 0);
      const nextRight = ((event.clientX - canvasRect.left) / canvasRect.width) * 100;
      widthInput.value = clamp(nextRight - left, 3, 100 - left).toFixed(2);
    }}
    renderBlock();
  }});

  window.addEventListener('pointerup', function() {{
    mode = null;
  }});

  [leftInput, topInput, widthInput, textInput, fontInput, sizeInput, weightInput, styleInput, colorInput, alignInput, lineHeightInput, letterInput, uppercaseInput, shadowInput, zoomInput].forEach(function(input) {{
    if (input) input.addEventListener('input', renderBlock);
    if (input) input.addEventListener('change', renderBlock);
  }});
  window.addEventListener('resize', renderBlock);

  renderBlock();
}})();
</script>
            ''',
            bg_url=bg_url,
            font_faces=font_faces,
        )
