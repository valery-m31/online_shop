
from celery.decorators import task

from django.core.mail import send_mail


EMAIL_HOST_USER = 'youremail@gmail.com'

@task(name="send_email_task")
def send_order_email(to_email, titles, prices, quantity, sum_total):
    message = ''
    total = 0
    for i, title in enumerate(titles):
        message += f"{titles[i]} Price {prices[i]} Quantity {quantity[i]} \
             Item total price {sum_total[i]} \n"
    for i in sum_total:
        total += i
    message += f"\nTotal {total}"
    send_mail(
        'Order Info',
        message,
        EMAIL_HOST_USER,
        [to_email,],
        fail_silently=False
        )
