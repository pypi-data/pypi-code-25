class BaseMultipleFileUploadMixin(object):
    inline_photo_model = None

    def save_model(self, request, obj, form, change):
        result = super(BaseMultipleFileUploadMixin, self).save_model(request, obj, form, change)
        if form.cleaned_data.get('multiupload', None):
            for image in form.cleaned_data['multiupload']:
                photo = self.inline_photo_model(
                    gallery=obj,
                    image=image
                )
                photo.save()
        return result
