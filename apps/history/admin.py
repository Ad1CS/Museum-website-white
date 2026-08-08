from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html

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
        return format_html(
            '''
<div class="history-admin-editor" style="max-width:820px;">
  <div style="margin:0 0 10px;color:#444;">
    Перетащите текст по фону. Поля X и Y обновятся автоматически, затем нажмите "Сохранить".
  </div>
  <div id="history-preview-scroll" style="max-height:680px;overflow:auto;border:1px solid #bbb;background:#777;">
    <div id="history-preview-canvas" style="position:relative;width:100%;aspect-ratio:2125/13379;background:url('{bg_url}') center top / 100% auto no-repeat;">
      <div id="history-preview-block" style="position:absolute;box-sizing:border-box;padding:4px 6px;border:1px dashed rgba(255,255,255,.8);cursor:move;white-space:pre-wrap;overflow-wrap:anywhere;"></div>
    </div>
  </div>
</div>
<script>
(function() {{
  const canvas = document.getElementById('history-preview-canvas');
  const block = document.getElementById('history-preview-block');
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
  if (!canvas || !block || !leftInput || !topInput) return;

  function numberValue(input, fallback) {{
    const value = parseFloat(input && input.value);
    return Number.isFinite(value) ? value : fallback;
  }}

  function renderBlock() {{
    const left = numberValue(leftInput, 50);
    const top = numberValue(topInput, 10);
    const width = numberValue(widthInput, 24);
    block.style.left = left + '%';
    block.style.top = top + '%';
    block.style.width = width + '%';
    block.style.fontFamily = fontInput ? fontInput.value : 'Arial, sans-serif';
    block.style.fontSize = numberValue(sizeInput, 32) + 'px';
    block.style.fontWeight = weightInput ? weightInput.value : '700';
    block.style.fontStyle = styleInput ? styleInput.value : 'normal';
    block.style.color = colorInput ? colorInput.value : '#ffffff';
    block.style.textAlign = alignInput ? alignInput.value : 'left';
    block.style.lineHeight = numberValue(lineHeightInput, 1.1);
    block.style.letterSpacing = numberValue(letterInput, 0) + 'px';
    block.style.textTransform = uppercaseInput && uppercaseInput.checked ? 'uppercase' : 'none';
    block.style.textShadow = shadowInput && shadowInput.checked ? '0 2px 10px rgba(0,0,0,.45)' : 'none';
    block.textContent = textInput && textInput.value ? textInput.value : 'Текст';
  }}

  let dragging = false;
  let offsetX = 0;
  let offsetY = 0;

  block.addEventListener('mousedown', function(event) {{
    dragging = true;
    const rect = block.getBoundingClientRect();
    offsetX = event.clientX - rect.left;
    offsetY = event.clientY - rect.top;
    event.preventDefault();
  }});

  window.addEventListener('mousemove', function(event) {{
    if (!dragging) return;
    const canvasRect = canvas.getBoundingClientRect();
    const blockRect = block.getBoundingClientRect();
    const nextLeft = ((event.clientX - canvasRect.left - offsetX) / canvasRect.width) * 100;
    const nextTop = ((event.clientY - canvasRect.top - offsetY) / canvasRect.height) * 100;
    const maxLeft = 100 - (blockRect.width / canvasRect.width) * 100;
    const maxTop = 100 - (blockRect.height / canvasRect.height) * 100;
    leftInput.value = Math.max(0, Math.min(maxLeft, nextLeft)).toFixed(2);
    topInput.value = Math.max(0, Math.min(maxTop, nextTop)).toFixed(2);
    renderBlock();
  }});

  window.addEventListener('mouseup', function() {{
    dragging = false;
  }});

  [leftInput, topInput, widthInput, textInput, fontInput, sizeInput, weightInput, styleInput, colorInput, alignInput, lineHeightInput, letterInput, uppercaseInput, shadowInput].forEach(function(input) {{
    if (input) input.addEventListener('input', renderBlock);
    if (input) input.addEventListener('change', renderBlock);
  }});

  renderBlock();
}})();
</script>
            ''',
            bg_url=bg_url,
        )
