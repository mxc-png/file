
# 本示例程序演示如何通过 boot.py 文件进行 soft-boot 控制后执行自己的源文件
# 使用 RT1021-MicroPython 核心板搭配对应拓展学习板的拨码开关控制

# 示例程序运行效果为复位后执行本文件 通过 D8 电平状态跳转执行 user_main.py
# C4 LED 会一秒周期闪烁
# 当 D9 引脚电平出现变化时退出测试程序

# 包含 display 库
from display import *

# 从 machine 库包含所有内容
from machine import *

#从motor库包含所有内容
from motor import *

# 包含 gc 与 time 类
import gc
import time

# 从 smartcar 库包含 ticker encoder
from smartcar import ticker
from smartcar import encoder


# 学习板上 D9  对应二号拨码开关

# 调用 machine 库的 Pin 类实例化一个引脚对象
# 配置参数为 引脚名称 引脚方向 模式配置 默认电平
# 详细内容参考 固件接口说明

switch2 = Pin('D9' , Pin.IN , pull = Pin.PULL_UP_47K, value = True)
state2  = switch2.value()

encoder_3 = encoder("C2" , "C3" , True)
encoder_4 = encoder("C0" , "C1" )

ticker_flag = False
ticker_count = 0

# 定义一个回调函数 需要一个参数 这个参数就是 ticker 实例自身
def time_pit_handler(time):
    global ticker_flag  # 需要注意的是这里得使用 global 修饰全局属性
    global ticker_count
    ticker_flag = True  # 否则它会新建一个局部变量
    ticker_count = (ticker_count + 1) if (ticker_count < 100) else (1)

# 实例化 PIT ticker 模块 参数为编号 [0-3] 最多四个
pit1 = ticker(1)

pit1.capture_list(encoder_3, encoder_4)

# 关联 Python 回调函数
pit1.callback(time_pit_handler)




# 定义片选引脚
cs = Pin('B29' , Pin.OUT, pull=Pin.PULL_UP_47K, value=1)
# 拉高拉低一次 CS 片选确保屏幕通信时序正常
cs.high()
cs.low()
# 定义控制引脚
rst = Pin('B31', Pin.OUT, pull=Pin.PULL_UP_47K, value=1)
dc  = Pin('B5' , Pin.OUT, pull=Pin.PULL_UP_47K, value=1)
blk = Pin('C21', Pin.OUT, pull=Pin.PULL_UP_47K, value=1)
# 新建 LCD 驱动实例 这里的索引范围与 SPI 示例一致 当前仅支持 IPS200
drv = LCD_Drv(SPI_INDEX=2, BAUDRATE=60000000, DC_PIN=dc, RST_PIN=rst, LCD_TYPE=LCD_Drv.LCD200_TYPE)
# 新建 LCD 实例
lcd = LCD(drv)
# color 接口设置屏幕显示颜色 [前景色,背景色]
lcd.color(0xFFFF, 0x0000)
# mode 接口设置屏幕显示模式 [0:竖屏,1:横屏,2:竖屏180旋转,3:横屏180旋转]
lcd.mode(2)
# 清屏 不传入参数就使用当前的 背景色 清屏
# 传入 RGB565 格式参数会直接把传入的颜色设置为背景色 然后清屏
lcd.clear(0x0000)



while True:
    motor_3,motor_4=motor_init()
    if (ticker_flag and ticker_count % 20 == 0):
        enc3_data = encoder_3.get()
        enc4_data = encoder_4.get()
        lcd.str12(0,  0, "left={:d}.".format(enc3_data), 0xF800)
        lcd.str16(0, 12, "right={:d}.".format(enc4_data), 0x07E0)
        ticker_flag = False
        
    # 如果拨码开关打开 对应引脚拉低 就退出循环
    # 这么做是为了防止写错代码导致异常 有一个退出的手段
    if switch2.value() != state2:
        pit1.stop()
        print("Test program stop.")
        break

    gc.collect()
