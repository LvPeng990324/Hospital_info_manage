from django.db import models


# 病人
class Sicker(models.Model):
    sicker_id = models.CharField(max_length=20, primary_key=True, verbose_name='编号')
    password = models.CharField(max_length=20, verbose_name='密码')
    name = models.CharField(max_length=100, verbose_name='姓名')
    gender = models.CharField(max_length=2, verbose_name='性别')
    phone = models.CharField(max_length=15, verbose_name='联系电话')
    home_location = models.CharField(max_length=100, verbose_name='家庭住址')
    department = models.CharField(max_length=20, verbose_name='挂号科室')
    doctor_id = models.CharField(max_length=20, verbose_name='就诊医生编号')
    condition = models.TextField(verbose_name='病情诊断')
    medicine = models.TextField(default='{}', verbose_name='开的药')
    money_to_pay = models.FloatField(default=0, verbose_name='待缴费')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '病人'
        verbose_name = '病人'


# 医生
class Doctor(models.Model):
    doctor_id = models.CharField(max_length=20, primary_key=True, verbose_name='编号')
    password = models.CharField(max_length=20, verbose_name='密码')
    name = models.CharField(max_length=100, verbose_name='姓名')
    gender = models.CharField(max_length=2, verbose_name='性别')
    phone = models.CharField(max_length=15, verbose_name='联系电话')
    department = models.CharField(max_length=20, verbose_name='所在科室')
    sicker_num = models.IntegerField(verbose_name='接诊人数')
    is_working = models.BooleanField(default=False, verbose_name='是否在工作')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '医生'
        verbose_name = '医生'


# 科室
class Department(models.Model):
    department_id = models.CharField(max_length=20, primary_key=True, verbose_name='科室编号')
    name = models.CharField(max_length=20, verbose_name='科室名称')
    password = models.CharField(max_length=20, verbose_name='密码')
    master_id = models.CharField(max_length=20, verbose_name='科室长编号')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '科室'
        verbose_name = '科室'


# 挂号管理员
class ReceptionAdmin(models.Model):
    reception_admin_id = models.CharField(max_length=20, primary_key=True, verbose_name='编号')
    password = models.CharField(max_length=20, verbose_name='密码')
    name = models.CharField(max_length=100, verbose_name='姓名')
    gender = models.CharField(max_length=2, verbose_name='性别')
    phone = models.CharField(max_length=15, verbose_name='联系电话')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '挂号管理员'
        verbose_name = '挂号管理员'


# 药品管理员
class MedicineAdmin(models.Model):
    medicine_admin_id = models.CharField(max_length=20, primary_key=True, verbose_name='编号')
    password = models.CharField(max_length=20, verbose_name='密码')
    name = models.CharField(max_length=100, verbose_name='姓名')
    gender = models.CharField(max_length=2, verbose_name='性别')
    phone = models.CharField(max_length=15, verbose_name='联系电话')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '药品管理员'
        verbose_name = '药品管理员'


# 药品分类
class MedicineCategory(models.Model):
    name = models.CharField(max_length=100, primary_key=True, verbose_name='药品分类名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '药品分类'
        verbose_name = '药品分类'


# 药品
class Medicine(models.Model):
    name = models.CharField(max_length=100, primary_key=True, verbose_name='药品名称')
    introduction = models.TextField(verbose_name='药品简介')
    category = models.CharField(max_length=100, verbose_name='药品分类')
    price = models.FloatField(verbose_name='药品价格')
    remain_number = models.IntegerField(verbose_name='库存')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '药品'
        verbose_name = '药品'


# 处方
class Prescription(models.Model):
    prescription_id = models.CharField(max_length=50, primary_key=True, verbose_name='处方编号')
    doctor_id = models.CharField(max_length=20, verbose_name='医生编号')
    sicker_id = models.CharField(max_length=20, verbose_name='病人编号')
    content = models.TextField(verbose_name='处方内容')
    given_date = models.DateTimeField(auto_now_add=True, verbose_name='开具日期')

    def __str__(self):
        return self.prescription_id

    class Meta:
        verbose_name_plural = '处方'
        verbose_name = '处方'




