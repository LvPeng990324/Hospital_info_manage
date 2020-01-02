from django.urls import path
from . import views

urlpatterns = [
    # 首页
    path('index/', views.index, name='index'),
    # 登录
    path('login/', views.login, name='login'),
    # 注册
    path('signup/', views.signup, name='signup'),
    # 显示用户页面
    path('show_user/', views.show_user, name='show_user'),
    # 病人更改个人信息
    path('change_sicker_information/', views.change_sicker_information, name='change_sicker_information'),
    # 病人线上缴费
    path('sicker_online_money_giving/', views.sicker_online_money_giving, name='sicker_online_money_giving'),
    # 登出
    path('logout/', views.logout, name='logout'),
    # 医生上班打卡
    path('doctor_start_work/', views.doctor_start_work, name='doctor_start_work'),
    # 医生下班打卡
    path('doctor_stop_work/', views.doctor_stop_work, name='doctor_stop_work'),
    # 医生上病人传病情诊断
    path('doctor_upload_condition/', views.doctor_upload_condition, name='doctor_upload_condition'),
    # 医生就诊结束
    path('doctor_finish_sicker/', views.doctor_finish_sicker, name='doctor_finish_sicker'),
    # 医生发起缴费
    path('doctor_ask_money', views.doctor_ask_money, name='doctor_ask_money'),
    # 医生开药
    path('doctor_make_prescription/', views.doctor_make_prescription, name='doctor_make_prescription'),
    # 增加药品方法
    path('add_medicine_to_prescription/', views.add_medicine_to_prescription, name='add_medicine_to_prescription'),
    # 减少药品方法
    path('reduce_medicine_to_prescription/', views.reduce_medicine_to_prescription, name='reduce_medicine_to_prescription'),
    # 确认开药(保存处方单)
    path('save_prescription/', views.save_prescription, name='save_prescription'),
    # 药品管理员搜索药品方法
    path('manage_medicine_search_medicine/', views.manage_medicine_search_medicine, name='manage_medicine_search_medicine'),
    # 修改药品信息方法
    path('change_medicine_information/', views.change_medicine_information, name='change_medicine_information'),
    # 更改药品库存方法
    path('change_medicine_remain_num/', views.change_medicine_remain_num, name='change_medicine_remain_num'),
    # 挂号病人方法
    path('make_reception/', views.make_reception, name='make_reception'),

    # 测试界面，正式上线删掉
    path('test/', views.test, name='test'),
]
