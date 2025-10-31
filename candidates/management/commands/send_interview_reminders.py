from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from candidates.models import Interview
import datetime


class Command(BaseCommand):
    help = 'Отправляет напоминания о предстоящих собеседованиях'

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_time = now + datetime.timedelta(hours=24)  # Напоминание за 24 часа

        # Находим собеседования, которые будут через 24 часа и напоминание еще не отправлено
        upcoming_interviews = Interview.objects.filter(
            scheduled_date__lte=reminder_time,
            scheduled_date__gt=now,
            status='scheduled',
            reminder_sent=False
        )

        for interview in upcoming_interviews:
            try:
                # Отправляем email напоминание
                subject = f'Напоминание: Собеседование с {interview.candidate}'
                message = f'''
Здравствуйте!

Напоминаем о запланированном собеседовании:

Кандидат: {interview.candidate.last_name} {interview.candidate.first_name} {interview.candidate.patronymic}
Должность: {interview.candidate.specialization or "Не указана"}
Дата и время: {interview.scheduled_date.strftime("%d.%m.%Y в %H:%M")}
Тип собеседования: {interview.get_interview_type_display()}
Заметки: {interview.notes or "Нет дополнительной информации"}

С уважением,
HR System
                '''

                # Отправляем email рекрутеру
                if interview.scheduled_by.email:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [interview.scheduled_by.email],
                        fail_silently=False,
                    )

                # Помечаем, что напоминание отправлено
                interview.reminder_sent = True
                interview.reminder_date = now
                interview.save()

                self.stdout.write(
                    self.style.SUCCESS(f'Напоминание отправлено для собеседования с {interview.candidate}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при отправке напоминания: {e}')
                )