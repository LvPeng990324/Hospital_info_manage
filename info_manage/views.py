from django.shortcuts import render, HttpResponse, redirect
from .models import Sicker, Doctor, ReceptionAdmin, Department, MedicineAdmin, MedicineCategory, Medicine, Prescription
import json
import datetime


# 主页
def index(request):
    return render(request, 'index.html')


# 注册
def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        home_location = request.POST.get('home_location')
        password = request.POST.get('password')
        password_again = request.POST.get('password_again')

        # 检验两次密码是否相同
        # 不相同返回二次密码不相同
        if password != password_again:
            return HttpResponse('二次密码不相同')
        # 生成病人编号
        # 规则为br加手机号
        sicker_id = 'br{}'.format(str(phone))
        # 将信息存入数据库
        Sicker.objects.get_or_create(
            sicker_id=sicker_id,
            name=name,
            gender=gender,
            phone=phone,
            home_location=home_location,
            password=password,
        )
        # 引导登录界面
        return redirect('login')

    else:
        # 先验证session是否有记录
        if request.session.get('is_login', None):
            # 已登录的重定向到个人页面
            return redirect('/show_user/')
        # 未登录的进入注册界面
        return render(request, 'signup.html')


# 登录
def login(request):
    if request.method == 'POST':
        login_id = request.POST.get('login_id')
        password = request.POST.get('password')
        # 从取出id前两位用来识别身份
        # 规则为：
        # br --> 病人
        # ys --> 医生
        # yp --> 药品管理员
        # ks --> 科室管理员
        # gh --> 挂号人员
        identity_code = login_id[:2]
        if identity_code == 'br':
            return login_sicker(request, login_id, password)
        elif identity_code == 'ys':
            return login_doctor(request, login_id, password)
        elif identity_code == 'yp':
            return login_medicine_admin(request, login_id, password)
        elif identity_code == 'ks':
            return login_department(request, login_id, password)
        elif identity_code == 'gh':
            return login_reception(request, login_id, password)
        else:
            return HttpResponse('id不存在')
    else:
        # 先验证session是否有记录
        if request.session.get('is_login', None):
            # 已登录的重定向到个人页面
            return redirect('/show_user/')
        # 未登录的进入登录界面
        return render(request, 'login.html')


# 用户界面展示
def show_user(request):
    # 验证是否未登录
    if not request.session.get('is_login', None):
        # 未登录的话重定向到登录界面
        return redirect('/login/')
    # 已经登录的正常引导显示信息界面
    # 先判断用户身份
    # 规则为：
    # br --> 病人
    # ys --> 医生
    # yp --> 药品管理员
    # ks --> 科室管理员
    # gh --> 挂号人员
    # 然后取出编号和密码传入相应的登录方法中
    identity_code = request.session.get('identity_code')
    if identity_code == 'br':
        login_id = request.session.get('user_id')
        password = Sicker.objects.get(sicker_id=login_id).password
        return login_sicker(request, login_id, password)
    elif identity_code == 'ys':
        login_id = request.session.get('user_id')
        password = Doctor.objects.get(doctor_id=login_id).password
        return login_doctor(request, login_id, password)
    elif identity_code == 'yp':
        login_id = request.session.get('user_id')
        password = MedicineAdmin.objects.get(medicine_admin_id=login_id).password
        return login_medicine_admin(request, login_id, password)
    elif identity_code == 'ks':
        login_id = request.session.get('user_id')
        password = Department.objects.get(department_id=login_id).password
        return login_department(request, login_id, password)
    elif identity_code == 'gh':
        login_id = request.session.get('user_id')
        password = ReceptionAdmin.objects.get(reception_admin_id=login_id).password
        return login_reception(request, login_id, password)
    else:
        HttpResponse('unknow error')


# 病人登录
def login_sicker(request, login_id, password):
    # 从病人表中查询该id
    # 查不到返回id不存在错误
    # 查到后比对密码,验证成功打包此病人信息并引导进入其首页
    sicker = Sicker.objects.filter(sicker_id=login_id)
    if not sicker:
        return HttpResponse('病人id不存在')
    sicker = sicker[0]
    if password != sicker.password:
        return HttpResponse('编号或密码错误')
    # 登录成功
    # 将信息记录session
    request.session['is_login'] = True  # 记录已登录
    request.session['user_id'] = login_id  # 记录编号
    request.session['identity_code'] = 'br'  # 记录用户身份code
    # 打包信息
    context = {
        'sicker_id': login_id,
        'name': sicker.name,
        'gender': sicker.gender,
        'phone': sicker.phone,
        'home_location': sicker.home_location,
        'money_to_pay': sicker.money_to_pay,
        'medicine': sicker.medicine,
        'department': sicker.department,
        'condition': sicker.condition,
    }
    # 如果有就诊医生就将医生信息打包
    if sicker.doctor_id:
        doctor = Doctor.objects.get(doctor_id=sicker.doctor_id)
        context['doctor'] = doctor
    # 引导页面
    return render(request, 'sicker.html', context=context)


# 病人更改个人信息
def change_sicker_information(request):
    if request.method == 'POST':
        sicker_id = request.session.get('user_id')
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        home_location = request.POST.get('home_location')
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        password_again = request.POST.get('password_again')

        # 先取出此人信息
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        # 验证密码是否正确
        # 如果不正确返回密码有误错误
        if password != sicker.password:
            return HttpResponse('密码有误！')
        # 判断是否输入了新密码
        # 输入的话就验证二次密码是否一致
        # 然后更新数据库
        if new_password:
            if new_password != password_again:
                return HttpResponse('二次密码不一致')
            password = new_password
        # 更新数据库
        sicker.name = name
        sicker.gender = gender
        sicker.phone = phone
        sicker.home_location = home_location
        sicker.password = password
        sicker.save()
        # 返回成功信息
        return HttpResponse('success')
    else:
        # 查询该病人信息
        sicker = Sicker.objects.get(sicker_id=request.session.get('user_id'))
        # 打包当前信息到前端
        context = {
            'name': sicker.name,
            'gender': sicker.gender,
            'phone': sicker.phone,
            'home_location': sicker.home_location,
        }
        return render(request, 'change_sicker_information.html', context=context)


# 病人线上缴费
def sicker_online_money_giving(request):
    if request.method == 'POST':
        sicker_id = request.POST.get('sicker_id')
        # 取出该病人
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        # 将该病人money_to_pay更新为0
        sicker.money_to_pay = 0
        # 保存到数据库
        sicker.save()
        # 重载病人页面
        return redirect('show_user')
    else:
        return redirect('show_user')


# 医生登录
def login_doctor(request, login_id, password):
    # 从医生表中查询该id
    # 查不到返回id不存在错误
    # 查到后比对密码,验证成功打包此医生以及就诊病人信息并引导进入其首页
    doctor = Doctor.objects.filter(doctor_id=login_id)
    if not doctor:
        return HttpResponse('医生id不存在')
    doctor = doctor[0]
    if password != doctor.password:
        return HttpResponse('编号或密码错误')
    # 登录成功
    # 将信息记录session
    request.session['is_login'] = True  # 记录已登录
    request.session['user_id'] = login_id  # 记录编号
    request.session['identity_code'] = 'ys'  # 记录用户身份code
    # 打包信息
    context = {
        'doctor_id': login_id,
        'name': doctor.name,
        'gender': doctor.gender,
        'phone': doctor.phone,
        'department': doctor.department,
        'is_working': doctor.is_working,
    }
    # 将所有病人信息打包信息打包
    sickers = Sicker.objects.filter(doctor_id=login_id)
    context['sickers'] = sickers
    # 引导页面
    return render(request, 'doctor.html', context=context)


# 医生上班打卡
def doctor_start_work(request):
    # 先取得此医生的编号
    doctor_id = request.session.get('user_id')
    # 从数据库中取出
    doctor = Doctor.objects.get(doctor_id=doctor_id)
    # 然后更改其状态为工作状态
    doctor.is_working = True
    # 保存更改
    doctor.save()
    # 重定向到其个人页面
    return redirect('/show_user/')


# 医生下班打卡
def doctor_stop_work(request):
    # 先取得此医生的编号
    doctor_id = request.session.get('user_id')
    # 查询此医生还有没有未处理完成的病人
    # 若有则不允许其下班
    sicker = Sicker.objects.filter(doctor_id=doctor_id)
    if sicker:
        return HttpResponse('您还有未处理完成的病人')
    # 若病人全部处理完则允许下班
    # 从数据库中取出
    doctor = Doctor.objects.get(doctor_id=doctor_id)
    # 然后更改其状态为非工作状态
    doctor.is_working = False
    # 保存更改
    doctor.save()
    # 重定向到其个人页面
    return redirect('/show_user/')


# 医生上传病人诊断结果
def doctor_upload_condition(request):
    if request.method == 'POST':
        sicker_id = request.POST.get('get_sicker_id')
        condition = request.POST.get('condition')
        # 取出该病人
        print(sicker_id)
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        # 更新病情诊断
        sicker.condition = condition
        # 保存更改
        sicker.save()
        # 返回医生页面
        return redirect('/show_user/')
    else:
        return redirect('/show_user/')


# 医生就诊结束
def doctor_finish_sicker(request):
    if request.method == 'POST':
        sicker_id = request.POST.get('sicker_id')
        # 从数据库中取出此病人
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        # 清空该病人的就诊信息，即除个人信息外的其他信息
        sicker.doctor_id = ''
        sicker.department = ''
        sicker.money_to_pay = 0
        sicker.condition = ''
        # 保存更改
        sicker.save()
        # 更新此医生的接诊人数
        doctor = Doctor.objects.get(doctor_id=request.session.get('user_id'))
        doctor.sicker_num -= 1
        doctor.save()
        # 重新引导医生页面
        return redirect('/show_user/')
    else:
        return redirect('/show_user/')


# 医生发起缴费
def doctor_ask_money(request):
    if request.method == 'POST':
        sicker_id = request.POST.get('sicker_id')
        ask_money = request.POST.get('ask_money')
        # 根据有无ask_money来判断是动作请求还是结果提交
        if not ask_money:
            # 没有ask_money，是动作请求
            # 引导ask_money页面并打包病人信息到前端
            context = get_sicker_medicine_information(sicker_id)
            # 引导页面
            return render(request, 'ask_money.html', context=context)
        # 有ask_money，是结果提交
        # 从数据库中取出该病人
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        # 更新其money_to_pay
        sicker.money_to_pay = ask_money
        # 保存更改
        sicker.save()
        # 引导回医生页面
        return redirect('show_user')
    else:
        return redirect('show_user')


# 医生开药
def doctor_make_prescription(request):
    # 用来查询药品的方法
    def search_medicine(request, medicine_name_piece, sicker_id):
        # 从数据库中模糊查询medicine_name_piece
        medicine = Medicine.objects.filter(name__contains=medicine_name_piece)
        # 建立存储药品对象实例的列表
        searched_medicine_list = []
        # 将搜索到的药品信息全部加入到searched_medicine_list中
        for medicine_name in medicine:
            searched_medicine_list.append(zip_medicine_information(medicine_name))
        # 将信息打包
        context = get_sicker_medicine_information(sicker_id)
        context['searched_medicine_list'] = searched_medicine_list
        # 将信息传给前端
        return render(request, 'make_prescription.html', context=context)

    if request.method == 'POST':
        sicker_id = request.POST.get('sicker_id')
        medicine_name_piece = request.POST.get('medicine_name_piece')
        medicine_name = request.POST.get('medicine_name')
        # 页面请求：有sicker_id没有medicine_name_piece和medicine_name
        # 药品查询：有medicine_name_piece
        # 确认开药：有medicine_name
        if sicker_id and not medicine_name_piece and not medicine_name:
            # 页面请求
            return show_make_prescription(request, sicker_id)
        if medicine_name_piece:
            # 药品查询
            return search_medicine(request, medicine_name_piece, sicker_id)
        if medicine_name:
            # 确认开药
            pass

    else:
        redirect('show_user')


# 用来打包药品信息的方法
def zip_medicine_information(medicine_name, sicker_id=''):
    class ZippedMedicine:
        name = ''
        price = 0
        introduction = ''
        category = ''
        remain_number = 0
        prescription_num = 0

    # 从数据库中搜索此药品
    medicine = Medicine.objects.get(name=medicine_name)
    # 实例化
    zipped_medicine = ZippedMedicine()
    zipped_medicine.name = medicine.name
    zipped_medicine.price = medicine.price
    zipped_medicine.introduction = medicine.introduction
    zipped_medicine.category = medicine.category
    zipped_medicine.remain_number = medicine.remain_number
    # 如果有sicker_id则添加prescription_num属性
    if sicker_id:
        # 取出病人
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        # 将该病人的开药记录转为字典
        sicker_medicine = json.loads(sicker.medicine)
        # 添加到实例中
        zipped_medicine.prescription_num = sicker_medicine[medicine_name]
    # 返回实例
    return zipped_medicine


# 返回病人信息以及病人开的所有药品的信息方法
def get_sicker_medicine_information(sicker_id):
    # 取出病人
    sicker = Sicker.objects.get(sicker_id=sicker_id)
    # 将该病人的开药记录转为字典
    medicine = json.loads(sicker.medicine)
    # 建立存储药品对象实例的列表
    medicine_list = []
    # 将给该病人开的所有药信息加入到medicine_list中
    for medicine_name in medicine.keys():
        medicine_list.append(zip_medicine_information(medicine_name, sicker_id))
    # 将信息打包
    context = {
        'medicine_list': medicine_list,
        'sicker': sicker,
    }
    # 返回信息
    return context


# 用来显示开药界面的方法(待改进，将药品信息打包进对象)
def show_make_prescription(request, sicker_id):
    context = get_sicker_medicine_information(sicker_id)
    # 引导前端页面
    return render(request, 'make_prescription.html', context=context)


# 处方添加药品方法
def add_medicine_to_prescription(request):
    sicker_id = request.POST.get('sicker_id')
    medicine_name = request.POST.get('medicine_name')
    # 从数据库中取出此病人
    sicker = Sicker.objects.get(sicker_id=sicker_id)
    # 将给此病人开的药转换为字典
    prescription_medicine = json.loads(sicker.medicine)
    # 如果要增加的药品已有，则自增1
    # 如果没有，则新建并赋值为1
    if medicine_name in prescription_medicine.keys():
        # 已有，自增1
        prescription_medicine[medicine_name] += 1
    else:
        # 没有，新建并赋值为1
        prescription_medicine[medicine_name] = 1
    # 将prescription_medicine转为字符串并存入数据库
    row_data = json.dumps(prescription_medicine)
    sicker.medicine = row_data
    sicker.save()
    # 重载开药界面
    # 打包数据
    context = get_sicker_medicine_information(sicker_id)
    # 引导页面
    return show_make_prescription(request, sicker_id)


# 减少药品方法
def reduce_medicine_to_prescription(request):
    sicker_id = request.POST.get('sicker_id')
    medicine_name = request.POST.get('medicine_name')
    # 从数据库中取出此病人
    sicker = Sicker.objects.get(sicker_id=sicker_id)
    # 将给此病人开的药转换为字典
    prescription_medicine = json.loads(sicker.medicine)
    # 如果要增加的药品已有，则自减1
    # 如果没有，则新建并赋值为1
    # 如果减完后为0，则删除它
    if medicine_name in prescription_medicine.keys():
        # 已有，自减1
        prescription_medicine[medicine_name] -= 1
        # 如果变成0，则删除
        if prescription_medicine[medicine_name] == 0:
            prescription_medicine.pop(medicine_name)
    else:
        # 没有，新建并赋值为1
        prescription_medicine[medicine_name] = 1
    # 将prescription_medicine转为字符串并存入数据库
    row_data = json.dumps(prescription_medicine)
    sicker.medicine = row_data
    sicker.save()
    # 重载开药界面
    # 打包数据
    context = get_sicker_medicine_information(sicker_id)
    # 引导页面
    return show_make_prescription(request, sicker_id)


# 确认开药
# 也就是将处方单保存备份
def save_prescription(request):
    sicker_id = request.POST.get('sicker_id')
    doctor_id = request.session.get('user_id')
    # 取出此病人
    sicker = Sicker.objects.get(sicker_id=sicker_id)
    # 将开药信息转为字典
    prescription_medicine = json.loads(sicker.medicine)
    # 将处方单内容记录到字符串中
    prescription_content = ''
    for medicine_name, medicine_num in prescription_medicine.items():
        prescription_content += '{} --> {}份\n'.format(medicine_name, medicine_num)
    # 生成处方编号
    # 规则：病人编号+医生编号+日期
    # 获取当前日期
    now_date = str(datetime.date.today())
    # 组合编号
    prescription_id = '{}_{}_{}'.format(sicker_id, doctor_id, now_date)
    # 保存到数据库
    Prescription.objects.create(
        prescription_id=prescription_id,
        sicker_id=sicker_id,
        doctor_id=doctor_id,
        content=prescription_content,
    )
    # 返回医生页面
    return redirect('show_user')


# 药品管理员登录
def login_medicine_admin(request, login_id, password):
    # 从药品管理员表中查询该id
    # 查不到返回id不存在错误
    # 查到后比对密码,验证成功打包此管理员信息并引导进入其首页
    medicine_admin = MedicineAdmin.objects.filter(medicine_admin_id=login_id)
    if not medicine_admin:
        return HttpResponse('药品管理员id不存在')
    medicine_admin = medicine_admin[0]
    if password != medicine_admin.password:
        return HttpResponse('编号或密码错误')
    # 登录成功
    # 将信息记录session
    request.session['is_login'] = True  # 记录已登录
    request.session['user_id'] = login_id  # 记录编号
    request.session['identity_code'] = 'yp'  # 记录用户身份code
    # 打包信息
    context = {
        'medicine_admin_id': login_id,
        'name': medicine_admin.name,
        'gender': medicine_admin.gender,
        'phone': medicine_admin.phone,
    }
    # 引导页面
    return render(request, 'manage_medicine.html', context=context)


# 药品管理员搜索药品方法
def manage_medicine_search_medicine(request):
    if request.method == 'POST':
        medicine_name_piece = request.POST.get('medicine_name_piece')
        # 从药品表中模糊搜索
        searched_medicine = Medicine.objects.filter(name__contains=medicine_name_piece)
        # 打包信息
        context = {
            'name': MedicineAdmin.objects.get(medicine_admin_id=request.session.get('user_id')).name,
            'searched_medicine': searched_medicine,
        }
        # 重载前端页面
        return render(request, 'manage_medicine.html', context=context)
    else:
        return redirect('show_user')


# 更改药品信息方法
def change_medicine_information(request):
    if request.method == 'POST':
        old_name = request.POST.get('old_name')
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        introduction = request.POST.get('introduction')
        # 取出此药品
        medicine = Medicine.objects.get(name=old_name)
        # 更新数据库
        medicine.name = name
        medicine.category = category
        medicine.price = price
        medicine.introduction = introduction
        # 保存更改
        medicine.save()
        # 重载药品管理员界面
        return redirect('show_user')

    else:
        medicine_name = request.GET.get('medicine_name')
        # 从数据库中取出此药品
        medicine = Medicine.objects.get(name=medicine_name)
        # 打包信息
        context = {
            'name': medicine.name,
            'category': medicine.category,
            'price': medicine.price,
            'introduction': medicine.introduction,
            'category_list': MedicineCategory.objects.all(),
        }
        # 引导前端页面
        return render(request, 'change_medicine_information.html', context=context)


# 更改药品库存方法
def change_medicine_remain_num(request):
    if request.method == 'POST':
        medicine_name = request.POST.get('get_medicine_name')
        change_num = int(request.POST.get('change_num'))
        # 取出此药品
        medicine = Medicine.objects.get(name=medicine_name)
        # 计算更改后药品库存
        now_remain_num = medicine.remain_number + change_num
        # 判断更改后库存是否小于0
        # 如果小于0则返回库存不足错误
        if now_remain_num < 0:
            return HttpResponse('{}库存不足'.format(medicine_name))
        # 更新药品库存
        medicine.remain_number = now_remain_num
        # 保存更改
        medicine.save()
        # 重载页面
        return redirect('show_user')
    else:
        redirect('show_user')


# 增加药品方法
def add_medicine(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        remain_num = request.POST.get('remain_num')
        introduction = request.POST.get('introduction')
        # 存入数据库
        Medicine.objects.create(
            name=name,
            category=category,
            price=price,
            remain_number=remain_num,
            introduction=introduction,
        )
        # 重载页面
        return redirect('show_user')
    else:
        # 打包所有药品分类
        context = {
            'category_list': MedicineCategory.objects.all(),
        }
        return render(request, 'add_medicine.html', context=context)


# 药品管理员给药方开药
def give_prescription_medicine(request):
    if request.method == 'POST':
        sicker_id = request.POST.get('sicker_id')
        # 从数据库中取出该病人的药方并转为字典
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        sicker_medicine = json.loads(Sicker.objects.get(sicker_id=sicker_id).medicine)
        # 遍历病人药方并从库存中减去开的数量
        for name, num in sicker_medicine.items():
            temp_medicine = Medicine.objects.get(name=name)
            temp_medicine.remain_number -= num
            temp_medicine.save()
        # 清空该病人的药方
        sicker.medicine = '{}'
        # 保存更改
        sicker.save()
        # 重载管理员页面
        return redirect('show_user')
    else:
        sicker_id = request.GET.get('sicker_id')
        # 从数据库中取出该病人
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        # 查询是否未缴费
        # 如果未缴费返回该病人未缴费错误
        if sicker.money_to_pay > 0:
            return HttpResponse('该病人还有{}元未缴费'.format(sicker.money_to_pay))
        # 将该病人药方转为字典
        sicker_medicine = json.loads(sicker.medicine)
        # 查询这些药品的库存并保存到另一字典中
        hospital_medicine = {}
        for medicine in sicker_medicine.keys():
            hospital_medicine[medicine] = Medicine.objects.get(name=medicine).remain_number

        # 创建药品名称-数量-库存对象
        class MedicineNum:
            name = ''
            sicker_num = 0
            remain_num = 0

        # 实例化MedicineNum
        # 建立两个列表存储病人药方药品-数量以及医院库存
        medicine_list = []
        for name, sicker_num in sicker_medicine.items():
            temp_medicine = MedicineNum()
            temp_medicine.name = name
            temp_medicine.sicker_num = sicker_num
            temp_medicine.remain_num = Medicine.objects.get(name=name).remain_number
            medicine_list.append(temp_medicine)
        # 打包发送给确认开药界面
        context = {
            'sicker_name': sicker.name,
            'sicker_id': sicker.sicker_id,
            'medicine_list': medicine_list,
        }
        return render(request, 'give_prescription_medicine.html', context=context)


# 科室管理员登录
def login_department(request, login_id, password):
    # 从科室管理员表中查询该id
    # 查不到返回id不存在错误
    # 查到后比对密码,验证成功打包此管理员信息并引导进入其首页
    department = Department.objects.filter(department_id=login_id)
    if not department:
        return HttpResponse('科室管理员id不存在')
    department = department[0]
    if password != department.password:
        return HttpResponse('编号或密码错误')
    # 登录成功
    # 将信息记录session
    request.session['is_login'] = True  # 记录已登录
    request.session['user_id'] = login_id  # 记录编号
    request.session['identity_code'] = 'ks'  # 记录用户身份code
    # 打包信息
    department_master = Doctor.objects.get(doctor_id=department.master_id)
    # 取出该科室所有医生信息
    doctors = Doctor.objects.filter(department=department.name)
    # 取出该科室所有就诊病人信息并计数
    sickers = Sicker.objects.filter(department=department.name)
    sickers_num = len(sickers)
    context = {
        'department_master_id': login_id,
        'department_name': department.name,
        'department_master_name': department_master.name,
        'gender': department_master.gender,
        'phone': department_master.phone,
        'doctors': doctors,
        'sickers': sickers,
        'sickers_num': sickers_num,
    }
    # 引导页面
    return render(request, 'department.html', context=context)


# 挂号人员登录
def login_reception(request, login_id, password):
    # 从挂号管理员表中查询该id
    # 查不到返回id不存在错误
    # 查到后比对密码,验证成功打包此管理员以及工作中医生信息并引导进入其首页
    reception_admin = ReceptionAdmin.objects.filter(reception_admin_id=login_id)
    if not reception_admin:
        return HttpResponse('挂号管理员id不存在')
    reception_admin = reception_admin[0]
    if password != reception_admin.password:
        return HttpResponse('编号或密码错误')
    # 登录成功
    # 将信息记录session
    request.session['is_login'] = True  # 记录已登录
    request.session['user_id'] = login_id  # 记录编号
    request.session['identity_code'] = 'gh'  # 记录用户身份code
    # 打包信息
    # 取出所有当前工作中医生
    doctors = Doctor.objects.filter(is_working=True)
    context = {
        'reception_admin_id': login_id,
        'name': reception_admin.name,
        'gender': reception_admin.gender,
        'phone': reception_admin.phone,
        'doctors': doctors,
    }
    # 引导页面
    return render(request, 'reception.html', context=context)


# 挂号病人方法
def make_reception(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('get_doctor_id')
        sicker_id = request.POST.get('sicker_id')
        # 取出该病人及医生
        sicker = Sicker.objects.get(sicker_id=sicker_id)
        doctor = Doctor.objects.get(doctor_id=doctor_id)
        # 更新病人的就诊医生编号以及就诊科室
        sicker.doctor_id = doctor_id
        sicker.department = doctor.department
        # 保存更改
        sicker.save()
        # 更新该医生的接诊人数
        doctor.sicker_num += 1
        # 保存更改
        doctor.save()
        # 重载页面
        return redirect('show_user')
    else:
        return redirect('show_user')


# 退出登录
def logout(request):
    # 清空session
    request.session.flush()
    # 重定向登录界面
    return redirect('/login/')
