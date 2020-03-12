from django.forms import ModelForm
from users.models import Person

class RegisterForm(ModelForm):
    # Add validation for fields
    class Meta:
        model = Person
        exclude = ['code']
        # labels = {'name': 'نام', 'last_name': 'نام خانوادگی', 'email': 'ایمیل شما', 'password': 'کلمه عبور'}
        help_texts = {'name': ('لطفا اینجا اسمتون رو بنویسید توجه کنید که باید حداقل 4 کاراکتر باشه (default 4).'),
                                'last_name': ('لطفا اینجا فامیلیتون رو بنویسید توجه کنید که باید حداقل 4 کاراکتر باشه (default 4).'),
                                'email': ('لینک تایید ساخت اکانت به این آدرس فرستاده می‌شود'),
                                'password': ('لطفا اینجا رمز یا کلمه عبورتون رو بنویسید توجه کنید که باید حداقل 8 کاراکتر باشه')}
        # error_messages = {'name': ('اسمتون رو خوب انتخاب نکردین لطفا دوباره تلاش کنین.'),
        #                                     'last_name': ('فامیلیتون رو خوب انتخاب نکردین لطفا دوباره تلاش کنین.'),
        #                                     'email': ('ایمیلتون معتبر نیست'),
        #                                     'password': ('کلمه عبورتون حداقل 8 کاراکتر نیست')}