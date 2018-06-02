from django.db import models


class StopWord(models.Model):
    phrase = models.CharField(max_length=50)
    is_list = models.BooleanField(default=False)

    @classmethod
    def get_stopwords(cls):
        return cls.objects.values('phrase', 'is_list')

    def __str__(self):
        return self.phrase


class History(models.Model):
    vk_timestamp = models.IntegerField() # перевести в дату
    user_id = models.IntegerField()
    has_stopword = models.BooleanField(default=False)
    is_not_member = models.BooleanField(default=False)
    text = models.TextField()

    def __str__(self):
        return f'{self.user_id}'

    @classmethod
    def save_message(
        cls, vk_timestamp, user_id, text, 
        has_stopword=False, is_not_member=False
    ):
        record = cls(vk_timestamp=vk_timestamp, user_id=int(user_id), text=text)
        if has_stopword:
            record.has_stopword = True
        if is_not_member:
            record.is_not_member = True
        record.save()

    @classmethod
    def save_messages_non_members(cls, data):
        for d in data:
            cls.save_message(*d, is_not_member=True)

    @classmethod
    def save_messages_have_stopword(cls, data):
        for d in data:
            cls.save_message(*d, has_stopword=True)

    class Meta:
        verbose_name_plural = 'History'