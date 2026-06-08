from django.db import models
from django.urls import reverse

class GalleryPeriod(models.Model):
    title = models.CharField("Название", max_length=200); date_range = models.CharField("Годы (текст)", max_length=100, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Период галереи"
        verbose_name_plural = "Периоды галереи"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

class MediaType(models.TextChoices):
    PHOTO = "photo", "Фотография"
    VIDEO = "video", "Видео"

class Album(models.Model):
    title       = models.CharField("Название", max_length=300)
    gallery_period = models.ForeignKey(GalleryPeriod, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name="albums", verbose_name="Период")
    is_newsreel = models.BooleanField("Кинохроника", default=False, help_text="Если отмечено, альбом попадет в отдельную категорию")
    description = models.TextField("Описание", blank=True)
    cover       = models.ImageField("Обложка", upload_to="gallery/covers/", blank=True, null=True)
    order       = models.PositiveIntegerField("Порядок", default=0)
    published   = models.BooleanField("Опубликован", default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Альбом"
        verbose_name_plural = "Альбомы"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("gallery:album_detail", args=[self.pk])

class Media(models.Model):
    album      = models.ForeignKey(Album, on_delete=models.CASCADE,
                                   related_name="media", verbose_name="Альбом")
    media_type = models.CharField("Тип", max_length=10,
                                  choices=MediaType.choices, default=MediaType.PHOTO)
    image      = models.ImageField("Изображение", upload_to="gallery/photos/",
                                   blank=True, null=True)
    video_file = models.FileField("Видеофайл", upload_to="gallery/videos/",
                                  blank=True, null=True)
    video_url  = models.URLField("Ссылка на видео (YouTube/Vimeo)", blank=True)
    caption    = models.TextField("Описание (редактируемое)", blank=True)
    date_text  = models.CharField("Год (текст)", max_length=100, blank=True)
    photographer = models.CharField("Фотограф", max_length=200, blank=True)
    fond_item  = models.ForeignKey(
        "fond.FondItem", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="gallery_photos", verbose_name="Предмет фонда (ссылка на оригинал)"
    )
    linked_staff = models.ManyToManyField(
        "staff.StaffMember", blank=True,
        related_name="photos", verbose_name="Изображённые / упомянутые сотрудники"
    )
    order      = models.PositiveIntegerField("Порядок", default=0)
    published  = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Медиафайл"
        verbose_name_plural = "Медиафайлы"
        ordering = ["order", "created_at"]

    def __str__(self):
        return self.caption[:50] or f"{self.get_media_type_display()} #{self.pk}"

    @property
    def is_video(self):
        return self.media_type == "video"

    @property
    def embed_url(self):
        url = self.video_url
        if not url: return None
        import re
        yt = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
        if yt: return f"https://www.youtube.com/embed/{yt.group(1)}"
        vm = re.search(r"vimeo\.com/(\d+)", url)
        if vm: return f"https://player.vimeo.com/video/{vm.group(1)}"
        return url

Photo = Media

